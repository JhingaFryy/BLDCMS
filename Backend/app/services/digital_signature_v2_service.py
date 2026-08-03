"""Module 40: Digital Signature (DSC) approval workflow using eMudhra emBridge - the sole
supported digital-signature provider (the earlier IREPSSigner-based implementation was removed in
Module 41.5; see docs/EMBRIDGE_INTEGRATION.md).

Cryptographic signing happens entirely on the supervisor's Windows PC, against the ProxKey token
physically attached there, via eMudhra emBridge's local REST API - this backend never contacts
emBridge and never sees a private key. It hands the client exact bytes to be signed (a raw digest,
not a whole PDF - see digital_signature_v2.embridge_pdf), then verifies what comes back using the
provider-agnostic PAdES verification logic in digital_signature.verification.

Signatures are stored in the `digital_signatures` table (DigitalSignature.provider = "embridge";
historical rows from the removed v1 signer hold "client-local-signer" and remain valid, unaltered
audit data) - a checksheet has exactly one signature, and that one-to-one relationship
(checksheet_id is a unique FK) is the natural, already-supported model.
"""
import base64
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.logging import get_logger
from app.models.checksheet_header import ChecksheetHeader
from app.models.digital_signature import DigitalSignature
from app.models.user import User
from app.schemas.checksheet_header import ChecksheetStatus
from app.schemas.digital_signature_v2 import CompleteSignatureRequestV2, PrepareSignatureRequestV2
from app.services import checksheet_service
from app.services.activity_log_service import Action, log_activity
from app.services.digital_signature.base import VerificationStatus
from app.services.digital_signature.errors import (
    CertificateExpiredError,
    CertificateMismatchError,
    CertificateMissingError,
    CertificateRevokedError,
    DigitalSignatureError,
    SignatureStorageError,
    SignatureVerificationFailedError,
)
from app.services.digital_signature.factory import get_trust_settings
from app.services.digital_signature.verification import (
    compute_sha1_thumbprint,
    compute_signature_hash,
    compute_thumbprint,
    extract_signer_certificate_der,
    extract_signer_certificate_info,
    load_trust_roots,
    verify_signed_pdf,
)
from app.services.digital_signature_v2.embridge_pdf import PreparedRegion, finalize_with_cms, prepare_for_external_signing
from app.services.notification_service import create_notification
from app.services.pdf_service import PdfService

pdf_service = PdfService()
logger = get_logger("app.digital_signature_v2")
security_logger = get_logger("app.security")

# Which failure types are genuine security events (vs. routine/expected business-rule failures
# already fully captured by activity_log_service.log_activity) - centralized security logging.
_SECURITY_EVENT_ACTIONS = {"INVALID_CERTIFICATE", "PIN_FAILURE", "TOKEN_DISCONNECTED"}

PROVIDER_NAME = "embridge"


def _clean_hex_like(value: str) -> str:
    """Strips whitespace and common hex byte-separator characters (colons, dashes) - formatting
    differences between how a .NET service (emBridge) and this Python backend render the same
    underlying bytes, not a difference in the bytes themselves."""
    return re.sub(r"[\s:\-]", "", value or "")


def _serial_int_candidates(serial: str) -> set[int]:
    """X.509 serial numbers are integers (RFC 5280 s4.1.2.2) - a DER encoding's leading 0x00 byte
    (added only to keep the ASN.1 INTEGER non-negative when the high bit of the following byte is
    set) carries no meaning beyond that. Comparing as integers is therefore both robust to
    formatting differences (hex case, byte-separator characters, leading zeros - "preserve leading
    zeros where appropriate" is satisfied by never stripping them textually, only by parsing the
    numeric value they encode) and the semantically correct way to compare two serial numbers, not
    a lossy shortcut. Tries both hex and decimal interpretations, since this backend has no
    confirmed guarantee of which base emBridge's `serialNumber` field uses."""
    cleaned = _clean_hex_like(serial)
    candidates: set[int] = set()
    if not cleaned:
        return candidates
    try:
        candidates.add(int(cleaned, 16))
    except ValueError:
        pass
    if cleaned.isdigit():
        try:
            candidates.add(int(cleaned, 10))
        except ValueError:
            pass
    return candidates


