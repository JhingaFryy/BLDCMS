"""Module 40: Digital Signature (DSC) v2 - eMudhra emBridge integration, the sole supported
digital-signature provider (the earlier IREPSSigner-based v1 endpoints on app.api.checksheet were
removed in Module 41.5; see docs/EMBRIDGE_INTEGRATION.md).
"""
import base64

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.rate_limit import rate_limit_by_employee
from app.database.database import get_db
from app.models.user import User
from app.schemas.checksheet_header import ChecksheetHeaderDetailResponse
from app.schemas.digital_signature_v2 import (
    CompleteSignatureRequestV2,
    DigitalSignatureResponseV2,
    EmBridgeHelperProxyRequest,
    PrepareSignatureRequestV2,
    PrepareSignatureResponseV2,
    SignatureEligibilityResponseV2,
)
from app.security.dependencies import get_current_user
from app.services import digital_signature_v2_service
from sqlalchemy.orm import Session

router = APIRouter(prefix="/checksheet", tags=["Digital Signature v2 (emBridge)"])

# eMudhra's own encryption service for emBridge requests/responses. Confirmed live and real (a raw
# request returns an actual Java stack trace naming the internal servlet class `bridglet.helper`),
# but it does not send permissive CORS headers for third-party origins - eMudhra's own demo page
# only ever calls it same-origin (see docs/EMBRIDGE_INTEGRATION.md). Calling it from this backend
# instead of the browser sidesteps that entirely: CORS is a browser same-origin policy, it does not
# apply to server-to-server HTTP calls at all, so this is not a workaround of any kind - it's the
# standard "backend proxy" pattern for a third-party API that only allows first-party browser
# access, which is well-established.
EMBRIDGE_HELPER_URL = "https://embridge.emudhra.com/helper"


@router.post(
    "/signature-v2/embridge-helper",
    dependencies=[Depends(rate_limit_by_employee(20, 300, "RATE_LIMIT_DIGITAL_SIGNATURE"))],
)
def proxy_embridge_helper(
    payload: EmBridgeHelperProxyRequest,
    current_user: User = Depends(get_current_user)
):
    """Relays a request verbatim to eMudhra's own encryption service (see EMBRIDGE_HELPER_URL
    above) and returns its response verbatim. This backend never inspects, decrypts, or otherwise
    understands the payload - it exists purely because the browser cannot call
    embridge.emudhra.com/helper directly (no CORS allowance for third-party origins), not because
    this backend needs to be involved in emBridge's encryption scheme."""
    try:
        response = httpx.post(EMBRIDGE_HELPER_URL, json=payload.model_dump(), timeout=20.0)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not reach eMudhra's emBridge encryption service.",
        ) from exc
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"emBridge encryption service returned HTTP {response.status_code}.",
        )
    return response.json()


@router.get("/{checksheet_id}/signature-v2/eligibility", response_model=SignatureEligibilityResponseV2)
def check_signature_eligibility_v2(
    checksheet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return digital_signature_v2_service.check_signature_eligibility(db, checksheet_id, current_user)


@router.post(
    "/{checksheet_id}/signature-v2/prepare",
    response_model=PrepareSignatureResponseV2,
    dependencies=[Depends(rate_limit_by_employee(20, 300, "RATE_LIMIT_DIGITAL_SIGNATURE"))],
)
def prepare_signature_document_v2(
    checksheet_id: int,
    payload: PrepareSignatureRequestV2,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    prepared_pdf_bytes, document_digest, region = digital_signature_v2_service.prepare_document_for_signing(
        db, checksheet_id, payload, current_user,
    )
    return PrepareSignatureResponseV2(
        prepared_pdf_base64=base64.b64encode(prepared_pdf_bytes).decode("ascii"),
        document_digest_base64=base64.b64encode(document_digest).decode("ascii"),
        reserved_region_start=region.reserved_region_start,
        reserved_region_end=region.reserved_region_end,
    )


@router.post(
    "/{checksheet_id}/signature-v2/complete",
    response_model=ChecksheetHeaderDetailResponse,
    dependencies=[Depends(rate_limit_by_employee(20, 300, "RATE_LIMIT_DIGITAL_SIGNATURE"))],
)
def complete_signature_v2(
    checksheet_id: int,
    payload: CompleteSignatureRequestV2,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ip_address = request.client.host if request.client else None
    return digital_signature_v2_service.complete_signature(db, checksheet_id, payload, current_user, ip_address)


@router.get("/{checksheet_id}/signature-v2", response_model=DigitalSignatureResponseV2)
def get_signature_v2(
    checksheet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return digital_signature_v2_service.get_signature_detail(db, checksheet_id, current_user)
