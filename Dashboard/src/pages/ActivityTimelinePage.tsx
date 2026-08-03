import { useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  TablePagination,
  TextField,
  Typography,
  type SelectChangeEvent
} from '@mui/material';
import {
  Build,
  Cancel,
  CheckCircle,
  Download,
  Edit,
  History,
  LibraryBooks,
  Login,
  Logout,
  NoteAdd,
  Notifications,
  PersonAdd,
  PersonRemove,
  PictureAsPdf,
  PrecisionManufacturing,
  Search,
  Send,
  Settings as SettingsIcon,
  Sms,
  Usb,
  VerifiedUser,
  ViewModule,
  WarningAmber
} from '@mui/icons-material';
import type { SvgIconComponent } from '@mui/icons-material';
import { apiService } from '../services/apiService';
import { useAuth } from '../contexts/AuthContext';
import { downloadBlob } from '../utils/downloadBlob';
import { formatIST } from '../utils/formatDate';
import type { ActivityLogItem, SectionItem, UserListItem, UserRole } from '../types';

const PAGE_SIZE_OPTIONS = [10, 20, 50];
const EXPORT_LIMIT = 5000;

const ACTION_META: Record<string, { label: string; icon: SvgIconComponent; color: string }> = {
  USER_LOGIN: { label: 'User Login', icon: Login, color: '#2e7d32' },
  USER_LOGOUT: { label: 'User Logout', icon: Logout, color: '#616161' },
  OTP_GENERATED: { label: 'OTP Generated', icon: Sms, color: '#0288d1' },
  OTP_VERIFIED: { label: 'OTP Verified', icon: VerifiedUser, color: '#0288d1' },
  CHECKSHEET_CREATED: { label: 'Checksheet Created', icon: NoteAdd, color: '#5c6bc0' },
  CHECKSHEET_SUBMITTED: { label: 'Checksheet Submitted', icon: Send, color: '#1976d2' },
  CHECKSHEET_APPROVED: { label: 'Checksheet Approved', icon: CheckCircle, color: '#2e7d32' },
  CHECKSHEET_REJECTED: { label: 'Checksheet Rejected', icon: Cancel, color: '#d32f2f' },
  USER_CREATED: { label: 'User Created', icon: PersonAdd, color: '#5c6bc0' },
  USER_UPDATED: { label: 'User Updated', icon: Edit, color: '#ff9800' },
  USER_DELETED: { label: 'User Deleted', icon: PersonRemove, color: '#d32f2f' },
  SECTION_CREATED: { label: 'Section Created', icon: ViewModule, color: '#5c6bc0' },
  EQUIPMENT_ADDED: { label: 'Equipment Added', icon: PrecisionManufacturing, color: '#5c6bc0' },
  EQUIPMENT_UPDATED: { label: 'Equipment Updated', icon: Build, color: '#ff9800' },
  TEMPLATE_CREATED: { label: 'Template Created', icon: LibraryBooks, color: '#5c6bc0' },
  TEMPLATE_UPDATED: { label: 'Template Updated', icon: Edit, color: '#ff9800' },
  NOTIFICATION_SENT: { label: 'Notification Sent', icon: Notifications, color: '#0288d1' },
  SYSTEM_SETTING_CHANGED: { label: 'System Setting Changed', icon: SettingsIcon, color: '#ff9800' },
  // Module 39: Digital Signature (DSC) audit trail.
  SIGNATURE_INITIATED: { label: 'Signature Initiated', icon: VerifiedUser, color: '#5c6bc0' },
  CERTIFICATE_VERIFIED: { label: 'Certificate Verified', icon: CheckCircle, color: '#2e7d32' },
  SIGNATURE_SUCCESS: { label: 'Signature Successful', icon: VerifiedUser, color: '#2e7d32' },
  PDF_SIGNED: { label: 'PDF Signed', icon: PictureAsPdf, color: '#2e7d32' },
  SIGNATURE_FAILED: { label: 'Signature Failed', icon: Cancel, color: '#d32f2f' },
  INVALID_CERTIFICATE: { label: 'Invalid Certificate', icon: WarningAmber, color: '#d32f2f' },
  EXPIRED_CERTIFICATE: { label: 'Expired Certificate', icon: WarningAmber, color: '#d32f2f' },
  PIN_FAILURE: { label: 'PIN Failure', icon: WarningAmber, color: '#d32f2f' },
  TOKEN_DISCONNECTED: { label: 'Token Disconnected', icon: Usb, color: '#d32f2f' }
};

