import { Suspense, lazy, useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Avatar,
  Box,
  Button,
  FormControl,
  Grid,
  InputLabel,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  MenuItem,
  Paper,
  Select,
  Stack,
  TextField,
  Typography,
  type SelectChangeEvent
} from '@mui/material';
import {
  Cancel,
  CheckCircle,
  Engineering,
  EditNote,
  GridOn,
  HourglassTop,
  LocalShipping,
  NoteAdd,
  PictureAsPdf,
  PrecisionManufacturing,
  Send,
  SupervisorAccount,
  TableRows,
  Today,
  Verified
} from '@mui/icons-material';
import { apiService } from '../services/apiService';
import { useAuth } from '../contexts/AuthContext';
import { downloadBlob } from '../utils/downloadBlob';
import { formatIST } from '../utils/formatDate';
import { gradients, glow } from '../theme/palette';
import StatCard from '../components/common/StatCard';
import EmptyState from '../components/common/EmptyState';
import ErrorState from '../components/common/ErrorState';
import type {
  ChecksheetAnalyticsSummary,
  EquipmentItem,
  LocomotiveItem,
  RecentActivityItem,
  SectionItem,
  UserListItem
} from '../types';

const DashboardCharts = lazy(() => import('../components/DashboardCharts'));

interface Filters {
  dateFrom: string;
  dateTo: string;
  sectionId: number | '';
  equipmentId: number | '';
  technology: string;
  locomotiveType: string;
  supervisorId: number | '';
}

const EMPTY_FILTERS: Filters = {
  dateFrom: '',
  dateTo: '',
  sectionId: '',
  equipmentId: '',
  technology: '',
  locomotiveType: '',
  supervisorId: ''
};

function buildSummaryRows(summary: ChecksheetAnalyticsSummary) {
  return [
    ['Total Locomotives', summary.total_locomotives],
    ['Total Equipment', summary.total_equipment],
    ['Total Technicians', summary.total_technicians],
    ['Total Supervisors', summary.total_supervisors],
    ["Today's Submitted Checksheets", summary.today_submitted],
    ['Pending Reviews', summary.pending_review],
    ['Digitally Signed', summary.signed],
    ['Rejected', summary.rejected],
    ['Needs Correction', summary.needs_correction]
  ] as const;
}

function eventLabel(item: RecentActivityItem): string {
  const actor = item.actor_name ? `${item.actor_name}${item.actor_role ? ` (${item.actor_role})` : ''}` : 'Someone';
  switch (item.event) {
    case 'SUBMITTED':
      return `${actor} submitted checksheet #${item.checksheet_id}`;
    case 'APPROVED':
      return `${actor} digitally signed checksheet #${item.checksheet_id}`;
    case 'REJECTED':
      return `${actor} rejected checksheet #${item.checksheet_id}`;
    default:
      return `Checksheet #${item.checksheet_id} was created`;
  }
}

function eventIcon(event: RecentActivityItem['event']) {
  switch (event) {
    case 'SUBMITTED':
      return <Send fontSize="small" />;
    case 'APPROVED':
      return <CheckCircle fontSize="small" />;
    case 'REJECTED':
      return <Cancel fontSize="small" />;
    default:
      return <NoteAdd fontSize="small" />;
  }
}

