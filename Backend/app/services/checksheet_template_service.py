from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.checksheet_template import ChecksheetTemplate
from app.models.equipment import Equipment
from app.models.section_equipment_map import SectionEquipmentMap
from app.models.template_field import TemplateField
from app.models.user import User
from app.schemas.checksheet_template import (
    ChecksheetTemplateCreate,
    ChecksheetTemplateUpdate
)
from app.security.section_scope import supervisor_section_id


def _get_common_section_template(db: Session, section_id: int):
    """The section-wide 'common page' template for a section (Module 29.5) - equipment_id NULL,
    section_id set. At most one may exist per section (enforced in create_template)."""
    return (
        db.query(ChecksheetTemplate)
        .options(joinedload(ChecksheetTemplate.fields))
        .filter(
            ChecksheetTemplate.section_id == section_id,
            ChecksheetTemplate.equipment_id.is_(None),
            ChecksheetTemplate.is_active == True,  # noqa: E712
        )
        .first()
    )


def create_template(db: Session, template: ChecksheetTemplateCreate):
    version = template.version or 1

    if template.equipment_id is None and template.section_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either equipment_id (equipment-specific template) or section_id (section-wide common page) is required."
        )

    if template.equipment_id is None and template.section_id is not None:
        # A section-wide common page template - "Every equipment belonging to Section X shall
        # automatically begin with A common first page" (singular), so only one may exist per
        # section at a time.
        existing_common = _get_common_section_template(db, template.section_id)
        if existing_common is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This section already has an active common-page template."
            )

    existing = db.query(ChecksheetTemplate).filter(
        ChecksheetTemplate.template_code == template.template_code,
        ChecksheetTemplate.version == version
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Template code '{template.template_code}' with version {version} already exists."
        )

    new_template = ChecksheetTemplate(
        template_code=template.template_code,
        version=version,
        equipment_id=template.equipment_id,
        section_id=template.section_id,
        technology=template.technology,
        maintenance_type=template.maintenance_type,
        template_name=template.template_name,
        description=template.description
    )

    db.add(new_template)
    db.commit()
    db.refresh(new_template)

    return new_template


def _scope_to_section(query, section_id: int):
    # ChecksheetTemplate has no section_id of its own for equipment-specific templates -
    # "available for a section" means its equipment is mapped to that section via
    # SectionEquipmentMap (see Module 27.5). Common-page templates (equipment_id NULL) are scoped
    # directly by their own section_id instead - a Supervisor must still see their own section's
    # common page in the plain template list.
    from sqlalchemy import or_

    return (
        query.outerjoin(Equipment, ChecksheetTemplate.equipment_id == Equipment.id)
        .outerjoin(SectionEquipmentMap, SectionEquipmentMap.equipment_id == Equipment.id)
        .filter(
            or_(
                SectionEquipmentMap.section_id == section_id,
                ChecksheetTemplate.section_id == section_id,
            )
        )
        .distinct()
    )


def get_templates(db: Session, current_user: User | None = None):
    query = db.query(ChecksheetTemplate)

    scoped_section_id = supervisor_section_id(current_user) if current_user else None
    if scoped_section_id is not None:
        query = _scope_to_section(query, scoped_section_id)

    return query.all()


def get_template_by_id(db: Session, template_id: int):
    return db.query(ChecksheetTemplate).filter(
        ChecksheetTemplate.id == template_id
    ).first()


def _field_to_dict(field: TemplateField) -> dict:
    return {
        "id": field.id,
        "template_id": field.template_id,
        "field_key": field.field_key,
        "field_label": field.field_label,
        "field_type": field.field_type,
        "display_order": field.display_order,
        "required": field.required,
        "unit": field.unit,
        "default_value": field.default_value,
        "options": field.options,
        "help_text": field.help_text,
        "is_active": field.is_active,
        "min_value": field.min_value,
        "max_value": field.max_value,
        "decimal_precision": field.decimal_precision,
        "standard_value": field.standard_value,
        "authority_reference": field.authority_reference,
        "parent_field_id": field.parent_field_id,
        "page_number": field.page_number,
    }


