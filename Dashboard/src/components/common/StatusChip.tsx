import { Box, alpha, useTheme } from '@mui/material';
import { statusMeta } from '../../theme/statusMeta';

interface StatusChipProps {
  status: string | null | undefined;
  /** Override the auto-derived label (e.g. Users page's Active/Inactive isn't a checksheet status). */
  label?: string;
  size?: 'small' | 'medium';
}

/**
 * Module 33: the single status badge used everywhere a checksheet status is shown - replaces the
 * plain-text status cell in ChecksheetsPage's table and the unstyled, uncolored `<Chip
 * label={status} />` in ChecksheetReviewDialog. Colors always come from theme.ts/statusMeta.ts,
 * never a locally hardcoded hex, so every screen agrees on what "Approved" looks like. A small
 * pulsing dot on Submitted/Under Review communicates "awaiting action" at a glance without
 * relying on color alone (kept subtle - opacity only, no layout-affecting animation).
 */
export default function StatusChip({ status, label, size = 'small' }: StatusChipProps) {
  const theme = useTheme();
  const meta = statusMeta(status);
  const isDark = theme.palette.mode === 'dark';
  const isPending = (status ?? '').toUpperCase() === 'SUBMITTED' || (status ?? '').toUpperCase() === 'UNDER_REVIEW';

  return (
    <Box
      component="span"
      sx={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 0.75,
        px: size === 'small' ? 1.1 : 1.5,
        py: size === 'small' ? 0.35 : 0.55,
        borderRadius: 999,
        fontSize: size === 'small' ? '0.72rem' : '0.8rem',
        fontWeight: 700,
        letterSpacing: 0.3,
        color: meta.color,
        bgcolor: alpha(meta.color, isDark ? 0.16 : 0.12),
        border: `1px solid ${alpha(meta.color, isDark ? 0.5 : 0.35)}`,
        whiteSpace: 'nowrap',
      }}
    >
      <Box
        component="span"
        sx={{
          width: 6,
          height: 6,
          borderRadius: '50%',
          bgcolor: meta.color,
          animation: isPending ? 'cyberPulseGlow 1.6s ease-in-out infinite' : 'none',
        }}
      />
      {label ?? meta.label}
    </Box>
  );
}
