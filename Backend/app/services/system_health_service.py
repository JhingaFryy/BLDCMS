import platform
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import fastapi
import psutil
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.core import metrics
from app.core.logging import LOG_DIR
from app.database.database import engine
from app.models.activity_log import ActivityLog
from app.models.checksheet_header import ChecksheetHeader
from app.models.digital_signature import DigitalSignature
from app.models.equipment import Equipment
from app.models.locomotive import Locomotive
from app.models.notification import Notification
from app.models.system_setting import SystemSetting
from app.models.user import User
from app.models.user_session import UserSession
from app.services.activity_log_service import Action

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
BACKEND_VERSION = "1.0"  # kept in sync with FastAPI(version=...) in main.py

# key -> (filename, display label) - a fixed whitelist so a log "key" from the client can never
# be turned into an arbitrary filesystem path.
LOG_FILES = {
    "application": ("application.log", "Application Log"),
    "auth": ("auth.log", "Auth Log"),
    "otp": ("otp.log", "OTP Log"),
    "api": ("api.log", "API Log"),
    "database": ("database.log", "Database Log"),
    "error": ("error.log", "Error Log"),
    "security": ("security.log", "Security Log"),
    "activity": ("activity.log", "Activity Log"),
    # Module 33.1: Dashboard (Vite) <-> Backend connectivity diagnostics - written by
    # app/core/logging.py's "app.vite" logger, populated via POST /system-health/vite-log.
    "vite_connection": ("vite_connection.log", "Vite Connection Logs"),
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _to_aware_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _check_backend_api() -> dict:
    # Self-check - if this code is executing at all, the backend process is up. response_time_ms
    # reflects the negligible cost of the check itself, not a full network round trip.
    start = time.monotonic()
    status = "Online"
    detail = None
    elapsed_ms = (time.monotonic() - start) * 1000
    return {"name": "Backend API", "status": status, "response_time_ms": elapsed_ms, "detail": detail}


def _check_database(db: Session) -> dict:
    start = time.monotonic()
    try:
        db.execute(text("SELECT 1"))
        status = "Online"
        detail = None
    except Exception as e:  # noqa: BLE001 - must never crash the health page
        status = "Offline"
        detail = str(e)
    elapsed_ms = (time.monotonic() - start) * 1000
    return {"name": "PostgreSQL Database", "status": status, "response_time_ms": elapsed_ms, "detail": detail}


def _check_android_connectivity(db: Session) -> dict:
    # The backend has no way to reach out and ping an Android device directly - what it can check
    # is the health of the tables/subsystems the Android app's own APIs (mobile-auth, sessions)
    # depend on to serve a request at all.
    start = time.monotonic()
    try:
        db.execute(text("SELECT 1 FROM user_sessions LIMIT 1"))
        status = "Online"
        detail = None
    except Exception as e:  # noqa: BLE001
        status = "Offline"
        detail = str(e)
    elapsed_ms = (time.monotonic() - start) * 1000
    return {"name": "Android API Connectivity", "status": status, "response_time_ms": elapsed_ms, "detail": detail}


def _check_notification_service(db: Session) -> dict:
    start = time.monotonic()
    try:
        db.execute(text("SELECT 1 FROM notifications LIMIT 1"))
        status = "Online"
        detail = None
    except Exception as e:  # noqa: BLE001
        status = "Offline"
        detail = str(e)
    elapsed_ms = (time.monotonic() - start) * 1000
    return {"name": "Notification Service", "status": status, "response_time_ms": elapsed_ms, "detail": detail}


def get_service_status(db: Session) -> list:
    checked_at = _now()
    checks = [
        _check_backend_api(),
        _check_database(db),
        _check_android_connectivity(db),
        _check_notification_service(db),
    ]
    return [{**check, "last_checked": checked_at} for check in checks]


def get_server_info(db: Session) -> dict:
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    uptime_seconds = max(0, int(time.time() - psutil.boot_time()))
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)
    uptime = f"{days}d {hours}h {minutes}m"

    try:
        postgresql_version = db.execute(text("SHOW server_version")).scalar()
    except Exception:  # noqa: BLE001 - never let a version lookup crash the page
        postgresql_version = None

    return {
        "cpu_usage_percent": psutil.cpu_percent(interval=0.1),
        "memory_usage_percent": memory.percent,
        "memory_used_gb": round(memory.used / (1024 ** 3), 2),
        "memory_total_gb": round(memory.total / (1024 ** 3), 2),
        "disk_usage_percent": disk.percent,
        "disk_used_gb": round(disk.used / (1024 ** 3), 2),
        "disk_total_gb": round(disk.total / (1024 ** 3), 2),
        "uptime": uptime,
        "python_version": platform.python_version(),
        "fastapi_version": fastapi.__version__,
        "postgresql_version": postgresql_version,
        "operating_system": f"{platform.system()} {platform.release()}",
    }


