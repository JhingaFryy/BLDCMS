from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.checksheet_template import ChecksheetTemplate
from app.models.checksheet_value import ChecksheetValue
from app.models.template_field import TemplateField
from app.schemas.template_field import TemplateFieldCreate, TemplateFieldUpdate


def create_field(db: Session, field: TemplateFieldCreate):
    if not db.query(ChecksheetTemplate.id).filter(ChecksheetTemplate.id == field.template_id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Template not found")

    new_field = TemplateField(
        template_id=field.template_id,
        field_key=field.field_key,
        field_label=field.field_label,
        field_type=field.field_type,
        display_order=field.display_order,
        required=field.required,
        unit=field.unit,
        default_value=field.default_value,
        options=field.options,
        help_text=field.help_text,
        min_value=field.min_value,
        max_value=field.max_value,
        decimal_precision=field.decimal_precision,
        standard_value=field.standard_value,
        authority_reference=field.authority_reference,
        parent_field_id=field.parent_field_id,
        page_number=field.page_number
    )

    db.add(new_field)
    db.commit()
    db.refresh(new_field)

    return new_field


def get_fields_by_template(db: Session, template_id: int):
    # Archived fields (is_deleted) must not appear while editing a template - they're kept only
    # for historical checksheet_value integrity, never for further editing. This is distinct from
    # is_active, which an admin can still toggle for a field that was never archived.
    return (
        db.query(TemplateField)
        .filter(
            TemplateField.template_id == template_id,
            TemplateField.is_deleted == False,  # noqa: E712
        )
        .order_by(TemplateField.display_order)
        .all()
    )


def get_field_by_id(db: Session, field_id: int):
    return db.query(TemplateField).filter(TemplateField.id == field_id).first()


def update_field(db: Session, field_id: int, field: TemplateFieldUpdate):
    existing_field = get_field_by_id(db, field_id)
    if not existing_field:
        return None

    if field.field_key is not None:
        existing_field.field_key = field.field_key
    if field.field_label is not None:
        existing_field.field_label = field.field_label
    if field.field_type is not None:
        existing_field.field_type = field.field_type
    if field.display_order is not None:
        existing_field.display_order = field.display_order
    if field.required is not None:
        existing_field.required = field.required
    if field.unit is not None:
        existing_field.unit = field.unit
    if field.default_value is not None:
        existing_field.default_value = field.default_value
    if field.options is not None:
        existing_field.options = field.options
    if field.help_text is not None:
        existing_field.help_text = field.help_text
    if field.is_active is not None:
        existing_field.is_active = field.is_active
    if field.min_value is not None:
        existing_field.min_value = field.min_value
    if field.max_value is not None:
        existing_field.max_value = field.max_value
    if field.decimal_precision is not None:
        existing_field.decimal_precision = field.decimal_precision
    if field.standard_value is not None:
        existing_field.standard_value = field.standard_value
    if field.authority_reference is not None:
        existing_field.authority_reference = field.authority_reference
    if field.parent_field_id is not None:
        existing_field.parent_field_id = field.parent_field_id
    if field.page_number is not None:
        existing_field.page_number = field.page_number

    db.commit()
    db.refresh(existing_field)
    return existing_field


def delete_field(db: Session, field_id: int):
    """
    Deletes a template field if it has never been used in a submitted checksheet.

    template_fields.id is referenced by checksheet_value.field_id (nullable=False, no ON DELETE
    CASCADE), so a hard DELETE on a field with real historical values would raise a
    ForeignKeyViolation. Instead, such a field is archived (is_active=False, is_deleted=True,
    deleted_at=now) rather than removed: historical checksheets keep reading it fine via
    ChecksheetValue.field (a direct FK lookup, unaffected by these flags - see
    checksheet_service._serialize_detail), while get_fields_by_template (template editing) and
    checksheet_template_service._compose_fields (new checksheets) both already filter it out.

    Returns None if the field doesn't exist, otherwise {"field_id": int, "archived": bool}.
    """
    field = get_field_by_id(db, field_id)
    if not field:
        return None

    in_use = (
        db.query(ChecksheetValue)
        .filter(ChecksheetValue.field_id == field_id)
        .first() is not None
    )

    if not in_use:
        try:
            db.delete(field)
            db.commit()
            return {"field_id": field_id, "archived": False}
        except IntegrityError:
            # A checksheet_value row referencing this field was inserted between the check above
            # and the DELETE (race condition) - archive instead of surfacing the raw DB error.
            db.rollback()
            field = get_field_by_id(db, field_id)

    field.is_active = False
    field.is_deleted = True
    field.deleted_at = datetime.now(timezone.utc)
    db.commit()

    return {"field_id": field_id, "archived": True}
