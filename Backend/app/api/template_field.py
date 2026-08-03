from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.template_field import (
    TemplateFieldCreate,
    TemplateFieldResponse,
    TemplateFieldUpdate
)
from app.security.dependencies import get_current_user
from app.services.activity_log_service import Action, log_activity
from app.services.template_field_service import (
    create_field,
    get_fields_by_template,
    get_field_by_id,
    update_field,
    delete_field
)

router = APIRouter(
    prefix="/template-fields",
    tags=["Template Fields"]
)


@router.post("/", response_model=TemplateFieldResponse)
def add_field(
    field: TemplateFieldCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_field = create_field(db, field)
    log_activity(
        db,
        Action.TEMPLATE_FIELD_ADDED,
        user=current_user,
        entity_type="template_field",
        entity_id=new_field.id,
        description=f"{current_user.employee_id} added template field {new_field.field_label} to template {new_field.template_id}",
        new_value={"template_id": new_field.template_id, "field_label": new_field.field_label},
    )
    return new_field


@router.get("/{template_id}", response_model=list[TemplateFieldResponse])
def list_fields(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_fields_by_template(db, template_id)


@router.put("/{field_id}", response_model=TemplateFieldResponse)
def edit_field(
    field_id: int,
    field: TemplateFieldUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated = update_field(db, field_id, field)
    if not updated:
        raise HTTPException(status_code=404, detail="Field not found")
    log_activity(
        db,
        Action.TEMPLATE_FIELD_UPDATED,
        user=current_user,
        entity_type="template_field",
        entity_id=updated.id,
        description=f"{current_user.employee_id} updated template field {updated.field_label}",
        new_value={"template_id": updated.template_id, "field_label": updated.field_label},
    )
    return updated


@router.delete("/{field_id}")
def remove_field(
    field_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = delete_field(db, field_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Field not found"
        )

    log_activity(
        db,
        Action.TEMPLATE_FIELD_REMOVED,
        user=current_user,
        entity_type="template_field",
        entity_id=field_id,
        description=f"{current_user.employee_id} removed template field {field_id}",
        new_value={"archived": result["archived"]},
    )

    if result["archived"]:
        return {
            "message": (
                "This template field has already been used in submitted checksheets and "
                "cannot be permanently deleted. It has been archived instead."
            ),
            "archived": True
        }

    return {
        "message": "Field deleted successfully",
        "archived": False
    }
