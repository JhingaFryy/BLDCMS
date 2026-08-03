from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    PaginatedUsersResponse
)
from app.security.dependencies import require_admin, require_supervisor
from app.services import user_service
from app.services.activity_log_service import Action, log_activity

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/", response_model=PaginatedUsersResponse)
def list_users(
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    section_id: Optional[int] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "asc",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_supervisor)
):
    return user_service.get_users(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        role=role,
        is_active=is_active,
        section_id=section_id,
        sort_by=sort_by,
        sort_order=sort_order
    )

@router.post("/", response_model=UserResponse)
def add_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    new_user = user_service.create_user(db, user_data)
    log_activity(
        db,
        Action.USER_CREATED,
        user=current_user,
        entity_type="user",
        entity_id=new_user.id,
        section_id=new_user.section_id,
        description=f"{current_user.employee_id} created user {new_user.employee_id} ({new_user.name})",
        new_value={"employee_id": new_user.employee_id, "name": new_user.name, "role": new_user.role},
    )
    return new_user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    before = db.query(User).filter(User.id == user_id).first()
    old_snapshot = None
    if before is not None:
        old_snapshot = {
            "name": before.name,
            "email": before.email,
            "role": before.role,
            "is_active": before.is_active,
            "section_id": before.section_id,
        }

    updated_user = user_service.update_user(db, user_id, user_data)
    log_activity(
        db,
        Action.USER_UPDATED,
        user=current_user,
        entity_type="user",
        entity_id=updated_user.id,
        section_id=updated_user.section_id,
        description=f"{current_user.employee_id} updated user {updated_user.employee_id} ({updated_user.name})",
        old_value=old_snapshot,
        new_value={
            "name": updated_user.name,
            "email": updated_user.email,
            "role": updated_user.role,
            "is_active": updated_user.is_active,
            "section_id": updated_user.section_id,
        },
    )
    return updated_user

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    target = db.query(User).filter(User.id == user_id).first()
    target_snapshot = None
    target_section_id = None
    target_employee_id = str(user_id)
    if target is not None:
        target_snapshot = {"employee_id": target.employee_id, "name": target.name, "role": target.role}
        target_section_id = target.section_id
        target_employee_id = target.employee_id

    result = user_service.delete_user(db, user_id, current_user.id)
    log_activity(
        db,
        Action.USER_DELETED,
        user=current_user,
        entity_type="user",
        entity_id=user_id,
        section_id=target_section_id,
        description=f"{current_user.employee_id} deleted user {target_employee_id}",
        old_value=target_snapshot,
    )
    return result
