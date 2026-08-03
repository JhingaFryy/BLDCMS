export type ViteLogSeverity = 'INFO' | 'WARNING' | 'ERROR';
export type ViteLogSource = 'Vite' | 'Dashboard';

// Deliberately NOT importing getApiBaseUrl from api/client.ts here - that module imports this one
// (to report connectivity events from its interceptors), so importing back would create a
// circular dependency between the two. This is the same one-line base-URL resolution duplicated,
// rather than shared, to keep this module import-free of api/client.ts entirely.
function resolveApiBaseUrl(): string {
  const envBaseUrl = (import.meta as ImportMeta & { env?: Record<string, string | undefined> }).env?.VITE_API_BASE_URL?.trim();
  return envBaseUrl ? envBaseUrl.replace(/\/+$/, '') : '';
}

/**
 * Module 33.1: reports a single Dashboard<->Backend connectivity event to
 * POST /system-health/vite-log, which appends it to logs/vite_connection.log (visible to Admins
 * under System Health > Vite Connection Logs).
 *
 * Deliberately NOT using the shared `api` client from api/client.ts - that client's response
 * interceptor shows a toast and redirects to /login on failure, which would be wrong here (a
 * failed connectivity *report* is not itself a connectivity event worth surfacing to the user,
 * and would risk infinite loops if the report itself is what's failing). Uses a bare `fetch` with
 * a short timeout instead, and never throws - a logging call must never be able to break the
 * feature that triggered it.
 */
export function logViteEvent(severity: ViteLogSeverity, source: ViteLogSource, message: string): void {
  const base = resolveApiBaseUrl();
  const url = `${base}/system-health/vite-log`;
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 5000);

  fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ severity, source, message: message.slice(0, 300) }),
    signal: controller.signal,
  })
    .catch(() => {
      // Best-effort only - see module doc comment above.
    })
    .finally(() => clearTimeout(timeout));
}
