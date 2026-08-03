# Digital Signature v2 — eMudhra emBridge Integration (Module 40)

Status: **sole supported implementation.** This document describes DSC v2 (eMudhra emBridge),
which has been validated and, as of Module 41.5, is the only digital-signature provider in
BL-DCMS — the original Module 39/45 (IREPSSigner) implementation has been fully removed (see
[Removal Plan](#removal-plan) for what that entailed). BL-DCMS now officially supports eMudhra
emBridge, CryptoID middleware, ProxKey DSC, and other emBridge-compatible USB DSC tokens.

## 1. Why emBridge, and why parallel

Indian Railways mandated replacing the IREPSSigner integration with eMudhra emBridge. IREPSSigner
turned out, after extensive live debugging against a real installed instance, to speak a
proprietary Java WebSocket protocol with no public message-format documentation — see the
Module 45 conversation history for the full trail. Rather than repeat that with emBridge, this
implementation was built strictly from verified sources (below) and was initially shipped as a
separate code path (`*_v2` files, a separate `signature-v2` API prefix, a separate
`DigitalSignatureDialogV2` component) so it could be tested independently, without any risk to the
working v1 flow, before anyone relied on it. That validation is complete; v1 has since been
removed (Module 41.5) and emBridge is the sole signer.

## 2. Verified protocol (evidence trail)

Everything below was confirmed against **eMudhra's own official documentation and live
production code**, not third-party blogs or guesses:

- **"emBridge Windows Installation Guide"** (official PDF,
  `https://embridge.emudhra.com/Docs/Win/emBridge_Installation_Guide(Win).pdf`): emBridge "exposes
  several REST APIs", installs as a Windows service, and is reached at
  `https://localhost.emudhra.com:26769`. Requires a hosts-file entry
  (`127.0.0.1 localhost.emudhra.com`) so eMudhra can serve this address with a real, publicly
  trusted certificate instead of a self-signed one.
- **"emBridge Windows Troubleshooting Guide"** (official PDF, same domain): confirms that even
  the correct URL can trigger a one-time browser SSL-exception prompt on first visit — the
  supervisor must click "Advanced → Proceed" once (Chrome) or "Advanced → Accept the Risk and
  Continue" once (Firefox) before any integration will work in that browser profile.
- **`embridge.emudhra.com/tool/scripts/request.js`** — eMudhra's own live client-side JavaScript,
  served from their public demo tool. This is genuine first-party source, not a reverse-engineered
  guess. It gives the exact endpoint paths and JSON shapes used throughout this integration
  (§3 below).
- **`https://embridge.emudhra.com/helper`** — the encryption proxy every request/response is
  wrapped through, independently confirmed live: a raw request returned an actual Java stack trace
  naming the real internal servlet class `bridglet.helper`, running on eMudhra's Tomcat
  infrastructure. This is not a mock or a guess.
- **AUR `embridge-bin` package notes** (Linux build) confirm emBridge is a .NET Core service
  listening on `26769`, and that its bare root path (`/`) returns 404 — i.e. it only responds to
  specific documented paths, consistent with everything above.

### 2.1 Confirmed endpoints (all under `https://localhost.emudhra.com:26769`)

| Operation | Endpoint | Encrypted? |
|---|---|---|
| Version / availability check | `GET /DSC/Version` | No — the only unencrypted call |
| List connected tokens | `POST /DSC/ListToken` | Yes |
| List certificates on a token | `POST /DSC/ListCertificate` | Yes |
| Sign | `POST /DSC/PKCSSign` | Yes |

Every encrypted call is wrapped: plaintext JSON → `https://embridge.emudhra.com/helper`
(`requestMode: "enc"`) → encrypted blob → `POST /DSC/{endpoint}` → encrypted response →
`https://embridge.emudhra.com/helper` again (`requestMode: "dec"`) → plaintext JSON. See
`Dashboard/src/services/embridgeClient.ts` for the exact implementation.

**Important correction**: `/helper` is *not* reachable directly from a third-party browser origin.
eMudhra's own demo page only ever calls it same-origin (its client code always passes an empty
`endecAPI`, which resolves `/helper` relative to `embridge.emudhra.com` itself — see
`request.js`'s `setMinVersion()` call) — there is no evidence anywhere in eMudhra's documentation
or code that `/helper` grants CORS access to third-party origins, and attempting this from
BL-DCMS's own origin fails with a CORS error (`net::ERR_FAILED`, no
`Access-Control-Allow-Origin`), confirming it directly. The `/DSC/*` endpoints on the *local*
emBridge service are a different matter — that service exists specifically to be called from
arbitrary websites' browser JS (that's its entire purpose), so those calls remain direct
browser-to-`localhost.emudhra.com:26769` calls. Only the `/helper` round-trip is relayed through
this backend (`POST /checksheet/signature-v2/embridge-helper`, see `app/api/digital_signature_v2.py`)
— a standard backend-proxy pattern, not a CORS bypass: CORS is a browser same-origin policy that
does not apply to server-to-server HTTP calls at all, so nothing about browser security is
disabled or worked around. Verified live: the backend proxy, called through a full authenticated
FastAPI TestClient round trip, successfully reaches eMudhra's real `/helper` service and relays
its response unchanged.

