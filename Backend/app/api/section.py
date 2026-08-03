from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.section import SectionCreate, SectionResponse, SectionUpdate
from app.security.dependencies import get_current_user, require_admin
from app.services.activity_log_service import Action, log_activity
from app.services.section_service import (
    create_section,
    delete_section,
    get_sections,
    update_section,
)

router = APIRouter(prefix="/sections", tags=["Sections"])


@router.get("/", response_model=list[SectionResponse])
def list_sections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_sections(db)


@router.post("/", response_model=SectionResponse)
def add_section(
    section: SectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    new_section = create_section(db, section.name)
    log_activity(
        db,
        Action.SECTION_CREATED,
        user=current_user,
        entity_type="section",
        entity_id=new_section.id,
        section_id=new_section.id,
        description=f"{current_user.employee_id} created section {new_section.name}",
        new_value={"name": new_section.name},
    )
    return new_section


@router.put("/{section_id}", response_model=SectionResponse)
def edit_section(
    section_id: int,
    section: SectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    updated_section = update_section(db, section_id, section.name)
    log_activity(
        db,
        Action.SECTION_UPDATED,
        user=current_user,
        entity_type="section",
        entity_id=updated_section.id,
        section_id=updated_section.id,
        description=f"{current_user.employee_id} updated section {updated_section.name}",
        new_value={"name": updated_section.name},
    )
    return updated_section


@router.delete("/{section_id}")
def remove_section(
    section_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    result = delete_section(db, section_id)
    log_activity(
        db,
        Action.SECTION_REMOVED,
        user=current_user,
        entity_type="section",
        entity_id=section_id,
        section_id=section_id,
        description=f"{current_user.employee_id} removed section {section_id}",
    )
    return result
