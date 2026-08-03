import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  Grid,
  IconButton,
  InputAdornment,
  LinearProgress,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Tooltip,
  Typography
} from '@mui/material';
import {
  CheckCircle,
  CloudQueue,
  Dns,
  Download,
  Error as ErrorIcon,
  Notifications,
  Refresh,
  Search,
  SortByAlpha,
  Storage,
  Visibility
} from '@mui/icons-material';
import { apiService } from '../services/apiService';
import { checkEmBridgeStatus } from '../services/embridgeClient';
import { downloadBlob } from '../utils/downloadBlob';
import { formatIST } from '../utils/formatDate';
import { parseLogLine, type LogSeverity } from '../utils/logLineParser';
import type { ActiveUserItem, LogFileInfo, LogTailResponse, ServiceStatusItem, SystemHealthOverview } from '../types';
import packageJson from '../../package.json';

const SEVERITY_COLORS: Record<LogSeverity, 'default' | 'info' | 'warning' | 'error'> = {
  DEBUG: 'default',
  INFO: 'info',
  WARNING: 'warning',
  ERROR: 'error',
  CRITICAL: 'error'
};

const SEVERITY_OPTIONS: LogSeverity[] = ['INFO', 'WARNING', 'ERROR', 'CRITICAL', 'DEBUG'];

const AUTO_REFRESH_MS = 30000;
const DASHBOARD_VERSION = packageJson.version;

const SERVICE_ICONS: Record<string, JSX.Element> = {
  'Backend API': <Dns />,
  'PostgreSQL Database': <Storage />,
  'Android API Connectivity': <CloudQueue />,
  'Notification Service': <Notifications />
};

function usageColor(percent: number): 'success' | 'warning' | 'error' {
  if (percent >= 85) return 'error';
  if (percent >= 65) return 'warning';
  return 'success';
}

function StatusCard({ item }: { item: ServiceStatusItem }) {
  const online = item.status === 'Online';
  return (
    <Card>
      <CardContent>
        <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
          <Box>
            <Stack direction="row" spacing={1} alignItems="center">
              {SERVICE_ICONS[item.name] ?? <Dns />}
              <Typography variant="subtitle1" fontWeight={700}>{item.name}</Typography>
            </Stack>
            <Box mt={1.5}>
              <Chip
                size="small"
                icon={online ? <CheckCircle /> : <ErrorIcon />}
                label={item.status}
                color={online ? 'success' : 'error'}
              />
            </Box>
            <Typography variant="body2" color="text.secondary" mt={1}>
              Response Time: {item.response_time_ms.toFixed(1)} ms
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Last Checked: {formatIST(item.last_checked)}
            </Typography>
            {item.detail ? (
              <Typography variant="caption" color="error.main" display="block" mt={0.5}>
                {item.detail}
              </Typography>
            ) : null}
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
}

function UsageRow({ label, percent, detail }: { label: string; percent: number; detail: string }) {
  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" mb={0.5}>
        <Typography variant="body2" fontWeight={600}>{label}</Typography>
        <Typography variant="body2" color="text.secondary">{detail}</Typography>
      </Stack>
      <LinearProgress
        variant="determinate"
        value={Math.min(100, percent)}
        color={usageColor(percent)}
        sx={{ height: 8, borderRadius: 4 }}
      />
    </Box>
  );
}

function InfoRow({ label, value }: { label: string; value?: string | number | null }) {
  return (
    <Stack direction="row" justifyContent="space-between">
      <Typography variant="body2" color="text.secondary">{label}</Typography>
      <Typography variant="body2" fontWeight={600}>{value ?? 'Not available'}</Typography>
    </Stack>
  );
}

const DB_STAT_LABELS: Array<[string, keyof SystemHealthOverview['database_stats']]> = [
  ['Number of Users', 'total_users'],
  ['Number of Technicians', 'total_technicians'],
  ['Number of Supervisors', 'total_supervisors'],
  ['Total Locomotives', 'total_locomotives'],
  ['Total Equipment', 'total_equipment'],
  ['Total Checksheets', 'total_checksheets'],
  ['Pending Reviews', 'pending_reviews'],
  ['Approved', 'approved'],
  ['Rejected', 'rejected']
];