def _serials_match(declared: str, embedded: str) -> bool:
    declared_candidates = _serial_int_candidates(declared)
    embedded_candidates = _serial_int_candidates(embedded)
    return bool(declared_candidates) and bool(embedded_candidates) and bool(declared_candidates & embedded_candidates)


def _dn_value_tokens(dn: str) -> set[str]:
    """Extracts just the VALUE portion of each RDN in a Distinguished Name string, ignoring
    attribute labels, order, and casing - deliberately not a full RFC 4514 parser, but tolerant
    enough to compare an asn1crypto `human_friendly` string ("Common Name: X, Organization: Y")
    against whatever string format emBridge/.NET uses for the same DN (commonly "CN=X, O=Y"),
    which comparing the raw formatted strings verbatim would almost never match on even for the
    same certificate - exactly the "friendly names or formatted strings" comparison this is meant
    to avoid."""
    if not dn:
        return set()
    values: set[str] = set()
    for token in re.split(r"[,;]", dn):
        token = token.strip()
        if not token:
            continue
        parts = re.split(r"[:=]", token, maxsplit=1)
        value = parts[-1].strip().lower()
        if value:
            values.add(value)
    return values


def _issuers_match(declared: str, embedded: str) -> bool:
    declared_tokens = _dn_value_tokens(declared)
    embedded_tokens = _dn_value_tokens(embedded)
    if not declared_tokens or not embedded_tokens:
        return False
    # Tolerant overlap, not set equality - different DN serializations may include/omit different
    # optional RDNs (e.g. locality/country) for the exact same issuing CA. This backs up the
    # serial-number comparison rather than replacing it, so a soft majority-overlap threshold is
    # appropriate here in a way it would not be for the serial number itself.
    overlap = declared_tokens & embedded_tokens
    smaller = min(len(declared_tokens), len(embedded_tokens))
    return smaller > 0 and len(overlap) / smaller >= 0.5


def _decode_der(der_base64: str | None) -> bytes | None:
    """Best-effort decode of emBridge's declared certificate DER bytes (its `certificateData`
    field, if the frontend forwarded it) - the exact encoding is not confirmed (raw base64 DER vs.
    PEM-wrapped), so this tries both and returns None (never raises) if neither produces a
    plausible DER structure (starting with the ASN.1 SEQUENCE tag 0x30). None is a normal,
    expected outcome when the client didn't supply certificate data - callers must fall back to
    the serial+issuer comparison in that case, not treat it as an error."""
    if not der_base64:
        return None
    candidate = der_base64.strip()
    if "BEGIN CERTIFICATE" in candidate:
        candidate = "".join(
            line.strip() for line in candidate.splitlines()
            if line.strip() and "BEGIN" not in line and "END" not in line
        )
    try:
        der_bytes = base64.b64decode(candidate, validate=False)
    except Exception:
        return None
    if not der_bytes or der_bytes[0] != 0x30:
        return None
    return der_bytes


def _log_certificate(label: str, subject: str, issuer: str, serial_number: str, der_bytes: bytes | None) -> None:
    """Logs one side of a certificate comparison (declared or embedded) with every field the
    module spec asks for, before any match/mismatch decision is made - so a rejection is always
    fully diagnosable from the log alone, not just from the final yes/no."""
    if der_bytes:
        sha1_fp = compute_sha1_thumbprint(der_bytes)
        sha256_fp = compute_thumbprint(der_bytes)
        der_length = str(len(der_bytes))
    else:
        sha1_fp = sha256_fp = "(no DER available)"
        der_length = "0"
    logger.info(
        "emBridge certificate comparison - %s: subject=%r issuer=%r serial=%r sha1=%s sha256=%s der_base64_length=%s",
        label, subject, issuer, serial_number, sha1_fp, sha256_fp, der_length,
    )


@dataclass
class _PreviewSignature:
    """Same purpose and same one-render-only constraint as Module 45's _PreviewSignature: the
    document handed to the signer (here: digested and sent to emBridge) must be rendered with its
    final visible "Digitally Signed By" content already in place, because the CMS signature
    emBridge returns is a cryptographic commitment to those exact bytes - re-rendering afterward
    with different visible content and reusing the same signature would make it invalid. The
    Dashboard therefore declares the certificate it picked from emBridge's own ListCertificate
    response (see PrepareSignatureRequestV2) BEFORE calling prepare, exactly like Module 45."""
    supervisor_name: str
    supervisor_employee_id: str
    signing_timestamp: datetime
    certificate_subject: str
    certificate_serial_number: str
    certificate_issuer: str
    certificate_valid_from: datetime
    certificate_valid_to: datetime
    verification_status: str


