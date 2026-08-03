import { useState } from 'react';
import {
  Box,
  Dialog,
  DialogContent,
  DialogTitle,
  IconButton,
  Stack,
  Typography,
  alpha,
  useTheme
} from '@mui/material';
import VerifiedRoundedIcon from '@mui/icons-material/VerifiedRounded';
import GppGoodRoundedIcon from '@mui/icons-material/GppGoodRounded';
import CloseRoundedIcon from '@mui/icons-material/CloseRounded';
import type { DigitalSignatureItem } from '../../types';
import { formatIST } from '../../utils/formatDate';

const VERIFICATION_LABELS: Record<string, string> = {
  VALID: 'Valid',
  INVALID: 'Invalid',
  EXPIRED_CERTIFICATE: 'Expired Certificate',
  REVOKED_CERTIFICATE: 'Revoked Certificate',
  CERTIFICATE_MISSING: 'Certificate Missing',
  SIGNATURE_CORRUPTED: 'Signature Corrupted'
};

function MetaRow({ label, value }: { label: string; value?: string | null }) {
  return (
    <Stack direction="row" justifyContent="space-between" spacing={2}>
      <Typography variant="body2" color="text.secondary">{label}</Typography>
      <Typography variant="body2" fontWeight={600} textAlign="right" sx={{ wordBreak: 'break-word', maxWidth: '65%' }}>
        {value || '—'}
      </Typography>
    </Stack>
  );
}

/**
 * Signature Badge + Certificate Verified badge shown wherever a checksheet's status is displayed
 * once it has been digitally signed with the supervisor's real Class-III DSC. Clicking it opens
 * the full signature metadata dialog (Supervisor Name, Employee ID, Certificate
 * Subject/Serial/Issuer/Validity/Thumbprint, Signing Timestamp, Signature Verification Status).
 */
export default function SignatureBadge({ signature }: { signature: DigitalSignatureItem }) {
  const theme = useTheme();
  const [open, setOpen] = useState(false);
  const isValid = signature.verification_status === 'VALID';
  const badgeColor = isValid ? theme.palette.success.main : theme.palette.error.main;

  return (
    <>
      <Stack
        direction="row"
        spacing={0.75}
        alignItems="center"
        onClick={() => setOpen(true)}
        sx={{ cursor: 'pointer', display: 'inline-flex', mt: 0.5 }}
      >
        <Box
          component="span"
          sx={{
            display: 'inline-flex', alignItems: 'center', gap: 0.4, px: 0.9, py: 0.2,
            borderRadius: 999, fontSize: '0.68rem', fontWeight: 700,
            color: badgeColor, bgcolor: alpha(badgeColor, theme.palette.mode === 'dark' ? 0.18 : 0.12),
            border: `1px solid ${alpha(badgeColor, 0.4)}`
          }}
        >
          <VerifiedRoundedIcon sx={{ fontSize: 13 }} /> Digitally Signed
        </Box>
        <Box
          component="span"
          sx={{
            display: 'inline-flex', alignItems: 'center', gap: 0.4, px: 0.9, py: 0.2,
            borderRadius: 999, fontSize: '0.68rem', fontWeight: 700,
            color: badgeColor, bgcolor: alpha(badgeColor, theme.palette.mode === 'dark' ? 0.18 : 0.12),
            border: `1px solid ${alpha(badgeColor, 0.4)}`
          }}
        >
          <GppGoodRoundedIcon sx={{ fontSize: 13 }} /> Certificate {VERIFICATION_LABELS[signature.verification_status] ?? signature.verification_status}
        </Box>
      </Stack>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Stack direction="row" alignItems="center" spacing={1}>
            <VerifiedRoundedIcon color={isValid ? 'success' : 'error'} />
            <span>Digital Signature Details</span>
          </Stack>
          <IconButton size="small" onClick={() => setOpen(false)}><CloseRoundedIcon fontSize="small" /></IconButton>
        </DialogTitle>
        <DialogContent dividers>
          <Stack spacing={1.25}>
            <MetaRow label="Supervisor Name" value={signature.supervisor_name} />
            <MetaRow label="Employee ID" value={signature.supervisor_employee_id} />
            <MetaRow label="Signing Timestamp (IST)" value={formatIST(signature.signing_timestamp)} />
            <MetaRow label="Signature Verification Status" value={VERIFICATION_LABELS[signature.verification_status] ?? signature.verification_status} />
            <MetaRow label="Certificate Subject" value={signature.certificate_subject} />
            <MetaRow label="Certificate Issuer" value={signature.certificate_issuer} />
            <MetaRow label="Certificate Serial Number" value={signature.certificate_serial_number} />
            <MetaRow label="Certificate Thumbprint" value={signature.certificate_thumbprint} />
            <MetaRow label="Certificate Validity Period" value={`${formatIST(signature.certificate_valid_from)} – ${formatIST(signature.certificate_valid_to)}`} />
            <MetaRow label="Signature Hash" value={signature.signature_hash} />
            <MetaRow label="Provider" value={signature.provider} />
          </Stack>
        </DialogContent>
      </Dialog>
    </>
  );
}
