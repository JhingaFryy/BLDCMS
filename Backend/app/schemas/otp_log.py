from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class DeviceMetadata(BaseModel):
    """Module 44: optional device attributes for the System Administration CLI's device
    registry (app/models/device_info.py). Every field is optional and additive - older Android
    builds that don't send them keep working exactly as before; the device_info row simply has
    fewer populated columns until the app is updated."""
    device_id: Optional[str] = None
    manufacturer: Optional[str] = None
    device_model: Optional[str] = None
    os_version: Optional[str] = None
    app_version: Optional[str] = None
    battery_level: Optional[int] = None
    network_type: Optional[str] = None
    storage_free_mb: Optional[int] = None
    storage_total_mb: Optional[int] = None
    disclosure_acknowledged: Optional[bool] = None


class LoginRequest(DeviceMetadata):
    employee_id: str
    password: str
    device_type: Optional[str] = "ANDROID"
    device_name: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class OTPRequest(DeviceMetadata):
    employee_id: str
    password: str
    device_type: Optional[str] = "ANDROID"
    device_name: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class OTPVerificationRequest(DeviceMetadata):
    employee_id: str
    otp: str
    device_type: Optional[str] = "ANDROID"
    device_name: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class OTPLogResponse(BaseModel):
    # Module 30: deliberately excludes the stored `otp` (hashed OTP) column - the Dashboard has no
    # legitimate reason to see even a hash of it, same reasoning as never returning password_hash.
    # `otp` here is the separate plaintext column (plain_otp), shown in lieu of a real SMS
    # gateway - only ever non-null in DEBUG=True mode (see otp_service.request_otp).
    id: int
    user_id: int
    employee_id: Optional[str] = None
    user_name: Optional[str] = None
    section_id: Optional[int] = None
    section_name: Optional[str] = None
    is_verified: bool
    attempts: int
    otp: Optional[str] = None
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedOTPLogResponse(BaseModel):
    items: List[OTPLogResponse]
    total: int
