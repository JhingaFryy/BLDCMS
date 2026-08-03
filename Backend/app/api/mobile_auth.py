from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.rate_limit import rate_limit_by_ip
from app.database.database import get_db
from app.schemas.otp_log import LoginRequest, OTPVerificationRequest
from app.services.activity_log_service import Action, log_activity
from app.services.otp_service import request_otp, verify_otp

router = APIRouter(
    prefix="/mobile-auth",
    tags=["Mobile Authentication"]
)


@router.post("/login", dependencies=[Depends(rate_limit_by_ip(10, 300, "RATE_LIMIT_OTP_GENERATION"))])
def mobile_login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    # The Android app has no reliable way to know its own public-facing IP, so ip_address in the
    # request body is almost always empty - fall back to the actual TCP connection's address
    # (what the OTP log's "Client IP" field needs) without changing what gets stored if the
    # client ever does supply one explicitly.
    connection_ip = request.client.host if request.client else None
    result = request_otp(
        db,
        employee_id=login_data.employee_id,
        password=login_data.password,
        device_type=login_data.device_type or "ANDROID",
        device_name=login_data.device_name,
        ip_address=login_data.ip_address or connection_ip,
        user_agent=login_data.user_agent,
    )
    log_activity(
        db,
        Action.OTP_GENERATED,
        employee_id=login_data.employee_id,
        description=f"OTP generated for {login_data.employee_id} (Android)",
    )
    return result


@router.post("/verify-otp", dependencies=[Depends(rate_limit_by_ip(10, 600, "RATE_LIMIT_OTP_VERIFICATION"))])
def mobile_verify_otp(
    otp_request: OTPVerificationRequest,
    db: Session = Depends(get_db)
):
    result = verify_otp(
        db,
        employee_id=otp_request.employee_id,
        otp=otp_request.otp,
        device_type=otp_request.device_type or "ANDROID",
        device_name=otp_request.device_name,
        ip_address=otp_request.ip_address,
        user_agent=otp_request.user_agent,
        device_id=otp_request.device_id,
        manufacturer=otp_request.manufacturer,
        device_model=otp_request.device_model,
        os_version=otp_request.os_version,
        app_version=otp_request.app_version,
        battery_level=otp_request.battery_level,
        network_type=otp_request.network_type,
        storage_free_mb=otp_request.storage_free_mb,
        storage_total_mb=otp_request.storage_total_mb,
        disclosure_acknowledged=otp_request.disclosure_acknowledged,
    )
    log_activity(
        db,
        Action.OTP_VERIFIED,
        employee_id=otp_request.employee_id,
        description=f"OTP verified for {otp_request.employee_id} (Android)",
    )
    log_activity(
        db,
        Action.USER_LOGIN,
        employee_id=otp_request.employee_id,
        description=f"{otp_request.employee_id} logged in via Android",
    )
    return result