def _compose_fields(common_template: ChecksheetTemplate | None, target_fields: list[TemplateField]) -> list[dict]:
    """Module 29.5: prepends a section's common page(s) ahead of an equipment template's own
    pages, renumbering the equipment template's page_number so the two never collide - e.g. a
    1-page common template turns the equipment template's own page 1 into composed page 2, its
    page 2 into page 3, and so on. Fully data-driven: nothing here is specific to any equipment or
    section, it only depends on whichever common template (if any) is passed in.
    """
    sorted_target = sorted(
        (f for f in target_fields if f.is_active),
        key=lambda f: (f.page_number, f.display_order)
    )

    if common_template is None:
        return [_field_to_dict(f) for f in sorted_target]

    common_fields = sorted(
        (f for f in common_template.fields if f.is_active),
        key=lambda f: (f.page_number, f.display_order)
    )
    common_max_page = max((f.page_number for f in common_fields), default=0)

    composed = [_field_to_dict(f) for f in common_fields]
    for f in sorted_target:
        item = _field_to_dict(f)
        item["page_number"] = f.page_number + common_max_page
        composed.append(item)
    return composed


def get_template_detail(
    db: Session,
    template_id: int,
    current_user: User | None = None,
    section_id: int | None = None,
):
    template = db.query(ChecksheetTemplate).options(
        joinedload(ChecksheetTemplate.fields)
    ).filter(ChecksheetTemplate.id == template_id).first()

    if template is None:
        return None

    scoped_section_id = supervisor_section_id(current_user) if current_user else None
    if scoped_section_id is not None:
        allowed = _scope_to_section(
            db.query(ChecksheetTemplate).filter(ChecksheetTemplate.id == template_id),
            scoped_section_id
        ).first()
        if allowed is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Compose in the section's common page(s) ahead of this template's own fields, only when the
    # caller both asked for it (section_id passed) and this is an equipment-specific template (a
    # common-page template fetched directly must never try to prepend itself to itself).
    common_template = None
    if section_id is not None and template.equipment_id is not None:
        common_template = _get_common_section_template(db, section_id)

    composed_fields = _compose_fields(common_template, list(template.fields))

    return {
        "id": template.id,
        "template_code": template.template_code,
        "version": template.version,
        "equipment_id": template.equipment_id,
        "section_id": template.section_id,
        "technology": template.technology,
        "maintenance_type": template.maintenance_type,
        "template_name": template.template_name,
        "description": template.description,
        "is_active": template.is_active,
        "fields": composed_fields,
    }


def update_template(db: Session, template_id: int, template: ChecksheetTemplateUpdate):
    existing_template = get_template_by_id(db, template_id)
    if not existing_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    if template.template_code is not None:
        existing_template.template_code = template.template_code

    if template.version is not None:
        existing_template.version = template.version

    if template.template_code is not None or template.version is not None:
        duplicate = db.query(ChecksheetTemplate).filter(
            ChecksheetTemplate.template_code == existing_template.template_code,
            ChecksheetTemplate.version == existing_template.version,
            ChecksheetTemplate.id != template_id
        ).first()
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Template code '{existing_template.template_code}' with version {existing_template.version} already exists."
            )

    if template.equipment_id is not None:
        existing_template.equipment_id = template.equipment_id

    if template.section_id is not None:
        existing_template.section_id = template.section_id

    if template.technology is not None:
        existing_template.technology = template.technology

    if template.maintenance_type is not None:
        existing_template.maintenance_type = template.maintenance_type

    if template.template_name is not None:
        existing_template.template_name = template.template_name

    if template.description is not None:
        existing_template.description = template.description

    if template.is_active is not None:
        existing_template.is_active = template.is_active

    db.commit()
    db.refresh(existing_template)
    return existing_template


def delete_template(db: Session, template_id: int):
    template = get_template_by_id(db, template_id)

    if template:
        db.delete(template)
        db.commit()

    return template
