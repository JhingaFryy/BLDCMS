/**
 * Backend timestamps are UTC but serialized without a timezone suffix (e.g.
 * "2026-07-09T09:38:18.821692"), so `new Date(...)` would otherwise parse them as the browser's
 * local time rather than UTC. This treats any offset-less ISO string as UTC, then renders it in
 * Asia/Kolkata (IST) - used consistently everywhere a timestamp is shown on the dashboard.
 */
export function formatIST(value?: string | null): string {
  if (!value) return '-';

  const hasTimezone = /Z$|[+-]\d{2}:?\d{2}$/.test(value);
  const date = new Date(hasTimezone ? value : `${value}Z`);
  if (Number.isNaN(date.getTime())) return value;

  const datePart = new Intl.DateTimeFormat('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    timeZone: 'Asia/Kolkata'
  }).format(date);

  const timePart = new Intl.DateTimeFormat('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
    timeZone: 'Asia/Kolkata'
  }).format(date);

  return `${datePart}, ${timePart} IST`;
}
