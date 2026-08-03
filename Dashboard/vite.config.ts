import { defineConfig, loadEnv, type Plugin, type ProxyOptions } from 'vite';
import react from '@vitejs/plugin-react';

// Minimal duck-typed shape of Node's http.IncomingMessage covering only what bypass() below
// reads - avoids depending on @types/node (not installed in this project) just for this.
interface ProxyRequest {
  headers: { accept?: string };
  url?: string;
}

/**
 * Several Dashboard SPA routes (e.g. /sections, /users, /settings, /system-health, /otp-logs,
 * /locomotives, /equipment, /templates, /template-fields, /section-equipment-map) happen to share
 * their exact path with a backend API proxy rule below. Without this, a hard refresh on one of
 * those pages sends the browser's full-page navigation request (Accept: text/html) into the API
 * proxy instead of Vite's normal "serve index.html for any unmatched route" SPA fallback - it gets
 * forwarded to the backend, which 307-redirects for the missing trailing slash to an absolute
 * http://<API_TARGET>/... URL, and the browser follows it straight out of the app.
 *
 * `bypass` runs before proxying: returning the request path tells Vite to serve that path itself
 * (triggering the normal SPA/static-file handling) instead of forwarding to the backend. A real
 * page load's Accept header includes "text/html" (browsers always send this for navigations);
 * apiService.ts's axios calls never do, so this only ever bypasses page loads, never real API
 * calls.
 */
function apiProxy(target: string): ProxyOptions {
  return {
    target,
    changeOrigin: true,
    secure: false,
    bypass: (req: ProxyRequest) => {
      if (req.headers.accept && req.headers.accept.indexOf('text/html') !== -1) {
        return req.url;
      }
    },
  };
}

/**
 * Module 33.1: reports "Vite development server started" to the backend's Vite Connection Logs
 * the moment `npm run dev`'s dev server actually starts listening. This runs in Node.js
 * (Vite's own process), not the browser, so it calls the backend directly rather than through the
 * dev server's own proxy (see the `proxy` map below) - that proxy only exists for requests the
 * browser makes once a page is loaded, which hasn't happened yet at this point.
 *
 * Only ever registered inside `server:` config (see `plugins` below is shared, but this plugin's
 * `configureServer` hook is only ever invoked by `vite dev`, never by `vite build`) - so this is
 * dev-only by construction, not by a runtime env check.
 */
function viteConnectionLoggerPlugin(apiTarget: string): Plugin {
  return {
    name: 'vite-connection-logger',
    configureServer(server) {
      server.httpServer?.once('listening', () => {
        fetch(`${apiTarget}/system-health/vite-log`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ severity: 'INFO', source: 'Vite', message: 'Vite development server started' }),
        }).catch(() => {
          // Best-effort - the backend may simply not be running yet when the dev server starts;
          // there is nothing useful to do about that here, and this must never fail the dev server.
        });
      });
    },
  };
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', '');
  const API_TARGET = env.VITE_API_BASE_URL || 'http://localhost:8080';

  return {
  plugins: [react(), viteConnectionLoggerPlugin(API_TARGET)],
    server: {
      host: '0.0.0.0',
      port: 3000,
      proxy: {
        '/auth': apiProxy(API_TARGET),
        '/sections': apiProxy(API_TARGET),
        '/locomotives': apiProxy(API_TARGET),
        '/equipment': apiProxy(API_TARGET),
        '/section-equipment-map': apiProxy(API_TARGET),
        '/templates': apiProxy(API_TARGET),
        '/template-fields': apiProxy(API_TARGET),
        '/checksheet': apiProxy(API_TARGET),
        '/users': apiProxy(API_TARGET),
        '/settings': apiProxy(API_TARGET),
        '/notifications': apiProxy(API_TARGET),
        '/system-health': apiProxy(API_TARGET),
        '/search': apiProxy(API_TARGET),
        '/activity-logs': apiProxy(API_TARGET),
        '/otp-logs': apiProxy(API_TARGET)
      }
    }
  };
});
