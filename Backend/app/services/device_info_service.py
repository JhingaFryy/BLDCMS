"""
Module 44: device registry backing the System Administration CLI's "devices" commands.

Written to by the Android login/OTP-verify flow (upsert_from_login, called after every
successful authentication that carries device metadata) and the disclosure-acknowledgment
endpoint. Read by the CLI only - no Dashboard or Android code path reads this module.
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.device_info import DeviceInfo

# Module 44: the only commands a CLI operator may queue for a device to pick up on its next
# contact with the backend - kept as a closed set here (not a free-text field) so a typo can
# never silently become a no-op "pending command" nobody notices.
VALID_PENDING_COMMANDS = {"CLEAR_APP_DATA"}


def upsert_from_login(
    db: Session,
    *,
    user_id: Optional[int],
    device_id: Optional[str],
    manufacturer: Optional[str] = None,
    device_model: Optional[str] = None,
    os_version: Optional[str] = None,
    app_version: Optional[str] = None,
    battery_level: Optional[int] = None,
    network_type: Optional[str] = None,
    storage_free_mb: Optional[int] = None,
    storage_total_mb: Optional[int] = None,
    disclosure_acknowledged: Optional[bool] = None,
) -> Optional[DeviceInfo]:
    """Best-effort, never raises - a device-metadata write must never block a login. Returns
    None (and logs nothing) if device_id wasn't supplied, since without it there's nothing to key
    the row on (this is normal for Dashboard/web logins, which don't carry device metadata at
    all, and for Android builds older than Module 44)."""
    if not device_id:
        return None

    try:
        device = db.query(DeviceInfo).filter(DeviceInfo.device_id == device_id).first()
        if device is None:
            device = DeviceInfo(device_id=device_id)
            db.add(device)

        device.user_id = user_id
        now = datetime.now(timezone.utc)
        device.last_seen_at = now

        # Only overwrite a field if this call actually supplied it - an older Android build (or a
        # login carrying only device_id) must never blank out richer data a newer build already
        # reported for the same device.
        for field, value in (
            ("manufacturer", manufacturer), ("device_model", device_model),
            ("os_version", os_version), ("app_version", app_version),
            ("battery_level", battery_level), ("network_type", network_type),
            ("storage_free_mb", storage_free_mb), ("storage_total_mb", storage_total_mb),
        ):
            if value is not None:
                setattr(device, field, value)

        if disclosure_acknowledged:
            device.disclosure_acknowledged_at = now

        _clear_pending_command_if_stale(device, now)

        db.commit()
        db.refresh(device)
        return device
    except Exception:
        db.rollback()
        return None


def _clear_pending_command_if_stale(device: DeviceInfo, contact_time: datetime) -> None:
    """A pending command is considered delivered/acted-on once the device makes ANY new
    authenticated contact after the command was issued - Android is expected to act on
    `pending_command` before or during that same contact (see /auth/me handling), so by the time
    the *next* login happens the command has already had a chance to run. This avoids needing a
    separate "ack" endpoint/round-trip."""
    if device.pending_command and device.pending_command_issued_at:
        issued_at = device.pending_command_issued_at
        if issued_at.tzinfo is None:
            issued_at = issued_at.replace(tzinfo=timezone.utc)
        if contact_time > issued_at:
            device.pending_command = None
            device.pending_command_issued_at = None


def acknowledge_disclosure(db: Session, device_id: str) -> Optional[DeviceInfo]:
    device = db.query(DeviceInfo).filter(DeviceInfo.device_id == device_id).first()
    if device is None:
        return None
    device.disclosure_acknowledged_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(device)
    return device


def get_pending_command(db: Session, device_id: Optional[str]) -> Optional[str]:
    if not device_id:
        return None
    device = db.query(DeviceInfo).filter(DeviceInfo.device_id == device_id).first()
    return device.pending_command if device else None


def list_devices(db: Session) -> list[DeviceInfo]:
    return db.query(DeviceInfo).order_by(DeviceInfo.last_seen_at.desc()).all()


def get_device(db: Session, device_id: str) -> Optional[DeviceInfo]:
    return db.query(DeviceInfo).filter(DeviceInfo.device_id == device_id).first()


def set_pending_command(db: Session, device_id: str, command: str) -> DeviceInfo:
    if command not in VALID_PENDING_COMMANDS:
        raise ValueError(f"Unknown command '{command}'. Valid commands: {sorted(VALID_PENDING_COMMANDS)}")
    device = get_device(db, device_id)
    if device is None:
        raise LookupError(f"No device registered with device_id '{device_id}'")
    device.pending_command = command
    device.pending_command_issued_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(device)
    return device
