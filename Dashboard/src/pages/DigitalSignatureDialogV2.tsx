import { useEffect, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Radio,
  RadioGroup,
  FormControlLabel,
  Stack,
  TextField,
  Typography,
  alpha,
  useTheme
} from '@mui/material';
import VerifiedUserRoundedIcon from '@mui/icons-material/VerifiedUserRounded';
import UsbRoundedIcon from '@mui/icons-material/UsbRounded';
import CheckCircleRoundedIcon from '@mui/icons-material/CheckCircleRounded';
import { apiService } from '../services/apiService';
import {
  checkEmBridgeStatus,
  listCertificates,
  listTokens,
  signHash,
  PinIncorrectError,
  TokenNotConnectedError
} from '../services/embridgeClient';
import type { ChecksheetItem, DeclaredCertificateV2, SigningCertificateItemV2 } from '../types';
import { formatIST } from '../utils/formatDate';
import { getErrorMessage } from '../utils/apiError';

interface DigitalSignatureDialogV2Props {
  open: boolean;
  checksheet: ChecksheetItem | null;
  onClose: () => void;
  onSigned: (updated: ChecksheetItem) => void;
}

type Stage = 'loading' | 'select' | 'pin' | 'signing' | 'success' | 'error';

// Module 40 requirement #3: "remember the last selected certificate for that Windows user only" -
// localStorage is scoped to the browser profile, which in practice tracks the Windows login for a
// dedicated supervisor workstation. Never synced to the backend - purely a client-side UX
// convenience, and never used to skip certificate validity/eligibility checks.
const LAST_CERT_STORAGE_KEY = 'bldcms.dscV2.lastCertificateSerial';

// Module 42: fire-and-forget telemetry for client-only emBridge events - never awaited at the
// call site, never allowed to affect the signing control flow (a telemetry failure is silently
// swallowed, not surfaced to the user).
function reportDscEvent(
  eventType: 'USB_TOKEN_DETECTED' | 'CERTIFICATE_SELECTED' | 'TOKEN_REMOVED' | 'PIN_FAILURE',
  checksheetId: number | null | undefined,
): void {
  apiService.reportDscClientEvent({ event_type: eventType, checksheet_id: checksheetId ?? null }).catch(() => {});
}

function certificateToDeclared(cert: SigningCertificateItemV2): DeclaredCertificateV2 {
  return {
    certificate_subject: cert.subject,
    certificate_issuer: cert.issuer,
    certificate_serial_number: cert.serial_number,
    certificate_valid_from: cert.valid_from,
    certificate_valid_to: cert.valid_to,
  };
}

/**
 * Module 40: "Digital Signature Window" - eMudhra emBridge based, the sole supported signing
 * flow (the earlier IREPSSigner-based DigitalSignatureDialog.tsx was removed in Module 41.5).
 * Flow: check emBridge installed/running -> list tokens -> list certificates -> supervisor picks
 * one -> backend prepares a digest to sign -> supervisor enters PIN -> emBridge signs the digest
 * locally against the ProxKey token -> upload the signature for backend verification + storage.
 * The PIN is held in component state only for the duration of the signHash() call and is cleared
 * immediately after, in both the success and failure paths - it is never sent to the backend,
 * logged, or cached (Module 40 requirement #4/#10).
 */
