from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.equipment import (
    EquipmentCreate,
    EquipmentResponse,
    EquipmentUpdate
)

from app.services.equipment_service import (
    create_equipment,
    delete_equipment,
    get_all_equipment,
    get_equipment,
    update_equipment
)
from app.security.dependencies import get_current_user, require_admin
from app.models.user import User
from app.services.activity_log_service import Action, log_activity

router = APIRouter(
    prefix="/equipment",
    tags=["Equipment"]
)


@router.post("/", response_model=EquipmentResponse)
def add_equipment(
    equipment: EquipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    new_equipment = create_equipment(db, equipment)
    log_activity(
        db,
        Action.EQUIPMENT_ADDED,
        user=current_user,
        entity_type="equipment",
        entity_id=new_equipment.id,
        description=f"{current_user.employee_id} added equipment {new_equipment.equipment_name} ({new_equipment.equipment_code})",
        new_value={"equipment_code": new_equipment.equipment_code, "equipment_name": new_equipment.equipment_name},
    )
    return new_equipment


@router.get("/", response_model=list[EquipmentResponse])
def list_equipment(
    section_id: int | None = None,
    technology: str | None = None,
    locomotive_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_all_equipment(db, current_user, section_id=section_id, technology=technology,
                              locomotive_id=locomotive_id)


@router.put("/{equipment_id}", response_model=EquipmentResponse)
def edit_equipment(
    equipment_id: int,
    equipment: EquipmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    updated_equipment = update_equipment(db, equipment_id, equipment)
    log_activity(
        db,
        Action.EQUIPMENT_UPDATED,
        user=current_user,
        entity_type="equipment",
        entity_id=updated_equipment.id,
        description=f"{current_user.employee_id} updated equipment {updated_equipment.equipment_name} ({updated_equipment.equipment_code})",
        new_value={"equipment_code": updated_equipment.equipment_code, "equipment_name": updated_equipment.equipment_name},
    )
    return updated_equipment


@router.delete("/{equipment_id}")
def remove_equipment(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    result = delete_equipment(db, equipment_id)
    log_activity(
        db,
        Action.EQUIPMENT_REMOVED,
        user=current_user,
        entity_type="equipment",
        entity_id=equipment_id,
        description=f"{current_user.employee_id} removed equipment {equipment_id}",
    )
    return result


@router.get("/{equipment_code}", response_model=EquipmentResponse)
def get_one_equipment(
    equipment_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_equipment(db, equipment_code, current_user)

