import { Box, Paper, Typography, useTheme } from '@mui/material';
import { motion } from 'framer-motion';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from 'recharts';
import type { ChecksheetAnalyticsSummary } from '../types';
import { cyberColors } from '../theme/palette';
import { statusTones } from '../theme/palette';

// Module 33: Pie slice colors now come from the single shared status-color system (statusTones in
// theme/palette.ts) instead of this component's own hardcoded hex map, so "Submitted" here always
// matches the exact shade used by StatusChip/StatCard elsewhere. "Needs Correction" isn't a real
// backend ChecksheetStatus value, so it keeps its own neutral-ish tone rather than borrowing one.
const STATUS_SLICE_COLORS: Record<string, string> = {
  Submitted: statusTones.submitted.color,
  Review: statusTones.underReview.color,
  Signed: statusTones.approved.color,
  Rejected: statusTones.rejected.color,
  'Needs Correction': cyberColors.amber
};

function ChartPanel({
  title,
  height = 260,
  isEmpty = false,
  children
}: {
  title: string;
  height?: number;
  isEmpty?: boolean;
  children: React.ReactElement;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.2 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      style={{ height: '100%' }}
    >
      <Paper sx={{ p: 2, height: '100%' }}>
        <Typography variant="subtitle1" fontWeight={700} mb={1}>{title}</Typography>
        <Box sx={{ height }}>
          {isEmpty ? (
            <EmptyChartMessage />
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              {children}
            </ResponsiveContainer>
          )}
        </Box>
      </Paper>
    </motion.div>
  );
}

/** Lazy-loaded (see DashboardPage) so recharts and this chart-rendering code is split into its own
 * chunk, only fetched once the Dashboard Analytics page actually mounts. */
export default function DashboardCharts({ summary }: { summary: ChecksheetAnalyticsSummary }) {
  const theme = useTheme();
  const gridColor = theme.palette.divider;
  const tickColor = theme.palette.text.secondary;

  const dailyTrend = summary.daily_trend.map((point) => ({
    date: point.date.slice(5),
    count: point.count
  }));

  const bySection = summary.by_section.map((row) => ({
    name: row.section_name ?? `Section ${row.section_id ?? '-'}`,
    count: row.count
  }));

  const byEquipment = summary.by_equipment.map((row) => ({
    name: row.equipment_name ?? `Equipment ${row.equipment_id ?? '-'}`,
    count: row.count
  }));

  const statusDistribution = [
    { name: 'Submitted', value: summary.status_distribution.SUBMITTED },
    { name: 'Review', value: summary.status_distribution.UNDER_REVIEW },
    { name: 'Signed', value: summary.status_distribution.APPROVED },
    { name: 'Rejected', value: summary.status_distribution.REJECTED },
    { name: 'Needs Correction', value: summary.needs_correction }
  ];

  const tooltipStyle = {
    backgroundColor: theme.palette.background.paper,
    border: `1px solid ${theme.palette.divider}`,
    borderRadius: 8,
    color: theme.palette.text.primary
  };

  return (
    <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
      <ChartPanel title="Checksheets Submitted per Day (last 30 days)">
        <LineChart data={dailyTrend}>
          <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
          <XAxis dataKey="date" interval={2} stroke={tickColor} tick={{ fill: tickColor, fontSize: 12 }} />
          <YAxis allowDecimals={false} stroke={tickColor} tick={{ fill: tickColor, fontSize: 12 }} />
          <Tooltip contentStyle={tooltipStyle} />
          <Line type="monotone" dataKey="count" stroke={cyberColors.electricBlue} strokeWidth={2.5} dot={false} activeDot={{ r: 5, fill: cyberColors.cyan }} />
        </LineChart>
      </ChartPanel>

      <ChartPanel title="Status Distribution">
        <PieChart>
          <Pie data={statusDistribution} dataKey="value" nameKey="name" outerRadius={90} label>
            {statusDistribution.map((entry) => (
              <Cell key={entry.name} fill={STATUS_SLICE_COLORS[entry.name] ?? cyberColors.purple} />
            ))}
          </Pie>
          <Tooltip contentStyle={tooltipStyle} />
          <Legend wrapperStyle={{ color: tickColor, fontSize: 12 }} />
        </PieChart>
      </ChartPanel>

      <ChartPanel title="Checksheets by Section" isEmpty={bySection.length === 0}>
        <BarChart data={bySection}>
          <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
          <XAxis dataKey="name" stroke={tickColor} tick={{ fill: tickColor, fontSize: 12 }} />
          <YAxis allowDecimals={false} stroke={tickColor} tick={{ fill: tickColor, fontSize: 12 }} />
          <Tooltip contentStyle={tooltipStyle} />
          <Bar dataKey="count" fill={cyberColors.electricBlue} radius={[4, 4, 0, 0]} />
        </BarChart>
      </ChartPanel>

      <ChartPanel title="Checksheets by Equipment" isEmpty={byEquipment.length === 0}>
        <BarChart data={byEquipment}>
          <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
          <XAxis dataKey="name" stroke={tickColor} tick={{ fill: tickColor, fontSize: 12 }} />
          <YAxis allowDecimals={false} stroke={tickColor} tick={{ fill: tickColor, fontSize: 12 }} />
          <Tooltip contentStyle={tooltipStyle} />
          <Bar dataKey="count" fill={cyberColors.neonGreen} radius={[4, 4, 0, 0]} />
        </BarChart>
      </ChartPanel>
    </Box>
  );
}

function EmptyChartMessage() {
  return (
    <Box sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <Typography color="text.secondary">No matching checksheets for this filter.</Typography>
    </Box>
  );
}