def _load_header_for_signing(db: Session, checksheet_id: int, current_user: User) -> ChecksheetHeader:
    header = db.query(ChecksheetHeader).filter(ChecksheetHeader.id == checksheet_id).first()
    if not header:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checksheet not found")

    if current_user.role not in ("Supervisor", "Admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only supervisors or admins can approve checksheets")

    checksheet_service.authorize_checksheet_access(header, current_user)

    if header.status != ChecksheetStatus.UNDER_REVIEW.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only checksheets under review can be digitally signed. Move it to Under Review first.",
        )
    return header


def _check_completeness(db: Session, header: ChecksheetHeader) -> None:
    provided_values = [{"field_id": v.field_id, "value": v.field_value} for v in header.values]
    missing = checksheet_service._validate_required_values_for_template(db, header.template_id, provided_values)
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Checksheet is incomplete - missing required field values: {', '.join(missing)}",
        )


def _parse_certificate_datetime(value: str | None) -> datetime | None:
    """Best-effort parse of a certificate validity date as reported by emBridge, for the visible
    "pending signature" preview block only - never a trust decision (see PrepareSignatureRequestV2).
    Tries ISO 8601 first (what emBridge's REST responses use elsewhere); returns None rather than
    raising if the value is missing or in a format this doesn't recognize, so a display-only
    formatting quirk can never block the signing flow the way a strict Pydantic `datetime` field
    used to (see docs/EMBRIDGE_INTEGRATION.md)."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _log_failure(db: Session, error: DigitalSignatureError, header: ChecksheetHeader, current_user: User, stage: str, ip_address: str | None) -> None:
    log_activity(
        db,
        error.audit_action,
        user=current_user,
        entity_type="checksheet",
        entity_id=header.id,
        section_id=header.section_id,
        description=f"{current_user.employee_id} - emBridge digital signature {stage} failed for checksheet #{header.id}: {error}",
        new_value={"provider": PROVIDER_NAME, "ip_address": ip_address},
    )
    if error.audit_action in _SECURITY_EVENT_ACTIONS:
        # Certificate mismatch, invalid certificate, PIN failure, token disconnected - genuine
        # security events, logged in addition to the activity_log_service call above, never in
        # place of it.
        security_logger.warning(
            "emBridge digital signature %s failed: %s", stage, error,
            extra={
                "action": f"SIGNATURE_{stage.upper().replace(' ', '_')}_FAILED",
                "success": False,
                "checksheet_id": header.id,
                "reason": str(error),
                "client_ip": ip_address,
            },
        )


def check_signature_eligibility(db: Session, checksheet_id: int, current_user: User) -> dict:
    header = _load_header_for_signing(db, checksheet_id, current_user)
    _check_completeness(db, header)
    return {"eligible": True}


def prepare_document_for_signing(
    db: Session, checksheet_id: int, payload: PrepareSignatureRequestV2, current_user: User,
) -> tuple[bytes, bytes, PreparedRegion]:
    """Returns (prepared_pdf_bytes, document_digest, region) - see embridge_pdf.py. The Dashboard
    sends document_digest to emBridge and must echo prepared_pdf_bytes/region back untouched to
    complete_signature()."""
    header = _load_header_for_signing(db, checksheet_id, current_user)
    _check_completeness(db, header)

    now = datetime.now(timezone.utc)
    valid_from = _parse_certificate_datetime(payload.certificate_valid_from)
    valid_to = _parse_certificate_datetime(payload.certificate_valid_to)

    # A genuinely parsed, genuinely expired date is still worth blocking on - this is the one
    # place an unparseable date is treated differently from an expired one: unparseable degrades
    # to "unknown, show a placeholder" (handled below), expired is a real, actionable rejection.
    if valid_to is not None and valid_to < now:
        error = DigitalSignatureError(f"Certificate expired on {valid_to}")
        error.audit_action = Action.EXPIRED_CERTIFICATE
        _log_failure(db, error, header, current_user, "certificate validation", None)
        raise HTTPException(status_code=error.http_status, detail="The selected certificate has expired.")

    log_activity(
        db, Action.SIGNATURE_INITIATED, user=current_user, entity_type="checksheet", entity_id=header.id,
        section_id=header.section_id,
        description=f"{current_user.employee_id} initiated emBridge digital signature for checksheet #{header.id}",
        new_value={"provider": PROVIDER_NAME},
    )

    preview_signature = _PreviewSignature(
        supervisor_name=current_user.name,
        supervisor_employee_id=current_user.employee_id,
        signing_timestamp=now,
        certificate_subject=payload.certificate_subject,
        certificate_serial_number=payload.certificate_serial_number,
        certificate_issuer=payload.certificate_issuer,
        certificate_valid_from=valid_from or now,
        certificate_valid_to=valid_to or now,
        verification_status=VerificationStatus.VALID,
    )
    unsigned_pdf_bytes = pdf_service.generate_checksheet_pdf_bytes(
        header, digital_signature=preview_signature, status_override=ChecksheetStatus.APPROVED.value,
    )
    return prepare_for_external_signing(unsigned_pdf_bytes)


def complete_signature(db: Session, checksheet_id: int, payload: CompleteSignatureRequestV2, current_user: User, ip_address: str | None):
    """Embeds the CMS blob emBridge returned into the prepared PDF, verifies the result with the
    same PAdES/CMS logic Module 45 uses, and - only if that verification succeeds - stores
    signature metadata and moves the checksheet to APPROVED."""
    header = _load_header_for_signing(db, checksheet_id, current_user)
    _check_completeness(db, header)
    _start = time.monotonic()

    try:
        prepared_pdf_bytes = base64.b64decode(payload.prepared_pdf_base64)
        signed_cms_bytes = base64.b64decode(payload.signed_cms_base64)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Malformed prepared PDF or signature payload.") from exc

    region = PreparedRegion(reserved_region_start=payload.reserved_region_start, reserved_region_end=payload.reserved_region_end)
    try:
        signed_pdf_bytes = finalize_with_cms(prepared_pdf_bytes, region, signed_cms_bytes)
    except Exception as exc:
        error = SignatureVerificationFailedError(f"Could not embed the signature returned by emBridge: {exc}")
        _log_failure(db, error, header, current_user, "embedding", ip_address)
        raise HTTPException(status_code=error.http_status, detail=error.user_message) from exc

    embedded_certificate = extract_signer_certificate_info(signed_pdf_bytes)
    if embedded_certificate is None:
        error = CertificateMissingError()
        _log_failure(db, error, header, current_user, "verification", ip_address)
        raise HTTPException(status_code=error.http_status, detail=error.user_message)

    # Certificate identity comparison (declared-before-signing vs. actually-embedded). Always
    # logged in full before any match/mismatch decision, per docs/EMBRIDGE_INTEGRATION.md - a
    # rejection here must always be fully diagnosable from the log, not just a yes/no.
    declared_der_bytes = _decode_der(payload.certificate_der_base64)
    embedded_der_bytes = extract_signer_certificate_der(signed_pdf_bytes)
    _log_certificate("declared (before signing)", payload.certificate_subject, payload.certificate_issuer, payload.certificate_serial_number, declared_der_bytes)
    _log_certificate("embedded (in signed PDF)", embedded_certificate.subject, embedded_certificate.issuer, embedded_certificate.serial_number, embedded_der_bytes)

    if declared_der_bytes and embedded_der_bytes:
        # Primary identity check: SHA-256 of the DER-encoded certificate. Unambiguous - no string
        # formatting, casing, or encoding question can affect it.
        declared_sha256 = compute_thumbprint(declared_der_bytes)
        embedded_sha256 = compute_thumbprint(embedded_der_bytes)
        certificates_match = declared_sha256 == embedded_sha256
        comparison_method = "SHA-256 DER fingerprint"
    else:
        # Fallback: normalized serial number (primary signal, integer-compared - see
        # _serials_match) plus a tolerant issuer-DN overlap check (secondary signal, never
        # compared as raw/formatted strings - see _issuers_match).
        serial_ok = _serials_match(payload.certificate_serial_number, embedded_certificate.serial_number)
        issuer_ok = _issuers_match(payload.certificate_issuer, embedded_certificate.issuer)
        certificates_match = serial_ok and issuer_ok
        comparison_method = f"normalized serial+issuer (serial_match={serial_ok}, issuer_match={issuer_ok})"

    logger.info("emBridge certificate comparison result: match=%s method=%s", certificates_match, comparison_method)

    if not certificates_match:
        error = CertificateMismatchError()
        _log_failure(db, error, header, current_user, "verification", ip_address)
        raise HTTPException(status_code=error.http_status, detail=error.user_message)

    ca_bundle_path, check_revocation = get_trust_settings(db)
    verification_status = verify_signed_pdf(
        signed_pdf_bytes, trust_roots=load_trust_roots(ca_bundle_path), check_revocation=check_revocation,
    )

    if verification_status == VerificationStatus.EXPIRED_CERTIFICATE:
        error = CertificateExpiredError()
        _log_failure(db, error, header, current_user, "verification", ip_address)
        raise HTTPException(status_code=error.http_status, detail=error.user_message)
    if verification_status == VerificationStatus.REVOKED_CERTIFICATE:
        error = CertificateRevokedError()
        _log_failure(db, error, header, current_user, "verification", ip_address)
        raise HTTPException(status_code=error.http_status, detail=error.user_message)
    if verification_status != VerificationStatus.VALID:
        error = SignatureVerificationFailedError()
        _log_failure(db, error, header, current_user, "verification", ip_address)
        raise HTTPException(status_code=error.http_status, detail=error.user_message)

    now = datetime.now(timezone.utc)

    log_activity(
        db, Action.CERTIFICATE_VERIFIED, user=current_user, entity_type="checksheet", entity_id=header.id,
        section_id=header.section_id,
        description=f"Certificate verified for checksheet #{header.id}: {embedded_certificate.subject}",
        new_value={
            "provider": PROVIDER_NAME,
            "certificate_subject": embedded_certificate.subject,
            "certificate_serial_number": embedded_certificate.serial_number,
            "certificate_issuer": embedded_certificate.issuer,
            "certificate_valid_to": embedded_certificate.valid_to.isoformat(),
            "ip_address": ip_address,
            "token_label": payload.token_label,
        },
    )
    _duration_ms = (time.monotonic() - _start) * 1000
    log_activity(
        db, Action.SIGNATURE_SUCCESS, user=current_user, entity_type="checksheet", entity_id=header.id,
        section_id=header.section_id,
        description=f"emBridge digital signature verified for checksheet #{header.id} by {current_user.employee_id}",
        new_value={"provider": PROVIDER_NAME, "ip_address": ip_address},
        duration_ms=_duration_ms,
    )

    old_pdf_path = header.pdf_path
    signed_pdf_path = pdf_service.save_pdf_bytes(signed_pdf_bytes, file_name_hint=f"checksheet_{header.id}_signed")
    signature_hash = compute_signature_hash(signed_pdf_bytes)

    log_activity(
        db, Action.PDF_SIGNED, user=current_user, entity_type="checksheet", entity_id=header.id,
        section_id=header.section_id,
        description=f"Signed PDF stored for checksheet #{header.id} (emBridge)",
        new_value={"pdf_path": signed_pdf_path, "signature_hash": signature_hash, "provider": PROVIDER_NAME},
    )

    # Everything from here through db.commit() is a genuinely-verified, genuinely-matching
    # signature being persisted - by this point every business-rule check has already passed, so
    # any exception here is an unexpected server-side failure (e.g. a database constraint), not a
    # rejection of the signature itself. Caught explicitly so it can never surface as an uncaught
    # crash: rolled back (so the checksheet is left cleanly in UNDER_REVIEW, never
    # half-approved), logged with the real exception and traceback for diagnosis, and returned to
    # the client as a controlled, structured error rather than a raw 500 - see
    # docs/EMBRIDGE_INTEGRATION.md for the production incident (a real certificate's Distinguished
    # Name exceeding the old VARCHAR(255) column) this specifically guards against.
    try:
        signature_row = DigitalSignature(
            checksheet_id=header.id,
            supervisor_id=current_user.id,
            supervisor_name=current_user.name,
            supervisor_employee_id=current_user.employee_id,
            certificate_subject=embedded_certificate.subject,
            certificate_issuer=embedded_certificate.issuer,
            certificate_serial_number=embedded_certificate.serial_number,
            certificate_thumbprint=embedded_certificate.thumbprint,
            certificate_valid_from=embedded_certificate.valid_from,
            certificate_valid_to=embedded_certificate.valid_to,
            signing_timestamp=now,
            signature_hash=signature_hash,
            verification_status=verification_status,
            provider=PROVIDER_NAME,
        )
        db.add(signature_row)

        header.status = ChecksheetStatus.APPROVED.value
        header.approved_at = now
        header.approved_by = current_user.id
        header.pdf_path = signed_pdf_path
        header.last_modified_at = now
        header.last_modified_by = current_user.id

        db.commit()
        db.refresh(header)
    except Exception:
        db.rollback()
        logger.exception(
            "Failed to persist a verified, matching emBridge signature for checksheet #%s - "
            "signature_subject=%r signature_serial=%r",
            header.id, embedded_certificate.subject, embedded_certificate.serial_number,
        )
        error = SignatureStorageError()
        _log_failure(db, error, header, current_user, "storage", ip_address)
        raise HTTPException(status_code=error.http_status, detail=error.user_message) from None

    if old_pdf_path and old_pdf_path != signed_pdf_path:
        old_file = Path(old_pdf_path)
        if old_file.exists():
            old_file.unlink()

    if header.technician:
        create_notification(
            db,
            user_id=header.technician.id,
            title="Checksheet Digitally Signed",
            message=f"Your checksheet #{header.id} ({header.work_type or 'checksheet'}) was approved and digitally signed by {current_user.name}.",
            notification_type="CHECKSHEET_SIGNED",
            checksheet_id=header.id,
        )

    log_activity(
        db, Action.CHECKSHEET_APPROVED, user=current_user, entity_type="checksheet", entity_id=header.id,
        section_id=header.section_id,
        description=f"Checksheet #{header.id} was digitally signed (emBridge) and approved by {current_user.employee_id}",
        old_value={"status": "UNDER_REVIEW"},
        new_value={"status": "APPROVED", "digitally_signed": True, "provider": PROVIDER_NAME},
    )

    return checksheet_service.get_checksheet_detail(db, header.id, current_user)


def get_signature_detail(db: Session, checksheet_id: int, current_user: User) -> dict:
    header = (
        db.query(ChecksheetHeader)
        .options(joinedload(ChecksheetHeader.digital_signature))
        .filter(ChecksheetHeader.id == checksheet_id)
        .first()
    )
    if not header:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checksheet not found")

    checksheet_service.authorize_checksheet_access(header, current_user)

    signature = header.digital_signature
    if signature is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This checksheet has not been digitally signed")

    # Live re-check: re-verify the signature against the PDF actually on disk, rather than only
    # ever trusting the status recorded at signing time - self-healing if the certificate has
    # since expired, been revoked (when dsc.enable_revocation_check is on), or the stored file is
    # missing/corrupted.
    pdf_file = Path(header.pdf_path) if header.pdf_path else None
    if pdf_file and pdf_file.exists():
        ca_bundle_path, check_revocation = get_trust_settings(db)
        current_status = verify_signed_pdf(
            pdf_file.read_bytes(), trust_roots=load_trust_roots(ca_bundle_path), check_revocation=check_revocation,
        )
    else:
        current_status = VerificationStatus.CERTIFICATE_MISSING

    if current_status != signature.verification_status:
        signature.verification_status = current_status
        db.commit()
        db.refresh(signature)

    return {
        "id": signature.id,
        "checksheet_id": signature.checksheet_id,
        "supervisor_id": signature.supervisor_id,
        "supervisor_name": signature.supervisor_name,
        "supervisor_employee_id": signature.supervisor_employee_id,
        "certificate_subject": signature.certificate_subject,
        "certificate_issuer": signature.certificate_issuer,
        "certificate_serial_number": signature.certificate_serial_number,
        "certificate_thumbprint": signature.certificate_thumbprint,
        "certificate_valid_from": signature.certificate_valid_from,
        "certificate_valid_to": signature.certificate_valid_to,
        "signing_timestamp": signature.signing_timestamp,
        "signature_hash": signature.signature_hash,
        "verification_status": signature.verification_status,
        "provider": signature.provider,
        "created_at": signature.created_at,
    }
