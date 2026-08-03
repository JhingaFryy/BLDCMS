import { Box, Tooltip, alpha, useTheme } from '@mui/material';
import HistoryRoundedIcon from '@mui/icons-material/HistoryRounded';

/**
 * Shown on a checksheet that is APPROVED but has no digital_signature row - i.e. it was approved
 * before the Digital Signature module existed. These are never retroactively signed (no
 * digital_signature row is ever backfilled for historical data) - this badge exists purely to
 * make that distinction visually obvious next to checksheets that were approved AND digitally
 * signed, without implying anything is wrong or incomplete about the historical record itself.
 */
export default function LegacyApprovalBadge() {
  const theme = useTheme();
  const color = theme.palette.info.main;

  return (
    <Tooltip title="Approved before Digital Signature was introduced - no certificate is required or expected for this record.">
      <Box
        component="span"
        sx={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 0.4,
          px: 0.9,
          py: 0.2,
          borderRadius: 999,
          fontSize: '0.68rem',
          fontWeight: 700,
          color,
          bgcolor: alpha(color, theme.palette.mode === 'dark' ? 0.18 : 0.12),
          border: `1px solid ${alpha(color, 0.4)}`,
          cursor: 'default'
        }}
      >
        <HistoryRoundedIcon sx={{ fontSize: 13 }} /> Legacy Approval (Unsigned)
      </Box>
    </Tooltip>
  );
}
