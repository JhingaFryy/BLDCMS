import os
import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.security.dependencies import get_current_user, require_supervisor
from app.schemas.checksheet_header import (
    ChecksheetHeaderCreate,
    ChecksheetHeaderDetailResponse,
    ChecksheetHeaderUpdate,
    ChecksheetStatus,
    ChecksheetStatusUpdate,
    PaginatedChecksheetResponse
)
from app.schemas.analytics import ChecksheetAnalyticsSummary
from app.services.checksheet_service import (
    authorize_checksheet_access,
    create_checksheet,
    delete_checksheet,
    get_checksheet_analytics,
    get_checksheet_detail,
    get_checksheet_list,
    update_checksheet,
    change_checksheet_status
)
from app.models.checksheet_header import ChecksheetHeader
from app.services.activity_log_service import Action, log_activity
from app.services.pdf_service import PdfService

router = APIRouter(
    prefix="/checksheet",
    tags=["Checksheet"]
)

pdf_service = PdfService()


def _checksheet_description(result: dict, verb: str) -> str:
    loco = result.get("locomotive_number") or "-"
    equipment = result.get("equipment_name") or "-"
    return f"Checksheet #{result.get('id')} ({loco} - {equipment}) {verb}"


def _regenerate_pdf(db: Session, header: ChecksheetHeader) -> str:
    # Always regenerates rather than reusing header.pdf_path, even if a file already exists - the
    # PDF's Standard/Authority/labels are derived from the *current* TemplateField metadata (e.g.
    # TemplateField.effective_standard_value's parent-chain inheritance), which can legitimately
    # change after a checksheet was submitted/approved (a template correction, or - as happened
    # here - a backend fix). A "only generate if missing" cache silently kept serving stale PDFs
    # after such a change; regenerating on every view/download guarantees the document a
    # Supervisor is looking at always matches the live data, at the cost of a cheap re-render.
    #
    # Module 39 exception: once a checksheet has been digitally signed, its PDF carries a
    # cryptographic signature over its exact bytes - regenerating it here would silently produce
    # a fresh, unsigned file and overwrite the signed one on disk, destroying the very signature
    # this module exists to create. A signed checksheet's PDF is served as-is, unregenerated,
    # exactly matching its immutability (view/download only, no edits of any kind).
    if getattr(header, "digital_signature", None) is not None and header.pdf_path and os.path.exists(header.pdf_path):
        return header.pdf_path

    old_path = header.pdf_path
    header.pdf_path = pdf_service.generate_checksheet_pdf(header)
    db.commit()
    if old_path and old_path != header.pdf_path and os.path.exists(old_path):
        os.remove(old_path)
    return header.pdf_path


