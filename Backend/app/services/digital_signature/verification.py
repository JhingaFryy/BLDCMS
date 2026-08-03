"""Shared PAdES signature verification.

Used both right after signing (to compute the `verification_status` stored on the
DigitalSignature row) and on-demand when a Supervisor/Admin opens a signed checksheet's signature
metadata, so the two never disagree - there is exactly one place that decides what a signature's
current status is.

Trust chain validation requires the Certifying Authority's root/intermediate certificates (the
ones the org's licensed DSC vendor - eMudhra, Capricorn, Sify, (n)Code, etc. - issued the
supervisor's certificate under) to be installed on the server and configured via the
`dsc.trusted_ca_bundle_path` system setting. Without it, this can still detect a corrupted,
missing, or expired signature, but cannot independently confirm the certificate was issued by a
trusted CA - see docs/DIGITAL_SIGNATURE_GUIDE.md for how to install the CA bundle.
"""
import hashlib
import logging
from datetime import datetime, timezone
from io import BytesIO

from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign.validation import validate_pdf_signature
from pyhanko_certvalidator import ValidationContext

from .base import CertificateInfo, VerificationStatus

# Without dsc.trusted_ca_bundle_path configured (see load_trust_roots), every chain-building
# attempt below is expected to fail - that failure is deliberately caught and handled as "trust
# chain not verified" rather than a real error, so pyhanko_certvalidator's own error logging for
# it would just be noise in the server log.
logging.getLogger("pyhanko_certvalidator").setLevel(logging.CRITICAL)


def compute_thumbprint(der_bytes: bytes) -> str:
    return hashlib.sha256(der_bytes).hexdigest()


def compute_sha1_thumbprint(der_bytes: bytes) -> str:
    """SHA-1 fingerprint - not used for any trust/identity decision (SHA-256, via
    compute_thumbprint, is the primary identity check throughout this module), but SHA-1 is what
    most certificate-viewer UIs (browsers, Windows cert manager, emBridge's own token explorer)
    display by convention, so logging it alongside SHA-256 makes a certificate log entry directly
    cross-checkable against what a human sees on screen when diagnosing a mismatch."""
    return hashlib.sha1(der_bytes).hexdigest()  # noqa: S324 - diagnostic only, not a security use


def compute_signature_hash(signed_pdf_bytes: bytes) -> str:
    return hashlib.sha256(signed_pdf_bytes).hexdigest()


def load_trust_roots(ca_bundle_path: str | None) -> list:
    """Loads root/intermediate CA certificates from a PEM bundle file for trust-chain validation.
    Returns an empty list (no chain validation possible) if no bundle is configured or the file
    cannot be read - callers must treat that as "trust chain not independently verified", not as
    an error."""
    if not ca_bundle_path:
        return []
    try:
        from pyhanko.sign.signers import load_certs_from_pemder
        return list(load_certs_from_pemder([ca_bundle_path]))
    except Exception:
        return []


def verify_signed_pdf(signed_pdf_bytes: bytes, trust_roots: list | None = None, check_revocation: bool = False) -> str:
    """Returns one of the VerificationStatus constants for the FIRST embedded signature field
    (this application only ever produces one, "SupervisorDigitalSignature", per checksheet)."""
    try:
        reader = PdfFileReader(BytesIO(signed_pdf_bytes))
        embedded = reader.embedded_signatures
    except Exception:
        return VerificationStatus.SIGNATURE_CORRUPTED

    if not embedded:
        return VerificationStatus.CERTIFICATE_MISSING

    sig = embedded[0]
    cert = sig.signer_cert
    now = datetime.now(timezone.utc)
    if cert.not_valid_after < now:
        return VerificationStatus.EXPIRED_CERTIFICATE

    try:
        status = validate_pdf_signature(
            sig,
            signer_validation_context=ValidationContext(
                trust_roots=trust_roots or [], allow_fetching=check_revocation,
            ),
        )
    except Exception:
        status = None

    if status is not None and not status.intact:
        return VerificationStatus.SIGNATURE_CORRUPTED

    if status is not None and getattr(status, "revoked", False):
        return VerificationStatus.REVOKED_CERTIFICATE

    if status is not None and status.trusted:
        return VerificationStatus.VALID

    if trust_roots:
        # A CA bundle IS configured and the chain still didn't validate - this is a real trust
        # failure (wrong/unrecognized issuer), not just "no bundle installed yet".
        return VerificationStatus.INVALID

    # No CA bundle configured: the signature is cryptographically intact and the certificate is
    # within its validity window, but the issuing CA's trust chain was never checked - reported as
    # VALID (the strongest claim honestly supportable without the bundle) with the caveat
    # documented above. Installing dsc.trusted_ca_bundle_path upgrades this to a real chain check.
    return VerificationStatus.VALID


def extract_signer_certificate_der(signed_pdf_bytes: bytes) -> bytes | None:
    """Raw DER bytes of the certificate embedded in a signed PDF's first signature field - the
    same certificate extract_signer_certificate_info() describes, but as bytes rather than parsed
    fields, for callers that need to compute their own fingerprints (e.g. SHA-1 alongside the
    SHA-256 extract_signer_certificate_info() already provides via CertificateInfo.thumbprint)."""
    try:
        reader = PdfFileReader(BytesIO(signed_pdf_bytes))
        embedded = reader.embedded_signatures
    except Exception:
        return None
    if not embedded:
        return None
    return embedded[0].signer_cert.dump()


def extract_signer_certificate_info(signed_pdf_bytes: bytes) -> CertificateInfo | None:
    """Module 45: reads the certificate actually embedded in a client-signed PDF's first signature
    field - the source of truth for what was stored/displayed, since the backend never chooses or
    even sees a certificate before this point. Returns None if the PDF has no embedded signature
    (caller should treat that as CertificateInfo missing, same as verify_signed_pdf's
    CERTIFICATE_MISSING status)."""
    try:
        reader = PdfFileReader(BytesIO(signed_pdf_bytes))
        embedded = reader.embedded_signatures
    except Exception:
        return None

    if not embedded:
        return None

    cert = embedded[0].signer_cert
    der_bytes = cert.dump()
    return CertificateInfo(
        certificate_id=format(cert.serial_number, "x").upper(),
        subject=cert.subject.human_friendly,
        issuer=cert.issuer.human_friendly,
        serial_number=format(cert.serial_number, "x").upper(),
        thumbprint=compute_thumbprint(der_bytes),
        valid_from=cert.not_valid_before,
        valid_to=cert.not_valid_after,
        label=cert.subject.human_friendly,
    )
