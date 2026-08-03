from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SignatureEligibilityResponseV2(BaseModel):
    eligible: bool


class PrepareSignatureRequestV2(BaseModel):
    """The certificate the supervisor picked from emBridge's own ListCertificate response (never
    seen by the backend directly - see services/embridgeClient.ts). Declared here, before
    signing, purely so the backend can render the real certificate details into the checksheet's
    visible "Digitally Signed By" block in the SAME PDF render that gets signed - the signature
    emBridge returns is a cryptographic commitment to those exact bytes, so unlike Module 45's
    first (buggy, since-fixed) draft, this document is only ever rendered once. complete_signature
    independently re-derives and cross-checks this same information from the embedded signature
    afterward and rejects the request if it disagrees (see digital_signature_v2_service.py)."""
    certificate_subject: str
    certificate_issuer: str
    certificate_serial_number: str
    # Deliberately str, not datetime: this is display-only metadata for the checksheet's visible
    # "pending signature" block, not a trust boundary - the real validity check happens later
    # against the certificate actually embedded in the signed PDF (complete_signature). A strict
    # `datetime` field here previously made the whole signing flow hard-fail with an opaque
    # Pydantic error whenever the client sent a value it couldn't parse (e.g. an empty string from
    # a frontend field-name mismatch - see docs/EMBRIDGE_INTEGRATION.md) even though the actual
    # security-relevant data was never at risk. Parsed leniently in
    # digital_signature_v2_service.py; a missing/unparseable value degrades to a clear placeholder
    # in the preview rather than blocking signing outright.
    certificate_valid_from: Optional[str] = None
    certificate_valid_to: Optional[str] = None


class PrepareSignatureResponseV2(BaseModel):
    """Returned by POST /checksheet/{id}/signature-v2/prepare. `document_digest_base64` is what
    the Dashboard sends to emBridge as `dataToSign` (dataType: "Sha256HashPKCS7"); the rest must
    be echoed back byte-for-byte/value-for-value to /signature-v2/complete once emBridge returns
    the signed CMS blob."""
    prepared_pdf_base64: str
    document_digest_base64: str
    reserved_region_start: int
    reserved_region_end: int


class CompleteSignatureRequestV2(BaseModel):
    prepared_pdf_base64: str
    reserved_region_start: int
    reserved_region_end: int
    signed_cms_base64: str
    # Declared purely so complete_signature can independently verify the certificate actually
    # embedded in the signed PDF is the one the supervisor picked, before trusting/storing
    # anything - the values actually stored are always re-derived from the signed PDF itself, never
    # taken from this declaration (see digital_signature_v2_service.py's certificate-mismatch
    # defense). `certificate_der_base64` (emBridge's `certificateData` field, if present) enables a
    # precise DER/SHA-256-based comparison; when absent, the comparison falls back to normalized
    # serial number + issuer.
    certificate_subject: str
    certificate_issuer: str
    certificate_serial_number: str
    certificate_der_base64: Optional[str] = None
    token_label: Optional[str] = None


class EmBridgeHelperProxyRequest(BaseModel):
    """Passthrough body for POST /checksheet/signature-v2/embridge-helper - forwarded verbatim to
    eMudhra's own https://embridge.emudhra.com/helper encryption service. Field names match
    emBridge's own API exactly (see docs/EMBRIDGE_INTEGRATION.md) - this backend never inspects or
    understands the encrypted payload, it only relays it server-to-server so the browser is never
    the one making the cross-origin request (see api/digital_signature_v2.py for why)."""
    requstedData: str
    requestedDataType: str
    requestMode: str
    version: str = ""


class DigitalSignatureResponseV2(BaseModel):
    id: int
    checksheet_id: int
    supervisor_id: Optional[int] = None
    supervisor_name: str
    supervisor_employee_id: str
    certificate_subject: str
    certificate_issuer: str
    certificate_serial_number: str
    certificate_thumbprint: str
    certificate_valid_from: datetime
    certificate_valid_to: datetime
    signing_timestamp: datetime
    signature_hash: str
    verification_status: str
    provider: str
    created_at: datetime

    class Config:
        from_attributes = True
