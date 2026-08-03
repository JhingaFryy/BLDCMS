from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.rate_limit import check_rate_limit
from app.core.request_context import set_authenticated_user
from app.database.database import get_db
from app.models.user import User
from app.models.user_session import UserSession
from app.security.jwt import decode_access_token
from app.services.session_service import validate_session

security = HTTPBearer()
logger = get_logger("app.auth")
security_logger = get_logger("app.security")


def _mark_authenticated(user: User) -> None:
    """Populates the current request's logging context with the resolved identity, so
    ApiLoggingMiddleware's end-of-request log line (and anything else logged for the rest of this
    request) automatically carries Username/Employee ID/Role/Section - see
    app.core.request_context."""
    set_authenticated_user(
        employee_id=user.employee_id,
        user_name=user.name,
        role=user.role,
        section=user.section.name if user.section else None,
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    payload = decode_access_token(token)

    if payload is None:
        # decode_access_token() already logged the specific JWT_INVALID/JWT_EXPIRED security
        # event (see app/security/jwt.py) - this is the "unauthorized endpoint access" outcome
        # that resulted from it.
        security_logger.warning(
            "Unauthorized access attempt: invalid or expired token",
            extra={"action": "UNAUTHORIZED_ACCESS", "success": False},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    employee_id = payload.get("sub")

    if employee_id is None:
        security_logger.warning(
            "Unauthorized access attempt: token missing subject claim",
            extra={"action": "UNAUTHORIZED_ACCESS", "success": False},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user = (
        db.query(User)
        .filter(User.employee_id == employee_id)
        .first()
    )

    if user is None:
        security_logger.warning(
            "Unauthorized access attempt: user not found",
            extra={"action": "UNAUTHORIZED_ACCESS", "success": False, "employee_id": employee_id},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    session = validate_session(db, payload)
    if session is None:
        security_logger.warning(
            "Unauthorized access attempt: invalid or revoked session",
            extra={"action": "UNAUTHORIZED_ACCESS", "success": False, "employee_id": employee_id},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked session"
        )

    _mark_authenticated(user)
    return user


def get_current_user_and_session(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> tuple[User, UserSession]:
    """Module 44: identical authentication logic to get_current_user() above, duplicated rather
    than refactored so that function - used by every other protected endpoint in the app - is
    left completely untouched. Only /auth/me (to surface a device's pending admin command, see
    app/api/auth.py) needs the UserSession alongside the User, since device_id lives on the
    session, not the user."""
    token = credentials.credentials

    payload = decode_access_token(token)

    if payload is None:
        # decode_access_token() already logged the specific JWT_INVALID/JWT_EXPIRED security
        # event (see app/security/jwt.py) - this is the "unauthorized endpoint access" outcome
        # that resulted from it.
        security_logger.warning(
            "Unauthorized access attempt: invalid or expired token",
            extra={"action": "UNAUTHORIZED_ACCESS", "success": False},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    employee_id = payload.get("sub")

    if employee_id is None:
        security_logger.warning(
            "Unauthorized access attempt: token missing subject claim",
            extra={"action": "UNAUTHORIZED_ACCESS", "success": False},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user = (
        db.query(User)
        .filter(User.employee_id == employee_id)
        .first()
    )

    if user is None:
        security_logger.warning(
            "Unauthorized access attempt: user not found",
            extra={"action": "UNAUTHORIZED_ACCESS", "success": False, "employee_id": employee_id},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    session = validate_session(db, payload)
    if session is None:
        security_logger.warning(
            "Unauthorized access attempt: invalid or revoked session",
            extra={"action": "UNAUTHORIZED_ACCESS", "success": False, "employee_id": employee_id},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked session"
        )

    _mark_authenticated(user)
    return user, session


def require_admin(
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "Admin":
        security_logger.warning(
            "Permission denied: Admin access required",
            extra={"action": "PERMISSION_DENIED", "success": False, "required_role": "Admin"},
        )
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    # Module 42: rate-limits every admin-only endpoint from this single chokepoint, rather than
    # adding Depends(rate_limit_by_employee(...)) to each one individually - inserted after the
    # role check so PERMISSION_DENIED (wrong role) and RATE_LIMIT_EXCEEDED (right role, too many
    # requests) stay distinguishable signals in security.log.
    check_rate_limit(current_user.employee_id, 120, 60, "RATE_LIMIT_ADMIN_API")
    return current_user


def require_supervisor(
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["Admin", "Supervisor"]:
        security_logger.warning(
            "Permission denied: Supervisor access required",
            extra={"action": "PERMISSION_DENIED", "success": False, "required_role": "Admin or Supervisor"},
        )
        raise HTTPException(
            status_code=403,
            detail="Supervisor access required"
        )
    return current_user


def require_technician(
    current_user: User = Depends(get_current_user)
):
    return current_user
