import { Box, Card, Stack, Typography, alpha, useTheme } from '@mui/material';
import { motion } from 'framer-motion';
import TrendingUpRoundedIcon from '@mui/icons-material/TrendingUpRounded';
import TrendingDownRoundedIcon from '@mui/icons-material/TrendingDownRounded';
import TrendingFlatRoundedIcon from '@mui/icons-material/TrendingFlatRounded';
import type { SvgIconComponent } from '@mui/icons-material';
import AnimatedCounter from './AnimatedCounter';

export interface StatCardTrend {
  /** Positive = up, negative = down, 0/omitted = flat. Purely presentational - callers compute it. */
  delta: number;
  label?: string;
}

interface StatCardProps {
  label: string;
  value: number;
  icon: SvgIconComponent;
  gradient: string;
  glowColor: string;
  trend?: StatCardTrend;
  loading?: boolean;
  onClick?: () => void;
}

/**
 * Module 33: the Dashboard Home KPI card - icon, gradient badge, hover glow, animated counter,
 * small trend indicator. One shared component instead of each page hand-rolling its own
 * `Card > CardContent` stat block (previously duplicated across DashboardPage/ChecksheetsPage/
 * ReportsPage with three different visual treatments).
 */
export default function StatCard({ label, value, icon: Icon, gradient, glowColor, trend, loading, onClick }: StatCardProps) {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';

  const TrendIcon = !trend || trend.delta === 0 ? TrendingFlatRoundedIcon : trend.delta > 0 ? TrendingUpRoundedIcon : TrendingDownRoundedIcon;
  const trendColor = !trend || trend.delta === 0 ? theme.palette.text.secondary : trend.delta > 0 ? theme.palette.success.main : theme.palette.error.main;

  return (
    <motion.div
      whileHover={{ y: -4 }}
      transition={{ duration: 0.18, ease: 'easeOut' }}
      style={{ height: '100%', cursor: onClick ? 'pointer' : 'default' }}
      onClick={onClick}
    >
      <Card
        sx={{
          height: '100%',
          p: 2.25,
          position: 'relative',
          overflow: 'hidden',
          transition: 'box-shadow 200ms ease, border-color 200ms ease',
          '&:hover': {
            boxShadow: glowColor,
            borderColor: alpha(glowColor === 'none' ? theme.palette.divider : theme.palette.primary.main, 0.4),
          },
        }}
      >
        <Box
          sx={{
            position: 'absolute',
            top: -30,
            right: -30,
            width: 120,
            height: 120,
            borderRadius: '50%',
            background: gradient,
            opacity: isDark ? 0.18 : 0.12,
            filter: 'blur(2px)',
          }}
        />
        <Stack direction="row" alignItems="flex-start" justifyContent="space-between" spacing={1} sx={{ position: 'relative' }}>
          <Stack spacing={0.5}>
            <Typography variant="overline" sx={{ color: 'text.secondary', letterSpacing: 0.6, fontWeight: 700 }}>
              {label}
            </Typography>
            {loading ? (
              <Box sx={{ width: 64, height: 34, borderRadius: 1, bgcolor: alpha(theme.palette.text.primary, 0.08) }} />
            ) : (
              <AnimatedCounter
                value={value}
                variant="h4"
                sx={{ fontWeight: 800, fontVariantNumeric: 'tabular-nums', lineHeight: 1.1 }}
              />
            )}
            {trend ? (
              <Stack direction="row" alignItems="center" spacing={0.5} sx={{ mt: 0.25 }}>
                <TrendIcon sx={{ fontSize: 16, color: trendColor }} />
                <Typography variant="caption" sx={{ color: trendColor, fontWeight: 700 }}>
                  {trend.delta > 0 ? '+' : ''}
                  {trend.delta}
                  {trend.label ? ` ${trend.label}` : ''}
                </Typography>
              </Stack>
            ) : null}
          </Stack>
          <Box
            sx={{
              width: 46,
              height: 46,
              borderRadius: '14px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: gradient,
              boxShadow: isDark ? glowColor : 'none',
              flexShrink: 0,
            }}
          >
            <Icon sx={{ color: '#fff', fontSize: 24 }} />
          </Box>
        </Stack>
      </Card>
    </motion.div>
  );
}
