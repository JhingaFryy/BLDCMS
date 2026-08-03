"""Typed error hierarchy for the Digital Signature subsystem.

Cryptographic signing happens entirely on the supervisor's Windows client (via eMudhra emBridge,
talking directly to the USB DSC token), so token/PIN/USB failures are detected and reported by the
Dashboard's client-side emBridge client, never by this backend. What remains here are the failure
modes the backend can actually observe once it receives a client-signed PDF: the embedded
signature doesn't verify, the embedded certificate has expired/been revoked, no signature is
embedded at all, or the certificate the client signed with doesn't match the one it declared
before signing.
"""


class DigitalSignatureError(Exception):
    """Base class for every server-side signing/verification failure. `audit_action` names which
    Action.* constant the caller should log for this failure (see app.services.activity_log_service).
    `http_status` is the HTTP status a caller should map this to (added for Module 40's
    structured-error-response requirement; existing Module 45 call sites that hardcode a status
    instead are unaffected by this attribute's presence - it's additive, not a behavior change)."""
    audit_action = "SIGNATURE_FAILED"
    user_message = "Digital signature failed."
    http_status = 422


class CertificateMissingError(DigitalSignatureError):
    audit_action = "INVALID_CERTIFICATE"
    user_message = "The uploaded document has no embedded digital signature."
    http_status = 422


class CertificateExpiredError(DigitalSignatureError):
    audit_action = "EXPIRED_CERTIFICATE"
    user_message = "The signing certificate has expired."
    http_status = 422


class CertificateRevokedError(DigitalSignatureError):
    audit_action = "INVALID_CERTIFICATE"
    user_message = "The signing certificate has been revoked."
    http_status = 422


class CertificateMismatchError(DigitalSignatureError):
    audit_action = "INVALID_CERTIFICATE"
    user_message = "The certificate used to sign the document does not match the certificate selected before signing."
    # 409 Conflict, not 422: the request itself is well-formed and every individual field is
    # valid - what's wrong is that two otherwise-valid pieces of state (the declared certificate
    # and the certificate actually embedded in the signed PDF) conflict with each other.
    http_status = 409


class SignatureVerificationFailedError(DigitalSignatureError):
    audit_action = "SIGNATURE_FAILED"
    user_message = "The signed document's cryptographic signature could not be verified."
    http_status = 422


class SignatureStorageError(DigitalSignatureError):
    """A signature was genuinely verified and matched, but could not be persisted (e.g. an
    unexpected database error). Distinct from every error above, which are business-rule
    rejections of the signature itself - this is a server-side storage failure after the signature
    was already accepted. Kept as a 500 (it isn't the client's fault and isn't a 4xx business
    rule), but always raised through the same controlled HTTPException path as everything else -
    never an uncaught crash - with the real exception logged server-side only."""
    audit_action = "SIGNATURE_FAILED"
    user_message = "The signature was verified but could not be saved. Please try again or contact support."
    http_status = 500
