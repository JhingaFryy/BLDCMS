from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user_session import UserSession

SESSION_TTL_MINUTES = 480
ANDROID_SESSION_TTL_DAYS = 365


def create_session(
    db: Session,
    *,
    user_id: int,
    device_type: str = "WEB",
    device_name: Optional[str] = None,
    device_id: Optional[str] = None,
    app_version: Optional[str] = None,
    refresh_token_hash: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    expires_at: Optional[datetime] = None,
) -> UserSession:
    if expires_at is None:
        if device_type == "ANDROID":
            expires_at = datetime.now(timezone.utc) + timedelta(days=ANDROID_SESSION_TTL_DAYS)
        else:
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=SESSION_TTL_MINUTES)

    session = UserSession(
        user_id=user_id,
        jti=str(uuid4()),
        refresh_token_hash=refresh_token_hash,
        device_type=device_type,
        device_name=device_name,
        device_id=device_id,
        app_version=app_version,
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=expires_at,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session_by_jti(db: Session, jti: str) -> Optional[UserSession]:
    return db.query(UserSession).filter(UserSession.jti == jti).first()


def get_session_by_refresh_token_hash(db: Session, refresh_token_hash: str) -> Optional[UserSession]:
    return db.query(UserSession).filter(UserSession.refresh_token_hash == refresh_token_hash).first()


def update_session_activity(db: Session, jti: str) -> Optional[UserSession]:
    session = get_session_by_jti(db, jti)
    if not session:
        return None

    session.last_activity = datetime.now(timezone.utc)
    db.commit()
    db.refresh(session)
    return session


def revoke_session(db: Session, jti: str, reason: Optional[str] = None) -> UserSession:
    session = get_session_by_jti(db, jti)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    session.revoked = True
    session.revoked_at = datetime.now(timezone.utc)
    session.revoked_reason = reason
    db.commit()
    db.refresh(session)
    return session


def revoke_sessions_for_user(db: Session, user_id: int, reason: Optional[str] = None) -> list[UserSession]:
    """Module 44: bulk revoke, used by the System Administration CLI's "force logout" command -
    every not-already-revoked session belonging to `user_id` is revoked in one pass (a user can
    be logged in on more than one device). Every affected row goes through validate_session()'s
    existing `revoked` check exactly like a single revoke_session() call, so no authorization
    code path is bypassed - this just applies the same flag to more rows."""
    sessions = (
        db.query(UserSession)
        .filter(UserSession.user_id == user_id, UserSession.revoked == False)  # noqa: E712
        .all()
    )
    now = datetime.now(timezone.utc)
    for session in sessions:
        session.revoked = True
        session.revoked_at = now
        session.revoked_reason = reason
    db.commit()
    for session in sessions:
        db.refresh(session)
    return sessions


def list_active_sessions(db: Session) -> list[UserSession]:
    """Module 44: all not-revoked, not-yet-expired sessions, for the CLI's "sessions list". The
    expiry check is done in Python (not as a SQL filter) to match validate_session()'s exact
    naive/aware datetime handling for expires_at, rather than risk a DB-session-timezone-
    dependent SQL comparison."""
    now = datetime.now(timezone.utc)
    candidates = (
        db.query(UserSession)
        .filter(UserSession.revoked == False)  # noqa: E712
        .order_by(UserSession.last_activity.desc())
        .all()
    )
    active = []
    for session in candidates:
        expires_at = session.expires_at
        if expires_at is None:
            active.append(session)
            continue
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at > now:
            active.append(session)
    return active


def validate_session(db: Session, payload: dict) -> Optional[UserSession]:
    jti = payload.get("jti")
    if not jti:
        return None

    session = get_session_by_jti(db, str(jti))
    if not session:
        return None

    if session.revoked:
        return None

    if session.expires_at is None:
        update_session_activity(db, str(jti))
        return session

    now = datetime.now(timezone.utc)
    expires_at = session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at <= now:
        return None

    update_session_activity(db, str(jti))
    return session
