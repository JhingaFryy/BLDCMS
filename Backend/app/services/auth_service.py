from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.user import User
from app.schemas.otp_log import LoginRequest
from app.security.password import verify_password
from app.security.jwt import create_access_token
from app.services.session_service import create_session

logger = get_logger("app.auth")
security_logger = get_logger("app.security")


def _get_user(db: Session, employee_id: str) -> User | None:
    return db.query(User).filter(User.employee_id == employee_id).first()


def _verify_user_credentials(user: User | None, password: str) -> bool:
    if not user or not user.is_active:
        return False
    return verify_password(password, user.password_hash)


def dashboard_login(db: Session, login_data: LoginRequest):
    logger.info("Dashboard authentication attempt for employee_id=%s", login_data.employee_id)

    user = _get_user(db, login_data.employee_id)
    if not user:
        logger.info("Dashboard authentication rejected: reason=User not found")
        security_logger.warning(
            "Login failed: user not found",
            extra={"action": "LOGIN_FAILED", "success": False, "employee_id": login_data.employee_id},
        )
        return None

    if not user.is_active:
        logger.info("Dashboard authentication rejected: reason=User inactive")
        security_logger.warning(
            "Login failed: user inactive",
            extra={"action": "LOGIN_FAILED", "success": False, "employee_id": login_data.employee_id},
        )
        return None

    if not verify_password(login_data.password, user.password_hash):
        logger.info("Dashboard authentication rejected: reason=Invalid password")
        security_logger.warning(
            "Login failed: invalid password",
            extra={"action": "LOGIN_FAILED", "success": False, "employee_id": login_data.employee_id},
        )
        return None

    session = create_session(
        db,
        user_id=user.id,
        device_type=(login_data.device_type or "WEB").upper(),
        device_name=login_data.device_name,
        ip_address=login_data.ip_address,
        user_agent=login_data.user_agent,
    )

    token = create_access_token(
        {
            "sub": user.employee_id,
            "role": user.role,
            "user_id": user.id,
            "jti": str(session.jti),
            "iat": int(session.created_at.timestamp()) if session.created_at else None,
        }
    )

    logger.info("Dashboard authentication accepted for employee_id=%s", login_data.employee_id)
    return {"access_token": token, "token_type": "bearer"}


def mobile_login(db: Session, login_data: LoginRequest):
    logger.info("Mobile authentication attempt for employee_id=%s", login_data.employee_id)

    user = _get_user(db, login_data.employee_id)
    if not user or not user.is_active:
        logger.info("Mobile authentication rejected: reason=User not found or inactive")
        security_logger.warning(
            "Login failed: user not found or inactive",
            extra={"action": "LOGIN_FAILED", "success": False, "employee_id": login_data.employee_id},
        )
        raise HTTPException(status_code=401, detail="Invalid employee ID or password")

    if not verify_password(login_data.password, user.password_hash):
        logger.info("Mobile authentication rejected: reason=Invalid password")
        security_logger.warning(
            "Login failed: invalid password",
            extra={"action": "LOGIN_FAILED", "success": False, "employee_id": login_data.employee_id},
        )
        raise HTTPException(status_code=401, detail="Invalid employee ID or password")

    logger.debug("OTP generation started for mobile login employee_id=%s", login_data.employee_id)
    return {
        "requires_otp": True,
        "message": "OTP sent",
    }
