from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog
from app.models.checksheet_header import ChecksheetHeader
from app.models.section import Section
from app.models.section_equipment_map import SectionEquipmentMap
from app.models.user import User


def get_sections(db: Session):
    return db.query(Section).all()


def create_section(db: Session, name: str):
    existing = db.query(Section).filter(Section.name == name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Section name already exists"
        )

    section = Section(name=name)
    db.add(section)
    db.commit()
    db.refresh(section)
    return section


def update_section(db: Session, section_id: int, name: str):
    section = db.query(Section).filter(Section.id == section_id).first()

    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )

    duplicate = db.query(Section).filter(Section.name == name, Section.id != section_id).first()
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Section name already exists"
        )

    section.name = name
    db.commit()
    db.refresh(section)
    return section


def delete_section(db: Session, section_id: int):
    section = db.query(Section).filter(Section.id == section_id).first()

    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )

    linked_user = db.query(User).filter(User.section_id == section_id).first()
    linked_mapping = db.query(SectionEquipmentMap).filter(SectionEquipmentMap.section_id == section_id).first()
    linked_checksheet = db.query(ChecksheetHeader).filter(ChecksheetHeader.section_id == section_id).first()

    if linked_user or linked_mapping or linked_checksheet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Section is in use and cannot be deleted"
        )

    # activity_logs.section_id is NOT an active-use relationship like the three checked above -
    # it's historical audit trail (e.g. the SECTION_CREATED entry from when this section was made
    # in the first place), which every real section accumulates almost immediately. Blocking
    # deletion on its presence would make virtually every section permanently undeletable; letting
    # it hit the DB's restrictive FK unhandled crashed with a raw 500 instead. The column is
    # nullable and already tolerated as such elsewhere (get_activities() outer-joins section for
    # exactly this reason) - detach it rather than either blocking the delete or losing the log
    # rows themselves.
    db.query(ActivityLog).filter(ActivityLog.section_id == section_id).update({"section_id": None})

    db.delete(section)
    db.commit()
    return {"message": "Section deleted successfully"}
