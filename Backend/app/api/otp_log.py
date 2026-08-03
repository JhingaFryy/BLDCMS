from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.otp_log import PaginatedOTPLogResponse
from app.security.dependencies import require_supervisor
from app.services.otp_service import get_otp_logs

router = APIRouter(
    prefix="/otp-logs",
    tags=["OTP Logs"]
)


@router.get("/", response_model=PaginatedOTPLogResponse)
def list_otp_logs(
    skip: int = 0,
    limit: int = 25,
    section_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    # Module 30: Admin or Supervisor may call this at all (Technician gets 403 here); which rows
    # they actually see is then narrowed inside get_otp_logs() via supervisor_section_id() - a
    # Supervisor is restricted to their own section's users regardless of what they pass in.
    current_user: User = Depends(require_supervisor)
):
    return get_otp_logs(
        db=db,
        current_user=current_user,
        skip=skip,
        limit=limit,
        section_id=section_id,
        search=search,
    )