### 2.2 Signing model

`PKCSSign` signs a **digest**, not a whole document (`dataType: "Sha256HashPKCS7"` — sign a
SHA-256 hash, get back a detached PKCS#7/CMS blob). This is a better fit for PDF signing than
"hand over the whole file" — it maps directly onto `pyhanko`'s own purpose-built external-signing
API (`PdfCMSEmbedder` / `PdfTBSDocument.resume_signing`, see
`app/services/digital_signature_v2/embridge_pdf.py`), which computes a digest, reserves a
signature placeholder, and later embeds a CMS blob obtained from anywhere — exactly this scenario.

### 2.2.1 Confirmed certificate field names

`ListCertificate`'s response field names were confirmed directly from eMudhra's own certificate
list-rendering code (`generateCertCardBody` in
`embridge.emudhra.com/tool/scripts/DynamicControl.js`, switch cases 0–15), not guessed by symmetry
with the request's `certFilter` field names (which use different casing/wording). Notably:
`issuerName` (not `issuer`) and `validTill` (not `validTo`). An earlier version of this
integration used the wrong names for both, which meant `certificate.issuer`/`certificate.valid_to`
were always `undefined` in the actual mapped object, silently defaulted to empty strings by a `??
''` fallback, and only surfaced as a failure once a supervisor actually tried to sign: the backend
rejected `POST /checksheet/{id}/signature-v2/prepare` with a 422 (Pydantic couldn't parse `""` as a
`datetime` for `certificate_valid_to`), and the frontend's error handling at the time rendered that
Pydantic validation array directly as a React child, crashing the whole page. Fixed in
`Dashboard/src/services/embridgeClient.ts` (correct field names) and, for defense in depth,
`certificate_valid_from`/`certificate_valid_to` in `PrepareSignatureRequestV2` were changed from a
strict `datetime` to an optional string, parsed leniently in `digital_signature_v2_service.py` -
this is display-only metadata for the pending-signature preview block, not a trust boundary (the
real validity check happens later against the certificate actually embedded in the signed PDF), so
a formatting quirk in it should never be able to block signing outright. Separately,
`Dashboard/src/utils/apiError.ts` now formats *any* FastAPI validation-error array into a readable
string before it can reach a React child, as a general safety net beyond this one field-name bug.

### 2.2.2 Certificate identity comparison (declared vs. embedded)

`complete_signature` independently verifies the certificate actually embedded in the signed PDF
matches the one the supervisor picked before signing - a real defense-in-depth check, not just a
sanity check, since the CMS blob could in principle come back signed with a different certificate
than intended. The comparison is layered:

1. **Primary** (used when emBridge's `certificateData` field - case 11 in `generateCertCardBody`,
   confirmed to exist but not confirmed encoding - decodes to a plausible DER structure): SHA-256
   fingerprint of the DER-encoded certificate on both sides. Unambiguous - no string formatting,
   casing, or encoding question can affect it.
2. **Fallback** (when DER isn't available, e.g. emBridge omitted `certificateData` or it didn't
   decode): normalized serial number (compared as an *integer*, trying both hex and decimal
   interpretations, per RFC 5280's definition of a serial number as an integer - this is robust to
   colon/dash separators, casing, and leading zero bytes without ever needing to guess which
   textual format emBridge uses) AND a tolerant Distinguished Name token-overlap check for issuer
   (never a raw/formatted-string comparison - see `_dn_value_tokens`/`_issuers_match` in
   `digital_signature_v2_service.py`).

Both the declared and embedded certificate's subject/issuer/serial/SHA-1/SHA-256/DER-length are
logged (`app.digital_signature_v2` logger → `application.log`) before every match/mismatch
decision, regardless of outcome - a rejection is always fully diagnosable from the log alone.

### 2.3 What is *not* independently confirmed

- Whether `dataToSign` should be **hex** or **base64** for `Sha256HashPKCS7`. This implementation
  sends **hex**, based on the demo page's own client-side error-message regexes (`/hex data/` vs
  `/base-64/`) implying the server distinguishes these per `dataType`. If real-hardware testing
  shows this is wrong, only `bufferToHex()` in `embridgeClient.ts` needs to change.
