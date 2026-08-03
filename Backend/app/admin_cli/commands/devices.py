"""Module 44: System Administration CLI - device inventory commands.

Reads app/models/device_info.py (device metadata reported at login/OTP-verify time) joined with
the most recent UserSession per device for session-level facts (last activity, revoked state).
All figures reflect the device's state as of its last contact with the backend - there is no
live/real-time telemetry channel to an Android device.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from app.database.database import SessionLocal
from app.models.user import User
from app.models.user_session import UserSession
from app.services import device_info_service, session_service


def _age_str(dt: Optional[datetime]) -> str:
    if dt is None:
        return "never"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    delta = datetime.now(timezone.utc) - dt
    seconds = int(delta.total_seconds())
    if seconds < 60:
        return f"{seconds}s ago"
    if seconds < 3600:
        return f"{seconds // 60}m ago"
    if seconds < 86400:
        return f"{seconds // 3600}h ago"
    return f"{seconds // 86400}d ago"


def _latest_session_for_device(db, device_id: str) -> Optional[UserSession]:
    return (
        db.query(UserSession)
        .filter(UserSession.device_id == device_id)
        .order_by(UserSession.last_activity.desc())
        .first()
    )


def list_devices() -> list[dict]:
    db = SessionLocal()
    try:
        rows = []
        for device in device_info_service.list_devices(db):
            user = db.query(User).filter(User.id == device.user_id).first() if device.user_id else None
            session = _latest_session_for_device(db, device.device_id)
            rows.append({
                "device_id": device.device_id,
                "user": user.employee_id if user else None,
                "user_name": user.name if user else None,
                "manufacturer": device.manufacturer,
                "model": device.device_model,
                "os_version": device.os_version,
                "app_version": device.app_version,
                "battery_level": device.battery_level,
                "network_type": device.network_type,
                "last_seen": _age_str(device.last_seen_at),
                "disclosure_acknowledged": device.disclosure_acknowledged_at is not None,
                "pending_command": device.pending_command,
                "session_active": bool(session and not session.revoked),
            })
        return rows
    finally:
        db.close()


def device_info(device_id: str) -> dict:
    db = SessionLocal()
    try:
        device = device_info_service.get_device(db, device_id)
        if device is None:
            raise LookupError(f"No device registered with device_id '{device_id}'")
        user = db.query(User).filter(User.id == device.user_id).first() if device.user_id else None
        sessions = (
            db.query(UserSession)
            .filter(UserSession.device_id == device_id)
            .order_by(UserSession.last_activity.desc())
            .limit(10)
            .all()
        )
        storage_used_pct = None
        if device.storage_total_mb and device.storage_free_mb is not None:
            used = device.storage_total_mb - device.storage_free_mb
            storage_used_pct = round((used / device.storage_total_mb) * 100, 1)

        return {
            "device_id": device.device_id,
            "user": user.employee_id if user else None,
            "user_name": user.name if user else None,
            "manufacturer": device.manufacturer,
            "model": device.device_model,
            "os_version": device.os_version,
            "app_version": device.app_version,
            "battery_level": device.battery_level,
            "network_type": device.network_type,
            "storage_free_mb": device.storage_free_mb,
            "storage_total_mb": device.storage_total_mb,
            "storage_used_pct": storage_used_pct,
            "last_seen_at": device.last_seen_at.isoformat() if device.last_seen_at else None,
            "disclosure_acknowledged_at": (
                device.disclosure_acknowledged_at.isoformat() if device.disclosure_acknowledged_at else None
            ),
            "pending_command": device.pending_command,
            "pending_command_issued_at": (
                device.pending_command_issued_at.isoformat() if device.pending_command_issued_at else None
            ),
            "registered_since": device.created_at.isoformat() if device.created_at else None,
            "recent_sessions": [
                {
                    "jti": s.jti,
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                    "last_activity": s.last_activity.isoformat() if s.last_activity else None,
                    "revoked": s.revoked,
                    "revoked_reason": s.revoked_reason,
                    "ip_address": s.ip_address,
                }
                for s in sessions
            ],
        }
    finally:
        db.close()


def force_logout(device_id: str) -> dict:
    """Revokes every active session tied to this device_id - the device-scoped equivalent of
    `sessions revoke`, for when the operator knows the device but not a specific session/jti."""
    db = SessionLocal()
    try:
        device = device_info_service.get_device(db, device_id)
        if device is None:
            raise LookupError(f"No device registered with device_id '{device_id}'")

        sessions = (
            db.query(UserSession)
            .filter(UserSession.device_id == device_id, UserSession.revoked == False)  # noqa: E712
            .all()
        )
        now = datetime.now(timezone.utc)
        for s in sessions:
            s.revoked = True
            s.revoked_at = now
            s.revoked_reason = "admin_cli_force_logout"
        db.commit()
        return {"device_id": device_id, "sessions_revoked": len(sessions)}
    finally:
        db.close()


def clear_app_data(device_id: str) -> dict:
    """Queues a CLEAR_APP_DATA command for the device to pick up on its next authenticated
    contact with the backend (see device_info_service and the /auth/me pending_admin_command
    field) - never touches anything outside BL-DCMS's own app-sandboxed storage on the device;
    Android's OS-level app sandbox makes it physically impossible for this command to reach any
    other app's data or the user's personal files."""
    db = SessionLocal()
    try:
        device = device_info_service.set_pending_command(db, device_id, "CLEAR_APP_DATA")
        return {
            "device_id": device_id,
            "pending_command": device.pending_command,
            "issued_at": device.pending_command_issued_at.isoformat(),
        }
    finally:
        db.close()
