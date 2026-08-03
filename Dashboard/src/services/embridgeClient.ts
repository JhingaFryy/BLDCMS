/**
 * Module 40: client for eMudhra emBridge - the sole supported digital-signature provider (the
 * earlier Module 45 IREPSSigner/CrisSigner integration was removed in Module 41.5 - see
 * docs/EMBRIDGE_INTEGRATION.md).
 *
 * VERIFIED against real, authoritative sources - not guessed (see docs/EMBRIDGE_INTEGRATION.md
 * for the full evidence trail):
 *   - eMudhra's official "emBridge Windows Installation Guide" PDF
 *     (https://embridge.emudhra.com/Docs/Win/emBridge_Installation_Guide(Win).pdf): emBridge
 *     "exposes several REST APIs", runs as a Windows service, and is reached at
 *     https://localhost.emudhra.com:26769 - which requires a one-time hosts-file entry
 *     (127.0.0.1 localhost.emudhra.com) and, per the companion Troubleshooting Guide, a one-time
 *     browser SSL-exception click-through (self-signed-adjacent cert on first visit).
 *   - The exact endpoint paths, request/response JSON shapes, and encryption wrapper below are
 *     taken directly from eMudhra's own live client code, fetched from their own public demo tool
 *     (https://embridge.emudhra.com/tool/scripts/request.js) - genuine first-party source, not a
 *     third-party blog. The encryption proxy it calls (https://embridge.emudhra.com/helper) was
 *     independently confirmed live and real (a raw request returned an actual Java stack trace
 *     naming the real internal servlet class `bridglet.helper`, running on eMudhra's own Tomcat
 *     infrastructure).
 *
 * CORRECTION (this revision): an earlier version of this file called
 * https://embridge.emudhra.com/helper directly from the browser. That fails with a CORS error -
 * eMudhra's own demo page only ever calls /helper same-origin (its own client code always passes
 * an empty `endecAPI`, which resolves the URL relative to embridge.emudhra.com itself - see
 * request.js's setMinVersion() call); there is no evidence anywhere in eMudhra's public
 * documentation or code that /helper grants cross-origin access to third-party web origins, and
 * the CORS failure is now direct empirical confirmation that it doesn't. Third-party browser code
 * was never meant to call it directly. The /DSC/* endpoints on the LOCAL emBridge service
 * (https://localhost.emudhra.com:26769) are a different matter - that service exists specifically
 * to be called from arbitrary websites' browser JS, which is its whole purpose, so those calls
 * remain direct browser-to-localhost calls below. Only the /helper encryption round-trip is now
 * relayed through this backend's POST /checksheet/signature-v2/embridge-helper (see
 * app/api/digital_signature_v2.py) - a standard backend-proxy pattern, not a CORS bypass: CORS is
 * a browser same-origin policy that simply does not apply to server-to-server HTTP calls, so
 * nothing about browser security is being disabled or worked around here.
 *
 * NOT independently confirmed - flagged honestly:
 *   - Whether emBridge expects `dataToSign` as hex or base64 for Sha256Hash* dataTypes. The demo
 *     page's own error-message regexes (`/hex data/`, `/base-64/`) suggest the SERVER'S error
 *     text distinguishes these per dataType - for Sha256HashPKCS7 specifically, the hex-data
 *     regex existing alongside a base64 one implies hash payloads are expected as hex, which is
 *     what this file sends. If real hardware testing shows otherwise, only bufferToHex() below
 *     needs to change.
 *   - Whether `signedText` in the PKCSSign response is base64-encoded DER (assumed here, as the
 *     conventional way to represent a binary CMS blob as displayable/copyable text - the demo
 *     page literally renders it into a text box with a "copy" button).
 *   - Whether eMudhra's public /helper is even the right encryption service for a third-party
 *     production integration at all, vs. something customer-specific eMudhra is expected to
 *     provision for a new integrator - this backend proxy makes the same request the demo page
 *     makes, server-to-server, but does not resolve that open provisioning question. Flagged for
 *     confirmation with eMudhra before relying on this at scale.
 */
import type { SigningCertificateItemV2 } from '../types';
import { apiService } from './apiService';

const EMBRIDGE_BASE_URL = 'https://localhost.emudhra.com:26769';
const REQUEST_TIMEOUT_MS = 20000;

export class EmBridgeError extends Error {}

/** emBridge isn't installed, isn't running, the hosts-file entry is missing, or the one-time SSL
 * exception at https://localhost.emudhra.com:26769 was never accepted in this browser. */
export class EmBridgeNotAvailableError extends EmBridgeError {}

