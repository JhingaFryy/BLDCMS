from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.locomotive import (
	LocomotiveCreate,
	LocomotiveResponse,
	LocomotiveUpdate
)
from app.security.dependencies import get_current_user, require_admin
from app.services.activity_log_service import Action, log_activity
from app.services.locomotive_service import (
	create_locomotive,
	delete_locomotive,
	get_all_locomotives,
	get_locomotive,
	update_locomotive
)

router = APIRouter(
	prefix="/locomotives",
	tags=["Locomotives"]
)

@router.post("/", response_model=LocomotiveResponse)
def add_locomotive(
	loco: LocomotiveCreate,
	db: Session = Depends(get_db),
	current_user: User = Depends(require_admin)
):
	new_loco = create_locomotive(db, loco)
	log_activity(
		db,
		Action.LOCOMOTIVE_ADDED,
		user=current_user,
		entity_type="locomotive",
		entity_id=new_loco.id,
		description=f"{current_user.employee_id} added locomotive {new_loco.loco_number}",
		new_value={"loco_number": new_loco.loco_number, "loco_model": new_loco.loco_model},
	)
	return new_loco

@router.get("/", response_model=list[LocomotiveResponse])
def list_locomotives(
	search: Optional[str] = None,
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user)
):
	return get_all_locomotives(db, search, current_user)

@router.put("/{loco_id}", response_model=LocomotiveResponse)
def edit_locomotive(
	loco_id: int,
	loco: LocomotiveUpdate,
	db: Session = Depends(get_db),
	current_user: User = Depends(require_admin)
):
	updated_loco = update_locomotive(db, loco_id, loco)
	log_activity(
		db,
		Action.LOCOMOTIVE_UPDATED,
		user=current_user,
		entity_type="locomotive",
		entity_id=updated_loco.id,
		description=f"{current_user.employee_id} updated locomotive {updated_loco.loco_number}",
		new_value={"loco_number": updated_loco.loco_number, "loco_model": updated_loco.loco_model},
	)
	return updated_loco

@router.delete("/{loco_id}")
def remove_locomotive(
	loco_id: int,
	db: Session = Depends(get_db),
	current_user: User = Depends(require_admin)
):
	result = delete_locomotive(db, loco_id)
	log_activity(
		db,
		Action.LOCOMOTIVE_REMOVED,
		user=current_user,
		entity_type="locomotive",
		entity_id=loco_id,
		description=f"{current_user.employee_id} removed locomotive {loco_id}",
	)
	return result

@router.get("/{loco_number}", response_model=LocomotiveResponse)
def get_one_locomotive(
	loco_number: str,
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user)
):
	return get_locomotive(db, loco_number, current_user)
