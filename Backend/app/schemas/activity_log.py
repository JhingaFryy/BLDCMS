from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ActivityLogItem(BaseModel):
    id: int
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    description: Optional[str] = None

    user_id: Optional[int] = None
    user_name: Optional[str] = None
    employee_id: Optional[str] = None
    role: Optional[str] = None

    section_id: Optional[int] = None
    section_name: Optional[str] = None

    old_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    activity_metadata: Optional[Dict[str, Any]] = None

    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedActivityLogResponse(BaseModel):
    items: List[ActivityLogItem]
    total: int


class ActivityFilterOptions(BaseModel):
    actions: List[str]
