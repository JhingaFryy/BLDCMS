"""Module 44: System Administration CLI - session management commands.

Operates entirely through the existing app/services/session_service.py - "revoke" sets the same
`revoked` flag that `validate_session()` (used by every authenticated request in the app) already
checks, so a revoked session is rejected on its very next use exactly like a normal logout. No
new authorization mechanism is introduced.
"""
from __future__ import annotations

from datetime import datetime, timezone

from app.database.database import SessionLocal
from app.models.user import User
from app.services import session_service


def list_sessions() -> list[dict]:
    db = SessionLocal()
    try:
        rows = []
        for s in session_service.list_active_sessions(db):
            user = db.query(User).filter(User.id == s.user_id).first()
            rows.append({
                "jti": s.jti,
                "user": user.employee_id if user else None,
                "user_name": user.name if user else None,
                "device_type": s.device_type,
                "device_name": s.device_name,
                "device_id": s.device_id,
                "app_version": s.app_version,
                "ip_address": s.ip_address,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "last_activity": s.last_activity.isoformat() if s.last_activity else None,
                "expires_at": s.expires_at.isoformat() if s.expires_at else None,
            })
        return rows
    finally:
        db.close()


def revoke_session(jti: str) -> dict:
    db = SessionLocal()
    try:
        session = session_service.revoke_session(db, jti, reason="admin_cli_revoke")
        return {"jti": session.jti, "revoked_at": session.revoked_at.isoformat()}
    finally:
        db.close()


def revoke_all_for_user(employee_id: str) -> dict:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.employee_id == employee_id).first()
        if user is None:
            raise LookupError(f"No user with employee_id '{employee_id}'")
        sessions = session_service.revoke_sessions_for_user(db, user.id, reason="admin_cli_force_logout")
        return {"employee_id": employee_id, "sessions_revoked": len(sessions)}
    finally:
        db.close()
