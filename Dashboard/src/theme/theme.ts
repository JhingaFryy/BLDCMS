import { alpha, createTheme, type PaletteMode, type Theme } from '@mui/material';
import { cyberColors, glow } from './palette';

/**
 * Module 33: the Cyber-Industrial Command Center theme. Dark mode is the hero look (Electric
 * Blue / Cyan / Deep Navy, glowing surfaces); light mode gets the same shape/typography/motion
 * language but a cleaner, glare-free palette (true neon-on-white reads poorly and fails contrast,
 * so light mode uses deeper, more saturated tones of the same hues rather than the raw neon
 * values) - both keep excellent readability per the module's explicit requirement. Nothing here
 * touches ThemeModeContext's System/Light/Dark preference logic; this only changes what mode
 * ultimately *looks like*.
 */
const darkShadows = [
  'none',
  '0 1px 2px rgba(0,0,0,0.4)',
  '0 2px 6px rgba(0,0,0,0.45)',
  '0 4px 10px rgba(0,0,0,0.45)',
  ...Array(21).fill('0 8px 28px -6px rgba(0,0,0,0.55)'),
] as Theme['shadows'];

export function buildAppTheme(mode: PaletteMode): Theme {
  const isDark = mode === 'dark';

  const theme = createTheme({
    palette: {
      mode,
      primary: {
        main: cyberColors.electricBlue,
        light: cyberColors.electricBlueLight,
        dark: '#1E5FCC',
        contrastText: '#FFFFFF',
      },
      secondary: {
        main: isDark ? cyberColors.cyan : '#0E8FA8',
        light: cyberColors.cyanLight,
        dark: '#0B7A90',
        contrastText: '#04141A',
      },
      success: {
        main: isDark ? cyberColors.neonGreen : '#128A5C',
        light: cyberColors.neonGreenLight,
        contrastText: '#04140C',
      },
      warning: {
        main: isDark ? cyberColors.amber : '#B57200',
        light: cyberColors.amberLight,
        contrastText: '#1A1200',
      },
      error: {
        main: isDark ? cyberColors.red : '#C82C46',
        light: cyberColors.redLight,
        contrastText: '#FFFFFF',
      },
      info: {
        main: isDark ? cyberColors.purple : '#6D3FD6',
        light: cyberColors.purpleLight,
        contrastText: '#FFFFFF',
      },
      background: isDark
        ? { default: cyberColors.deepNavy, paper: cyberColors.navySurface }
        : { default: '#EEF2FB', paper: '#FFFFFF' },
      text: isDark
        ? { primary: cyberColors.textPrimaryDark, secondary: cyberColors.textSecondaryDark }
        : { primary: '#0F1C33', secondary: '#4A5773' },
      divider: isDark ? alpha(cyberColors.navyBorder, 0.8) : alpha('#0F1C33', 0.12),
    },
    shape: { borderRadius: 14 },
    typography: {
      fontFamily: '"Inter", "Roboto", "Segoe UI", Arial, sans-serif',
      h1: { fontWeight: 700 },
      h2: { fontWeight: 700 },
      h3: { fontWeight: 700 },
      h4: { fontWeight: 700, letterSpacing: -0.5 },
      h5: { fontWeight: 700, letterSpacing: -0.25 },
      h6: { fontWeight: 700 },
      subtitle1: { fontWeight: 600 },
      subtitle2: { fontWeight: 600 },
      button: { fontWeight: 600, textTransform: 'none' as const },
    },
    transitions: {
      duration: { shortest: 120, shorter: 160, short: 200, standard: 240, complex: 300 },
    },
    // Explicitly setting `shadows: undefined` here (rather than omitting the key) makes MUI's
    // deep-merge treat it as an override and lose its own default 25-entry shadow array entirely -
    // any Paper-based component then crashes trying to index into `theme.shadows`. So light mode
    // must omit the key altogether (spreading `{}`) to fall back to MUI's defaults, not pass
    // `shadows: undefined` explicitly.
    ...(isDark ? { shadows: darkShadows } : {}),
    components: {
      MuiCssBaseline: {
        styleOverrides: (t) => ({
          '::selection': { background: alpha(t.palette.primary.main, 0.35) },
          '*::-webkit-scrollbar': { width: 10, height: 10 },
          '*::-webkit-scrollbar-track': { background: 'transparent' },
          '*::-webkit-scrollbar-thumb': {
            background: isDark ? alpha(cyberColors.electricBlue, 0.35) : alpha('#0F1C33', 0.25),
            borderRadius: 8,
          },
          '*::-webkit-scrollbar-thumb:hover': {
            background: isDark ? alpha(cyberColors.electricBlue, 0.55) : alpha('#0F1C33', 0.4),
          },
        }),
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundImage: 'none',
          },
          rounded: { borderRadius: 16 },
          outlined: ({ theme: t }) => ({
            borderColor: t.palette.mode === 'dark' ? alpha(cyberColors.navyBorder, 0.9) : t.palette.divider,
          }),
        },
        defaultProps: { elevation: 0 },
      },
      MuiCard: {
        styleOverrides: {
          root: ({ theme: t }) => ({
            borderRadius: 18,
            border: `1px solid ${t.palette.mode === 'dark' ? alpha(cyberColors.navyBorder, 0.9) : t.palette.divider}`,
            backgroundImage:
              t.palette.mode === 'dark'
                ? `linear-gradient(160deg, ${alpha(cyberColors.navySurfaceElevated, 0.9)} 0%, ${alpha(cyberColors.navySurface, 0.95)} 100%)`
                : 'none',
            transition: 'transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease',
          }),
        },
      },
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: 12,
            paddingInline: 18,
            paddingBlock: 9,
            transition: 'transform 150ms ease, box-shadow 150ms ease, background-color 150ms ease',
          },
          containedPrimary: {
            backgroundImage: `linear-gradient(135deg, ${cyberColors.electricBlue} 0%, ${cyberColors.cyan} 100%)`,
            boxShadow: 'none',
            '&:hover': { boxShadow: glow.primary, transform: 'translateY(-1px)' },
          },
          containedSecondary: {
            backgroundImage: `linear-gradient(135deg, #0B7A90 0%, ${cyberColors.cyan} 100%)`,
            boxShadow: 'none',
            '&:hover': { boxShadow: glow.cyan, transform: 'translateY(-1px)' },
          },
          containedError: {
            '&:hover': { boxShadow: glow.error, transform: 'translateY(-1px)' },
          },
          containedSuccess: {
            '&:hover': { boxShadow: glow.success, transform: 'translateY(-1px)' },
          },
          outlined: {
            '&:hover': { transform: 'translateY(-1px)' },
          },
        },
      },
      MuiIconButton: {
        styleOverrides: {
          root: { transition: 'transform 150ms ease, background-color 150ms ease' },
        },
      },
      MuiChip: {
        styleOverrides: {
          root: { borderRadius: 999, fontWeight: 600 },
        },
      },
      MuiTextField: {
        defaultProps: { variant: 'outlined' },
      },
      MuiOutlinedInput: {
        styleOverrides: {
          root: ({ theme: t }) => ({
            borderRadius: 12,
            transition: 'box-shadow 160ms ease, border-color 160ms ease',
            '&.Mui-focused': {
              boxShadow: `0 0 0 3px ${alpha(t.palette.primary.main, 0.25)}`,
            },
          }),
        },
      },
      MuiTableContainer: {
        styleOverrides: {
          root: ({ theme: t }) => ({
            borderRadius: 16,
            border: `1px solid ${t.palette.mode === 'dark' ? alpha(cyberColors.navyBorder, 0.9) : t.palette.divider}`,
          }),
        },
      },
      MuiTableHead: {
        styleOverrides: {
          root: ({ theme: t }) => ({
            position: 'sticky',
            top: 0,
            zIndex: 2,
            '& .MuiTableCell-root': {
              fontWeight: 700,
              fontSize: '0.75rem',
              letterSpacing: 0.4,
              textTransform: 'uppercase',
              color: t.palette.text.secondary,
              backgroundColor: t.palette.mode === 'dark' ? cyberColors.navySurfaceElevated : '#F4F7FD',
              borderBottom: `1px solid ${t.palette.mode === 'dark' ? alpha(cyberColors.navyBorder, 0.9) : t.palette.divider}`,
            },
          }),
        },
      },
      MuiTableRow: {
        styleOverrides: {
          root: ({ theme: t }) => ({
            transition: 'background-color 120ms ease',
            '&:nth-of-type(odd)': {
              backgroundColor:
                t.palette.mode === 'dark' ? alpha(cyberColors.navySurfaceElevated, 0.35) : alpha('#0F1C33', 0.015),
            },
            '&.MuiTableRow-hover:hover': {
              backgroundColor: alpha(t.palette.primary.main, t.palette.mode === 'dark' ? 0.12 : 0.06),
            },
          }),
        },
      },
      MuiTableCell: {
        styleOverrides: {
          root: ({ theme: t }) => ({
            borderBottom: `1px solid ${t.palette.mode === 'dark' ? alpha(cyberColors.navyBorder, 0.6) : t.palette.divider}`,
          }),
        },
      },
      MuiLinearProgress: {
        styleOverrides: {
          root: ({ theme: t }) => ({
            borderRadius: 999,
            height: 8,
            backgroundColor: t.palette.mode === 'dark' ? alpha(cyberColors.navyBorder, 0.6) : alpha('#0F1C33', 0.08),
          }),
          bar: { borderRadius: 999 },
        },
      },
      MuiDrawer: {
        styleOverrides: {
          paper: { border: 'none' },
        },
      },
      MuiAppBar: {
        defaultProps: { elevation: 0 },
      },
      MuiDialog: {
        styleOverrides: {
          paper: { borderRadius: 20 },
        },
      },
      MuiTooltip: {
        styleOverrides: {
          tooltip: ({ theme: t }) => ({
            backgroundColor: t.palette.mode === 'dark' ? cyberColors.navySurfaceElevated : '#1F2937',
            border: t.palette.mode === 'dark' ? `1px solid ${alpha(cyberColors.navyBorder, 0.9)}` : 'none',
            fontSize: '0.75rem',
          }),
        },
      },
      MuiAlert: {
        styleOverrides: {
          root: { borderRadius: 14 },
        },
      },
      MuiSkeleton: {
        styleOverrides: {
          root: ({ theme: t }) => ({
            backgroundColor: t.palette.mode === 'dark' ? alpha(cyberColors.navyBorder, 0.4) : undefined,
          }),
        },
      },
    },
  });

  return theme;
}
