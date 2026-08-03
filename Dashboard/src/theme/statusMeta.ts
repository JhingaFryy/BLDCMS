import { statusTones, type StatusTone } from './palette';

/**
 * Module 33: normalizes the backend's raw ChecksheetStatus enum (DRAFT/SUBMITTED/UNDER_REVIEW/
 * APPROVED/REJECTED - see app/schemas/checksheet_header.py's ChecksheetStatus) into the single
 * shared status-color/label system in palette.ts. This is the ONE place that maps a backend
 * status string to a display label - StatusChip, DashboardCharts, and ReportsPage all call this
 * instead of each maintaining (and drifting from) their own STATUS_COLORS map.
 */
export function statusMeta(rawStatus: string | null | undefined) {
  const tone = statusToneFor(rawStatus);
  return statusTones[tone];
}

export function statusToneFor(rawStatus: string | null | undefined): StatusTone {
  switch ((rawStatus ?? '').toUpperCase()) {
    case 'DRAFT':
      return 'pending';
    case 'SUBMITTED':
      return 'submitted';
    case 'UNDER_REVIEW':
      return 'underReview';
    case 'APPROVED':
      return 'approved';
    case 'REJECTED':
      return 'rejected';
    default:
      return 'neutral';
  }
}
