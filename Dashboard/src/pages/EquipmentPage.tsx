import {
  Alert,
  Box,
  Button,
  Checkbox,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  IconButton,
  Paper,
  Skeleton,
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
import { useEffect, useMemo, useRef, useState, type FormEvent } from 'react';
import { useSearchParams } from 'react-router-dom';
import { apiService } from '../services/apiService';
import type { EquipmentFormValues, EquipmentItem } from '../types';

const emptyFormValues: EquipmentFormValues = {
  equipment_code: '',
  equipment_name: '',
  is_active: true
};

export default function EquipmentPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const deepLinkHandled = useRef(false);

  const [items, setItems] = useState<EquipmentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [search, setSearch] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedEquipment, setSelectedEquipment] = useState<EquipmentItem | null>(null);
  const [formValues, setFormValues] = useState<EquipmentFormValues>(emptyFormValues);
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success'
  });

  const loadEquipment = async () => {
    setLoading(true);

    try {
      const response = await apiService.getEquipment();
      setItems(response.data || []);
      setError(null);
    } catch (err) {
      setItems([]);
      const response = (err as { response?: { data?: { detail?: string } } }).response;
      setError(response?.data?.detail || 'Unable to load equipment from the backend.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let mounted = true;

    const fetchEquipment = async () => {
      if (!mounted) return;
      await loadEquipment();
    };

    fetchEquipment();

    return () => {
      mounted = false;
    };
  }, []);

  // Global Search (Module 28) deep-links here as /equipment?id=<id> - once the full list has
  // loaded, resolve and open that record's existing edit dialog exactly once.
  useEffect(() => {
    if (deepLinkHandled.current || loading) return;
    const idParam = searchParams.get('id');
    if (!idParam) return;

    const match = items.find((item) => String(item.id) === idParam);
    if (match) {
      deepLinkHandled.current = true;
      openEditDialog(match);
      searchParams.delete('id');
      setSearchParams(searchParams, { replace: true });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [items, loading, searchParams]);

  const filteredItems = useMemo(() => {
    const term = search.trim().toLowerCase();

    if (!term) return items;

    return items.filter((item) => {
      const haystack = [item.equipment_code, item.equipment_name, item.used_in, item.is_active ? 'active' : 'inactive']
        .filter(Boolean)
        .join(' ')
        .toLowerCase();

      return haystack.includes(term);
    });
  }, [items, search]);

  const pagedItems = useMemo(() => {
    const startIndex = page * rowsPerPage;
    return filteredItems.slice(startIndex, startIndex + rowsPerPage);
  }, [filteredItems, page, rowsPerPage]);

  const stats = useMemo(() => ({
    total: items.length,
    active: items.filter((item) => item.is_active).length,
    inactive: items.filter((item) => !item.is_active).length
  }), [items]);

  const resetDialog = () => {
    setDialogOpen(false);
    setSelectedEquipment(null);
    setFormValues(emptyFormValues);
    setFormError(null);
  };

  const openCreateDialog = () => {
    setSelectedEquipment(null);
    setFormValues(emptyFormValues);
    setFormError(null);
    setDialogOpen(true);
  };

  const openEditDialog = (equipment: EquipmentItem) => {
    setSelectedEquipment(equipment);
    setFormValues({
      equipment_code: equipment.equipment_code || '',
      equipment_name: equipment.equipment_name || '',
      is_active: equipment.is_active ?? true
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

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!formValues.equipment_code.trim()) {
      setFormError('Equipment code is required.');
      return;
    }

    if (!formValues.equipment_name.trim()) {
      setFormError('Equipment name is required.');
      return;
    }

    setSubmitting(true);
    setFormError(null);

    try {
      if (selectedEquipment) {
        await apiService.updateEquipment(selectedEquipment.id as number, {
          equipment_code: formValues.equipment_code.trim(),
          equipment_name: formValues.equipment_name.trim(),
          is_active: formValues.is_active
        });
      } else {
        await apiService.createEquipment({
          equipment_code: formValues.equipment_code.trim(),
          equipment_name: formValues.equipment_name.trim()
        });
      }

      setSnackbar({
        open: true,
        message: selectedEquipment ? 'Equipment updated successfully.' : 'Equipment created successfully.',
        severity: 'success'
      });
      resetDialog();
      await loadEquipment();
    } catch (error) {
      setFormError(getErrorMessage(error, 'The equipment could not be saved.'));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedEquipment) return;

    try {
      await apiService.deleteEquipment(selectedEquipment.id as number);
      setSnackbar({ open: true, message: 'Equipment deleted successfully.', severity: 'success' });
      setDeleteDialogOpen(false);
      setSelectedEquipment(null);
      await loadEquipment();
    } catch (error) {
      setSnackbar({ open: true, message: getErrorMessage(error, 'Unable to delete equipment.'), severity: 'error' });
    }
  };

  return (
    <Box>
      <Stack spacing={2.5}>
        <Paper sx={{ p: 3, borderRadius: 3 }}>
          <Typography variant="h4" fontWeight={700} mb={1}>Equipment</Typography>
          <Typography variant="body1" color="text.secondary">Manage operational equipment inventory with search, lifecycle actions, and backend-backed updates.</Typography>
        </Paper>

        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
          {loading ? (
            Array.from({ length: 3 }).map((_, index) => (
              <Paper key={index} sx={{ flex: 1, p: 2.5, borderRadius: 3 }}>
                <Skeleton variant="text" width="40%" />
                <Skeleton variant="text" width="70%" sx={{ mt: 1 }} />
              </Paper>
            ))
          ) : (
            [
              { label: 'Total Equipment', value: stats.total, color: 'primary' as const },
              { label: 'Active', value: stats.active, color: 'success' as const },
              { label: 'Inactive', value: stats.inactive, color: 'warning' as const }
            ].map((card) => (
              <Paper key={card.label} sx={{ flex: 1, p: 2.5, borderRadius: 3 }}>
                <Typography variant="overline" color="text.secondary">{card.label}</Typography>
                <Typography variant="h4" fontWeight={700}>{card.value}</Typography>
              </Paper>
            ))
          )}
        </Stack>

        <Paper sx={{ p: 3, borderRadius: 3 }}>
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems={{ xs: 'stretch', md: 'center' }} justifyContent="space-between">
            <TextField
              value={search}
              onChange={(event) => {
                setSearch(event.target.value);
                setPage(0);
              }}
              placeholder="Search by code or name"
              InputProps={{ startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} /> }}
              sx={{ minWidth: { xs: '100%', md: 320 } }}
            />
            <Button variant="contained" startIcon={<Add />} onClick={openCreateDialog}>
              Add Equipment
            </Button>
          </Stack>
        </Paper>

        {error ? <Alert severity="error">{error}</Alert> : null}

        <Paper sx={{ borderRadius: 3, overflow: 'hidden' }}>
          {loading ? (
            <Box sx={{ p: 3 }}>
              <Skeleton variant="rectangular" height={56} sx={{ mb: 1.5 }} />
              <Skeleton variant="rectangular" height={48} sx={{ mb: 1 }} />
              <Skeleton variant="rectangular" height={48} sx={{ mb: 1 }} />
              <Skeleton variant="rectangular" height={48} />
            </Box>
          ) : filteredItems.length === 0 ? (
            <Box sx={{ p: 5, textAlign: 'center' }}>
              <Typography variant="h6" fontWeight={700} mb={1}>No equipment found</Typography>
              <Typography variant="body2" color="text.secondary" mb={2}>Try changing your search or create a new equipment record.</Typography>
              <Button variant="outlined" onClick={() => { setSearch(''); setPage(0); }}>
                Reset search
              </Button>
            </Box>
          ) : (
            <>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>ID</TableCell>
                      <TableCell>Code</TableCell>
                      <TableCell>Name</TableCell>
                      <TableCell>Used In</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {pagedItems.map((item) => (
                      <TableRow key={item.id ?? item.equipment_code} hover>
                        <TableCell>{item.id}</TableCell>
                        <TableCell>{item.equipment_code}</TableCell>
                        <TableCell>{item.equipment_name}</TableCell>
                        <TableCell>{item.used_in || 'Not Mapped'}</TableCell>
                        <TableCell>
                          <Chip label={item.is_active ? 'Active' : 'Inactive'} color={item.is_active ? 'success' : 'default'} />
                        </TableCell>
                        <TableCell align="right">
                          <Stack direction="row" spacing={1} justifyContent="flex-end">
                            <IconButton size="small" onClick={() => openEditDialog(item)}>
                              <Edit fontSize="small" />
                            </IconButton>
                            <IconButton size="small" color="error" onClick={() => { setSelectedEquipment(item); setDeleteDialogOpen(true); }}>
                              <Delete fontSize="small" />
                            </IconButton>
                          </Stack>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              <TablePagination
                component="div"
                count={filteredItems.length}
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
        <DialogTitle>{selectedEquipment ? 'Edit Equipment' : 'Add Equipment'}</DialogTitle>
        <DialogContent>
          <Box component="form" id="equipment-form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
            <Stack spacing={2.2}>
              {formError ? <Alert severity="error">{formError}</Alert> : null}
              <TextField
                label="Equipment Code"
                value={formValues.equipment_code}
                onChange={(event) => setFormValues((current) => ({ ...current, equipment_code: event.target.value }))}
                required
              />
              <TextField
                label="Equipment Name"
                value={formValues.equipment_name}
                onChange={(event) => setFormValues((current) => ({ ...current, equipment_name: event.target.value }))}
                required
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={formValues.is_active}
                    onChange={(event) => setFormValues((current) => ({ ...current, is_active: event.target.checked }))}
                  />
                }
                label="Active"
              />
            </Stack>
          </Box>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={resetDialog}>Cancel</Button>
          <Button type="submit" form="equipment-form" variant="contained" disabled={submitting}>
            {submitting ? <Skeleton variant="circular" width={20} height={20} /> : selectedEquipment ? 'Save Changes' : 'Create Equipment'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete equipment</DialogTitle>
        <DialogContent>
          <Typography>Are you sure you want to delete {selectedEquipment?.equipment_code || 'this equipment'}?</Typography>
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
