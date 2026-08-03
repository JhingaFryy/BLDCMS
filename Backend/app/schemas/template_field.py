from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class TemplateFieldType(str, Enum):
    TEXT = 'text'
    TEXTAREA = 'textarea'
    NUMBER = 'number'
    NUMERIC_RANGE = 'numeric_range'
    GROUP = 'group'
    SELECT = 'select'
    RADIO = 'radio'
    CHECKBOX = 'checkbox'
    DATE = 'date'
    DATETIME = 'datetime'
    BOOLEAN = 'boolean'


class TemplateFieldCreate(BaseModel):
    template_id: int
    field_key: str
    field_label: str
    field_type: TemplateFieldType
    display_order: int
    required: bool = True
    unit: Optional[str] = None
    default_value: Optional[str] = None
    options: Optional[str] = None
    help_text: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    decimal_precision: Optional[int] = None
    standard_value: Optional[str] = None
    authority_reference: Optional[str] = None
    parent_field_id: Optional[int] = None
    page_number: int = 1


class TemplateFieldUpdate(BaseModel):
    field_key: Optional[str] = None
    field_label: Optional[str] = None
    field_type: Optional[TemplateFieldType] = None
    display_order: Optional[int] = None
    required: Optional[bool] = None
    unit: Optional[str] = None
    default_value: Optional[str] = None
    options: Optional[str] = None
    help_text: Optional[str] = None
    is_active: Optional[bool] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    decimal_precision: Optional[int] = None
    standard_value: Optional[str] = None
    authority_reference: Optional[str] = None
    parent_field_id: Optional[int] = None
    page_number: Optional[int] = None


class TemplateFieldResponse(BaseModel):
    id: int
    template_id: int
    field_key: str
    field_label: str
    field_type: TemplateFieldType
    display_order: int
    required: bool
    unit: Optional[str] = None
    default_value: Optional[str] = None
    options: Optional[str] = None
    help_text: Optional[str] = None
    is_active: bool
    # Archival status (set by DELETE when blocked by real historical checksheet_value
    # references) - never settable via Create/Update, only ever produced by delete_field().
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    decimal_precision: Optional[int] = None
    standard_value: Optional[str] = None
    authority_reference: Optional[str] = None
    parent_field_id: Optional[int] = None
    page_number: int = 1

    class Config:
        from_attributes = True
