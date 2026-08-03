import { Paper, alpha, useTheme, type PaperProps } from '@mui/material';

/**
 * Module 33: a glassmorphism surface - translucent, blurred, softly bordered - used by the Login
 * card over the animated gradient/particles backdrop. `backdrop-filter: blur()` is GPU-composited
 * on modern browsers, so this stays cheap even though it looks expensive.
 */
export default function GlassCard({ sx, children, ...rest }: PaperProps) {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';

  return (
    <Paper
      elevation={0}
      sx={{
        borderRadius: 5,
        p: { xs: 3.5, sm: 5 },
        background: isDark ? alpha('#0F1830', 0.55) : alpha('#FFFFFF', 0.7),
        border: `1px solid ${alpha(isDark ? '#3A4E7A' : '#FFFFFF', isDark ? 0.4 : 0.6)}`,
        backdropFilter: 'blur(18px)',
        WebkitBackdropFilter: 'blur(18px)',
        boxShadow: isDark
          ? '0 24px 60px -20px rgba(0,0,0,0.65), 0 0 0 1px rgba(47,125,255,0.08)'
          : '0 24px 60px -24px rgba(15,28,51,0.25)',
        ...sx,
      }}
    >
      {children}
    </Paper>
  );
}