def get_application_info(db: Session) -> dict:
    android_version = (
        db.query(SystemSetting.value)
        .filter(SystemSetting.key == "android_app_version")
        .scalar()
    )

    build_date = None
    main_py = BACKEND_DIR / "main.py"
    if main_py.exists():
        build_date = datetime.fromtimestamp(main_py.stat().st_mtime, tz=timezone.utc)

    return {
        "backend_version": BACKEND_VERSION,
        "android_version": android_version,
        "build_date": build_date,
    }


def get_database_stats(db: Session) -> dict:
    total_users = db.query(User).count()
    total_technicians = db.query(User).filter(User.role == "Technician").count()
    total_supervisors = db.query(User).filter(User.role == "Supervisor").count()
    total_locomotives = db.query(Locomotive).count()
    total_equipment = db.query(Equipment).count()
    total_checksheets = db.query(ChecksheetHeader).count()
    pending_reviews = (
        db.query(ChecksheetHeader)
        .filter(ChecksheetHeader.status.in_(["SUBMITTED", "UNDER_REVIEW"]))
        .count()
    )
    approved = db.query(ChecksheetHeader).filter(ChecksheetHeader.status == "APPROVED").count()
    rejected = db.query(ChecksheetHeader).filter(ChecksheetHeader.status == "REJECTED").count()

    return {
        "total_users": total_users,
        "total_technicians": total_technicians,
        "total_supervisors": total_supervisors,
        "total_locomotives": total_locomotives,
        "total_equipment": total_equipment,
        "total_checksheets": total_checksheets,
        "pending_reviews": pending_reviews,
        "approved": approved,
        "rejected": rejected,
    }


ACTIVE_WINDOW_MINUTES = 15


def get_active_users(db: Session) -> list:
    # Android sessions are valid for up to 365 days (see session_service.ANDROID_SESSION_TTL_DAYS)
    # so "not revoked and not expired" alone would list nearly every login of the past year, not
    # who's actually online now. last_activity is kept fresh (~every 45s) by the Android app's own
    # background notification poll for as long as it's running - even backgrounded - so a short
    # recency window is a meaningful "currently logged in" signal rather than a login-history dump.
    cutoff = (_now() - timedelta(minutes=ACTIVE_WINDOW_MINUTES)).replace(tzinfo=None)

    sessions = (
        db.query(UserSession)
        .join(User, UserSession.user_id == User.id)
        .filter(UserSession.revoked == False)  # noqa: E712
        .filter(UserSession.last_activity >= cutoff)
        .order_by(UserSession.last_activity.desc())
        .all()
    )

    active = []
    seen_user_ids = set()
    for session in sessions:
        user = session.user
        if user is None or user.id in seen_user_ids:
            # Same user active from more than one session/device - only the most recent (sessions
            # are already ordered by last_activity desc) is shown, one row per person.
            continue
        seen_user_ids.add(user.id)
        active.append({
            "employee_id": user.employee_id,
            "name": user.name,
            "role": user.role,
            "login_time": _to_aware_utc(session.created_at),
            "last_activity": _to_aware_utc(session.last_activity),
        })
    return active


def get_daily_counts(db: Session) -> dict:
    today = _now().date()

    signature_count = (
        db.query(func.count(DigitalSignature.id))
        .filter(func.date(DigitalSignature.signing_timestamp) == today)
        .scalar()
    ) or 0

    submission_count = (
        db.query(func.count(ActivityLog.id))
        .filter(ActivityLog.action == Action.CHECKSHEET_SUBMITTED)
        .filter(func.date(ActivityLog.created_at) == today)
        .scalar()
    ) or 0

    approval_count = (
        db.query(func.count(ActivityLog.id))
        .filter(ActivityLog.action == Action.CHECKSHEET_APPROVED)
        .filter(func.date(ActivityLog.created_at) == today)
        .scalar()
    ) or 0

    return {
        "date": today.isoformat(),
        "signature_count": signature_count,
        "checksheet_submission_count": submission_count,
        "approval_count": approval_count,
    }


