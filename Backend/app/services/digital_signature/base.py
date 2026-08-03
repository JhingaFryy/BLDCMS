"""Shared Digital Signature data shapes.

The backend never signs documents itself - the supervisor's USB DSC token is physically attached
only to the client PC, never to this server. What remains here are the plain data shapes the
orchestration service (digital_signature_v2_service) and verification.py need: the canonical
verification-status vocabulary and a certificate-metadata shape, used to describe (a) the
certificate the Dashboard declares it is about to sign with, and (b) the certificate actually
found embedded in a signed PDF after the fact.
"""
from dataclasses import dataclass
from datetime import datetime


class VerificationStatus:
    """Canonical signature verification status strings (Module 39)."""
    VALID = "VALID"
    INVALID = "INVALID"
    EXPIRED_CERTIFICATE = "EXPIRED_CERTIFICATE"
    REVOKED_CERTIFICATE = "REVOKED_CERTIFICATE"
    CERTIFICATE_MISSING = "CERTIFICATE_MISSING"
    SIGNATURE_CORRUPTED = "SIGNATURE_CORRUPTED"


@dataclass
class CertificateInfo:
    """Metadata describing one signing certificate. `certificate_id` is opaque to the backend -
    it is whatever the client-side local signer uses to identify this certificate again."""
    certificate_id: str
    subject: str
    issuer: str
    serial_number: str
    thumbprint: str
    valid_from: datetime
    valid_to: datetime
    label: str
