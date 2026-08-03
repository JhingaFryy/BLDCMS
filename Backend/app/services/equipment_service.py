from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.equipment import Equipment
from app.models.locomotive import Locomotive
from app.models.section_equipment_map import SectionEquipmentMap
from app.models.checksheet_template import ChecksheetTemplate
from app.models.user import User
from app.schemas.equipment import EquipmentCreate, EquipmentUpdate
from app.security.section_scope import supervisor_section_id
from app.services.section_equipment_map_service import equipment_code_matches_locomotive_model, normalize_technology


def create_equipment(db: Session, equipment: EquipmentCreate):

    existing = db.query(Equipment).filter(
        Equipment.equipment_code == equipment.equipment_code
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Equipment already exists"
        )

    new_equipment = Equipment(
        equipment_code=equipment.equipment_code,
        equipment_name=equipment.equipment_name
    )

    db.add(new_equipment)
    db.commit()
    db.refresh(new_equipment)

    return new_equipment


def get_all_equipment(
    db: Session,
    current_user: User | None = None,
    section_id: int | None = None,
    technology: str | None = None,
    locomotive_id: int | None = None,
):
    query = db.query(Equipment)

    # A Supervisor's own section always wins over any client-supplied section_id (Module 27.5's
    # rule: section scoping is derived from the authenticated user, never trusted from a client
    # param). Technicians/Admins have no server-enforced section, so a caller-supplied section_id
    # (e.g. the Android app's own section, per its profile) is honored as a plain filter.
    scoped_section_id = supervisor_section_id(current_user) if current_user else None
    effective_section_id = scoped_section_id if scoped_section_id is not None else section_id
    normalized_technology = normalize_technology(technology)

    # Module 40: some sections (M4-HR) map more than one equipment record to the same
    # section+technology, distinguished only by Locomotive Model (e.g. "Bogie Frame-1" exists as
    # both a WAG9HC and a WAP-7 equipment record, both technology='3-Phase') - passing
    # locomotive_id resolves which one actually applies via the equipment_code suffix convention.
    # Optional and additive: callers that don't pass it (every existing call site, every other
    # section) see no change in behavior at all.
    loco_model = None
    if locomotive_id is not None:
        locomotive = db.query(Locomotive).filter(Locomotive.id == locomotive_id).first()
        loco_model = locomotive.loco_model if locomotive else None

    if effective_section_id is not None or normalized_technology is not None:
        # Equipment has no section_id/technology of its own - both live on SectionEquipmentMap
        # (see Module 27.5 for section, Module 29.12 for technology). Filtering happens against
        # the database mapping, never a hardcoded equipment list (Module 29.12's requirement).
        mapping_query = db.query(SectionEquipmentMap.equipment_id, SectionEquipmentMap.technology).filter(
            SectionEquipmentMap.is_active == True
        )
        if effective_section_id is not None:
            mapping_query = mapping_query.filter(SectionEquipmentMap.section_id == effective_section_id)

        matching_ids = {
            equipment_id
            for equipment_id, mapped_technology in mapping_query.all()
            if normalized_technology is None or normalize_technology(mapped_technology) == normalized_technology
        }
        query = query.filter(Equipment.id.in_(matching_ids))

    if locomotive_id is not None:
        candidate_equipment = query.all()
        matching_ids = {
            equipment.id for equipment in candidate_equipment
            if equipment_code_matches_locomotive_model(db, equipment, loco_model)
        }
        query = db.query(Equipment).filter(Equipment.id.in_(matching_ids))

    equipment_list = query.all()
    if not equipment_list:
        return []

    technology_map: dict[int, set[str]] = {}

    mapping_rows = db.query(
        SectionEquipmentMap.equipment_id,
        SectionEquipmentMap.technology
    ).distinct().all()

    for equipment_id, technology in mapping_rows:
        if equipment_id is None or technology is None:
            continue
        technology_map.setdefault(equipment_id, set()).add(technology)

    for equipment in equipment_list:
        technologies = technology_map.get(equipment.id, set())
        equipment.used_in = ', '.join(sorted(technologies)) if technologies else 'Not Mapped'

    return equipment_list


def get_equipment(db: Session, equipment_code: str, current_user: User | None = None):

    equipment = db.query(Equipment).filter(
        Equipment.equipment_code == equipment_code
    ).first()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )

    scoped_section_id = supervisor_section_id(current_user) if current_user else None
    if scoped_section_id is not None:
        mapped = (
            db.query(SectionEquipmentMap)
            .filter(
                SectionEquipmentMap.equipment_id == equipment.id,
                SectionEquipmentMap.section_id == scoped_section_id
            )
            .first()
        )
        if mapped is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return equipment


def update_equipment(db: Session, equipment_id: int, equipment_update: EquipmentUpdate):
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )

    duplicate = db.query(Equipment).filter(
        Equipment.equipment_code == equipment_update.equipment_code,
        Equipment.id != equipment_id
    ).first()

    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Equipment already exists"
        )

    equipment.equipment_code = equipment_update.equipment_code
    equipment.equipment_name = equipment_update.equipment_name
    equipment.is_active = equipment_update.is_active

    db.commit()
    db.refresh(equipment)
    return equipment


def delete_equipment(db: Session, equipment_id: int):
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )

    db.delete(equipment)
    try:
        db.commit()
    except IntegrityError:
        # Equipment referenced by a section-equipment mapping, a checksheet template, or an
        # existing checksheet is genuinely still in use - surface that clearly instead of letting
        # the ForeignKeyViolation propagate as an unhandled 500.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete this equipment: it is still in use (mapped to a section, "
                   "referenced by a template, or has existing checksheets).",
        )
    return {"message": "Equipment deleted successfully"}