def get_request_metrics() -> dict:
    return {
        "avg_response_time_ms": metrics.get_average_response_time_ms(),
        "slowest_endpoints": metrics.get_slowest_endpoints(),
        "most_frequent_endpoints": metrics.get_most_frequent_endpoints(),
        "recent_failed_requests": metrics.get_recent_failed_requests(),
        "recent_exceptions": metrics.get_recent_exceptions(),
    }


DIGITAL_SIGNATURE_STATUS_WINDOW_HOURS = 24


def get_digital_signature_status(db: Session) -> dict:
    cutoff = _now() - timedelta(hours=DIGITAL_SIGNATURE_STATUS_WINDOW_HOURS)
    cutoff_naive = cutoff.replace(tzinfo=None)

    recent_success_count = (
        db.query(func.count(ActivityLog.id))
        .filter(ActivityLog.action == Action.SIGNATURE_SUCCESS)
        .filter(ActivityLog.created_at >= cutoff_naive)
        .scalar()
    ) or 0

    recent_failure_count = (
        db.query(func.count(ActivityLog.id))
        .filter(ActivityLog.action == Action.SIGNATURE_FAILED)
        .filter(ActivityLog.created_at >= cutoff_naive)
        .scalar()
    ) or 0

    last_signature_at = (
        db.query(func.max(DigitalSignature.signing_timestamp)).scalar()
    )

    return {
        "recent_success_count": recent_success_count,
        "recent_failure_count": recent_failure_count,
        "last_signature_at": _to_aware_utc(last_signature_at),
    }


def get_pdf_generation_stats(db: Session) -> dict:
    today = _now().date()

    rows = (
        db.query(ActivityLog.created_at, ActivityLog.activity_metadata)
        .filter(ActivityLog.action == Action.CHECKSHEET_PDF_GENERATED)
        .filter(ActivityLog.activity_metadata.isnot(None))
        .all()
    )

    durations_today: list[float] = []
    count_today = 0
    for created_at, meta in rows:
        is_today = created_at is not None and created_at.date() == today
        if is_today:
            count_today += 1
        duration = (meta or {}).get("duration_ms") if isinstance(meta, dict) else None
        if duration is not None and is_today:
            durations_today.append(duration)

    average_duration_ms = round(sum(durations_today) / len(durations_today), 1) if durations_today else None

    return {
        "average_duration_ms": average_duration_ms,
        "count_today": count_today,
    }


def get_db_connection_info() -> dict:
    pool = engine.pool
    return {
        "checked_out": pool.checkedout(),
        "pool_size": pool.size(),
    }


def get_overview(db: Session) -> dict:
    return {
        "service_status": get_service_status(db),
        "server_info": get_server_info(db),
        "application_info": get_application_info(db),
        "database_stats": get_database_stats(db),
        "active_users": get_active_users(db),
        "daily_counts": get_daily_counts(db),
        "request_metrics": get_request_metrics(),
        "digital_signature_status": get_digital_signature_status(db),
        "pdf_generation_stats": get_pdf_generation_stats(db),
        "database_connection_info": get_db_connection_info(),
    }


def list_log_files() -> list:
    files = []
    for key, (filename, label) in LOG_FILES.items():
        path = LOG_DIR / filename
        exists = path.exists()
        files.append({
            "key": key,
            "label": label,
            "exists": exists,
            "size_bytes": path.stat().st_size if exists else 0,
            "last_modified": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc) if exists else None,
        })
    return files


def tail_log_file(key: str, lines: int = 200) -> dict:
    if key not in LOG_FILES:
        raise ValueError(f"Unknown log file: {key}")

    filename, label = LOG_FILES[key]
    path = LOG_DIR / filename
    if not path.exists():
        return {"key": key, "label": label, "lines": []}

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        # Module 30: log files are no longer rotated (see core/logging.py) - they grow
        # indefinitely, so reading the whole file for a tail is wasteful on a long-lived
        # deployment, but correctness-wise still fine; a seek-from-end approach would be the
        # right follow-up if this ever becomes a real performance problem.
        all_lines = f.readlines()

    tail = all_lines[-lines:] if lines > 0 else all_lines
    return {"key": key, "label": label, "lines": [line.rstrip("\n") for line in tail]}


def get_log_file_path(key: str) -> Path:
    if key not in LOG_FILES:
        raise ValueError(f"Unknown log file: {key}")
    filename, _label = LOG_FILES[key]
    path = LOG_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Log file not found: {filename}")
    return path
