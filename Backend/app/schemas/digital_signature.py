from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DigitalSignatureResponse(BaseModel):
    id: int
    checksheet_id: int
    supervisor_id: Optional[int] = None
    supervisor_name: str
    supervisor_employee_id: str
    certificate_subject: str
    certificate_issuer: str
    certificate_serial_number: str
    certificate_thumbprint: str
    certificate_valid_from: datetime
    certificate_valid_to: datetime
    signing_timestamp: datetime
    signature_hash: str
    verification_status: str
    provider: str
    created_at: datetime

    class Config:
        from_attributes = True
