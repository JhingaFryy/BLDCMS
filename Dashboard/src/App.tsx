import { useMemo } from 'react';
import { CssBaseline, ThemeProvider } from '@mui/material';
import { Slide, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import AppRoutes from './routes/AppRoutes';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeModeProvider, useThemeMode } from './contexts/ThemeModeContext';
import { buildAppTheme } from './theme/theme';
import './theme/toast.css';

function ThemedApp() {
  const { resolvedMode } = useThemeMode();

  const theme = useMemo(() => buildAppTheme(resolvedMode), [resolvedMode]);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <AppRoutes />
        <ToastContainer
          position="top-right"
          autoClose={3500}
          theme={resolvedMode}
          transition={Slide}
          toastClassName="cyber-toast"
        />
      </AuthProvider>
    </ThemeProvider>
  );
}

export default function App() {
  return (
    <ThemeModeProvider>
      <ThemedApp />
    </ThemeModeProvider>
  );
}