export default function DigitalSignatureDialogV2({ open, checksheet, onClose, onSigned }: DigitalSignatureDialogV2Props) {
  const theme = useTheme();
  const [stage, setStage] = useState<Stage>('loading');
  const [statusMessage, setStatusMessage] = useState('');
  const [certificates, setCertificates] = useState<SigningCertificateItemV2[]>([]);
  const [selectedCertSerial, setSelectedCertSerial] = useState<string>('');
  const [pin, setPin] = useState('');
  const [error, setError] = useState<string | null>(null);

  const loadCertificates = async (checksheetId: number) => {
    setStage('loading');
    setError(null);

    setStatusMessage('Checking checksheet eligibility…');
    try {
      await apiService.checkSignatureEligibilityV2(checksheetId);
    } catch (err) {
      console.error('[DigitalSignatureDialogV2] eligibility check failed:', err);
      setError(getErrorMessage(err, 'This checksheet cannot be signed right now.'));
      setStage('error');
      return;
    }

    setStatusMessage('Detecting emBridge…');
    let embridgeStatus: { available: boolean; version: string | null };
    try {
      embridgeStatus = await checkEmBridgeStatus();
    } catch (err) {
      // checkEmBridgeStatus() is written to never throw (it catches internally and returns
      // {available: false}), but this guard is kept in case that ever changes - "every async call
      // wrapped in try/catch" should hold regardless of what the callee currently promises.
      console.error('[DigitalSignatureDialogV2] emBridge status check threw unexpectedly:', err);
      setError('Unable to check whether emBridge is running.');
      setStage('error');
      return;
    }
    if (!embridgeStatus.available) {
      setError(
        'emBridge Not Installed / Service Not Running - could not reach https://localhost.emudhra.com:26769. ' +
        'Install emBridge from https://embridge.emudhra.com/, confirm the emBridge service is running, and ' +
        'confirm the one-time SSL exception has been accepted in this browser.'
      );
      setStage('error');
      return;
    }

    setStatusMessage('Detecting USB DSC token…');
    let tokens;
    try {
      tokens = await listTokens();
      reportDscEvent('USB_TOKEN_DETECTED', checksheetId);
    } catch (err) {
      console.error('[DigitalSignatureDialogV2] listTokens failed:', err);
      setError(getErrorMessage(err, 'Token Not Connected - connect the ProxKey USB token and try again.'));
      setStage('error');
      return;
    }

    setStatusMessage('Loading certificates…');
    try {
      const allCerts: SigningCertificateItemV2[] = [];
      for (const token of tokens) {
        if (!token?.keyStoreDisplayName) continue; // malformed token entry - skip rather than crash
        // eslint-disable-next-line no-await-in-loop
        const certs = await listCertificates(token.keyStoreDisplayName);
        allCerts.push(...certs);
      }
      if (allCerts.length === 0) throw new Error('No signing certificate found on the connected token.');
      setCertificates(allCerts);

      const remembered = window.localStorage.getItem(LAST_CERT_STORAGE_KEY);
      const rememberedCert = allCerts.find((c) => c.serial_number === remembered);
      setSelectedCertSerial((rememberedCert ?? allCerts[0]).serial_number);
      setStage('select');
    } catch (err) {
      console.error('[DigitalSignatureDialogV2] listCertificates failed:', err);
      setError(getErrorMessage(err, 'Unable to load certificates from emBridge.'));
      setStage('error');
    }
  };

  useEffect(() => {
    if (!open || !checksheet?.id) return;
    loadCertificates(checksheet.id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, checksheet?.id]);

  const handleContinueToPin = () => {
    if (!selectedCertSerial) return;
    window.localStorage.setItem(LAST_CERT_STORAGE_KEY, selectedCertSerial);
    reportDscEvent('CERTIFICATE_SELECTED', checksheet?.id);
    setPin('');
    setStage('pin');
  };

  const handleSign = async () => {
    if (!checksheet?.id || !pin) return;
    const certificate = certificates.find((c) => c.serial_number === selectedCertSerial);
    if (!certificate) return;

    setStage('signing');
    setError(null);
    let signedOk = false;
    let completedChecksheet: ChecksheetItem | null = null;
    try {
      const declared = certificateToDeclared(certificate);

      const prepareRes = await apiService.prepareSignatureDocumentV2(checksheet.id, declared);
      const prepareData = prepareRes?.data;
      if (
        !prepareData ||
        typeof prepareData.prepared_pdf_base64 !== 'string' ||
        typeof prepareData.document_digest_base64 !== 'string' ||
        typeof prepareData.reserved_region_start !== 'number' ||
        typeof prepareData.reserved_region_end !== 'number'
      ) {
        console.error('[DigitalSignatureDialogV2] /signature-v2/prepare returned an unexpected shape:', prepareData);
        throw new Error('The server returned an unexpected response while preparing the document.');
      }
      const { prepared_pdf_base64, document_digest_base64, reserved_region_start, reserved_region_end } = prepareData;

      const signedCmsBase64 = await signHash(document_digest_base64, certificate, pin);
      if (!signedCmsBase64) {
        console.error('[DigitalSignatureDialogV2] signHash returned an empty signature.');
        throw new Error('emBridge did not return a signed value.');
      }

      const completeRes = await apiService.completeSignatureV2(checksheet.id, {
        prepared_pdf_base64,
        reserved_region_start,
        reserved_region_end,
        signed_cms_base64: signedCmsBase64,
        certificate_subject: declared.certificate_subject,
        certificate_issuer: declared.certificate_issuer,
        certificate_serial_number: declared.certificate_serial_number,
        certificate_der_base64: certificate.der_base64,
        token_label: certificate.key_store_display_name,
      });
      if (!completeRes?.data) {
        console.error('[DigitalSignatureDialogV2] /signature-v2/complete returned an unexpected shape:', completeRes?.data);
        throw new Error('The server returned an unexpected response after signing.');
      }

      // Signing and backend verification/storage have now genuinely succeeded - the checksheet IS
      // approved server-side at this point. Everything past here (telling the parent page to
      // refresh) is best-effort UI bookkeeping, not part of the signing operation itself, so its
      // own failures must never be reported as "signature failed" (which would be false and would
      // leave the supervisor thinking they need to sign again).
      signedOk = true;
      completedChecksheet = completeRes.data;
    } catch (err) {
      console.error('[DigitalSignatureDialogV2] Signing failed:', err);
      if (err instanceof TokenNotConnectedError) {
        reportDscEvent('TOKEN_REMOVED', checksheet?.id);
      } else if (err instanceof PinIncorrectError) {
        reportDscEvent('PIN_FAILURE', checksheet?.id);
      }
      setError(getErrorMessage(err, 'Digital signature failed.'));
      setStage('error');
    } finally {
      // Never held in memory longer than this single signing attempt (Module 40 requirement #4).
      setPin('');
    }

    if (signedOk && completedChecksheet) {
      setStage('success');
      try {
        onSigned(completedChecksheet);
      } catch (err) {
        // The signature and backend approval already succeeded by this point - a failure here is
        // in the parent page's own post-signing refresh, not in signing itself. Log it for
        // diagnostics, but do not show a misleading "signature failed" error, and do not let it
        // propagate - the ErrorBoundary at the app root would catch it if it did, but a checksheet
        // that was just successfully signed should never present as a failure to the supervisor.
        console.error('[DigitalSignatureDialogV2] onSigned callback threw after a successful signature:', err);
      }
    }
  };

  const retry = () => {
    if (!checksheet?.id) return;
    if (certificates.length > 0) {
      setStage('select');
      setError(null);
    } else {
      loadCertificates(checksheet.id);
    }
  };

  return (
    <Dialog open={open} onClose={stage === 'signing' ? undefined : onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Stack direction="row" alignItems="center" spacing={1.5}>
          <VerifiedUserRoundedIcon color="primary" />
          <span>Digital Signature (emBridge){checksheet?.id ? ` — Checksheet #${checksheet.id}` : ''}</span>
        </Stack>
      </DialogTitle>
      <DialogContent dividers>
        {stage === 'loading' ? (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2, p: 4 }}>
            <CircularProgress />
            <Typography variant="body2" color="text.secondary">{statusMessage}</Typography>
          </Box>
        ) : null}

        {stage === 'select' ? (
          <Stack spacing={2}>
            <Alert severity="success" icon={<CheckCircleRoundedIcon />}>
              emBridge Installed · Service Running · USB Token Connected · Certificate Loaded
            </Alert>
            <Typography variant="body2" color="text.secondary">
              Select the Class-III Digital Signature Certificate to sign this checksheet with.
              Signing happens on this PC through eMudhra emBridge using your connected ProxKey USB
              token. The signature will be cryptographically embedded in the generated PDF, and the
              checksheet will be locked from further edits once signed.
            </Typography>
            <RadioGroup value={selectedCertSerial} onChange={(e) => setSelectedCertSerial(e.target.value)}>
              {certificates.map((cert) => (
                <Box
                  key={cert.serial_number}
                  sx={{
                    border: `1px solid ${alpha(theme.palette.primary.main, 0.25)}`,
                    borderRadius: 2,
                    p: 1.5,
                    mb: 1,
                    bgcolor: selectedCertSerial === cert.serial_number ? alpha(theme.palette.primary.main, 0.06) : 'transparent'
                  }}
                >
                  <FormControlLabel
                    value={cert.serial_number}
                    control={<Radio />}
                    sx={{ alignItems: 'flex-start', width: '100%' }}
                    label={
                      <Stack spacing={0.25} sx={{ pt: 0.5 }}>
                        <Typography variant="subtitle2" fontWeight={700}>{cert.subject}</Typography>
                        <Typography variant="caption" color="text.secondary">Issuer: {cert.issuer}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          Serial: {cert.serial_number} · Valid {formatIST(cert.valid_from)} – {formatIST(cert.valid_to)}
                        </Typography>
                      </Stack>
                    }
                  />
                </Box>
              ))}
            </RadioGroup>
          </Stack>
        ) : null}

        {stage === 'pin' ? (
          <Stack spacing={2}>
            <Typography variant="body2" color="text.secondary">
              Enter your USB token PIN to sign. The PIN is sent only to emBridge on this PC
              (https://localhost.emudhra.com:26769) - it is never sent to, stored, or logged by the
              BL-DCMS server.
            </Typography>
            <TextField
              label="Token PIN"
              type="password"
              autoFocus
              fullWidth
              value={pin}
              onChange={(e) => setPin(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter' && pin) handleSign(); }}
            />
          </Stack>
        ) : null}

        {stage === 'signing' ? (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2, p: 4 }}>
            <CircularProgress />
            <Typography variant="body2" color="text.secondary">Signing with emBridge and verifying the result…</Typography>
          </Box>
        ) : null}

        {stage === 'success' ? (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 1.5, p: 4 }}>
            <CheckCircleRoundedIcon color="success" sx={{ fontSize: 48 }} />
            <Typography variant="subtitle1" fontWeight={700}>Checksheet digitally signed</Typography>
            <Typography variant="body2" color="text.secondary" textAlign="center">
              The checksheet has been approved, signed via emBridge, and locked from further edits.
            </Typography>
          </Box>
        ) : null}

        {error ? (
          <Alert severity="error" icon={<UsbRoundedIcon />} sx={{ mt: stage === 'error' ? 0 : 2 }}>
            {error}
          </Alert>
        ) : null}
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 3 }}>
        <Button onClick={onClose} disabled={stage === 'signing'}>
          {stage === 'success' ? 'Close' : 'Cancel'}
        </Button>
        {stage === 'error' ? <Button variant="outlined" onClick={retry}>Try Again</Button> : null}
        {stage === 'select' ? (
          <Button variant="contained" color="primary" disabled={!selectedCertSerial} onClick={handleContinueToPin}>
            Continue
          </Button>
        ) : null}
        {stage === 'pin' ? (
          <Button
            variant="contained"
            color="primary"
            startIcon={<VerifiedUserRoundedIcon />}
            disabled={!pin}
            onClick={handleSign}
          >
            Sign &amp; Approve
          </Button>
        ) : null}
      </DialogActions>
    </Dialog>
  );
}