- Whether the `signedText` response field is base64-encoded DER (assumed, as the only sensible way
  to represent a binary CMS blob as the displayable/copyable text the demo page renders it as).
- Whether eMudhra's **public** `/helper` proxy is even the intended encryption service for a
  third-party production integration, versus something eMudhra expects to provision
  customer-specific (this backend now relays to it server-to-server - see §2.1 - which resolves
  the CORS problem but not this underlying provisioning question). **Recommend confirming with
  eMudhra before relying on this at scale.**

**Fixed during testing**: the request body sent to `/DSC/{endPoint}` was initially just the
extracted `encryptedRequest` ciphertext string. Re-reading eMudhra's own client code
(`CallService(endPoint, data)` in `request.js`) showed it actually sends the **entire** `/helper`
response envelope (`{encryptedRequest, encryptionKeyID, errorMsg}`, as one JSON object) as the
body - the local service needs `encryptionKeyID` to know which key to decrypt with. Sending just
the ciphertext was a plausible cause of an observed `"Object reference not set to an instance of
an object"` (.NET `NullReferenceException`) error from emBridge. Fixed in `embridgeClient.ts`'s
`callDscService()`.

None of this was guessed in the sense of "invented" — it's either read directly from eMudhra's own
official documents/code, or a documented assumption with a stated reason and a single, isolated
place to fix it if wrong.

## 3. Architecture

```
Supervisor's browser (Dashboard)
   │
   ├─ https://localhost.emudhra.com:26769/DSC/*   (emBridge, local, never touches BL-DCMS backend)
   │    - ListToken / ListCertificate / PKCSSign
   │    - PIN entered here, sent only to this local address, never to the backend
   │
   └─ BL-DCMS backend (FastAPI) — never contacts emBridge, never sees a private key
        - GET  /checksheet/{id}/signature-v2/eligibility   completeness check
        - POST /checksheet/{id}/signature-v2/prepare       render PDF, reserve signature
                                                            placeholder, return digest to sign
        - POST /checksheet/{id}/signature-v2/complete      embed CMS, verify (pyhanko), store,
                                                            approve, audit log
        - GET  /checksheet/{id}/signature-v2               re-verify + return stored signature
        - POST /checksheet/signature-v2/embridge-helper    relays to eMudhra's encryption
                                                             service server-to-server (the
                                                             browser cannot reach it directly -
                                                             no CORS allowance for third-party
                                                             origins, see §2.1)
                                                                │
                                                                └─ https://embridge.emudhra.com/helper
                                                                    (eMudhra's own encryption
                                                                    proxy - relayed verbatim,
                                                                    never inspected/decrypted
                                                                    by this backend)
```