/** emBridge is reachable but reports no ProxKey (or other) token currently connected. */
export class TokenNotConnectedError extends EmBridgeError {}

/** emBridge is reachable and a token is connected, but no signing certificate was found. */
export class CertificateNotFoundError extends EmBridgeError {}

/** The supervisor entered an incorrect token PIN (`keyStorePassphrase`). */
export class PinIncorrectError extends EmBridgeError {}

/** Generic passthrough for any other emBridge-reported failure. */
export class SigningFailedError extends EmBridgeError {}

let cachedVersion: string | null = null;

async function withTimeout<T>(fn: (signal: AbortSignal) => Promise<T>): Promise<T> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    return await fn(controller.signal);
  } finally {
    window.clearTimeout(timeout);
  }
}

/** GET /DSC/Version - the one emBridge call that bypasses the encryption wrapper entirely (per
 * eMudhra's own client code). Used both to detect "emBridge installed and running" (requirement
 * #1) and to learn the version string every subsequent encrypted call must include. */
export async function checkEmBridgeStatus(): Promise<{ available: boolean; version: string | null }> {
  try {
    const response = await withTimeout((signal) =>
      fetch(`${EMBRIDGE_BASE_URL}/DSC/Version`, { method: 'GET', signal })
    );
    if (!response.ok) return { available: false, version: null };
    const data = await response.json();
    // `data` is untrusted network input - it could be `null`, a primitive, or missing fields, any
    // of which would throw on unguarded property access (e.g. `null.version`).
    cachedVersion = (data && typeof data === 'object' && typeof data.version === 'string') ? data.version : null;
    return { available: true, version: cachedVersion };
  } catch (err) {
    // Covers both network failures and a response body that isn't valid JSON (response.json()
    // throws a SyntaxError in that case) - either way, emBridge is not usably reachable.
    // eslint-disable-next-line no-console
    console.warn('[embridgeClient] emBridge Version check failed:', err);
    return { available: false, version: null };
  }
}

interface HelperResponse {
  encryptedRequest: string | null;
  encryptionKeyID: string | null;
  errorMsg: string | null;
}

async function encryptRequest(plainJson: string, requestedDataType: string): Promise<HelperResponse> {
  let response;
  try {
    response = await apiService.proxyEmBridgeHelper({
      requstedData: plainJson,
      requestedDataType,
      requestMode: 'enc',
      version: cachedVersion ?? '',
    });
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('[embridgeClient] encryptRequest failed:', requestedDataType, err);
    throw new EmBridgeNotAvailableError('Could not reach eMudhra\'s emBridge encryption service.');
  }
  // response.data is untrusted network input - guard against null/non-object before reading
  // properties off it, rather than trusting the declared axios response type.
  const body = response.data;
  if (!body || typeof body !== 'object') {
    // eslint-disable-next-line no-console
    console.error('[embridgeClient] encryptRequest got an unexpected response shape:', requestedDataType, body);
    throw new EmBridgeError('emBridge\'s encryption service returned an unexpected response.');
  }
  return {
    encryptedRequest: body.encryptedRequest ?? null,
    encryptionKeyID: body.encryptionKeyID ?? null,
    errorMsg: body.errorMsg ?? null,
  };
}

async function decryptResponse<T>(encryptedResponseData: string, requestedDataType: string): Promise<T> {
  let response;
  try {
    response = await apiService.proxyEmBridgeHelper({
      requstedData: encryptedResponseData,
      requestedDataType,
      requestMode: 'dec',
      version: cachedVersion ?? '',
    });
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('[embridgeClient] decryptResponse failed:', requestedDataType, err);
    throw new EmBridgeNotAvailableError('Could not reach eMudhra\'s emBridge encryption service.');
  }
  // Our backend proxy always normalizes the relayed response to real application/json (see
  // proxy_embridge_helper in app/api/digital_signature_v2.py), so axios has already parsed this -
  // no second JSON.parse needed here, unlike eMudhra's own demo code. Still, the decrypted payload
  // is untrusted network input, so guard against null/undefined before handing it to callers that
  // will immediately destructure fields off it (listTokens/listCertificates/signHash).
  if (response.data === null || response.data === undefined) {
    // eslint-disable-next-line no-console
    console.error('[embridgeClient] decryptResponse got an empty response body:', requestedDataType);
    throw new EmBridgeError('emBridge returned an empty response.');
  }
  return response.data as T;
}

interface DscEnvelope {
  status: number;
  version: string;
  responseData: string;
  errorMessage: string | null;
}

/** Full round trip for one DSC operation: encrypt the plain JSON request, POST it to
 * https://localhost.emudhra.com:26769/DSC/{endPoint}, then decrypt the response - mirrors
 * eMudhra's own encRequest() -> CallService() -> DecryptLoad() sequence exactly. */
