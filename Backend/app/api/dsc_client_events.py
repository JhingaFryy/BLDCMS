"""Module 42: client-only Digital Signature (emBridge) telemetry.

USB token detection, certificate selection, token removal, and PIN failure are events emBridge
only ever tells the browser about - this backend has no way to observe them directly (see
Dashboard/src/services/embridgeClient.ts). This endpoint exists purely so those moments still show
up in security.log for operational visibility. Deliberately a separate router/file from
app/api/digital_signature_v2.py so it never collides with that file's own edits.

Logs directly via the app.security logger with bare action strings (DSC_CLIENT_*) - NOT through
log_activity()/Action, since this is a raw security signal (a client-observed event), not a
DB-audited business action, exactly like existing UNAUTHORIZED_ACCESS/PERMISSION_DENIED/
INVALID_PAYLOAD/HTTP_REQUEST entries. Also deliberately does NOT reuse Action.PIN_FAILURE/
Action.TOKEN_DISCONNECTED - those are already wired to a semantically different, server-side-
detected failure class in digital_signature_v2_service._log_failure(); reusing them here would
make security.log ambiguous about which failure class actually fired.
"""
from typing import Literal, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.logging import get_logger
from app.models.user import User
from app.security.dependencies import get_current_user

router = APIRouter(prefix="/checksheet", tags=["Digital Signature Client Telemetry"])

security_logger = get_logger("app.security")

_EVENT_TYPES = Literal["USB_TOKEN_DETECTED", "CERTIFICATE_SELECTED", "TOKEN_REMOVED", "PIN_FAILURE"]


class DscClientEvent(BaseModel):
    event_type: _EVENT_TYPES
    checksheet_id: Optional[int] = None
    detail: Optional[str] = Field(default=None, max_length=300)


@router.post("/signature-v2/client-event", status_code=204)
def report_dsc_client_event(
    event: DscClientEvent,
    current_user: User = Depends(get_current_user),
):
    security_logger.info(
        f"DSC client event: {event.event_type}",
        extra={
            "action": f"DSC_CLIENT_{event.event_type}",
            "success": event.event_type not in ("TOKEN_REMOVED", "PIN_FAILURE"),
            "checksheet_id": event.checksheet_id,
            "detail": event.detail,
        },
    )