function actionMeta(action: string) {
  return ACTION_META[action] ?? { label: action, icon: History, color: '#757575' };
}

function actionLabel(action: string) {
  return actionMeta(action).label;
}

interface Filters {
  dateFrom: string;
  dateTo: string;
  sectionId: number | '';
  userId: number | '';
  role: UserRole | '';
  action: string;
}

const EMPTY_FILTERS: Filters = {
  dateFrom: '',
  dateTo: '',
  sectionId: '',
  userId: '',
  role: '',
  action: ''
};

function buildParams(filters: Filters, search: string) {
  const params: Record<string, unknown> = {};
  if (search.trim()) params.search = search.trim();
  if (filters.dateFrom) params.date_from = filters.dateFrom;
  if (filters.dateTo) params.date_to = filters.dateTo;
  if (filters.sectionId) params.section_id = filters.sectionId;
  if (filters.userId) params.user_id = filters.userId;
  if (filters.role) params.role = filters.role;
  if (filters.action) params.action = filters.action;
  return params;
}

function ActivityCard({ item, onClick }: { item: ActivityLogItem; onClick: () => void }) {
  const meta = actionMeta(item.action);
  const Icon = meta.icon;

  return (
    <Card
      onClick={onClick}
      sx={{
        cursor: 'pointer',
        borderLeft: '4px solid',
        borderLeftColor: meta.color,
        '&:hover': { boxShadow: 4 }
      }}
    >
      <CardContent>
        <Stack direction="row" spacing={2} alignItems="flex-start">
          <Box
            sx={{
              width: 40,
              height: 40,
              borderRadius: '50%',
              bgcolor: `${meta.color}22`,
              color: meta.color,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}
          >
            <Icon fontSize="small" />
          </Box>
          <Box flexGrow={1} minWidth={0}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={1}>
              <Typography variant="subtitle1" fontWeight={700}>{meta.label}</Typography>
              <Typography variant="caption" color="text.secondary">{formatIST(item.created_at)}</Typography>
            </Stack>
            {item.description ? (
              <Typography variant="body2" color="text.secondary" mt={0.5}>{item.description}</Typography>
            ) : null}
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap mt={1}>
              {item.user_name ? <Chip size="small" label={item.user_name} /> : null}
              {item.employee_id ? <Chip size="small" variant="outlined" label={item.employee_id} /> : null}
              {item.role ? <Chip size="small" variant="outlined" label={item.role} /> : null}
              {item.section_name ? <Chip size="small" variant="outlined" color="primary" label={item.section_name} /> : null}
            </Stack>
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
}

function ValueBlock({ label, value }: { label: string; value?: Record<string, unknown> | null }) {
  if (!value || Object.keys(value).length === 0) {
    return (
      <Box>
        <Typography variant="overline" color="text.secondary">{label}</Typography>
        <Typography variant="body2" color="text.secondary">Not available</Typography>
      </Box>
    );
  }
  return (
    <Box>
      <Typography variant="overline" color="text.secondary">{label}</Typography>
      <Box component="pre" sx={{ m: 0, fontSize: 12, fontFamily: 'monospace', whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
        {JSON.stringify(value, null, 2)}
      </Box>
    </Box>
  );
}

export default function ActivityTimelinePage() {
  const { user } = useAuth();
  const isAdmin = user?.role === 'Admin';

  const [items, setItems] = useState<ActivityLogItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(20);

  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [filters, setFilters] = useState<Filters>(EMPTY_FILTERS);

  const [sections, setSections] = useState<SectionItem[]>([]);
  const [users, setUsers] = useState<UserListItem[]>([]);
  const [actionTypes, setActionTypes] = useState<string[]>([]);

  const [selected, setSelected] = useState<ActivityLogItem | null>(null);
  const [exporting, setExporting] = useState<'csv' | 'excel' | null>(null);
  const [exportError, setExportError] = useState<string | null>(null);

  useEffect(() => {
    const timer = window.setTimeout(() => setDebouncedSearch(search.trim()), 300);
    return () => window.clearTimeout(timer);
  }, [search]);

  useEffect(() => {
    let mounted = true;
    Promise.all([
      apiService.getSections(),
      apiService.getUsers({ skip: 0, limit: 500, sort_by: 'name', sort_order: 'asc' }),
      apiService.getActivityActions()
    ])
      .then(([sectionsRes, usersRes, actionsRes]) => {
        if (!mounted) return;
        setSections(sectionsRes.data || []);
        setUsers(usersRes.data.items || []);
        setActionTypes(actionsRes.data.actions || []);
      })
      .catch(() => {
        // Filter dropdown lookups are a convenience only - failing here must not block the
        // main timeline, which loads independently below.
      });
    return () => {
      mounted = false;
    };
  }, []);

  const loadActivities = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiService.getActivities({
        skip: page * rowsPerPage,
        limit: rowsPerPage,
        ...buildParams(filters, debouncedSearch)
      });
      setItems(response.data.items || []);
      setTotal(response.data.total || 0);
    } catch {
      setItems([]);
      setTotal(0);
      setError('Unable to load activity timeline from the backend.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadActivities();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, rowsPerPage, debouncedSearch, filters]);

  const updateFilter = <K extends keyof Filters>(key: K, value: Filters[K]) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
    setPage(0);
  };

  const resetFilters = () => {
    setFilters(EMPTY_FILTERS);
    setSearch('');
    setPage(0);
  };

  const exportRows = async (): Promise<ActivityLogItem[]> => {
    const response = await apiService.getActivities({
      skip: 0,
      limit: EXPORT_LIMIT,
      ...buildParams(filters, debouncedSearch)
    });
    return response.data.items || [];
  };

  const exportCsv = async () => {
    setExporting('csv');
    setExportError(null);
    try {
      const rows = await exportRows();
      const lines = ['Date & Time (IST),Action,User Name,Employee ID,Role,Section,Description'];
      rows.forEach((row) => {
        const cells = [
          formatIST(row.created_at),
          actionLabel(row.action),
          row.user_name ?? '',
          row.employee_id ?? '',
          row.role ?? '',
          row.section_name ?? '',
          (row.description ?? '').replace(/"/g, '""')
        ];
        lines.push(cells.map((cell) => `"${cell}"`).join(','));
      });
      downloadBlob(new Blob([lines.join('\n')], { type: 'text/csv' }), `activity_timeline_${Date.now()}.csv`);
    } catch {
      setExportError('Unable to export CSV.');
    } finally {
      setExporting(null);
    }
  };

  const exportExcel = async () => {
    setExporting('excel');
    setExportError(null);
    try {
      const rows = await exportRows();
      const XLSX = await import('xlsx');
      const sheet = XLSX.utils.json_to_sheet(
        rows.map((row) => ({
          'Date & Time (IST)': formatIST(row.created_at),
          Action: actionLabel(row.action),
          'User Name': row.user_name ?? '',
          'Employee ID': row.employee_id ?? '',
          Role: row.role ?? '',
          Section: row.section_name ?? '',
          Description: row.description ?? ''
        }))
      );
      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, sheet, 'Activity Timeline');
      XLSX.writeFile(workbook, `activity_timeline_${Date.now()}.xlsx`);
    } catch {
      setExportError('Unable to export Excel workbook.');
    } finally {
      setExporting(null);
    }
  };

  const detailEntity = useMemo(() => {
    if (!selected) return '-';
    if (!selected.entity_type) return '-';
    return `${selected.entity_type}${selected.entity_id ? ` #${selected.entity_id}` : ''}`;
  }, [selected]);

  return (
    <Box>
      <Stack spacing={2.5}>
        <Paper sx={{ p: 3, borderRadius: 3 }}>
          <Stack direction="row" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={2}>
            <Box>
              <Typography variant="h4" fontWeight={700} mb={1}>Activity Timeline &amp; Audit Center</Typography>
              <Typography variant="body1" color="text.secondary">
                {isAdmin ? 'System-wide operational activity, newest first.' : 'Activity for your assigned section, newest first.'}
              </Typography>
            </Box>
            {isAdmin ? (
              <Stack direction="row" spacing={1.5}>
                <Button
                  variant="outlined"
                  startIcon={exporting === 'csv' ? <CircularProgress size={16} /> : <Download />}
                  onClick={exportCsv}
                  disabled={exporting !== null}
                >
                  Export CSV
                </Button>
                <Button
                  variant="outlined"
                  startIcon={exporting === 'excel' ? <CircularProgress size={16} /> : <Download />}
                  onClick={exportExcel}
                  disabled={exporting !== null}
                >
                  Export Excel
                </Button>
              </Stack>
            ) : null}
          </Stack>
        </Paper>

        <Paper sx={{ p: 2.5 }}>
          <Stack spacing={2}>
            <Typography variant="subtitle1" fontWeight={700}>Filters</Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  value={search}
                  onChange={(event) => { setSearch(event.target.value); setPage(0); }}
                  placeholder="Search by name, employee ID, locomotive, equipment, checksheet #"
                  InputProps={{ startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} /> }}
                />
              </Grid>
              <Grid item xs={6} sm={3} md={2}>
                <TextField
                  fullWidth
                  label="From"
                  type="date"
                  InputLabelProps={{ shrink: true }}
                  value={filters.dateFrom}
                  onChange={(event) => updateFilter('dateFrom', event.target.value)}
                />
              </Grid>
              <Grid item xs={6} sm={3} md={2}>
                <TextField
                  fullWidth
                  label="To"
                  type="date"
                  InputLabelProps={{ shrink: true }}
                  value={filters.dateTo}
                  onChange={(event) => updateFilter('dateTo', event.target.value)}
                />
              </Grid>
              {isAdmin ? (
                <Grid item xs={6} sm={3} md={2}>
                  <FormControl fullWidth>
                    <InputLabel>Section</InputLabel>
                    <Select
                      label="Section"
                      value={filters.sectionId}
                      onChange={(event: SelectChangeEvent<number | ''>) => updateFilter('sectionId', event.target.value as number | '')}
                    >
                      <MenuItem value="">All</MenuItem>
                      {sections.map((s) => <MenuItem key={s.id} value={s.id}>{s.name}</MenuItem>)}
                    </Select>
                  </FormControl>
                </Grid>
              ) : null}
              <Grid item xs={6} sm={3} md={2}>
                <FormControl fullWidth>
                  <InputLabel>Role</InputLabel>
                  <Select
                    label="Role"
                    value={filters.role}
                    onChange={(event: SelectChangeEvent<string>) => updateFilter('role', event.target.value as UserRole | '')}
                  >
                    <MenuItem value="">All</MenuItem>
                    <MenuItem value="Admin">Admin</MenuItem>
                    <MenuItem value="Supervisor">Supervisor</MenuItem>
                    <MenuItem value="Technician">Technician</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth>
                  <InputLabel>User</InputLabel>
                  <Select
                    label="User"
                    value={filters.userId}
                    onChange={(event: SelectChangeEvent<number | ''>) => updateFilter('userId', event.target.value as number | '')}
                  >
                    <MenuItem value="">All</MenuItem>
                    {users.map((u) => <MenuItem key={u.id} value={u.id}>{u.name}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Activity Type</InputLabel>
                  <Select
                    label="Activity Type"
                    value={filters.action}
                    onChange={(event: SelectChangeEvent<string>) => updateFilter('action', event.target.value)}
                  >
                    <MenuItem value="">All</MenuItem>
                    {actionTypes.map((a) => <MenuItem key={a} value={a}>{actionLabel(a)}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
            <Stack direction="row" spacing={1.5}>
              <Button variant="text" onClick={resetFilters}>Reset Filters</Button>
            </Stack>
            {exportError ? <Alert severity="error" onClose={() => setExportError(null)}>{exportError}</Alert> : null}
          </Stack>
        </Paper>

        {error ? (
          <Alert severity="error" action={<Button color="inherit" size="small" onClick={loadActivities}>Retry</Button>}>
            {error}
          </Alert>
        ) : null}

        {loading && items.length === 0 ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
            <CircularProgress />
          </Box>
        ) : items.length === 0 ? (
          <Paper sx={{ p: 5, textAlign: 'center' }}>
            <Typography variant="h6" fontWeight={700} mb={1}>No activity found</Typography>
            <Typography variant="body2" color="text.secondary">Try adjusting the filters or search terms.</Typography>
          </Paper>
        ) : (
          <>
            <Stack spacing={1.5}>
              {items.map((item) => (
                <ActivityCard key={item.id} item={item} onClick={() => setSelected(item)} />
              ))}
            </Stack>
            <Paper>
              <TablePagination
                component="div"
                count={total}
                page={page}
                rowsPerPage={rowsPerPage}
                onPageChange={(_, nextPage) => setPage(nextPage)}
                onRowsPerPageChange={(event) => {
                  setRowsPerPage(parseInt(event.target.value, 10));
                  setPage(0);
                }}
                rowsPerPageOptions={PAGE_SIZE_OPTIONS}
              />
            </Paper>
          </>
        )}
      </Stack>

      <Dialog open={selected !== null} onClose={() => setSelected(null)} maxWidth="sm" fullWidth>
        <DialogTitle>Activity Detail</DialogTitle>
        <DialogContent dividers>
          {selected ? (
            <Stack spacing={2}>
              <Box>
                <Typography variant="overline" color="text.secondary">Action</Typography>
                <Typography variant="body1" fontWeight={700}>{actionLabel(selected.action)}</Typography>
              </Box>
              <Box>
                <Typography variant="overline" color="text.secondary">Timestamp</Typography>
                <Typography variant="body2">{formatIST(selected.created_at)}</Typography>
              </Box>
              <Box>
                <Typography variant="overline" color="text.secondary">Performed By</Typography>
                <Typography variant="body2">
                  {selected.user_name ? `${selected.user_name} (${selected.employee_id ?? '-'}) - ${selected.role ?? '-'}` : 'System / Unknown'}
                </Typography>
              </Box>
              <Box>
                <Typography variant="overline" color="text.secondary">Section</Typography>
                <Typography variant="body2">{selected.section_name ?? 'Not available'}</Typography>
              </Box>
              <Box>
                <Typography variant="overline" color="text.secondary">Entity</Typography>
                <Typography variant="body2">{detailEntity}</Typography>
              </Box>
              {selected.description ? (
                <Box>
                  <Typography variant="overline" color="text.secondary">Description</Typography>
                  <Typography variant="body2">{selected.description}</Typography>
                </Box>
              ) : null}
              <Divider />
              <ValueBlock label="Old Value" value={selected.old_value} />
              <ValueBlock label="New Value" value={selected.new_value} />
            </Stack>
          ) : null}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelected(null)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
