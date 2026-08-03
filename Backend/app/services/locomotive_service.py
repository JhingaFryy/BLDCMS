from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.checksheet_header import ChecksheetHeader
from app.models.locomotive import Locomotive
from app.models.user import User
from app.schemas.locomotive import LocomotiveCreate, LocomotiveUpdate
from app.security.section_scope import supervisor_section_id

LOCO_TECHNOLOGY = {
	"WAP-4": "CONVENTIONAL",
	"WAP-5": "3_PHASE",
	"WAP-7": "3_PHASE",
	"WAG9HC": "3_PHASE"
}


def _validate_locomotive_model(loco_model: str):
	if loco_model not in LOCO_TECHNOLOGY:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Invaild Locomotive Model"
		)


def create_locomotive(db: Session, loco: LocomotiveCreate):
	#Check if locomotive already exisits
	existing = db.query(Locomotive).filter(
		Locomotive.loco_number == loco.loco_number
	).first()

	if existing:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Locomotive already exists"
		)

	_validate_locomotive_model(loco.loco_model)

	technology = LOCO_TECHNOLOGY[loco.loco_model]

	new_loco = Locomotive(
		loco_number=loco.loco_number,
		loco_model=loco.loco_model,
		technology=technology
	)

	db.add(new_loco)
	db.commit()
	db.refresh(new_loco)

	return new_loco


def get_all_locomotives(db: Session, search: Optional[str] = None, current_user: Optional[User] = None):
	query = db.query(Locomotive)
	if search:
		query = query.filter(Locomotive.loco_number.startswith(search))

	scoped_section_id = supervisor_section_id(current_user) if current_user else None
	if scoped_section_id is not None:
		# Locomotive has no section_id of its own - "belongs to a section" means it has at least
		# one checksheet against that section (see Module 27.5).
		query = (
			query.join(ChecksheetHeader, ChecksheetHeader.locomotive_id == Locomotive.id)
			.filter(ChecksheetHeader.section_id == scoped_section_id)
			.distinct()
		)

	return query.all()


def get_locomotive(db: Session, loco_number: str, current_user: Optional[User] = None):
	loco = db.query(Locomotive).filter(
		Locomotive.loco_number == loco_number
	).first()

	if not loco:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Locomotive not found"
		)

	scoped_section_id = supervisor_section_id(current_user) if current_user else None
	if scoped_section_id is not None:
		belongs = (
			db.query(ChecksheetHeader)
			.filter(
				ChecksheetHeader.locomotive_id == loco.id,
				ChecksheetHeader.section_id == scoped_section_id
			)
			.first()
		)
		if belongs is None:
			raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

	return loco


def update_locomotive(db: Session, loco_id: int, loco_update: LocomotiveUpdate):
	loco = db.query(Locomotive).filter(Locomotive.id == loco_id).first()

	if not loco:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Locomotive not found"
		)

	duplicate = db.query(Locomotive).filter(
		Locomotive.loco_number == loco_update.loco_number,
		Locomotive.id != loco_id
	).first()

	if duplicate:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Locomotive already exists"
		)

	_validate_locomotive_model(loco_update.loco_model)

	loco.loco_number = loco_update.loco_number
	loco.loco_model = loco_update.loco_model
	loco.technology = loco_update.technology or LOCO_TECHNOLOGY[loco_update.loco_model]
	loco.is_active = loco_update.is_active

	db.commit()
	db.refresh(loco)
	return loco


def delete_locomotive(db: Session, loco_id: int):
	loco = db.query(Locomotive).filter(Locomotive.id == loco_id).first()

	if not loco:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Locomotive not found"
		)

	db.delete(loco)
	db.commit()
	return {"message": "Locomotive deleted successfully"}

