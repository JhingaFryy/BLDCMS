import { Component, type ErrorInfo, type ReactNode } from 'react';
import { Box, Button, Stack, Typography } from '@mui/material';
import ErrorOutlineRoundedIcon from '@mui/icons-material/ErrorOutlineRounded';

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  error: Error | null;
}

/**
 * There was previously no error boundary anywhere in the Dashboard, so any uncaught exception
 * thrown during React's render phase (as opposed to inside an event handler's own try/catch,
 * which React does not treat specially) unmounts the *entire* tree, producing a blank page with
 * no way to recover short of a manual browser refresh - this was reported for the Digital
 * Signature v2 (emBridge) flow specifically, but the same failure mode applies anywhere in the
 * app. This is the app-wide safety net: it can't prevent a bug, but it guarantees a bug shows a
 * recoverable error screen instead of a blank one, and always logs full diagnostics to the
 * console (componentDidCatch's `info.componentStack` pinpoints which component tree was
 * rendering when it failed, which a bare try/catch around an async function can never capture).
 */
export default class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { error: null };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    // eslint-disable-next-line no-console
    console.error('[ErrorBoundary] Uncaught render error:', error, '\nComponent stack:', info.componentStack);
  }

  private handleReload = () => {
    window.location.reload();
  };

  private handleDismiss = () => {
    this.setState({ error: null });
  };

  render() {
    if (this.state.error) {
      return (
        <Box sx={{ display: 'flex', minHeight: '100vh', alignItems: 'center', justifyContent: 'center', p: 3 }}>
          <Stack spacing={2} alignItems="center" sx={{ maxWidth: 480, textAlign: 'center' }}>
            <ErrorOutlineRoundedIcon color="error" sx={{ fontSize: 56 }} />
            <Typography variant="h6" fontWeight={700}>Something went wrong</Typography>
            <Typography variant="body2" color="text.secondary">
              An unexpected error occurred and this part of the page could not be displayed. No
              data was lost - anything in progress (such as a checksheet approval) was not
              completed. Check the browser console for technical details, or reload the page.
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ fontFamily: 'monospace', wordBreak: 'break-word' }}>
              {this.state.error.message}
            </Typography>
            <Stack direction="row" spacing={1.5}>
              <Button variant="outlined" onClick={this.handleDismiss}>Try to continue</Button>
              <Button variant="contained" onClick={this.handleReload}>Reload page</Button>
            </Stack>
          </Stack>
        </Box>
      );
    }
    return this.props.children;
  }
}