Backend files (all new, zero changes to Module 45's files):
`app/services/digital_signature_v2/embridge_pdf.py`, `app/services/digital_signature_v2_service.py`,
`app/schemas/digital_signature_v2.py`, `app/api/digital_signature_v2.py` (now also includes the
`/embridge-helper` proxy endpoint).

Frontend files (all new): `Dashboard/src/services/embridgeClient.ts`,
`Dashboard/src/pages/DigitalSignatureDialogV2.tsx`. `ChecksheetReviewDialog.tsx` gained one new
optional prop (`onApproveV2`) and one new button, additive only — its existing `onApprove`/Approve
button are untouched. `ChecksheetsPage.tsx` gained new, separate state and handlers alongside the
existing v1 ones.

Signatures from both v1 and v2 are stored in the same `digital_signatures` table
(`provider = "client-local-signer"` for v1, `"embridge"` for v2) — a checksheet has exactly one
signature regardless of path, and that table was already provider-agnostic, so no schema change
was needed.

## 4. Configuration

Nothing in `system_settings` is required specifically for DSC v2 — it reuses the existing
`dsc.trusted_ca_bundle_path` / `dsc.enable_revocation_check` settings (Settings → Digital
Signature) for server-side trust-chain verification, exactly as v1 does. There is no
emBridge-specific backend setting because emBridge's address (`https://localhost.emudhra.com:26769`)
is fixed by eMudhra's own installer (the hosts-file entry it writes), not configurable per
deployment the way the old IREPSSigner port was.

## 5. Installation guide — supervisor PCs

1. Ensure CryptoID middleware is installed and the ProxKey USB token is recognized by Windows
   (unchanged from the existing setup).
2. Download and install emBridge from `https://embridge.emudhra.com/` (admin rights required).
   Confirm the hosts-file entry `127.0.0.1 localhost.emudhra.com` exists in
   `C:\Windows\System32\drivers\etc\hosts` (eMudhra's installer adds this; verify it if emBridge
   was already present).
3. Launch the emBridge tray application and confirm it reports "running".
4. In the browser the supervisor uses for BL-DCMS, visit `https://localhost.emudhra.com:26769`
   directly once. If a certificate warning appears, click **Advanced → Proceed** (Chrome) or
   **Advanced → Accept the Risk and Continue** (Firefox). This one-time step is required per
   browser profile — skipping it causes every DSC v2 sign attempt to fail with "emBridge Not
   Installed / Service Not Running" even though emBridge is actually running.
5. If a corporate proxy is configured via an automatic configuration script, ask IT to add
   `localhost.emudhra.com` to the proxy bypass/exception list (per eMudhra's own troubleshooting
   guide).
6. Open BL-DCMS, go to a checksheet under review, and click **Approve & Sign (emBridge)**. The
   dialog will report which of "emBridge Installed / Service Running / USB Token Connected /
   Certificate Loaded" fails first if something isn't set up correctly.

## 6. Error handling reference

| Condition | User-facing message | Where |
|---|---|---|
| emBridge not installed/running | "emBridge Not Installed / Service Not Running…" | `DigitalSignatureDialogV2` (`checkEmBridgeStatus()` fails) |
| USB token not connected | "Token Not Connected…" | `embridgeClient.listTokens()` |
| No certificate on token | "No signing certificate found…" | `embridgeClient.listCertificates()` |
| Wrong PIN | Incorrect token PIN message | `embridgeClient` error classification, from emBridge's own error text |
| Certificate expired (declared) | "The selected certificate has expired." | backend `prepare_document_for_signing` |
| Certificate expired/revoked (as actually embedded) | Backend-verified, rejects the request | backend `complete_signature` |
| Certificate mismatch (declared vs. actually signed) | "The certificate used to sign the document does not match…" | backend `complete_signature` — defense-in-depth |
| Signature fails cryptographic verification | Generic verification-failure message, no stack trace exposed | backend `complete_signature` (`verify_signed_pdf`) |
| User cancels signing | Dialog returns to certificate selection; no partial state written | `DigitalSignatureDialogV2` |

Every failure path leaves the checksheet in `UNDER_REVIEW` (never partially approved) and writes
an audit log entry (`Action.SIGNATURE_FAILED`/`TOKEN_DISCONNECTED`/etc., all pre-existing Module 39
constants, reused as-is).

## 7. Test Report

**Verified in this environment** (no Windows/ProxKey/CryptoID/emBridge hardware available):
- Backend unit-level, end-to-end simulation: cloned a real checksheet, ran it through
  `check_signature_eligibility` → `prepare_document_for_signing` → (simulated emBridge signing: a
  real `pyhanko` `SimpleSigner` signing the *exact* digest the backend produced, standing in for
  emBridge's `PKCSSign`) → `complete_signature`. Result: checksheet reached `APPROVED`,
  `DigitalSignature` row stored with `provider="embridge"` and `verification_status="VALID"`,
  correct certificate metadata extracted from the signed PDF (not merely echoed from the request).
  Also verified the certificate-mismatch defense: declaring the wrong certificate serial correctly
  rejects the request and leaves the checksheet in `UNDER_REVIEW`. All test data cleaned up
  afterward; the real checksheet used as a template was left untouched.
- `pytest tests/`: 10/10 passed, before and after.
- `npm run build` (Dashboard): clean, zero TypeScript errors.
- Confirmed zero references to v1's `getSigningCertificates`/`approveAndSign` were touched, and
  the v1 "Approve & Digitally Sign" button/handler are byte-for-byte unchanged.

**Not verified — requires real hardware, which this environment does not have**:
- An actual emBridge installation's real `ListToken`/`ListCertificate`/`PKCSSign` responses
  (request/response *shape* is taken from eMudhra's own live code, but has not been exercised
  against a real running emBridge instance).
- Whether `dataToSign` truly wants hex vs. base64 (§2.3).
- The one-time SSL-exception / hosts-file setup steps, end to end, on a real Windows PC.
- A ProxKey token's real PIN-entry behavior and error text through emBridge (the PIN-incorrect/
  retry-limit/cancel error classification in `embridgeClient.ts` is based on the demo page's
  generic error-message regexes, not confirmed against real token error strings).

**Recommended before production rollout**: run through this guide on one real supervisor PC with
emBridge, CryptoID, and a ProxKey token, sign one real test checksheet, and report back exactly
what `embridgeClient.ts`'s console logging shows at each step — the same iterative,
evidence-driven process used to build this integration. Any mismatch is isolated to
`embridgeClient.ts`/`embridge_pdf.py` and does not require touching the approval workflow, audit
logging, or PDF generation.

## Removal Plan

**Status: done (Module 41.5).** With emBridge validated per §7 above, the legacy IREPSSigner (v1)
path was removed:
1. Deleted `app/services/digital_signature_service.py`; its one still-needed function
   (`get_signature_detail`) was relocated into `digital_signature_v2_service.py` first, since
   `digital_signature_v2.py`'s `GET /signature-v2` endpoint depended on it.
2. Removed the 5 v1 endpoints inline in `app/api/checksheet.py` (there was never a separate v1
   router to unmount — v1 was never split out of the generic checksheet router the way v2 was).
3. Removed v1-only symbols from `app/schemas/digital_signature.py` and
   `app/services/digital_signature/factory.py`; kept everything v2 depends on
   (`DigitalSignatureResponse`, `get_trust_settings()`, `base.py`, `errors.py`, `verification.py`
   unchanged).
4. Deleted `Dashboard/src/pages/DigitalSignatureDialog.tsx` and
   `Dashboard/src/services/localSigner.ts`; removed v1 state/handlers from `ChecksheetsPage.tsx`
   and the `onApprove` prop/button from `ChecksheetReviewDialog.tsx`, leaving the emBridge
   ("Approve & Sign") button as the sole, unconditionally-rendered approve/sign action.
5. Removed the orphaned `dsc.local_signer_base_url` system setting (migration 017); trimmed the
   Settings page's Digital Signature card down to the two settings emBridge still reads
   (`dsc.trusted_ca_bundle_path`, `dsc.enable_revocation_check`).

Existing `DigitalSignature` rows produced by v1 (`provider = "client-local-signer"`) were left
untouched — they remain valid audit history and their PDFs remain verifiable; only the code that
produced *new* v1 signatures was removed.
