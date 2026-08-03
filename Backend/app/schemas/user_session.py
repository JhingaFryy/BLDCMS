from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class DeviceType(str, Enum):
    WEB = "WEB"
    ANDROID = "ANDROID"


class UserSessionCreate(BaseModel):
    user_id: int
    jti: str
    refresh_token_hash: Optional[str] = None
    device_type: DeviceType = DeviceType.WEB
    device_name: Optional[str] = None
    device_id: Optional[str] = None
    app_version: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    expires_at: datetime


class UserSessionResponse(BaseModel):
    id: int
    user_id: int
    jti: UUID
    device_type: str
    device_name: Optional[str]
    device_id: Optional[str]
    app_version: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    revoked: bool
    revoked_at: Optional[datetime]
    revoked_reason: Optional[str]

    class Config:
        from_attributes = True
