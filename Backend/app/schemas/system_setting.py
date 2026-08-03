from pydantic import BaseModel
from typing import Optional


class SystemSettingResponse(BaseModel):
    key: str
    value: Optional[str] = None
    category: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class SystemSettingUpdate(BaseModel):
    value: Optional[str] = None


class SystemSettingsResponse(BaseModel):
    items: list[SystemSettingResponse]

    class Config:
        from_attributes = True
