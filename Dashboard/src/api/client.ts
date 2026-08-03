import axios, { AxiosError } from 'axios';
import { toast } from 'react-toastify';
import { storage } from '../utils/storage';
import { logViteEvent } from '../utils/viteConnectionLogger';

export const getApiBaseUrl = () => {
  const envBaseUrl = (import.meta as ImportMeta & { env?: Record<string, string | undefined> }).env?.VITE_API_BASE_URL?.trim();
  // If VITE_API_BASE_URL is explicitly set, use it; otherwise use relative origin so Vite proxy handles requests.
  return envBaseUrl ? envBaseUrl.replace(/\/+$/, '') : '';
};

/** Display-only label for the Settings page - reflects what api/client.ts actually does above:
 * an explicit VITE_API_BASE_URL is used verbatim, otherwise requests go through Vite's own dev
 * proxy (see vite.config.ts), which forwards to http://localhost:8080 by default. */
export const getApiBaseUrlLabel = () => getApiBaseUrl() || 'Proxied via dev server (default target: http://localhost:8080)';

const base = getApiBaseUrl() || undefined;
const api = axios.create({
  baseURL: base,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' }
});

api.interceptors.request.use((config) => {
  const token = storage.getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Module 33.1: tracks Backend API reachability across requests so connectivity events log a
// state TRANSITION (e.g. online->offline) rather than one line per request - flooding
// vite_connection.log with "connected successfully" on every single successful call would defeat
// "logs should be concise and meaningful". Module-level state is fine here: one Dashboard tab has
// one shared axios instance / one connectivity story.
let backendStatus: 'unknown' | 'online' | 'offline' = 'unknown';
let consecutiveFailures = 0;

api.interceptors.response.use(
  (response) => {
    if (backendStatus !== 'online') {
      logViteEvent(
        'INFO',
        'Dashboard',
        backendStatus === 'offline'
          ? `Backend API reconnected after ${consecutiveFailures} failed attempt(s)`
          : 'Backend API connected successfully'
      );
      backendStatus = 'online';
      consecutiveFailures = 0;
    }
    return response;
  },
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      storage.clearToken();
      storage.clearUser();
      window.location.assign('/login');
    }

    if (error.code === 'ECONNABORTED') {
      // A single slow request timing out doesn't necessarily mean the backend is fully
      // unreachable (unlike the branches below), so this doesn't touch backendStatus.
      logViteEvent('WARNING', 'Dashboard', `Backend API request timeout after ${api.defaults.timeout}ms`);
    } else if (!error.response) {
      // No response at all - refused connection, DNS failure, or a CORS preflight the browser
      // blocked before a real response ever came back (the browser hides the exact reason from
      // JS either way, so this is a best-effort label, not a certain diagnosis).
      consecutiveFailures += 1;
      const crossOrigin = Boolean(api.defaults.baseURL) && !api.defaults.baseURL?.startsWith(window.location.origin);
      if (backendStatus !== 'offline') {
        logViteEvent(
          'ERROR',
          'Dashboard',
          crossOrigin
            ? 'Backend API unreachable (possible CORS or network failure)'
            : 'Backend API unreachable (ECONNREFUSED or network error)'
        );
        backendStatus = 'offline';
      } else {
        logViteEvent('WARNING', 'Dashboard', `API reconnect attempt #${consecutiveFailures} failed`);
      }
      toast.error('Network error. Please verify the backend service.');
    } else if (error.response.status >= 500) {
      // Routine 4xx responses are business-logic outcomes (validation, not-found, etc.), not
      // connectivity problems - only 5xx (the backend itself failing) is worth a connectivity log.
      logViteEvent(
        'WARNING',
        'Dashboard',
        `Failed request: ${(error.config?.method ?? '?').toUpperCase()} ${error.config?.url ?? '?'} -> ${error.response.status}`
      );
    }

    return Promise.reject(error);
  }
);

// Module 33.1: the browser's own network state, independent of whether the backend specifically
// is reachable - e.g. a laptop going into airplane mode vs. only the backend process being down.
window.addEventListener('online', () => logViteEvent('INFO', 'Dashboard', 'Network connection restored'));
window.addEventListener('offline', () => logViteEvent('WARNING', 'Dashboard', 'Network connection lost'));

export default api;
