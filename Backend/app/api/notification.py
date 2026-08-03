from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.notification import NotificationResponse, PaginatedNotificationResponse, UnreadCountResponse
from app.security.dependencies import get_current_user
from app.services.notification_service import (
    get_notifications,
    get_notifications_since,
    get_unread_count,
    mark_all_read,
    mark_notification_read,
)

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


@router.get("/", response_model=PaginatedNotificationResponse)
def list_notifications(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_notifications(db, current_user, skip, limit)


@router.get("/unread-count", response_model=UnreadCountResponse)
def unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {"unread_count": get_unread_count(db, current_user)}


@router.get("/since", response_model=List[NotificationResponse])
def notifications_since(
    after: datetime,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_notifications_since(db, current_user, after, limit)


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def read_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return mark_notification_read(db, notification_id, current_user)


@router.patch("/read-all")
def read_all_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return mark_all_read(db, current_user)