export default function DashboardPage() {
  const { user } = useAuth();
  // The backend enforces this unconditionally regardless of what section_id is sent (Module
  // 27.5) - hidden rather than merely disabled, since it would otherwise silently have no effect.
  const isSupervisor = user?.role === 'Supervisor';

  const [summary, setSummary] = useState<ChecksheetAnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [exporting, setExporting] = useState<'pdf' | 'excel' | 'csv' | null>(null);
  const [exportError, setExportError] = useState<string | null>(null);

  const [sections, setSections] = useState<SectionItem[]>([]);
  const [equipment, setEquipment] = useState<EquipmentItem[]>([]);
  const [locomotives, setLocomotives] = useState<LocomotiveItem[]>([]);
  const [supervisors, setSupervisors] = useState<UserListItem[]>([]);

  const [filters, setFilters] = useState<Filters>(EMPTY_FILTERS);
  const [appliedFilters, setAppliedFilters] = useState<Filters>(EMPTY_FILTERS);

  useEffect(() => {
    let mounted = true;
    Promise.all([
      apiService.getSections(),
      apiService.getEquipment(),
      apiService.getLocomotives(),
      apiService.getUsers({ skip: 0, limit: 1000, role: 'Supervisor' })
    ])
      .then(([sectionsRes, equipmentRes, locomotivesRes, supervisorsRes]) => {
        if (!mounted) return;
        setSections(sectionsRes.data || []);
        setEquipment(equipmentRes.data || []);
        setLocomotives(locomotivesRes.data || []);
        setSupervisors(supervisorsRes.data.items || []);
      })
      .catch(() => {
        // Filter dropdown lookups are a convenience only - failing here must not block the
        // main analytics summary, which loads independently below.
      });
    return () => {
      mounted = false;
    };
  }, []);

  const technologyOptions = useMemo(
    () => Array.from(new Set(locomotives.map((l) => l.technology).filter((v): v is string => !!v))).sort(),
    [locomotives]
  );
  const locomotiveTypeOptions = useMemo(
    () => Array.from(new Set(locomotives.map((l) => l.loco_model).filter((v): v is string => !!v))).sort(),
    [locomotives]
  );

  const buildParams = (source: Filters) => {
    const params: Record<string, unknown> = {};
    if (source.dateFrom) params.date_from = source.dateFrom;
    if (source.dateTo) params.date_to = source.dateTo;
    if (source.sectionId) params.section_id = source.sectionId;
    if (source.equipmentId) params.equipment_id = source.equipmentId;
    if (source.technology) params.technology = source.technology;
    if (source.locomotiveType) params.locomotive_type = source.locomotiveType;
    if (source.supervisorId) params.supervisor_id = source.supervisorId;
    return params;
  };

  const loadSummary = async (source: Filters) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiService.getChecksheetAnalytics(buildParams(source));
      setSummary(response.data);
    } catch {
      setError('Unable to load dashboard analytics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSummary(EMPTY_FILTERS);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const applyFilters = () => {
    setAppliedFilters(filters);
    loadSummary(filters);
  };

  const resetFilters = () => {
    setFilters(EMPTY_FILTERS);
    setAppliedFilters(EMPTY_FILTERS);
    loadSummary(EMPTY_FILTERS);
  };

  // Module 33: the 7 primary KPI cards named by the redesign spec, each backed by an existing
  // analytics field (no backend/business-logic changes) - "Active Technicians"/"Active
  // Supervisors" reuse the pre-existing total_technicians/total_supervisors counts, since the
  // analytics endpoint has never filtered those by is_active or login state.
  const primaryCards = summary
    ? [
        { label: 'Pending', value: summary.pending_review, icon: HourglassTop, gradient: gradients.warning, glowColor: glow.warning },
        { label: 'Submitted', value: summary.status_distribution.SUBMITTED, icon: Send, gradient: gradients.primary, glowColor: glow.primary },
        { label: 'Approved', value: summary.signed, icon: Verified, gradient: gradients.success, glowColor: glow.success },
        { label: 'Rejected', value: summary.rejected, icon: Cancel, gradient: gradients.error, glowColor: glow.error },
        { label: "Today's Checksheets", value: summary.today_submitted, icon: Today, gradient: gradients.purple, glowColor: glow.purple },
        { label: 'Active Technicians', value: summary.total_technicians, icon: Engineering, gradient: gradients.primary, glowColor: glow.cyan },
        { label: 'Active Supervisors', value: summary.total_supervisors, icon: SupervisorAccount, gradient: gradients.purple, glowColor: glow.purple }
      ]
    : [];

  // Secondary metrics retained from the original 9-card set that aren't part of the module's
  // named 7 - shown as a smaller supplementary row so no existing data disappears from the page.
  const secondaryCards = summary
    ? [
        { label: 'Total Locomotives', value: summary.total_locomotives, icon: LocalShipping, gradient: gradients.navy, glowColor: glow.primary },
        { label: 'Total Equipment', value: summary.total_equipment, icon: PrecisionManufacturing, gradient: gradients.navy, glowColor: glow.cyan },
        { label: 'Needs Correction', value: summary.needs_correction, icon: EditNote, gradient: gradients.warning, glowColor: glow.warning }
      ]
    : [];

  const exportCsv = () => {
    if (!summary) return;
    setExportError(null);
    const lines: string[] = ['Dashboard Analytics Summary', `Generated,${new Date().toISOString()}`, ''];
    lines.push('Metric,Value');
    buildSummaryRows(summary).forEach(([label, value]) => lines.push(`"${label}",${value}`));
    lines.push('', 'Daily Trend (last 30 days)', 'Date,Count');
    summary.daily_trend.forEach((point) => lines.push(`${point.date},${point.count}`));
    lines.push('', 'By Section', 'Section,Count');
    summary.by_section.forEach((row) => lines.push(`"${(row.section_name ?? 'Unknown').replace(/"/g, '""')}",${row.count}`));
    lines.push('', 'By Equipment', 'Equipment,Count');
    summary.by_equipment.forEach((row) => lines.push(`"${(row.equipment_name ?? 'Unknown').replace(/"/g, '""')}",${row.count}`));
    lines.push(
      '',
      'Status Distribution',
      'Status,Count',
      `Submitted,${summary.status_distribution.SUBMITTED}`,
      `Under Review,${summary.status_distribution.UNDER_REVIEW}`,
      `Signed,${summary.status_distribution.APPROVED}`,
      `Rejected,${summary.status_distribution.REJECTED}`,
      `Needs Correction,${summary.needs_correction}`
    );

    const blob = new Blob([lines.join('\n')], { type: 'text/csv' });
    downloadBlob(blob, `dashboard_analytics_${Date.now()}.csv`);
  };

  const exportExcel = async () => {
    if (!summary) return;
    setExporting('excel');
    setExportError(null);
    try {
      const XLSX = await import('xlsx');
      const workbook = XLSX.utils.book_new();

      const summarySheet = XLSX.utils.json_to_sheet(
        buildSummaryRows(summary).map(([Metric, Value]) => ({ Metric, Value }))
      );
      XLSX.utils.book_append_sheet(workbook, summarySheet, 'Summary');

      const trendSheet = XLSX.utils.json_to_sheet(summary.daily_trend.map((p) => ({ Date: p.date, Count: p.count })));
      XLSX.utils.book_append_sheet(workbook, trendSheet, 'Daily Trend');

      const sectionSheet = XLSX.utils.json_to_sheet(
        summary.by_section.map((row) => ({ Section: row.section_name ?? 'Unknown', Count: row.count }))
      );
      XLSX.utils.book_append_sheet(workbook, sectionSheet, 'By Section');

      const equipmentSheet = XLSX.utils.json_to_sheet(
        summary.by_equipment.map((row) => ({ Equipment: row.equipment_name ?? 'Unknown', Count: row.count }))
      );
      XLSX.utils.book_append_sheet(workbook, equipmentSheet, 'By Equipment');

      const statusSheet = XLSX.utils.json_to_sheet([
        { Status: 'Submitted', Count: summary.status_distribution.SUBMITTED },
        { Status: 'Under Review', Count: summary.status_distribution.UNDER_REVIEW },
        { Status: 'Signed', Count: summary.status_distribution.APPROVED },
        { Status: 'Rejected', Count: summary.status_distribution.REJECTED },
        { Status: 'Needs Correction', Count: summary.needs_correction }
      ]);
      XLSX.utils.book_append_sheet(workbook, statusSheet, 'Status Distribution');

      XLSX.writeFile(workbook, `dashboard_analytics_${Date.now()}.xlsx`);
    } catch {
      setExportError('Unable to export Excel workbook.');
    } finally {
      setExporting(null);
    }
  };

  const exportPdf = async () => {
    setExporting('pdf');
    setExportError(null);
    try {
      const response = await apiService.exportReportPdf(buildParams(appliedFilters));
      downloadBlob(new Blob([response.data], { type: 'application/pdf' }), 'checksheets_report.pdf');
    } catch {
      setExportError('Unable to export PDF report.');
    } finally {
      setExporting(null);
    }
  };

  return (
    <Box>
      <Stack spacing={2.5}>
        <Paper sx={{ p: 3, borderRadius: 3 }}>
          <Typography variant="h4" fontWeight={700} mb={1}>Dashboard Analytics</Typography>
          <Typography variant="body1" color="text.secondary">Workshop activity at a glance.</Typography>
        </Paper>

        <Paper sx={{ p: 2.5 }}>
          <Stack spacing={2}>
            <Typography variant="subtitle1" fontWeight={700}>Filters</Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  label="From"
                  type="date"
                  fullWidth
                  InputLabelProps={{ shrink: true }}
                  value={filters.dateFrom}
                  onChange={(e) => setFilters((prev) => ({ ...prev, dateFrom: e.target.value }))}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  label="To"
                  type="date"
                  fullWidth
                  InputLabelProps={{ shrink: true }}
                  value={filters.dateTo}
                  onChange={(e) => setFilters((prev) => ({ ...prev, dateTo: e.target.value }))}
                />
              </Grid>
              {isSupervisor ? null : (
                <Grid item xs={12} sm={6} md={3}>
                  <FormControl fullWidth>
                    <InputLabel>Section</InputLabel>
                    <Select
                      label="Section"
                      value={filters.sectionId}
                      onChange={(e: SelectChangeEvent<number | ''>) => setFilters((prev) => ({ ...prev, sectionId: e.target.value as number | '' }))}
                    >
                      <MenuItem value="">All</MenuItem>
                      {sections.map((s) => <MenuItem key={s.id} value={s.id}>{s.name}</MenuItem>)}
                    </Select>
                  </FormControl>
                </Grid>
              )}
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Equipment</InputLabel>
                  <Select
                    label="Equipment"
                    value={filters.equipmentId}
                    onChange={(e: SelectChangeEvent<number | ''>) => setFilters((prev) => ({ ...prev, equipmentId: e.target.value as number | '' }))}
                  >
                    <MenuItem value="">All</MenuItem>
                    {equipment.map((eq) => <MenuItem key={eq.id} value={eq.id}>{eq.equipment_name}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Technology</InputLabel>
                  <Select
                    label="Technology"
                    value={filters.technology}
                    onChange={(e: SelectChangeEvent<string>) => setFilters((prev) => ({ ...prev, technology: e.target.value }))}
                  >
                    <MenuItem value="">All</MenuItem>
                    {technologyOptions.map((t) => <MenuItem key={t} value={t}>{t}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Locomotive Type</InputLabel>
                  <Select
                    label="Locomotive Type"
                    value={filters.locomotiveType}
                    onChange={(e: SelectChangeEvent<string>) => setFilters((prev) => ({ ...prev, locomotiveType: e.target.value }))}
                  >
                    <MenuItem value="">All</MenuItem>
                    {locomotiveTypeOptions.map((t) => <MenuItem key={t} value={t}>{t}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Supervisor</InputLabel>
                  <Select
                    label="Supervisor"
                    value={filters.supervisorId}
                    onChange={(e: SelectChangeEvent<number | ''>) => setFilters((prev) => ({ ...prev, supervisorId: e.target.value as number | '' }))}
                  >
                    <MenuItem value="">All</MenuItem>
                    {supervisors.map((s) => <MenuItem key={s.id} value={s.id}>{s.name}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>

            <Stack direction="row" spacing={1.5} flexWrap="wrap" useFlexGap alignItems="center">
              <Button variant="contained" onClick={applyFilters} disabled={loading}>Apply Filters</Button>
              <Button variant="text" onClick={resetFilters} disabled={loading}>Reset</Button>
              <Box sx={{ flexGrow: 1 }} />
              <Button
                variant="outlined"
                startIcon={<PictureAsPdf />}
                onClick={exportPdf}
                disabled={!summary || exporting !== null}
              >
                {exporting === 'pdf' ? 'Exporting...' : 'Export PDF'}
              </Button>
              <Button
                variant="outlined"
                startIcon={<GridOn />}
                onClick={exportExcel}
                disabled={!summary || exporting !== null}
              >
                {exporting === 'excel' ? 'Exporting...' : 'Export Excel'}
              </Button>
              <Button
                variant="outlined"
                startIcon={<TableRows />}
                onClick={exportCsv}
                disabled={!summary || exporting !== null}
              >
                Export CSV
              </Button>
            </Stack>
            {exportError ? <Alert severity="error" onClose={() => setExportError(null)}>{exportError}</Alert> : null}
          </Stack>
        </Paper>

        {error ? (
          <Paper sx={{ p: 0 }}>
            <ErrorState message={error} onRetry={() => loadSummary(appliedFilters)} />
          </Paper>
        ) : null}

        {loading && !summary ? (
          <Grid container spacing={2.5}>
            {Array.from({ length: 7 }).map((_, i) => (
              <Grid item xs={12} sm={6} md={3} key={i}>
                <StatCard label="" value={0} icon={HourglassTop} gradient={gradients.navy} glowColor="none" loading />
              </Grid>
            ))}
          </Grid>
        ) : null}

        {summary ? (
          <>
            <Grid container spacing={2.5}>
              {primaryCards.map((card) => (
                <Grid item xs={12} sm={6} md={3} key={card.label}>
                  <StatCard label={card.label} value={card.value} icon={card.icon} gradient={card.gradient} glowColor={card.glowColor} />
                </Grid>
              ))}
            </Grid>

            <Grid container spacing={2.5}>
              {secondaryCards.map((card) => (
                <Grid item xs={12} sm={6} md={4} key={card.label}>
                  <StatCard label={card.label} value={card.value} icon={card.icon} gradient={card.gradient} glowColor={card.glowColor} />
                </Grid>
              ))}
            </Grid>

            <Suspense fallback={
              <Grid container spacing={2.5}>
                {Array.from({ length: 2 }).map((_, i) => (
                  <Grid item xs={12} md={6} key={i}>
                    <Paper sx={{ p: 3, height: 320 }} />
                  </Grid>
                ))}
              </Grid>
            }>
              <DashboardCharts summary={summary} />
            </Suspense>

            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight={700} mb={2}>Recent Activity</Typography>
              {summary.recent_activity.length === 0 ? (
                <EmptyState title="No recent activity" message="Nothing matches this filter yet - activity will appear here as checksheets are submitted, signed, or rejected." icon={NoteAdd} />
              ) : (
                <List>
                  {summary.recent_activity.map((item) => (
                    <ListItem key={`${item.checksheet_id}-${item.event}-${item.at}`} divider>
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: 'primary.main' }}>{eventIcon(item.event)}</Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={eventLabel(item)}
                        secondary={`${[item.locomotive_number, item.equipment_name, item.section_name].filter(Boolean).join(' · ')} — ${formatIST(item.at)}`}
                      />
                    </ListItem>
                  ))}
                </List>
              )}
            </Paper>
          </>
        ) : null}
      </Stack>
    </Box>
  );
}
