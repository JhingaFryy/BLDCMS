"""Module 40: PDF signature-placeholder preparation and finalization for the eMudhra emBridge
integration.

emBridge's own documented signing operation (`POST /DSC/PKCSSign` with `dataType:
"Sha256HashPKCS7"` - see docs/EMBRIDGE_INTEGRATION.md) signs a SHA-256 digest and returns a
detached PKCS#7/CMS blob - it never receives or returns whole PDF bytes. That means embedding the
signature into the checksheet PDF is this backend's job, split across two HTTP calls:

1. `prepare_for_external_signing()` renders the checksheet PDF (via
   pdf_service.generate_checksheet_pdf_bytes()) and reserves a signature placeholder in it, without
   signing anything. It returns the exact bytes the Dashboard should send back untouched in step 2,
   plus the raw digest bytes to hand to emBridge.
2. `finalize_with_cms()` takes those exact bytes back (unmodified) plus the CMS blob emBridge
   returned, and writes the CMS into the reserved placeholder region - no PDF re-rendering, no
   re-signing, just filling in the one reserved region. This does not require keeping any
   in-memory state between the two calls (the reserved region's start/end offsets are the only
   thing that needs to round-trip, and they travel with the prepared PDF bytes themselves - see
   PreparedRegion below).

Both functions are thin wrappers around pyhanko's own low-level external-signing API
(pyhanko.sign.signers.cms_embedder.PdfCMSEmbedder and
pyhanko.sign.signers.pdf_signer.PdfTBSDocument.resume_signing), which is purpose-built for exactly
this "digest computed here, CMS produced elsewhere" scenario - see their docstrings for the
"interrupted signing process" language this module relies on. No cryptography happens in this
file; the private key never leaves the supervisor's ProxKey token.
"""
from dataclasses import dataclass
from io import BytesIO

from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign.fields import SigFieldSpec, SigSeedSubFilter
from pyhanko.sign.signers.cms_embedder import PdfCMSEmbedder, SigIOSetup, SigObjSetup
from pyhanko.sign.signers.pdf_byterange import PreparedByteRangeDigest, SignatureObject
from pyhanko.sign.signers.pdf_signer import PdfTBSDocument

FIELD_NAME = "SupervisorDigitalSignature"
MD_ALGORITHM = "sha256"
# Signature contents are hex-encoded in the PDF, so this must be >= 2x the largest DER-encoded
# PKCS#7 SignedData blob emBridge can return. 16 KiB reserved (32 KiB of hex) is generous headroom
# for a single Class-III DSC certificate chain.
BYTES_RESERVED = 16 * 1024


@dataclass
class PreparedRegion:
    """Everything needed to resume signing in finalize_with_cms(), after the prepared PDF bytes
    have made a round trip through the Dashboard and emBridge. Deliberately just two ints - no
    server-side session/state to keep alive between the two HTTP calls."""
    reserved_region_start: int
    reserved_region_end: int


def prepare_for_external_signing(pdf_bytes: bytes) -> tuple[bytes, bytes, PreparedRegion]:
    """Returns (prepared_pdf_bytes, document_digest, region). `prepared_pdf_bytes` must be sent
    back unmodified to finalize_with_cms(); `document_digest` is the raw SHA-256 digest to send to
    emBridge as `dataToSign` (base64-encoded) with `dataType: "Sha256HashPKCS7"`."""
    writer = IncrementalPdfFileWriter(BytesIO(pdf_bytes))
    embedder = PdfCMSEmbedder(new_field_spec=SigFieldSpec(sig_field_name=FIELD_NAME))
    cms_writer = embedder.write_cms(field_name=FIELD_NAME, writer=writer)

    next(cms_writer)  # -> yields sig_field_ref, no action needed
    sig_obj = SignatureObject(
        subfilter=SigSeedSubFilter.ADOBE_PKCS7_DETACHED,
        bytes_reserved=BYTES_RESERVED,
        reason="Supervisor approval of BL-DCMS checksheet",
        location="BL-DCMS",
    )
    cms_writer.send(SigObjSetup(sig_placeholder=sig_obj))  # -> yields sig_obj_ref, no action needed

    output = BytesIO()
    prepared_digest, output = cms_writer.send(
        SigIOSetup(md_algorithm=MD_ALGORITHM, in_place=False, output=output)
    )
    assert isinstance(prepared_digest, PreparedByteRangeDigest)

    return (
        output.getvalue(),
        prepared_digest.document_digest,
        PreparedRegion(
            reserved_region_start=prepared_digest.reserved_region_start,
            reserved_region_end=prepared_digest.reserved_region_end,
        ),
    )


def finalize_with_cms(prepared_pdf_bytes: bytes, region: PreparedRegion, cms_der_bytes: bytes) -> bytes:
    """Writes `cms_der_bytes` (the PKCS#7/CMS blob emBridge returned) into the placeholder region
    reserved by prepare_for_external_signing(), producing the final signed PDF. Raises
    pyhanko.sign.general.SigningError if cms_der_bytes doesn't fit in the reserved region."""
    output = BytesIO(prepared_pdf_bytes)
    prepared_digest = PreparedByteRangeDigest(
        document_digest=b"",  # unused by fill_with_cms() - only the offsets below matter here
        reserved_region_start=region.reserved_region_start,
        reserved_region_end=region.reserved_region_end,
    )
    PdfTBSDocument.resume_signing(
        output=output,
        prepared_digest=prepared_digest,
        signature_cms=cms_der_bytes,
    )
    return output.getvalue()