function ActiveUsersTable({ users }: { users: ActiveUserItem[] }) {
  if (users.length === 0) {
    return <Typography color="text.secondary">No users are currently active.</Typography>;
  }
  return (
    <TableContainer>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Employee ID</TableCell>
            <TableCell>Name</TableCell>
            <TableCell>Role</TableCell>
            <TableCell>Login Time</TableCell>
            <TableCell>Last Activity</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {users.map((u) => (
            <TableRow key={`${u.employee_id}-${u.login_time}`} hover>
              <TableCell>{u.employee_id}</TableCell>
              <TableCell>{u.name}</TableCell>
              <TableCell>{u.role}</TableCell>
              <TableCell>{formatIST(u.login_time)}</TableCell>
              <TableCell>{formatIST(u.last_activity)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

interface ParsedSecurityEvent {
  raw: string;
  timestamp?: string;
  action?: string;
  message?: string;
  success?: boolean;
}

function parseSecurityLogLine(line: string): ParsedSecurityEvent {
  try {
    const parsed = JSON.parse(line);
    return {
      raw: line,
      timestamp: parsed.timestamp,
      action: parsed.action,
      message: parsed.message,
      success: parsed.success,
    };
  } catch {
    return { raw: line };
  }
}

function SecurityEventsCard() {
  const [events, setEvents] = useState<ParsedSecurityEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const res = await apiService.getLogTail('security', 15);
      setEvents(res.data.lines.map(parseSecurityLogLine).reverse());
      setError(null);
    } catch {
      setError('Unable to load recent security events.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const interval = setInterval(load, AUTO_REFRESH_MS);
    return () => clearInterval(interval);
  }, [load]);

  return (
    <Card sx={{ height: '100%' }}>
      <CardHeader title="Recent Security Events" />
      <Divider />
      <CardContent>
        {loading ? (
          <CircularProgress size={20} />
        ) : error ? (
          <Alert severity="error">{error}</Alert>
        ) : events.length === 0 ? (
          <Typography color="text.secondary">No recent security events.</Typography>
        ) : (
          <Stack spacing={1} sx={{ maxHeight: 320, overflowY: 'auto' }}>
            {events.map((event, idx) => (
              <Stack key={idx} direction="row" justifyContent="space-between" spacing={1} alignItems="flex-start">
                <Box sx={{ minWidth: 0 }}>
                  <Typography variant="body2" fontWeight={600} noWrap>{event.action ?? 'Unknown'}</Typography>
                  <Typography variant="caption" color="text.secondary" noWrap>{event.message}</Typography>
                </Box>
                <Chip
                  size="small"
                  label={event.success === false ? 'Failed' : 'Info'}
                  color={event.success === false ? 'error' : 'default'}
                />
              </Stack>
            ))}
          </Stack>
        )}
      </CardContent>
    </Card>
  );
}

function EmBridgeStatusTile() {
  const [status, setStatus] = useState<{ available: boolean; version: string | null } | null>(null);

  useEffect(() => {
    let mounted = true;
    checkEmBridgeStatus().then((result) => {
      if (mounted) setStatus(result);
    });
    const interval = setInterval(() => {
      checkEmBridgeStatus().then((result) => {
        if (mounted) setStatus(result);
      });
    }, AUTO_REFRESH_MS);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  const online = status?.available ?? false;

  return (
    <Card>
      <CardContent>
        <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
          <Box>
            <Typography variant="subtitle1" fontWeight={700}>emBridge Status</Typography>
            <Typography variant="body2" color="text.secondary">
              {status === null ? 'Checking…' : status.version ? `Version ${status.version}` : 'Checked from this browser only'}
            </Typography>
          </Box>
          <Chip
            size="small"
            label={status === null ? 'Checking' : online ? 'Online' : 'Offline'}
            color={status === null ? 'default' : online ? 'success' : 'error'}
          />
        </Stack>
      </CardContent>
    </Card>
  );
}

function LogFilesSection() {
  const [logs, setLogs] = useState<LogFileInfo[]>([]);
  const [logsError, setLogsError] = useState<string | null>(null);
  const [viewing, setViewing] = useState<LogTailResponse | null>(null);
  const [viewLoading, setViewLoading] = useState<string | null>(null);
  const [downloading, setDownloading] = useState<string | null>(null);

  const [search, setSearch] = useState('');
  const [severityFilter, setSeverityFilter] = useState<LogSeverity | 'ALL'>('ALL');
  const [newestFirst, setNewestFirst] = useState(false);

  const loadLogs = useCallback(() => {
    setLogsError(null);
    apiService
      .getLogFiles()
      .then((res) => setLogs(res.data))
      .catch(() => setLogsError('Unable to load log file list.'));
  }, []);

  useEffect(() => {
    loadLogs();
    // Module 33.1: keeps the log file list (size/last modified) fresh alongside the rest of the
    // page's existing 30s auto-refresh, rather than only ever loading once on mount.
    const interval = setInterval(loadLogs, AUTO_REFRESH_MS);
    return () => clearInterval(interval);
  }, [loadLogs]);

  const viewLog = async (key: string) => {
    setViewLoading(key);
    setSearch('');
    setSeverityFilter('ALL');
    setNewestFirst(false);
    try {
      const res = await apiService.getLogTail(key, 200);
      setViewing(res.data);
    } catch {
      setLogsError('Unable to load log entries.');
    } finally {
      setViewLoading(null);
    }
  };

  const parsedLines = useMemo(() => (viewing?.lines ?? []).map(parseLogLine), [viewing]);

  const visibleLines = useMemo(() => {
    const term = search.trim().toLowerCase();
    let result = parsedLines.filter((line) => {
      if (severityFilter !== 'ALL' && line.severity !== severityFilter) return false;
      if (term && !line.raw.toLowerCase().includes(term)) return false;
      return true;
    });
    if (newestFirst) result = [...result].reverse();
    return result;
  }, [parsedLines, search, severityFilter, newestFirst]);

  const downloadLog = async (item: LogFileInfo) => {
    setDownloading(item.key);
    try {
      const res = await apiService.downloadLogFile(item.key);
      downloadBlob(new Blob([res.data], { type: 'text/plain' }), `${item.key}.log`);
    } catch {
      setLogsError('Unable to download log file.');
    } finally {
      setDownloading(null);
    }
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6" fontWeight={700}>Log Files</Typography>
        <IconButton size="small" onClick={loadLogs} aria-label="Refresh log file list">
          <Refresh fontSize="small" />
        </IconButton>
      </Stack>
      {logsError ? <Alert severity="error" sx={{ mb: 2 }} onClose={() => setLogsError(null)}>{logsError}</Alert> : null}
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Log</TableCell>
              <TableCell>Size</TableCell>
              <TableCell>Last Modified</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {logs.map((log) => (
              <TableRow key={log.key} hover>
                <TableCell>{log.label}</TableCell>
                <TableCell>{log.exists ? `${(log.size_bytes / 1024).toFixed(1)} KB` : '-'}</TableCell>
                <TableCell>{log.exists ? formatIST(log.last_modified) : '-'}</TableCell>
                <TableCell align="right">
                  <Tooltip title="View latest entries">
                    <span>
                      <IconButton
                        size="small"
                        disabled={!log.exists || viewLoading === log.key}
                        onClick={() => viewLog(log.key)}
                      >
                        {viewLoading === log.key ? <CircularProgress size={16} /> : <Visibility fontSize="small" />}
                      </IconButton>
                    </span>
                  </Tooltip>
                  <Tooltip title="Download full log">
                    <span>
                      <IconButton
                        size="small"
                        disabled={!log.exists || downloading === log.key}
                        onClick={() => downloadLog(log)}
                      >
                        {downloading === log.key ? <CircularProgress size={16} /> : <Download fontSize="small" />}
                      </IconButton>
                    </span>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={viewing !== null} onClose={() => setViewing(null)} maxWidth="md" fullWidth>
        <DialogTitle>{viewing?.label}</DialogTitle>
        <DialogContent dividers>
          <Stack spacing={1.5} mb={2}>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5} alignItems={{ xs: 'stretch', sm: 'center' }}>
              <TextField
                size="small"
                placeholder="Search log entries"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                sx={{ flexGrow: 1 }}
                InputProps={{ startAdornment: <InputAdornment position="start"><Search fontSize="small" /></InputAdornment> }}
              />
              <Tooltip title={newestFirst ? 'Showing newest first' : 'Showing oldest first'}>
                <ToggleButton
                  size="small"
                  value="newestFirst"
                  selected={newestFirst}
                  onChange={() => setNewestFirst((v) => !v)}
                >
                  <SortByAlpha fontSize="small" sx={{ mr: 0.75 }} />
                  Newest First
                </ToggleButton>
              </Tooltip>
            </Stack>
            <ToggleButtonGroup
              size="small"
              exclusive
              value={severityFilter}
              onChange={(_, value) => value && setSeverityFilter(value)}
            >
              <ToggleButton value="ALL">All</ToggleButton>
              {SEVERITY_OPTIONS.map((severity) => (
                <ToggleButton key={severity} value={severity}>{severity}</ToggleButton>
              ))}
            </ToggleButtonGroup>
          </Stack>

          <Box sx={{ maxHeight: '55vh', overflow: 'auto' }}>
            {visibleLines.length === 0 ? (
              <Typography color="text.secondary" sx={{ py: 2 }}>
                {viewing && viewing.lines.length > 0 ? 'No log entries match the current search/filter.' : 'No log entries available.'}
              </Typography>
            ) : (
              <Stack spacing={0.5}>
                {visibleLines.map((line, index) => (
                  <Stack
                    key={index}
                    direction="row"
                    spacing={1}
                    alignItems="flex-start"
                    sx={{
                      fontFamily: 'monospace',
                      fontSize: 12,
                      py: 0.5,
                      px: 0.75,
                      borderRadius: 1,
                      '&:hover': { bgcolor: 'action.hover' }
                    }}
                  >
                    {line.severity ? (
                      <Chip
                        size="small"
                        label={line.severity}
                        color={SEVERITY_COLORS[line.severity]}
                        sx={{ height: 20, fontSize: 10, fontWeight: 700, flexShrink: 0 }}
                      />
                    ) : null}
                    <Box component="span" sx={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
                      {line.timestamp ? <Box component="span" sx={{ color: 'text.secondary' }}>[{line.timestamp}] </Box> : null}
                      {line.severity ? line.message : line.raw}
                    </Box>
                  </Stack>
                ))}
              </Stack>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewing(null)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
}

export default function SystemHealthPage() {
  const [overview, setOverview] = useState<SystemHealthOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefreshed, setLastRefreshed] = useState<Date | null>(null);

  const loadOverview = useCallback(async () => {
    setError(null);
    try {
      const res = await apiService.getSystemHealthOverview();
      setOverview(res.data);
      setLastRefreshed(new Date());
    } catch {
      setError('Unable to load system health data. The backend may be unreachable.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadOverview();
    const interval = setInterval(loadOverview, AUTO_REFRESH_MS);
    return () => clearInterval(interval);
  }, [loadOverview]);

  const dbStatCards = useMemo(() => {
    if (!overview) return [];
    return DB_STAT_LABELS.map(([label, key]) => ({ label, value: overview.database_stats[key] }));
  }, [overview]);

  return (
    <Box>
      <Stack spacing={2.5}>
        <Paper sx={{ p: 3, borderRadius: 3 }}>
          <Stack direction="row" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={2}>
            <Box>
              <Typography variant="h4" fontWeight={700} mb={1}>System Health &amp; Monitoring</Typography>
              <Typography variant="body1" color="text.secondary">
                Live backend, database, and application status. Auto-refreshes every 30 seconds.
              </Typography>
            </Box>
            <Stack alignItems="flex-end" spacing={1}>
              <Button
                variant="contained"
                startIcon={loading ? <CircularProgress size={16} color="inherit" /> : <Refresh />}
                onClick={loadOverview}
                disabled={loading}
              >
                Refresh Now
              </Button>
              {lastRefreshed ? (
                <Typography variant="caption" color="text.secondary">
                  Last refreshed: {lastRefreshed.toLocaleTimeString()}
                </Typography>
              ) : null}
            </Stack>
          </Stack>
        </Paper>

        {error ? (
          <Alert severity="error" action={<Button color="inherit" size="small" onClick={loadOverview}>Retry</Button>}>
            {error}
          </Alert>
        ) : null}

        {loading && !overview ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
            <CircularProgress />
          </Box>
        ) : null}

        {overview ? (
          <>
            <Typography variant="h6" fontWeight={700}>System Status</Typography>
            <Grid container spacing={2.5}>
              {overview.service_status.map((item) => (
                <Grid item xs={12} sm={6} md={3} key={item.name}>
                  <StatusCard item={item} />
                </Grid>
              ))}
            </Grid>

            <Grid container spacing={2.5}>
              <Grid item xs={12} md={6}>
                <Card sx={{ height: '100%' }}>
                  <CardHeader title="Server Information" />
                  <Divider />
                  <CardContent>
                    <Stack spacing={2}>
                      <UsageRow
                        label="CPU Usage"
                        percent={overview.server_info.cpu_usage_percent}
                        detail={`${overview.server_info.cpu_usage_percent.toFixed(1)}%`}
                      />
                      <UsageRow
                        label="Memory Usage"
                        percent={overview.server_info.memory_usage_percent}
                        detail={`${overview.server_info.memory_used_gb} / ${overview.server_info.memory_total_gb} GB`}
                      />
                      <UsageRow
                        label="Disk Usage"
                        percent={overview.server_info.disk_usage_percent}
                        detail={`${overview.server_info.disk_used_gb} / ${overview.server_info.disk_total_gb} GB`}
                      />
                      <Divider />
                      <InfoRow label="System Uptime" value={overview.server_info.uptime} />
                      <InfoRow label="Python Version" value={overview.server_info.python_version} />
                      <InfoRow label="FastAPI Version" value={overview.server_info.fastapi_version} />
                      <InfoRow label="PostgreSQL Version" value={overview.server_info.postgresql_version} />
                      <InfoRow label="Operating System" value={overview.server_info.operating_system} />
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={6}>
                <Card sx={{ height: '100%' }}>
                  <CardHeader title="Application Information" />
                  <Divider />
                  <CardContent>
                    <Stack spacing={2}>
                      <InfoRow label="Backend Version" value={overview.application_info.backend_version} />
                      <InfoRow label="Dashboard Version" value={DASHBOARD_VERSION} />
                      <InfoRow label="Android Version (current release)" value={overview.application_info.android_version} />
                      <InfoRow
                        label="Build Date"
                        value={overview.application_info.build_date ? formatIST(overview.application_info.build_date) : null}
                      />
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            <Typography variant="h6" fontWeight={700}>Database</Typography>
            <Grid container spacing={2.5}>
              {dbStatCards.map((card) => (
                <Grid item xs={12} sm={6} md={4} key={card.label}>
                  <Card>
                    <CardContent>
                      <Typography variant="overline" color="text.secondary">{card.label}</Typography>
                      <Typography variant="h5" fontWeight={700}>{card.value}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>

            <Typography variant="h6" fontWeight={700}>Operational Metrics</Typography>
            <Grid container spacing={2.5}>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="overline" color="text.secondary">Daily Signature Count</Typography>
                    <Typography variant="h5" fontWeight={700}>{overview.daily_counts.signature_count}</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="overline" color="text.secondary">Daily Checksheet Submissions</Typography>
                    <Typography variant="h5" fontWeight={700}>{overview.daily_counts.checksheet_submission_count}</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="overline" color="text.secondary">Daily Approval Count</Typography>
                    <Typography variant="h5" fontWeight={700}>{overview.daily_counts.approval_count}</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="overline" color="text.secondary">DB Connections</Typography>
                    <Typography variant="h5" fontWeight={700}>
                      {overview.database_connection_info.checked_out} / {overview.database_connection_info.pool_size}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="overline" color="text.secondary">Avg API Response Time</Typography>
                    <Typography variant="h5" fontWeight={700}>
                      {overview.request_metrics.avg_response_time_ms != null ? `${overview.request_metrics.avg_response_time_ms} ms` : 'Not available'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="overline" color="text.secondary">Avg PDF Generation Time</Typography>
                    <Typography variant="h5" fontWeight={700}>
                      {overview.pdf_generation_stats.average_duration_ms != null ? `${overview.pdf_generation_stats.average_duration_ms} ms` : 'Not available'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="overline" color="text.secondary">Digital Signatures (24h)</Typography>
                    <Typography variant="h5" fontWeight={700}>
                      {overview.digital_signature_status.recent_success_count} ok / {overview.digital_signature_status.recent_failure_count} failed
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <EmBridgeStatusTile />
              </Grid>
            </Grid>

            <Grid container spacing={2.5}>
              <Grid item xs={12} md={6}>
                <Card sx={{ height: '100%' }}>
                  <CardHeader title="Slowest Endpoints" />
                  <Divider />
                  <CardContent>
                    {overview.request_metrics.slowest_endpoints.length === 0 ? (
                      <Typography color="text.secondary">No request data yet this session.</Typography>
                    ) : (
                      <TableContainer>
                        <Table size="small">
                          <TableHead>
                            <TableRow>
                              <TableCell>Endpoint</TableCell>
                              <TableCell align="right">Avg (ms)</TableCell>
                              <TableCell align="right">Count</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {overview.request_metrics.slowest_endpoints.map((e) => (
                              <TableRow key={e.endpoint}>
                                <TableCell>{e.endpoint}</TableCell>
                                <TableCell align="right">{e.avg_duration_ms}</TableCell>
                                <TableCell align="right">{e.count}</TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    )}
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={6}>
                <Card sx={{ height: '100%' }}>
                  <CardHeader title="Recent Failed Requests" />
                  <Divider />
                  <CardContent>
                    {overview.request_metrics.recent_failed_requests.length === 0 ? (
                      <Typography color="text.secondary">No failed requests this session.</Typography>
                    ) : (
                      <TableContainer>
                        <Table size="small">
                          <TableHead>
                            <TableRow>
                              <TableCell>Endpoint</TableCell>
                              <TableCell align="right">Status</TableCell>
                              <TableCell align="right">Time</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {overview.request_metrics.recent_failed_requests.map((r, idx) => (
                              <TableRow key={idx}>
                                <TableCell>{r.method} {r.endpoint}</TableCell>
                                <TableCell align="right">{r.status_code}</TableCell>
                                <TableCell align="right">{formatIST(r.timestamp)}</TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            <Grid container spacing={2.5}>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3, height: '100%' }}>
                  <Typography variant="h6" fontWeight={700} mb={2}>
                    Active Users ({overview.active_users.length})
                  </Typography>
                  <ActiveUsersTable users={overview.active_users} />
                </Paper>
              </Grid>
              <Grid item xs={12} md={6}>
                <SecurityEventsCard />
              </Grid>
            </Grid>

            <LogFilesSection />
          </>
        ) : null}
      </Stack>
    </Box>
  );
}
