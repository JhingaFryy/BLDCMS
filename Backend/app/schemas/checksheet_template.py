from typing import List, Optional

from pydantic import BaseModel

from app.schemas.template_field import TemplateFieldResponse


class ChecksheetTemplateCreate(BaseModel):
    template_code: str
    version: Optional[int] = 1
    # Exactly one of equipment_id / section_id should be meaningful in practice: an
    # equipment-specific template sets equipment_id (existing behavior, unchanged); a section-wide
    # "common page" template (Module 29.5) sets section_id instead and leaves equipment_id unset.
    equipment_id: Optional[int] = None
    section_id: Optional[int] = None
    technology: str
    # Module 32: set only for a template that shares (equipment_id, technology) with another
    # active template - e.g. Traction Motor's GC vs Overhaul checksheets.
    maintenance_type: Optional[str] = None
    template_name: str
    description: Optional[str] = None


class ChecksheetTemplateUpdate(BaseModel):
    template_code: Optional[str] = None
    version: Optional[int] = None
    equipment_id: Optional[int] = None
    section_id: Optional[int] = None
    technology: Optional[str] = None
    maintenance_type: Optional[str] = None
    template_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ChecksheetTemplateResponse(BaseModel):
    id: int
    template_code: str
    version: int
    equipment_id: Optional[int] = None
    section_id: Optional[int] = None
    technology: str
    maintenance_type: Optional[str] = None
    template_name: str
    description: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class ChecksheetTemplateDetailResponse(ChecksheetTemplateResponse):
    fields: List[TemplateFieldResponse] = []