@router.post("/", response_model=ChecksheetHeaderDetailResponse)
def save_checksheet(
    checksheet: ChecksheetHeaderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = create_checksheet(db, checksheet, current_user)
    log_activity(
        db,
        Action.CHECKSHEET_CREATED,
        user=current_user,
        entity_type="checksheet",
        entity_id=result.get("id"),
        section_id=result.get("section_id"),
        description=_checksheet_description(result, "was created"),
        new_value={"status": result.get("status")},
    )
    return result


@router.get("/", response_model=PaginatedChecksheetResponse)
def list_checksheets(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=500),
    search: str | None = None,
    section_id: int | None = None,
    equipment_id: int | None = None,
    locomotive_id: int | None = None,
    locomotive_type: str | None = None,
    technology: str | None = None,
    work_type: str | None = None,
    status: ChecksheetStatus | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_checksheet_list(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        section_id=section_id,
        equipment_id=equipment_id,
        locomotive_id=locomotive_id,
        locomotive_type=locomotive_type,
        technology=technology,
        work_type=work_type,
        status=status,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_order=sort_order,
        current_user=current_user
    )


@router.get("/{checksheet_id}", response_model=ChecksheetHeaderDetailResponse)
def get_checksheet(
    checksheet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_checksheet_detail(db, checksheet_id, current_user)


@router.post("/{checksheet_id}/pdf/generate")
def generate_checksheet_pdf(
    checksheet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    header = db.query(ChecksheetHeader).filter(ChecksheetHeader.id == checksheet_id).first()
    if not header:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checksheet not found")

    authorize_checksheet_access(header, current_user)

    _start = time.monotonic()
    pdf_path = _regenerate_pdf(db, header)
    _duration_ms = (time.monotonic() - _start) * 1000
    log_activity(
        db,
        Action.CHECKSHEET_PDF_GENERATED,
        user=current_user,
        entity_type="checksheet",
        entity_id=header.id,
        section_id=header.section_id,
        description=f"Checksheet #{header.id} PDF generated by {current_user.employee_id}",
        new_value={"pdf_path": pdf_path},
        duration_ms=_duration_ms,
    )
    return {"message": "PDF generated", "pdf_path": pdf_path}


@router.get("/{checksheet_id}/pdf/download")
def download_checksheet_pdf(
    checksheet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    header = db.query(ChecksheetHeader).filter(ChecksheetHeader.id == checksheet_id).first()
    if not header:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checksheet not found")

    authorize_checksheet_access(header, current_user)

    # Every checksheet row offers View/Download regardless of status, not just APPROVED ones (a
    # Supervisor should be able to preview a still-pending checksheet before deciding) - generated
    # fresh on every request (see _regenerate_pdf) rather than requiring the separate
    # /pdf/generate call first, reusing the same generate_checksheet_pdf used on approval.
    pdf_path = _regenerate_pdf(db, header)

    return FileResponse(path=pdf_path, media_type="application/pdf", filename=f"checksheet_{checksheet_id}.pdf")


@router.get("/{checksheet_id}/pdf/preview")
def preview_checksheet_pdf(
    checksheet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    header = db.query(ChecksheetHeader).filter(ChecksheetHeader.id == checksheet_id).first()
    if not header:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checksheet not found")

    authorize_checksheet_access(header, current_user)

    pdf_path = _regenerate_pdf(db, header)

    return FileResponse(path=pdf_path, media_type="application/pdf")


@router.get("/report/pdf")
def export_report_pdf(
    skip: int = 0,
    limit: int = 1000,
    search: str | None = None,
    section_id: int | None = None,
    equipment_id: int | None = None,
    locomotive_id: int | None = None,
    locomotive_type: str | None = None,
    technology: str | None = None,
    work_type: str | None = None,
    status: ChecksheetStatus | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    items = get_checksheet_list(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        section_id=section_id,
        equipment_id=equipment_id,
        locomotive_id=locomotive_id,
        locomotive_type=locomotive_type,
        technology=technology,
        work_type=work_type,
        status=status,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_order=sort_order,
        current_user=current_user
    )["items"]
    pdf_path = pdf_service.generate_pdf(
        title="Checksheets Report",
        metadata={"Generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")},
        sections=[{"title": "Filtered Checksheets", "headers": ["ID", "Status", "Technician", "Section", "Equipment", "Created"], "rows": [(item.get("id"), item.get("status"), item.get("technician_mobile"), item.get("section_id"), item.get("equipment_id"), item.get("created_at")) for item in items]}]
    )
    return FileResponse(path=pdf_path, media_type="application/pdf", filename="checksheets_report.pdf")


@router.get("/analytics/summary", response_model=ChecksheetAnalyticsSummary)
def checksheet_analytics_summary(
    section_id: int | None = None,
    equipment_id: int | None = None,
    locomotive_id: int | None = None,
    locomotive_type: str | None = None,
    technology: str | None = None,
    work_type: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    supervisor_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_supervisor)
):
    return get_checksheet_analytics(
        db=db,
        section_id=section_id,
        equipment_id=equipment_id,
        locomotive_id=locomotive_id,
        locomotive_type=locomotive_type,
        technology=technology,
        work_type=work_type,
        date_from=date_from,
        date_to=date_to,
        supervisor_id=supervisor_id,
        current_user=current_user
    )


@router.put("/{checksheet_id}", response_model=ChecksheetHeaderDetailResponse)
def edit_checksheet(
    checksheet_id: int,
    payload: ChecksheetHeaderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = update_checksheet(db, checksheet_id, payload, current_user)
    log_activity(
        db,
        Action.CHECKSHEET_UPDATED,
        user=current_user,
        entity_type="checksheet",
        entity_id=result.get("id"),
        section_id=result.get("section_id"),
        description=_checksheet_description(result, "was updated"),
    )
    return result


@router.delete("/{checksheet_id}")
def remove_checksheet(
    checksheet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = delete_checksheet(db, checksheet_id, current_user)
    log_activity(
        db,
        Action.CHECKSHEET_DELETED,
        user=current_user,
        entity_type="checksheet",
        entity_id=checksheet_id,
        description=f"Checksheet #{checksheet_id} deleted by {current_user.employee_id}",
    )
    return result


_STATUS_ACTIONS = {
    "SUBMITTED": (Action.CHECKSHEET_SUBMITTED, "was submitted"),
    "APPROVED": (Action.CHECKSHEET_APPROVED, "was approved"),
    "REJECTED": (Action.CHECKSHEET_REJECTED, "was rejected"),
}


@router.patch("/{checksheet_id}/status", response_model=ChecksheetHeaderDetailResponse)
def update_checksheet_status(
    checksheet_id: int,
    payload: ChecksheetStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    old_header = db.query(ChecksheetHeader).filter(ChecksheetHeader.id == checksheet_id).first()
    old_status = old_header.status if old_header else None

    result = change_checksheet_status(db, checksheet_id, payload, current_user)

    action_info = _STATUS_ACTIONS.get(payload.status.value if hasattr(payload.status, "value") else payload.status)
    if action_info is not None:
        action, verb = action_info
        log_activity(
            db,
            action,
            user=current_user,
            entity_type="checksheet",
            entity_id=result.get("id"),
            section_id=result.get("section_id"),
            description=_checksheet_description(result, verb),
            old_value={"status": old_status},
            new_value={"status": result.get("status")},
        )
    return result