async function callDscService<T>(endPoint: string, plainRequest: object): Promise<T> {
  if (!cachedVersion) {
    await checkEmBridgeStatus();
    if (!cachedVersion) {
      throw new EmBridgeNotAvailableError('emBridge is not reachable on this PC. Confirm it is installed and running.');
    }
  }

  const encrypted = await encryptRequest(JSON.stringify(plainRequest), endPoint);
  if (encrypted.errorMsg && encrypted.errorMsg !== '' && encrypted.errorMsg !== 'null') {
    throw new EmBridgeError(encrypted.errorMsg);
  }

  let envelopeResponse: Response;
  try {
    envelopeResponse = await withTimeout((signal) =>
      fetch(`${EMBRIDGE_BASE_URL}/DSC/${endPoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal,
        // eMudhra's own client code (request.js's encRequest() -> CallService()) sends the ENTIRE
        // /helper response envelope as the request body here, not just the extracted
        // encryptedRequest string - the local /DSC/{endPoint} handler expects
        // {encryptedRequest, encryptionKeyID, errorMsg} as one JSON object (it needs
        // encryptionKeyID too, to know which key to decrypt with). Sending just the ciphertext
        // string, as an earlier version of this file did, is a plausible cause of the
        // "Object reference not set to an instance of an object" (.NET NullReferenceException)
        // error some deployments hit.
        body: JSON.stringify(encrypted),
      })
    );
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('[embridgeClient] Could not reach local emBridge service:', endPoint, err);
    throw new EmBridgeNotAvailableError(
      `Could not reach emBridge at ${EMBRIDGE_BASE_URL}. Confirm the emBridge service is running ` +
      'and that the one-time SSL exception has been accepted in this browser (visit ' +
      `${EMBRIDGE_BASE_URL} directly once if unsure).`
    );
  }

  let envelope: DscEnvelope;
  try {
    // envelopeResponse.json() throws a SyntaxError if the body isn't valid JSON (e.g. an HTML
    // error page from an intercepting proxy/firewall, or a truncated response) - must not let
    // that escape uncaught.
    envelope = await envelopeResponse.json();
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('[embridgeClient] emBridge returned a non-JSON response:', endPoint, envelopeResponse.status, err);
    throw new EmBridgeError(`emBridge returned an unreadable response (HTTP ${envelopeResponse.status}).`);
  }
  if (!envelope || typeof envelope !== 'object' || typeof envelope.status !== 'number') {
    // eslint-disable-next-line no-console
    console.error('[embridgeClient] emBridge response missing expected fields:', endPoint, envelope);
    throw new EmBridgeError('emBridge returned an unexpected response shape.');
  }

  if (envelope.version) cachedVersion = envelope.version;

  if (envelope.status !== 1) {
    const message = envelope.errorMessage ?? 'emBridge reported a failure.';
    throw classifyEmBridgeError(message);
  }

  if (!envelope.responseData) {
    // eslint-disable-next-line no-console
    console.error('[embridgeClient] emBridge reported success but returned no responseData:', endPoint, envelope);
    throw new EmBridgeError('emBridge reported success but returned no data.');
  }

  return decryptResponse<T>(envelope.responseData, endPoint);
}

function classifyEmBridgeError(message: string): EmBridgeError {
  const lower = message.toLowerCase();
  if (/no connected token|token not found|ckr_device_error/.test(lower)) {
    return new TokenNotConnectedError('No ProxKey USB token detected. Connect the token and try again.');
  }
  if (/certificate/.test(lower) && /not found|no.*found/.test(lower)) {
    return new CertificateNotFoundError('No signing certificate found on the connected token.');
  }
  if (/pass ?phrase|pin|c_login|ckr_user_already_logged_in/.test(lower)) {
    return new PinIncorrectError('Incorrect token PIN. Check the PIN and try again.');
  }
  return new SigningFailedError(message);
}

interface EmBridgeTokenDto {
  keyStoreDisplayName: string;
  [key: string]: unknown;
}

export async function listTokens(): Promise<EmBridgeTokenDto[]> {
  const result = await callDscService<{ tokens: EmBridgeTokenDto[] | null }>('ListToken', {
    AppID: Math.random().toString().slice(2, 12),
    tokenStatus: 'CONNECTED',
    tokenType: 'HARDWARE',
  });
  const tokens = result.tokens ?? [];
  if (tokens.length === 0) {
    throw new TokenNotConnectedError('No PROXKey USB token detected. Connect the token and try again.');
  }
  return tokens;
}

/** Field names verified directly from eMudhra's own certificate-rendering code
 * (generateCertCardBody in embridge.emudhra.com/tool/scripts/DynamicControl.js, cases 0-15) -
 * NOT the same names used in the certFilter request or guessed by symmetry with it. In
 * particular the response uses `issuerName` (not `issuer`) and `validTill` (not `validTo`) -
 * an earlier version of this file used the wrong names for both, which meant
 * certificate.issuer/certificate.valid_to were always undefined, silently defaulted to empty
 * strings by the `?? ''` fallbacks below, and then failed backend Pydantic validation
 * (certificate_valid_to expects a real datetime, not "") the moment a supervisor tried to sign -
 * see docs/EMBRIDGE_INTEGRATION.md for the full diagnosis. `thumbprint` is not part of emBridge's
 * response at all (no case for it in the real rendering code) and is never sent to the backend;
 * it's kept here purely for display and always empty. */
interface EmBridgeCertificateDto {
  keyId: string;
  subject: string;
  issuerName: string;
  serialNumber: string;
  label?: string;
  validFrom: string;
  validTill: string;
  // Case 11 ("Certificate Data") in generateCertCardBody - confirmed to exist as a field, but its
  // exact encoding (raw base64 DER vs. PEM-wrapped) is not confirmed. Passed through as-is; the
  // backend decodes it defensively and falls back to a serial+issuer comparison if it can't be
  // parsed as a certificate (see _decode_der in digital_signature_v2_service.py) - never assumed
  // to be well-formed on this side.
  certificateData?: string;
}

export async function listCertificates(keyStoreDisplayName: string): Promise<SigningCertificateItemV2[]> {
  const result = await callDscService<{ certificates: EmBridgeCertificateDto[] | null }>('ListCertificate', {
    appID: Math.random().toString().slice(2, 12),
    keyStoreDisplayName,
    certFilter: { commonName: '', issuerName: '', serialNumber: '', isNotExpired: '' },
  });
  const certificates = (result.certificates ?? []).filter((cert): cert is EmBridgeCertificateDto => Boolean(cert));
  if (certificates.length === 0) {
    throw new CertificateNotFoundError('No signing certificate found on the connected token.');
  }
  return certificates.map((cert) => {
    if (!cert.validFrom || !cert.validTill) {
      // eslint-disable-next-line no-console
      console.warn('[embridgeClient] Certificate is missing validFrom/validTill from emBridge:', cert);
    }
    return {
      key_id: cert.keyId ?? '',
      subject: cert.subject ?? cert.label ?? 'Unknown certificate',
      issuer: cert.issuerName ?? '',
      serial_number: cert.serialNumber ?? '',
      thumbprint: '',
      valid_from: cert.validFrom ?? '',
      valid_to: cert.validTill ?? '',
      der_base64: cert.certificateData || null,
      key_store_display_name: keyStoreDisplayName,
    };
  });
}

function bufferToHex(buffer: ArrayBuffer): string {
  return Array.from(new Uint8Array(buffer)).map((b) => b.toString(16).padStart(2, '0')).join('');
}

/** Signs `documentDigestBase64` (a SHA-256 digest, base64-encoded - as returned by the backend's
 * /signature-v2/prepare) against `certificate`, prompting the supervisor for their PIN via
 * emBridge's own PIN-entry workflow. Returns the base64-encoded PKCS#7/CMS signature blob to
 * upload to the backend's /signature-v2/complete. */
export async function signHash(documentDigestBase64: string, certificate: SigningCertificateItemV2, pin: string): Promise<string> {
  let dataToSignHex: string;
  try {
    const digestBytes = Uint8Array.from(atob(documentDigestBase64), (c) => c.charCodeAt(0));
    dataToSignHex = bufferToHex(digestBytes.buffer);
  } catch (err) {
    // atob() throws DOMException("The string to be decoded is not correctly encoded.") for
    // malformed base64 - a backend bug, but must not crash the signing flow.
    // eslint-disable-next-line no-console
    console.error('[embridgeClient] Could not decode document digest from backend:', err);
    throw new SigningFailedError('The document digest received from the server was invalid.');
  }

  const result = await callDscService<{ signedText: string }>('PKCSSign', {
    appID: Math.random().toString().slice(2, 12),
    keyStorePassphrase: pin,
    keyStoreDisplayName: certificate.key_store_display_name,
    keyId: certificate.key_id,
    dataToSign: dataToSignHex,
    dataType: 'Sha256HashPKCS7',
    timeStamp: Date.now(),
  });
  if (!result || !result.signedText) {
    throw new SigningFailedError('emBridge did not return a signed value.');
  }
  return result.signedText;
}
