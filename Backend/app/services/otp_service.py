import hashlib
import os
import random
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, contains_eager, joinedload

from app.core.logging import get_logger
from app.models.otp_log import OTPLog
from app.models.user import User
from app.security.password import verify_password
from app.security.jwt import create_access_token
from app.security.section_scope import supervisor_section_id
from app.services import device_info_service
from app.services.session_service import create_session

logger = get_logger("app.otp")
security_logger = get_logger("app.security")
DEVELOPMENT_MODE = os.getenv("DEBUG", "true").lower() in ("1", "true", "yes")
# Independent of DEBUG (which only controls log verbosity, see app/core/logging.py) - this
# deployment has no SMS gateway, so the OTP Logs admin screen reading OTPLog.plain_otp is the
# only way a technician's OTP ever reaches anyone. Defaults to DEVELOPMENT_MODE's value so a
# plain local/dev checkout with no SHOW_OTP_PLAINTEXT set behaves exactly as before.
SHOW_OTP_PLAINTEXT = os.getenv("SHOW_OTP_PLAINTEXT", str(DEVELOPMENT_MODE)).lower() in ("1", "true", "yes")
OTP_LENGTH = 6
OTP_EXPIRE_MINUTES = 5
MAX_OTP_ATTEMPTS = 5
MAX_OTP_REQUESTS_PER_HOUR = 5
MIN_REQUEST_INTERVAL_SECONDS = 30


def _hash_otp(otp: str) -> str:
    return hashlib.sha256(otp.encode("utf-8")).hexdigest()


def _get_user(db: Session, employee_id: str) -> Optional[User]:
    return db.query(User).filter(User.employee_id == employee_id).first()


def _to_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _get_recent_otp_requests_count(db: Session, user_id: int) -> int:
    window_start = datetime.now(timezone.utc) - timedelta(hours=1)
    return db.query(OTPLog).filter(
        OTPLog.user_id == user_id,
        OTPLog.created_at >= window_start
    ).count()


def _get_last_otp_log(db: Session, user_id: int) -> Optional[OTPLog]:
    return (
        db.query(OTPLog)
        .filter(OTPLog.user_id == user_id)
        .order_by(OTPLog.created_at.desc())
        .first()
    )


