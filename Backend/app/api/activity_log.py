from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.activity_log import ActivityFilterOptions, PaginatedActivityLogResponse
from app.security.dependencies import require_admin
from app.services.activity_log_service import ALL_ACTIONS, get_activities

router = APIRouter(
    prefix="/activity-logs",
    tags=["Activity Logs"]
)


@router.get("/", response_model=PaginatedActivityLogResponse)
def list_activities(
    skip: int = 0,
    limit: int = 25,
    search: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    section_id: Optional[int] = None,
    user_id: Optional[int] = None,
    role: Optional[str] = None,
    action: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return get_activities(
        db=db,
        current_user=current_user,
        skip=skip,
        limit=limit,
        search=search,
        date_from=date_from,
        date_to=date_to,
        section_id=section_id,
        user_id=user_id,
        role=role,
        action=action,
    )


@router.get("/actions", response_model=ActivityFilterOptions)
def list_action_types(
    current_user: User = Depends(require_admin)
):
    return {"actions": ALL_ACTIONS}
