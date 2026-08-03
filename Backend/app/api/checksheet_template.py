from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.checksheet_template import (
    ChecksheetTemplateCreate,
    ChecksheetTemplateDetailResponse,
    ChecksheetTemplateResponse,
    ChecksheetTemplateUpdate,
)
from app.security.dependencies import get_current_user
from app.services.activity_log_service import Action, log_activity
from app.services.checksheet_template_service import (
    create_template,
    get_templates,
    get_template_by_id,
    get_template_detail,
    update_template,
    delete_template,
)

router = APIRouter(
    prefix="/templates",
    tags=["Checksheet Templates"]
)


@router.post("/", response_model=ChecksheetTemplateResponse)
def add_template(
    template: ChecksheetTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_template = create_template(db, template)
    log_activity(
        db,
        Action.TEMPLATE_CREATED,
        user=current_user,
        entity_type="template",
        entity_id=new_template.id,
        description=f"{current_user.employee_id} created template {new_template.template_name} ({new_template.template_code})",
        new_value={"template_code": new_template.template_code, "template_name": new_template.template_name},
    )
    return new_template


@router.get("/", response_model=list[ChecksheetTemplateResponse])
def list_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_templates(db, current_user)


@router.get("/{template_id}", response_model=ChecksheetTemplateDetailResponse)
def get_template(
    template_id: int,
    section_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # section_id (Module 29.5) is optional and backward-compatible: omitted, this behaves exactly
    # as before (just the equipment template's own fields). Passed, the caller's section common
    # page (if that section has one) is composed in ahead of the equipment template's own pages -
    # the Android checksheet-fill route already carries sectionId in its own path today, so this
    # is a natural, additive extension of the existing endpoint rather than a new one.
    template = get_template_detail(db, template_id, current_user, section_id=section_id)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return template


@router.put("/{template_id}", response_model=ChecksheetTemplateResponse)
def edit_template(
    template_id: int,
    template: ChecksheetTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated_template = update_template(db, template_id, template)
    log_activity(
        db,
        Action.TEMPLATE_UPDATED,
        user=current_user,
        entity_type="template",
        entity_id=updated_template.id,
        description=f"{current_user.employee_id} updated template {updated_template.template_name} ({updated_template.template_code})",
        new_value={"template_code": updated_template.template_code, "template_name": updated_template.template_name},
    )
    return updated_template


@router.delete("/{template_id}")
def remove_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    template = delete_template(db, template_id)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    log_activity(
        db,
        Action.TEMPLATE_DELETED,
        user=current_user,
        entity_type="template",
        entity_id=template_id,
        description=f"{current_user.employee_id} deleted template {template_id}",
    )

    return {"message": "Template deleted successfully"}
