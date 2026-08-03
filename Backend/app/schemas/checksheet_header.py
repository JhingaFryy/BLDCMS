from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.schemas.digital_signature import DigitalSignatureResponse


class ChecksheetStatus(str, Enum):
    DRAFT = 'DRAFT'
    SUBMITTED = 'SUBMITTED'
    UNDER_REVIEW = 'UNDER_REVIEW'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'


class ChecksheetFieldValue(BaseModel):
    field_id: int
    value: str


class ChecksheetHeaderCreate(BaseModel):
    locomotive_id: int
    section_id: int
    # Module 36: optional - NULL for sections with no equipment at all (M6-HR), whose template
    # selection depends only on section_id + locomotive technology. Every other section's
    # checksheets continue to always provide this, unchanged.
    equipment_id: Optional[int] = None
    template_id: int

    technician_mobile: Optional[str] = Field(default=None, max_length=15)

    work_type: str = Field(max_length=20)
    # Module 32: optional checksheet-level metadata, only meaningful for Traction Motor
    # checksheets - null for every other equipment, exactly like most other equipment never
    # populate a Traction Motor Number.
    traction_motor_number: Optional[str] = Field(default=None, max_length=20)
    maintenance_type: Optional[str] = Field(default=None, max_length=20)
    status: Optional[ChecksheetStatus] = ChecksheetStatus.DRAFT

    values: List[ChecksheetFieldValue]


class ChecksheetHeaderUpdate(BaseModel):
    locomotive_id: Optional[int] = None
    section_id: Optional[int] = None
    equipment_id: Optional[int] = None
    template_id: Optional[int] = None
    technician_mobile: Optional[str] = Field(default=None, max_length=15)
    work_type: Optional[str] = Field(default=None, max_length=20)
    traction_motor_number: Optional[str] = Field(default=None, max_length=20)
    maintenance_type: Optional[str] = Field(default=None, max_length=20)
    values: Optional[List[ChecksheetFieldValue]] = None


class ChecksheetStatusUpdate(BaseModel):
    status: ChecksheetStatus
    rejection_reason: Optional[str] = None


class ChecksheetFieldValueResponse(BaseModel):
    field_id: int
    field_label: str
    field_key: str
    field_type: str
    display_order: int
    required: bool
    unit: Optional[str] = None
    default_value: Optional[str] = None
    options: Optional[str] = None
    help_text: Optional[str] = None
    field_value: Optional[str] = None
    # Module 29.8: Standard/Authority reference values for the Supervisor Review screen and PDF -
    # read directly from the submitted field's own TemplateField metadata, never generated.
    standard_value: Optional[str] = None
    authority_reference: Optional[str] = None
    # Module 29.9: "PASS" or "FAIL", produced entirely by app.services.validation_service against
    # this field's template metadata - never computed by the Dashboard/Android/PDF themselves.
    validation_status: Optional[str] = None

    class Config:
        from_attributes = True


class ChecksheetHeaderResponse(BaseModel):
    id: int
    locomotive_id: int
    section_id: int
    equipment_id: int
    template_id: int
    template_name: Optional[str] = None
    technician_mobile: str
    technician_name: Optional[str] = None
    technician_employee_id: Optional[str] = None
    work_type: Optional[str] = None
    traction_motor_number: Optional[str] = None
    maintenance_type: Optional[str] = None
    locomotive_number: Optional[str] = None
    locomotive_type: Optional[str] = None
    technology: Optional[str] = None
    equipment_name: Optional[str] = None
    section_name: Optional[str] = None
    status: Optional[ChecksheetStatus] = None
    submitted_at: Optional[datetime] = None
    submitted_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[int] = None
    rejected_at: Optional[datetime] = None
    rejected_by: Optional[int] = None
    rejection_reason: Optional[str] = None
    last_modified_at: Optional[datetime] = None
    last_modified_by: Optional[int] = None
    pdf_path: Optional[str] = None
    created_at: datetime
    # Module 39: present only once this checksheet has actually been digitally signed.
    digital_signature: Optional[DigitalSignatureResponse] = None

    class Config:
        from_attributes = True


class ChecksheetHeaderDetailResponse(ChecksheetHeaderResponse):
    values: List[ChecksheetFieldValueResponse] = Field(default_factory=list)
    status_history: Optional[List[str]] = None


class PaginatedChecksheetResponse(BaseModel):
    items: List[ChecksheetHeaderResponse]
    total: int

    class Config:
        from_attributes = True
