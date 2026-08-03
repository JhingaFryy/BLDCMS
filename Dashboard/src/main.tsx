import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from './App';
import ErrorBoundary from './components/common/ErrorBoundary';
import './styles.css';
import { logViteEvent } from './utils/viteConnectionLogger';

// Module 33.1: fired once per real page load (module top-level, not a React effect - React 18
// StrictMode double-invokes effects/renders in development, which would double-log this if it
// lived inside App's own mount effect instead).
logViteEvent('INFO', 'Dashboard', 'Dashboard started');

// Development-only: Vite's HMR client (import.meta.hot) is undefined in production builds - Vite
// strips this whole branch out of the production bundle via dead-code elimination, so none of it
// can run in production regardless of any runtime check, satisfying "development-only events must
// only be logged in development mode" by construction rather than by an explicit env check.
if (import.meta.hot) {
  logViteEvent('INFO', 'Vite', 'HMR client connected');
  import.meta.hot.on('vite:beforeUpdate', () => logViteEvent('INFO', 'Vite', 'Hot Module Reload triggered'));
  import.meta.hot.on('vite:afterUpdate', () => logViteEvent('INFO', 'Vite', 'Hot Module Reload applied'));
  import.meta.hot.on('vite:beforeFullReload', () => logViteEvent('WARNING', 'Vite', 'Full page reload triggered'));
  import.meta.hot.on('vite:error', (payload) => logViteEvent('ERROR', 'Vite', `Build error: ${payload.err?.message ?? 'unknown error'}`));
  import.meta.hot.on('vite:ws:disconnect', () => logViteEvent('WARNING', 'Vite', 'Dev server WebSocket (HMR) connection lost'));
  import.meta.hot.on('vite:ws:connect', () => logViteEvent('INFO', 'Vite', 'Dev server WebSocket (HMR) connection established'));
}

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  </React.StrictMode>
);
