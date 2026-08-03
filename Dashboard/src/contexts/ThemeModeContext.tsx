import { createContext, useContext, useEffect, useMemo, useState } from 'react';

export type ThemeModePreference = 'system' | 'light' | 'dark';

interface ThemeModeContextValue {
  preference: ThemeModePreference;
  resolvedMode: 'light' | 'dark';
  setPreference: (mode: ThemeModePreference) => void;
}

const STORAGE_KEY = 'rdcms.themeMode';
const ThemeModeContext = createContext<ThemeModeContextValue | undefined>(undefined);

function readStoredPreference(): ThemeModePreference {
  const stored = localStorage.getItem(STORAGE_KEY);
  return stored === 'light' || stored === 'dark' || stored === 'system' ? stored : 'system';
}

export function ThemeModeProvider({ children }: { children: React.ReactNode }) {
  const [preference, setPreferenceState] = useState<ThemeModePreference>(readStoredPreference);
  const [systemPrefersDark, setSystemPrefersDark] = useState(
    () => window.matchMedia('(prefers-color-scheme: dark)').matches
  );

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const listener = (event: MediaQueryListEvent) => setSystemPrefersDark(event.matches);
    mediaQuery.addEventListener('change', listener);
    return () => mediaQuery.removeEventListener('change', listener);
  }, []);

  const setPreference = (mode: ThemeModePreference) => {
    localStorage.setItem(STORAGE_KEY, mode);
    setPreferenceState(mode);
  };

  const resolvedMode: 'light' | 'dark' = preference === 'system' ? (systemPrefersDark ? 'dark' : 'light') : preference;

  const value = useMemo(
    () => ({ preference, resolvedMode, setPreference }),
    [preference, resolvedMode]
  );

  return <ThemeModeContext.Provider value={value}>{children}</ThemeModeContext.Provider>;
}

export function useThemeMode() {
  const context = useContext(ThemeModeContext);
  if (!context) throw new Error('useThemeMode must be used within ThemeModeProvider');
  return context;
}
