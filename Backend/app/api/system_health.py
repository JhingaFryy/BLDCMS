from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.database.database import get_db
from app.models.user import User
from app.schemas.system_health import LogFileInfo, LogTailResponse, SystemHealthOverview, ViteLogEventCreate
from app.security.dependencies import require_admin
from app.services import system_health_service

router = APIRouter(
    prefix="/system-health",
    tags=["System Health"]
)


@router.get("/overview", response_model=SystemHealthOverview)
def overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return system_health_service.get_overview(db)


@router.get("/logs", response_model=list[LogFileInfo])
def list_logs(
    current_user: User = Depends(require_admin)
):
    return system_health_service.list_log_files()


@router.get("/logs/{log_key}", response_model=LogTailResponse)
def tail_log(
    log_key: str,
    lines: int = Query(default=200, ge=1, le=2000),
    current_user: User = Depends(require_admin)
):
    try:
        return system_health_service.tail_log_file(log_key, lines)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown log file")


@router.get("/logs/{log_key}/download")
def download_log(
    log_key: str,
    current_user: User = Depends(require_admin)
):
    try:
        path = system_health_service.get_log_file_path(log_key)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown log file")
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log file not found")

    return FileResponse(path, media_type="text/plain", filename=path.name)


@router.post("/vite-log", status_code=status.HTTP_204_NO_CONTENT)
def report_vite_log_event(event: ViteLogEventCreate):
    # Deliberately no auth dependency - these events must be reportable from the pre-login screen,
    # from a session whose token just expired, and (the whole point of "Backend API unreachable" /
    # "reconnect attempts") from a Dashboard that may not be able to reach an authenticated
    # endpoint at all right now. Pydantic's Literal severity/source + capped message length (see
    # ViteLogEventCreate) is the guardrail in place of auth; CORS (main.py) already restricts which
    # browser origins can call this at all. Read access to the resulting log is still Admin-only,
    # unchanged, via the existing /system-health/logs* routes above.
    logger = get_logger("app.vite")
    message = f"[{event.source}] {event.message}"
    if event.severity == "ERROR":
        logger.error(message)
    elif event.severity == "WARNING":
        logger.warning(message)
    else:
        logger.info(message)
