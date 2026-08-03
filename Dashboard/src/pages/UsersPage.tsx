import {
  Alert,
  Autocomplete,
  Box,
  Button,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  IconButton,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Snackbar,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  TextField,
  Typography
} from '@mui/material';
import { Add, Delete, Edit, Search } from '@mui/icons-material';
import GroupRoundedIcon from '@mui/icons-material/GroupRounded';
import HowToRegRoundedIcon from '@mui/icons-material/HowToRegRounded';
import AdminPanelSettingsRoundedIcon from '@mui/icons-material/AdminPanelSettingsRounded';
import SupervisorAccountRoundedIcon from '@mui/icons-material/SupervisorAccountRounded';
import { useEffect, useMemo, useRef, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { apiService } from '../services/apiService';
import { authService } from '../services/authService';
import type { UserFormValues, UserListItem, UserProfile, UserRole, SectionItem } from '../types';
import { gradients, glow } from '../theme/palette';
import StatCard from '../components/common/StatCard';
import EmptyState from '../components/common/EmptyState';
import ErrorState from '../components/common/ErrorState';
import TableSkeleton from '../components/common/TableSkeleton';

// Sentinel option representing "no section filter applied" in the searchable Section dropdown.
const ALL_SECTIONS_OPTION: SectionItem = { id: undefined, name: 'All Sections' };

const emptyFormValues: UserFormValues = {
  employee_id: '',
  name: '',
  mobile: '',
  email: '',
  role: 'Technician',
  is_active: true,
  password: ''
  ,section_id: ''
};

export default function UsersPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const deepLinkHandled = useRef(false);

  const [users, setUsers] = useState<UserListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState<'All' | UserRole>('All');
  const [statusFilter, setStatusFilter] = useState<'All' | 'Active' | 'Inactive'>('All');
  const [sectionFilter, setSectionFilter] = useState<SectionItem>(ALL_SECTIONS_OPTION);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<UserListItem | null>(null);
  const [formValues, setFormValues] = useState<UserFormValues>(emptyFormValues);
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(null);
  const [sections, setSections] = useState<SectionItem[]>([]);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success'
  });

  useEffect(() => {
    const timer = window.setTimeout(() => setDebouncedSearch(search.trim()), 400);
    return () => window.clearTimeout(timer);
  }, [search]);

  const loadUsers = async (searchOverride?: string) => {
    setLoading(true);

    try {
      const response = await apiService.getUsers({
        skip: page * rowsPerPage,
        limit: rowsPerPage,
        search: (searchOverride ?? debouncedSearch) || undefined,
        role: roleFilter === 'All' ? undefined : roleFilter,
        is_active: statusFilter === 'All' ? undefined : statusFilter === 'Active',
        section_id: sectionFilter.id === undefined ? undefined : sectionFilter.id,
        sort_by: 'created_at',
        sort_order: 'desc'
      });

      setUsers(response.data.items || []);
      setTotal(response.data.total || 0);
      setError(null);
    } catch (err) {
      setUsers([]);
      setTotal(0);
      setError(getErrorMessage(err, 'Unable to load users from the backend.'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let mounted = true;

    const fetchUsers = async () => {
      if (!mounted) return;
      await loadUsers(debouncedSearch);
    };

    fetchUsers();

    return () => {
      mounted = false;
    };
  }, [debouncedSearch, page, rowsPerPage, roleFilter, statusFilter, sectionFilter]);

  useEffect(() => {
    let mounted = true;
    authService.me()
      .then((response) => {
        if (mounted) {
          setCurrentUser(response.data as UserProfile);
        }
      })
      .catch(() => undefined);

    // load sections for section dropdown
    apiService.getSections()
      .then((res) => {
        if (mounted) setSections(res.data || []);
      })
      .catch(() => undefined);

    return () => {
      mounted = false;
    };
  }, []);

  // Global Search (Module 28) deep-links here as /users?id=<employee_id> - the record may not be
  // on the currently displayed page (this table is server-paginated), so it's resolved via a
  // dedicated one-off call to the existing search-by-employee_id endpoint rather than relying on
  // whatever page of `users` happens to be loaded.
  useEffect(() => {
    if (deepLinkHandled.current) return;
    const idParam = searchParams.get('id');
    if (!idParam) return;

    deepLinkHandled.current = true;
    apiService
      .getUsers({ skip: 0, limit: 5, search: idParam })
      .then((res) => {
        const match = res.data.items.find((user) => user.employee_id === idParam);
        if (match) openEditDialog(match);
      })
      .catch(() => undefined)
      .finally(() => {
        searchParams.delete('id');
        setSearchParams(searchParams, { replace: true });
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  const stats = useMemo(() => {
    const activeUsers = users.filter((user) => user.is_active).length;
    const adminUsers = users.filter((user) => user.role === 'Admin').length;
    const supervisorUsers = users.filter((user) => user.role === 'Supervisor').length;

    return {
      total: total || users.length,
      active: activeUsers,
      admin: adminUsers,
      supervisor: supervisorUsers
    };
  }, [total, users]);

  const resetDialog = () => {
    setDialogOpen(false);
    setSelectedUser(null);
    setFormValues(emptyFormValues);
    setFormError(null);
  };

  const openCreateDialog = () => {
    setSelectedUser(null);
    setFormValues(emptyFormValues);
    setFormError(null);
    setDialogOpen(true);
  };

  const openEditDialog = (user: UserListItem) => {
    setSelectedUser(user);
    setFormValues({
      employee_id: user.employee_id,
      name: user.name,
      mobile: user.mobile,
      email: user.email || '',
      role: user.role,
      is_active: user.is_active,
      password: '',
      section_id: user.section_id ?? ''
    });
    setFormError(null);
    setDialogOpen(true);
  };

  const getErrorMessage = (error: unknown, fallback: string) => {
    if (typeof error === 'object' && error !== null && 'response' in error) {
      const response = (error as { response?: { data?: { detail?: string } } }).response;
      if (response?.data?.detail) {
        return response.data.detail;
      }
    }

    return fallback;
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!formValues.employee_id.trim()) {
      setFormError('Employee ID is required.');
      return;
    }

    if (!formValues.name.trim()) {
      setFormError('Name is required.');
      return;
    }

    if (!formValues.mobile.trim()) {
      setFormError('Mobile number is required.');
      return;
    }

    if (!selectedUser && !formValues.password.trim()) {
      setFormError('Password is required for new users.');
      return;
    }

    // Business rule: Section required for Technician and Supervisor
    if ((formValues.role === 'Technician' || formValues.role === 'Supervisor') && (formValues.section_id === '' || formValues.section_id === undefined || formValues.section_id === null)) {
      setFormError('Section is required for Technician and Supervisor roles.');
      return;
    }

    setSubmitting(true);
    setFormError(null);

    try {
      if (selectedUser) {
        await apiService.updateUser(selectedUser.id, {
          name: formValues.name.trim(),
          mobile: formValues.mobile.trim(),
          email: formValues.email.trim() || null,
          role: formValues.role,
          is_active: formValues.is_active,
          section_id: formValues.section_id === '' ? null : formValues.section_id,
          password: formValues.password.trim() || undefined
        });
      } else {
        await apiService.createUser({
          employee_id: formValues.employee_id.trim(),
          name: formValues.name.trim(),
          mobile: formValues.mobile.trim(),
          email: formValues.email.trim() || null,
          role: formValues.role,
          is_active: formValues.is_active,
          section_id: formValues.section_id === '' ? null : formValues.section_id,
          password: formValues.password.trim()
        });
      }

      setSnackbar({
        open: true,
        message: selectedUser ? 'User updated successfully.' : 'User created successfully.',
        severity: 'success'
      });
      resetDialog();
      await loadUsers(search.trim());
    } catch (error) {
      setFormError(getErrorMessage(error, 'The user could not be saved.'));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedUser) return;

    try {
      await apiService.deleteUser(selectedUser.id);
      setSnackbar({ open: true, message: 'User deleted successfully.', severity: 'success' });
      setDeleteDialogOpen(false);
      setSelectedUser(null);
      await loadUsers(search.trim());
    } catch (error) {
      setSnackbar({ open: true, message: getErrorMessage(error, 'Unable to delete user.'), severity: 'error' });
    }
  };

  return (
    <Box>
      <Stack spacing={2.5}>
        <Paper sx={{ p: 3, borderRadius: 3 }}>
          <Typography variant="h4" fontWeight={700} mb={1}>Users</Typography>
          <Typography variant="body1" color="text.secondary">Manage BL-DCMS user accounts with search, role-based filters, and lifecycle actions.</Typography>
        </Paper>

        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
          {[
            { label: 'Total Users', value: stats.total, icon: GroupRoundedIcon, gradient: gradients.navy, glowColor: glow.cyan },
            { label: 'Active Users', value: stats.active, icon: HowToRegRoundedIcon, gradient: gradients.success, glowColor: glow.success },
            { label: 'Admins', value: stats.admin, icon: AdminPanelSettingsRoundedIcon, gradient: gradients.primary, glowColor: glow.primary },
            { label: 'Supervisors', value: stats.supervisor, icon: SupervisorAccountRoundedIcon, gradient: gradients.purple, glowColor: glow.purple }
          ].map((card) => (
            <Box key={card.label} sx={{ flex: 1 }}>
              <StatCard label={card.label} value={card.value} icon={card.icon} gradient={card.gradient} glowColor={card.glowColor} loading={loading} />
            </Box>
          ))}
        </Stack>

        <Paper sx={{ p: 3, borderRadius: 3 }}>
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems={{ xs: 'stretch', md: 'center' }} justifyContent="space-between">
            <TextField
              value={search}
              onChange={(event) => {
                setSearch(event.target.value);
                setPage(0);
              }}
              placeholder="Search by name, employee ID, mobile or email"
              InputProps={{ startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} /> }}
              sx={{ minWidth: { xs: '100%', md: 320 } }}
            />
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <FormControl sx={{ minWidth: 140 }} size="small">
                <InputLabel>Role</InputLabel>
                <Select
                  value={roleFilter}
                  label="Role"
                  onChange={(event) => {
                    setRoleFilter(event.target.value as 'All' | UserRole);
                    setPage(0);
                  }}
                >
                  <MenuItem value="All">All</MenuItem>
                  <MenuItem value="Admin">Admin</MenuItem>
                  <MenuItem value="Supervisor">Supervisor</MenuItem>
                  <MenuItem value="Technician">Technician</MenuItem>
                </Select>
              </FormControl>
              <FormControl sx={{ minWidth: 140 }} size="small">
                <InputLabel>Status</InputLabel>
                <Select
                  value={statusFilter}
                  label="Status"
                  onChange={(event) => {
                    setStatusFilter(event.target.value as 'All' | 'Active' | 'Inactive');
                    setPage(0);
                  }}
                >
                  <MenuItem value="All">All</MenuItem>
                  <MenuItem value="Active">Active</MenuItem>
                  <MenuItem value="Inactive">Inactive</MenuItem>
                </Select>
              </FormControl>
              <Autocomplete<SectionItem, false, true, false>
                size="small"
                sx={{ minWidth: { xs: '100%', sm: 220 } }}
                options={[ALL_SECTIONS_OPTION, ...sections]}
                value={sectionFilter}
                disableClearable
                getOptionLabel={(option) => option.name || 'All Sections'}
                isOptionEqualToValue={(option, value) => option.id === value.id}
                onChange={(_, value) => {
                  setSectionFilter(value ?? ALL_SECTIONS_OPTION);
                  setPage(0);
                }}
                renderInput={(params) => (
                  <TextField {...params} label="Section" placeholder="Search section..." />
                )}
              />
              <Button variant="contained" startIcon={<Add />} onClick={openCreateDialog}>
                Add User
              </Button>
            </Stack>
          </Stack>
        </Paper>

        {error ? (
          <Paper sx={{ p: 0 }}>
            <ErrorState message={error} onRetry={() => loadUsers(search.trim())} />
          </Paper>
        ) : null}

        <Paper sx={{ borderRadius: 3, overflow: 'hidden' }}>
          {!loading && users.length === 0 ? (
            <EmptyState
              title="No users found"
              message="Try adjusting the search or filters to locate the right account."
              actionLabel="Reset filters"
              onAction={() => { setSearch(''); setRoleFilter('All'); setStatusFilter('All'); setSectionFilter(ALL_SECTIONS_OPTION); setPage(0); }}
            />
          ) : (
            <>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>User</TableCell>
                      <TableCell>Section</TableCell>
                      <TableCell>Employee ID</TableCell>
                      <TableCell>Role</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Mobile</TableCell>
                      <TableCell>Email</TableCell>
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  {loading ? (
                    <TableSkeleton rows={rowsPerPage > 10 ? 10 : rowsPerPage} columns={8} />
                  ) : (
                  <TableBody>
                    {users.map((user) => (
                      <TableRow key={user.id} hover>
                        <TableCell>
                          <Typography fontWeight={700}>{user.name}</Typography>
                          <Typography variant="body2" color="text.secondary">{user.mobile}</Typography>
                        </TableCell>
                        <TableCell>{user.section_name || '—'}</TableCell>
                        <TableCell>{user.employee_id}</TableCell>
                        <TableCell>
                          <Chip label={user.role} color={user.role === 'Admin' ? 'primary' : user.role === 'Supervisor' ? 'warning' : 'default'} />
                        </TableCell>
                        <TableCell>
                          <Chip label={user.is_active ? 'Active' : 'Inactive'} color={user.is_active ? 'success' : 'default'} />
                        </TableCell>
                        <TableCell>{user.mobile}</TableCell>
                        <TableCell>{user.email || '—'}</TableCell>
                        <TableCell align="right">
                          <Stack direction="row" spacing={1} justifyContent="flex-end">
                            <IconButton size="small" onClick={() => openEditDialog(user)}>
                              <Edit fontSize="small" />
                            </IconButton>
                            <IconButton size="small" color="error" onClick={() => { setSelectedUser(user); setDeleteDialogOpen(true); }} disabled={currentUser?.id === String(user.id)}>
                              <Delete fontSize="small" />
                            </IconButton>
                          </Stack>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                  )}
                </Table>
              </TableContainer>
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
                rowsPerPageOptions={[5, 10, 25]}
              />
            </>
          )}
        </Paper>
      </Stack>

      <Dialog open={dialogOpen} onClose={resetDialog} maxWidth="sm" fullWidth>
        <DialogTitle>{selectedUser ? 'Edit User' : 'Add User'}</DialogTitle>
        <DialogContent>
          <Box component="form" id="user-form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
            <Stack spacing={2.2}>
              {formError ? <Alert severity="error">{formError}</Alert> : null}
              <TextField
                label="Employee ID"
                value={formValues.employee_id}
                onChange={(event) => setFormValues((current) => ({ ...current, employee_id: event.target.value }))}
                disabled={Boolean(selectedUser)}
                required
              />
              <TextField
                label="Full Name"
                value={formValues.name}
                onChange={(event) => setFormValues((current) => ({ ...current, name: event.target.value }))}
                required
              />
              <TextField
                label="Mobile"
                value={formValues.mobile}
                onChange={(event) => setFormValues((current) => ({ ...current, mobile: event.target.value }))}
                required
              />
              <TextField
                label="Email"
                type="email"
                value={formValues.email}
                onChange={(event) => setFormValues((current) => ({ ...current, email: event.target.value }))}
              />
              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                <FormControl fullWidth>
                  <InputLabel>Role</InputLabel>
                  <Select
                    value={formValues.role}
                    label="Role"
                    onChange={(event) => setFormValues((current) => ({ ...current, role: event.target.value as UserRole }))}
                  >
                    <MenuItem value="Admin">Admin</MenuItem>
                    <MenuItem value="Supervisor">Supervisor</MenuItem>
                    <MenuItem value="Technician">Technician</MenuItem>
                  </Select>
                </FormControl>
                <FormControl fullWidth>
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={formValues.is_active ? 'Active' : 'Inactive'}
                    label="Status"
                    onChange={(event) => setFormValues((current) => ({ ...current, is_active: event.target.value === 'Active' }))}
                  >
                    <MenuItem value="Active">Active</MenuItem>
                    <MenuItem value="Inactive">Inactive</MenuItem>
                  </Select>
                </FormControl>
              </Stack>
              <FormControl fullWidth>
                <InputLabel>Section</InputLabel>
                <Select
                  value={formValues.section_id}
                  label="Section"
                  onChange={(event) => setFormValues((current) => ({ ...current, section_id: event.target.value as number | '' }))}
                >
                  <MenuItem value="">None</MenuItem>
                  {sections.map((s) => (
                    <MenuItem key={s.id} value={s.id}>{s.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
              <TextField
                label={selectedUser ? 'New Password (optional)' : 'Password'}
                type="password"
                value={formValues.password}
                onChange={(event) => setFormValues((current) => ({ ...current, password: event.target.value }))}
                helperText={selectedUser ? 'Leave blank to keep the current password.' : undefined}
                required={!selectedUser}
              />
            </Stack>
          </Box>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={resetDialog}>Cancel</Button>
          <Button type="submit" form="user-form" variant="contained" disabled={submitting}>
            {submitting ? <CircularProgress size={20} color="inherit" /> : selectedUser ? 'Save Changes' : 'Create User'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete user</DialogTitle>
        <DialogContent>
          <Typography>Are you sure you want to delete {selectedUser?.name || 'this user'}?</Typography>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button color="error" variant="contained" onClick={handleDelete}>Delete</Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar((current) => ({ ...current, open: false }))}
        message={snackbar.message}
      />
    </Box>
  );
}
