/**
 * Module 33: the Cyber-Industrial Command Center color system - Electric Blue / Cyan / Deep Navy
 * as primaries, Neon Green / Purple / Amber / Red as accents. Single source of truth for both the
 * MUI theme (theme.ts) and any component that needs a raw hex (gradients, chart colors, glow
 * shadows) that MUI's palette object itself can't express.
 */

export const cyberColors = {
  electricBlue: '#2F7DFF',
  electricBlueLight: '#6AA6FF',
  cyan: '#22D3EE',
  cyanLight: '#67E8F9',
  deepNavy: '#060B18',
  navySurface: '#0D1526',
  navySurfaceElevated: '#121B30',
  navyBorder: '#22314E',
  neonGreen: '#1FE08A',
  neonGreenLight: '#6CF5B6',
  purple: '#9D6BFF',
  purpleLight: '#C4A6FF',
  amber: '#FFB020',
  amberLight: '#FFCB6B',
  red: '#FF4D6A',
  redLight: '#FF8A9B',
  textPrimaryDark: '#E7EDFB',
  textSecondaryDark: '#94A3C4',
} as const;

/** Gradient tokens keyed by semantic role - used by StatCard/glass surfaces/buttons rather than
 * every component inventing its own `linear-gradient(...)` string. */
export const gradients = {
  primary: `linear-gradient(135deg, ${cyberColors.electricBlue} 0%, ${cyberColors.cyan} 100%)`,
  success: `linear-gradient(135deg, #0FA968 0%, ${cyberColors.neonGreen} 100%)`,
  warning: `linear-gradient(135deg, #D98A00 0%, ${cyberColors.amber} 100%)`,
  error: `linear-gradient(135deg, #D6304C 0%, ${cyberColors.red} 100%)`,
  purple: `linear-gradient(135deg, #6D3FD6 0%, ${cyberColors.purple} 100%)`,
  navy: `linear-gradient(160deg, ${cyberColors.navySurfaceElevated} 0%, ${cyberColors.navySurface} 100%)`,
  loginBackdrop:
    `radial-gradient(circle at 15% 20%, rgba(47,125,255,0.25), transparent 45%), ` +
    `radial-gradient(circle at 85% 10%, rgba(34,211,238,0.2), transparent 40%), ` +
    `radial-gradient(circle at 50% 90%, rgba(157,107,255,0.18), transparent 45%), ` +
    `linear-gradient(160deg, ${cyberColors.deepNavy} 0%, #0A1226 60%, ${cyberColors.deepNavy} 100%)`,
  loginBackdropLight:
    `radial-gradient(circle at 15% 20%, rgba(47,125,255,0.16), transparent 45%), ` +
    `radial-gradient(circle at 85% 10%, rgba(34,211,238,0.14), transparent 40%), ` +
    `radial-gradient(circle at 50% 90%, rgba(157,107,255,0.12), transparent 45%), ` +
    `linear-gradient(160deg, #E8EEFC 0%, #F3F6FD 60%, #EAF0FB 100%)`,
} as const;

/** Soft glow box-shadows keyed by semantic role, used on hover/focus states. Kept as `box-shadow`
 * (a compositor-friendly property alongside transform/opacity) rather than filter/blur tricks, so
 * hover transitions stay GPU-cheap. */
export const glow = {
  primary: `0 0 0 1px rgba(47,125,255,0.4), 0 8px 24px -4px rgba(47,125,255,0.45)`,
  cyan: `0 0 0 1px rgba(34,211,238,0.4), 0 8px 24px -4px rgba(34,211,238,0.45)`,
  success: `0 0 0 1px rgba(31,224,138,0.4), 0 8px 24px -4px rgba(31,224,138,0.45)`,
  warning: `0 0 0 1px rgba(255,176,32,0.4), 0 8px 24px -4px rgba(255,176,32,0.45)`,
  error: `0 0 0 1px rgba(255,77,106,0.4), 0 8px 24px -4px rgba(255,77,106,0.45)`,
  purple: `0 0 0 1px rgba(157,107,255,0.4), 0 8px 24px -4px rgba(157,107,255,0.45)`,
} as const;

export type StatusTone = 'pending' | 'submitted' | 'underReview' | 'approved' | 'rejected' | 'neutral';

/**
 * Module 33: the SINGLE source of truth for checksheet-status color/label mapping - replaces the
 * two independent, inconsistent STATUS_COLORS maps that previously lived in DashboardCharts.tsx
 * (keyed by display label) and ReportsPage.tsx (keyed by raw backend enum), and the bare
 * unstyled `<Chip label={status} />` in ChecksheetReviewDialog.tsx / plain text in
 * ChecksheetsPage.tsx. Backend status enum values (DRAFT/SUBMITTED/UNDER_REVIEW/APPROVED/
 * REJECTED) map to one of these tones; any other display-label variant already used elsewhere
 * (e.g. "Signed", "Needs Correction") is normalized in statusMeta().
 */
export const statusTones: Record<StatusTone, { color: string; glowColor: string; label: string }> = {
  pending: { color: cyberColors.amber, glowColor: glow.warning, label: 'Draft' },
  submitted: { color: cyberColors.electricBlueLight, glowColor: glow.primary, label: 'Submitted' },
  underReview: { color: cyberColors.purpleLight, glowColor: glow.purple, label: 'Under Review' },
  approved: { color: cyberColors.neonGreenLight, glowColor: glow.success, label: 'Approved' },
  rejected: { color: cyberColors.redLight, glowColor: glow.error, label: 'Rejected' },
  neutral: { color: cyberColors.textSecondaryDark, glowColor: 'none', label: 'Unknown' },
};
