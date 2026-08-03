from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.user import User
from app.schemas.section_equipment_map import (
    SectionEquipmentMapCreate,
    SectionEquipmentMapResponse
)
from app.security.dependencies import get_current_user
from app.services.activity_log_service import Action, log_activity

from app.services.section_equipment_map_service import (
    create_mapping,
    get_all_mappings,
    delete_mapping
)

router = APIRouter(
    prefix="/section-equipment-map",
    tags=["Section Equipment Mapping"]
)


@router.post("/", response_model=SectionEquipmentMapResponse)
def add_mapping(
    mapping: SectionEquipmentMapCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_mapping = create_mapping(db, mapping)
    log_activity(
        db,
        Action.SECTION_EQUIPMENT_MAPPING_ADDED,
        user=current_user,
        entity_type="section_equipment_map",
        entity_id=new_mapping.id,
        description=f"{current_user.employee_id} mapped equipment {new_mapping.equipment_id} to section {new_mapping.section_id}",
        new_value={"section_id": new_mapping.section_id, "equipment_id": new_mapping.equipment_id},
    )
    return new_mapping


@router.get("/", response_model=list[SectionEquipmentMapResponse])
def list_mappings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_all_mappings(db)


@router.delete("/{mapping_id}")
def remove_mapping(
    mapping_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    mapping = delete_mapping(db, mapping_id)

    if mapping:
        log_activity(
            db,
            Action.SECTION_EQUIPMENT_MAPPING_REMOVED,
            user=current_user,
            entity_type="section_equipment_map",
            entity_id=mapping_id,
            description=f"{current_user.employee_id} removed section-equipment mapping {mapping_id}",
        )
        return {
            "message": "Mapping deleted successfully"
        }

    return {
        "message": "Mapping not found"
    }
