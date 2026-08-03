from typing import Optional

from pydantic import BaseModel


class SectionEquipmentMapCreate(BaseModel):
    section_id: int
    equipment_id: int
    technology: str


class SectionEquipmentMapResponse(BaseModel):
    id: int
    section_id: int
    equipment_id: int
    technology: str
    is_active: bool
    section_name: Optional[str] = None
    equipment_name: Optional[str] = None

    class Config:
        from_attributes = True
