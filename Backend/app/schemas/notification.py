from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class NotificationType(str, Enum):
    CHECKSHEET_SUBMITTED = "CHECKSHEET_SUBMITTED"
    CHECKSHEET_SIGNED = "CHECKSHEET_SIGNED"
    CHECKSHEET_REJECTED = "CHECKSHEET_REJECTED"
    CHECKSHEET_NEEDS_CORRECTION = "CHECKSHEET_NEEDS_CORRECTION"
    SYSTEM = "SYSTEM"


class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    type: str
    created_at: datetime
    is_read: bool
    checksheet_id: Optional[int] = None

    class Config:
        from_attributes = True


class PaginatedNotificationResponse(BaseModel):
    items: List[NotificationResponse]
    total: int
    unread_count: int

    class Config:
        from_attributes = True


class UnreadCountResponse(BaseModel):
    unread_count: int