def request_otp(
    db: Session,
    employee_id: str,
    password: str,
    device_type: str = "ANDROID",
    device_name: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
):
    user = _get_user(db, employee_id)
    if not user or not user.is_active:
        logger.info(
            "OTP generation rejected: user not found or inactive",
            extra={"action": "LOGIN_FAILED", "success": False, "employee_id": employee_id},
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid employee ID or password")

    if not verify_password(password, user.password_hash):
        logger.info(
            "OTP generation rejected: invalid password",
            extra={"action": "LOGIN_FAILED", "success": False, "employee_id": employee_id},
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid employee ID or password")

    recent_requests = _get_recent_otp_requests_count(db, user.id)
    if recent_requests >= MAX_OTP_REQUESTS_PER_HOUR:
        logger.info(
            "OTP generation rejected: hourly limit exceeded",
            extra={"action": "LOGIN_FAILED", "success": False, "employee_id": employee_id},
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many OTP requests. Please try again later."
        )

    last_log = _get_last_otp_log(db, user.id)
    if last_log and last_log.created_at:
        last_created_at = _to_utc(last_log.created_at)
        elapsed = datetime.now(timezone.utc) - last_created_at
        if elapsed.total_seconds() < MIN_REQUEST_INTERVAL_SECONDS:
            logger.info(
                "OTP generation rejected: cooldown active",
                extra={"action": "LOGIN_FAILED", "success": False, "employee_id": employee_id},
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Please wait before requesting a new OTP."
            )

    otp_code = f"{random.randint(0, 10**OTP_LENGTH - 1):0{OTP_LENGTH}d}"
    otp_hash = _hash_otp(otp_code)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRE_MINUTES)

    otp_log = OTPLog(
        user_id=user.id,
        otp=otp_hash,
        # Gated by SHOW_OTP_PLAINTEXT, not DEBUG - the plain code must never be persisted anywhere
        # (DB included) unless this deployment has explicitly opted in, only the hash above is
        # ever stored otherwise.
        plain_otp=otp_code if SHOW_OTP_PLAINTEXT else None,
        expires_at=expires_at,
    )
    db.add(otp_log)
    db.commit()
    db.refresh(otp_log)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    expires_at_display = expires_at.strftime("%Y-%m-%d %H:%M:%S UTC")
    client_ip = ip_address or "unknown"

    # The plain OTP is never logged, regardless of SHOW_OTP_PLAINTEXT - centralized security
    # logging requires this absolutely (see app.core.json_logging's redaction, a second line of
    # defense if a future change to this function ever tried to pass it through `extra`). It
    # remains available, when SHOW_OTP_PLAINTEXT is set, through a different, existing, deliberate
    # mechanism - OTPLog.plain_otp, readable via the OTP Logs admin screen - not through any log file.
    logger.info(
        "OTP generated",
        extra={
            "action": "OTP_GENERATED", "success": True,
            "employee_id": employee_id, "user_name": user.name,
            "expires_at": expires_at_display, "client_ip": client_ip,
        },
    )

    return {"requires_otp": True, "message": "OTP sent"}


def verify_otp(
    db: Session,
    employee_id: str,
    otp: str,
    device_type: str = "ANDROID",
    device_name: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    device_id: Optional[str] = None,
    manufacturer: Optional[str] = None,
    device_model: Optional[str] = None,
    os_version: Optional[str] = None,
    app_version: Optional[str] = None,
    battery_level: Optional[int] = None,
    network_type: Optional[str] = None,
    storage_free_mb: Optional[int] = None,
    storage_total_mb: Optional[int] = None,
    disclosure_acknowledged: Optional[bool] = None,
):
    user = _get_user(db, employee_id)
    if not user or not user.is_active:
        logger.info(
            "OTP verification rejected: user not found or inactive",
            extra={"action": "OTP_VERIFY_FAILED", "success": False, "employee_id": employee_id, "client_ip": ip_address or "unknown"},
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid employee ID or OTP")

    otp_log = (
        db.query(OTPLog)
        .filter(OTPLog.user_id == user.id)
        .order_by(OTPLog.created_at.desc())
        .first()
    )

    now = datetime.now(timezone.utc)
    if not otp_log or otp_log.is_verified:
        logger.info(
            "OTP verification rejected: no active OTP",
            extra={"action": "OTP_VERIFY_FAILED", "success": False, "employee_id": employee_id, "client_ip": ip_address or "unknown"},
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired OTP")

    expires_at = _to_utc(otp_log.expires_at)
    if expires_at <= now:
        logger.info(
            "OTP expired",
            extra={"action": "OTP_EXPIRED", "success": False, "employee_id": employee_id, "client_ip": ip_address or "unknown"},
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="OTP has expired")

    if otp_log.attempts >= MAX_OTP_ATTEMPTS:
        # "Repeated failed authentication attempts" security event - MAX_OTP_ATTEMPTS incorrect
        # entries against the same OTP is exactly that pattern, and this counter already existed
        # (see otp_log.attempts below) - reusing it here rather than building a second, parallel
        # attempt-tracking mechanism.
        security_logger.warning(
            "Repeated failed authentication attempts: OTP attempt limit reached",
            extra={"action": "REPEATED_FAILED_AUTH", "success": False, "employee_id": employee_id, "client_ip": ip_address or "unknown", "attempts": otp_log.attempts},
        )
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many OTP verification attempts")

    otp_log.attempts += 1
    db.commit()
    db.refresh(otp_log)

    if _hash_otp(otp) != otp_log.otp:
        logger.info(
            "OTP verification rejected: invalid OTP",
            extra={"action": "OTP_INVALID", "success": False, "employee_id": employee_id, "client_ip": ip_address or "unknown", "attempts": otp_log.attempts},
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OTP")

    otp_log.is_verified = True
    db.commit()

    logger.info(
        "OTP verified, login successful",
        extra={"action": "OTP_VERIFIED", "success": True, "employee_id": employee_id, "user_name": user.name, "client_ip": ip_address or "unknown"},
    )

    session = create_session(
        db,
        user_id=user.id,
        device_type=device_type,
        device_name=device_name,
        device_id=device_id,
        app_version=app_version,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    # Module 44: best-effort device registry upsert for the System Administration CLI - never
    # allowed to affect the login outcome above (see device_info_service.upsert_from_login).
    device_info_service.upsert_from_login(
        db,
        user_id=user.id,
        device_id=device_id,
        manufacturer=manufacturer,
        device_model=device_model,
        os_version=os_version,
        app_version=app_version,
        battery_level=battery_level,
        network_type=network_type,
        storage_free_mb=storage_free_mb,
        storage_total_mb=storage_total_mb,
        disclosure_acknowledged=disclosure_acknowledged,
    )

    # The JWT's own exp claim must match the session row's expires_at (e.g. 365 days for ANDROID,
    # see session_service.ANDROID_SESSION_TTL_DAYS) - otherwise create_access_token()'s fixed
    # 8-hour default silently overrides the long-lived session and logs the user out regardless of
    # the session still being valid, which is not what a "stay logged in" mobile session means.
    token_expires_delta = None
    session_expires_at = _to_utc(session.expires_at)
    if session_expires_at is not None:
        token_expires_delta = session_expires_at - datetime.now(timezone.utc)

    token = create_access_token(
        {
            "sub": user.employee_id,
            "role": user.role,
            "user_id": user.id,
            "jti": str(session.jti),
            "iat": int(session.created_at.timestamp()) if session.created_at else None,
        },
        expires_delta=token_expires_delta,
    )

    return {"access_token": token, "token_type": "bearer"}


def _serialize_otp_log(log: OTPLog) -> dict:
    return {
        "id": log.id,
        "user_id": log.user_id,
        "employee_id": log.user.employee_id if log.user else None,
        "user_name": log.user.name if log.user else None,
        "section_id": log.user.section_id if log.user else None,
        "section_name": log.user.section.name if log.user and log.user.section else None,
        "is_verified": log.is_verified,
        "attempts": log.attempts,
        "otp": log.plain_otp,
        "expires_at": log.expires_at,
        "created_at": log.created_at,
    }


def get_otp_logs(
    db: Session,
    current_user: User,
    skip: int = 0,
    limit: int = 25,
    section_id: Optional[int] = None,
    search: Optional[str] = None,
) -> dict:
    """Admin sees every OTP log; a Supervisor sees only OTP logs belonging to users in
    their own section - enforced here via supervisor_section_id(), never left to the Dashboard to
    filter. OTPLog has no section_id of its own, so scoping joins through User.section_id."""
    query = (
        db.query(OTPLog)
        .join(User, OTPLog.user_id == User.id)
        .options(contains_eager(OTPLog.user).joinedload(User.section))
    )

    scoped_section_id = supervisor_section_id(current_user)
    if scoped_section_id is not None:
        # Unconditional - ANDed with whatever section_id filter (if any) the client also sent, so
        # a Supervisor can never widen results beyond their own section by passing a different
        # value (same pattern as checksheet_service.get_checksheet_list).
        query = query.filter(User.section_id == scoped_section_id)

    if section_id is not None:
        query = query.filter(User.section_id == section_id)

    if search:
        term = f"%{search.strip()}%"
        query = query.filter(or_(User.employee_id.ilike(term), User.name.ilike(term)))

    total = query.count()
    logs = (
        query.order_by(OTPLog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {"items": [_serialize_otp_log(log) for log in logs], "total": total}
