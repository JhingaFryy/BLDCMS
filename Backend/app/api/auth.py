from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.rate_limit import rate_limit_by_ip
from app.database.database import get_db
from app.schemas.otp_log import LoginRequest, OTPRequest, OTPVerificationRequest
from app.services import device_info_service
from app.services.activity_log_service import Action, log_activity
from app.services.auth_service import dashboard_login
from app.services.otp_service import request_otp, verify_otp
from app.services.session_service import revoke_session
from app.security.dependencies import get_current_user, get_current_user_and_session, security
from app.security.jwt import decode_access_token
from app.models.user import User
from app.models.user_session import UserSession

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/login", dependencies=[Depends(rate_limit_by_ip(10, 300, "RATE_LIMIT_LOGIN"))])
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    token = dashboard_login(db, login_data)
    if token is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid Employee ID or Password"
        )
    log_activity(
        db,
        Action.USER_LOGIN,
        employee_id=login_data.employee_id,
        description=f"{login_data.employee_id} logged in via Dashboard",
    )
    return token


@router.post("/request-otp", dependencies=[Depends(rate_limit_by_ip(10, 300, "RATE_LIMIT_OTP_GENERATION"))])
def request_otp_route(
    otp_request: OTPRequest,
    db: Session = Depends(get_db)
):
    result = request_otp(
        db,
        employee_id=otp_request.employee_id,
        password=otp_request.password,
        device_type=otp_request.device_type or "ANDROID",
        device_name=otp_request.device_name,
        ip_address=otp_request.ip_address,
        user_agent=otp_request.user_agent,
    )
    log_activity(
        db,
        Action.OTP_GENERATED,
        employee_id=otp_request.employee_id,
        description=f"OTP generated for {otp_request.employee_id}",
    )
    return result


@router.post("/verify-otp", dependencies=[Depends(rate_limit_by_ip(10, 600, "RATE_LIMIT_OTP_VERIFICATION"))])
def verify_otp_route(
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
    )
    log_activity(
        db,
        Action.OTP_VERIFIED,
        employee_id=otp_request.employee_id,
        description=f"OTP verified for {otp_request.employee_id}",
    )
    log_activity(
        db,
        Action.USER_LOGIN,
        employee_id=otp_request.employee_id,
        description=f"{otp_request.employee_id} logged in",
    )
    return result


@router.get("/me")
def get_me(
    current_user_and_session: tuple[User, UserSession] = Depends(get_current_user_and_session),
    db: Session = Depends(get_db),
):
    current_user, session = current_user_and_session
    # Module 44: surfaces a System-Administration-CLI-issued pending command (e.g.
    # "CLEAR_APP_DATA") to the device on its next profile fetch after login, without a dedicated
    # polling endpoint - Android already calls /auth/me right after authenticating. Read-only
    # here; the device_info row's pending_command is cleared on the device's *next* login (see
    # device_info_service._clear_pending_command_if_stale), not by this endpoint.
    pending_admin_command = device_info_service.get_pending_command(db, session.device_id)
    return {
        "id": current_user.id,
        "employee_id": current_user.employee_id,
        "name": current_user.name,
        "mobile": current_user.mobile,
        "email": current_user.email,
        "role": current_user.role,
        "section_id": getattr(current_user, 'section_id', None),
        "section_name": getattr(current_user, 'section_name', None),
        "pending_admin_command": pending_admin_command,
    }


@router.post("/acknowledge-device-notice")
def acknowledge_device_notice(
    current_user_and_session: tuple[User, UserSession] = Depends(get_current_user_and_session),
    db: Session = Depends(get_db),
):
    """Module 44: called once by Android when the technician dismisses the in-app notice
    explaining what the organization's IT administrators can see/manage on this device (device
    inventory metadata, BL-DCMS app storage/data, sessions) via the System Administration CLI.
    Records a real, disclosed acknowledgment - never inferred or defaulted."""
    _, session = current_user_and_session
    if not session.device_id:
        raise HTTPException(status_code=400, detail="No device_id associated with this session")
    device = device_info_service.acknowledge_disclosure(db, session.device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Device not registered yet - log in again first")
    return {"acknowledged_at": device.disclosure_acknowledged_at}


@router.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    payload = decode_access_token(credentials.credentials)
    jti = payload.get("jti") if payload else None

    if jti:
        revoke_session(db, jti, reason="user_logout")

    log_activity(
        db,
        Action.USER_LOGOUT,
        user=current_user,
        description=f"{current_user.employee_id} logged out",
    )

    return {"message": "Logged out successfully"}
