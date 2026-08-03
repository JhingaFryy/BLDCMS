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
  FormControl,
  FormControlLabel,
  IconButton,
  InputLabel,
  MenuItem,
  Paper,
  Select,
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
import type { LocomotiveFormValues, LocomotiveItem } from '../types';

const modelOptions = ['WAP-4', 'WAP-5', 'WAP-7', 'WAG9HC'];

const emptyFormValues: LocomotiveFormValues = {
  loco_number: '',
  loco_model: 'WAP-4',
  is_active: true
};

export default function LocomotivesPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const deepLinkHandled = useRef(false);

  const [items, setItems] = useState<LocomotiveItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [search, setSearch] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedLocomotive, setSelectedLocomotive] = useState<LocomotiveItem | null>(null);
  const [formValues, setFormValues] = useState<LocomotiveFormValues>(emptyFormValues);
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success'
  });

  const loadLocomotives = async () => {
    setLoading(true);

    try {
      const response = await apiService.getLocomotives();
      setItems(response.data || []);
      setError(null);
    } catch (err) {
      setItems([]);
      const response = (err as { response?: { data?: { detail?: string } } }).response;
      setError(response?.data?.detail || 'Unable to load locomotives from the backend.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let mounted = true;

    const fetchLocomotives = async () => {
      if (!mounted) return;
      await loadLocomotives();
    };

    fetchLocomotives();

    return () => {
      mounted = false;
    };
  }, []);

  // Global Search (Module 28) deep-links here as /locomotives?id=<id> - once the full list has
  // loaded, resolve and open that record's existing edit dialog exactly once, then drop the
  // param so it doesn't re-trigger on subsequent state changes (e.g. after editing the record).
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
      const haystack = [
        item.loco_number,
        item.loco_model,
        item.technology,
        item.is_active ? 'active' : 'inactive'
      ]
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
    models: new Set(items.map((item) => item.loco_model).filter(Boolean)).size,
    technologies: new Set(items.map((item) => item.technology).filter(Boolean)).size
  }), [items]);

  const resetDialog = () => {
    setDialogOpen(false);
    setSelectedLocomotive(null);
    setFormValues(emptyFormValues);
    setFormError(null);
  };

  const openCreateDialog = () => {
    setSelectedLocomotive(null);
    setFormValues(emptyFormValues);
    setFormError(null);
    setDialogOpen(true);
  };

  const openEditDialog = (locomotive: LocomotiveItem) => {
    setSelectedLocomotive(locomotive);
    setFormValues({
      loco_number: locomotive.loco_number || '',
      loco_model: locomotive.loco_model || 'WAP-4',
      is_active: locomotive.is_active ?? true
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

    if (!formValues.loco_number.trim()) {
      setFormError('Locomotive number is required.');
      return;
    }

    if (!formValues.loco_model.trim()) {
      setFormError('Locomotive model is required.');
      return;
    }

    setSubmitting(true);
    setFormError(null);

    try {
      if (selectedLocomotive) {
        await apiService.updateLocomotive(selectedLocomotive.id as number, {
          loco_number: formValues.loco_number.trim(),
          loco_model: formValues.loco_model.trim(),
          is_active: formValues.is_active
        });
      } else {
        await apiService.createLocomotive({
          loco_number: formValues.loco_number.trim(),
          loco_model: formValues.loco_model.trim()
        });
      }

      setSnackbar({
        open: true,
        message: selectedLocomotive ? 'Locomotive updated successfully.' : 'Locomotive created successfully.',
        severity: 'success'
      });
      resetDialog();
      await loadLocomotives();
    } catch (error) {
      setFormError(getErrorMessage(error, 'The locomotive could not be saved.'));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedLocomotive) return;

    try {
      await apiService.deleteLocomotive(selectedLocomotive.id as number);
      setSnackbar({ open: true, message: 'Locomotive deleted successfully.', severity: 'success' });
      setDeleteDialogOpen(false);
      setSelectedLocomotive(null);
      await loadLocomotives();
    } catch (error) {
      setSnackbar({ open: true, message: getErrorMessage(error, 'Unable to delete locomotive.'), severity: 'error' });
    }
  };

  return (
    <Box>
      <Stack spacing={2.5}>
        <Paper sx={{ p: 3, borderRadius: 3 }}>
          <Typography variant="h4" fontWeight={700} mb={1}>Locomotives</Typography>
          <Typography variant="body1" color="text.secondary">Manage the fleet with search, lifecycle actions, and backend-backed updates.</Typography>
        </Paper>

        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
          {loading ? (
            Array.from({ length: 4 }).map((_, index) => (
              <Paper key={index} sx={{ flex: 1, p: 2.5, borderRadius: 3 }}>
                <Skeleton variant="text" width="40%" />
                <Skeleton variant="text" width="70%" sx={{ mt: 1 }} />
              </Paper>
            ))
          ) : (
            [
              { label: 'Total Locomotives', value: stats.total, color: 'primary' as const },
              { label: 'Active', value: stats.active, color: 'success' as const },
              { label: 'Models', value: stats.models, color: 'info' as const },
              { label: 'Technologies', value: stats.technologies, color: 'warning' as const }
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
              placeholder="Search by number, model or technology"
              InputProps={{ startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} /> }}
              sx={{ minWidth: { xs: '100%', md: 320 } }}
            />
            <Button variant="contained" startIcon={<Add />} onClick={openCreateDialog}>
              Add Locomotive
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
              <Typography variant="h6" fontWeight={700} mb={1}>No locomotives found</Typography>
              <Typography variant="body2" color="text.secondary" mb={2}>Try changing your search or create a new locomotive.</Typography>
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
                      <TableCell>Number</TableCell>
                      <TableCell>Model</TableCell>
                      <TableCell>Technology</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {pagedItems.map((item) => (
                      <TableRow key={item.id ?? item.loco_number} hover>
                        <TableCell>{item.id}</TableCell>
                        <TableCell>{item.loco_number}</TableCell>
                        <TableCell>{item.loco_model}</TableCell>
                        <TableCell>{item.technology}</TableCell>
                        <TableCell>
                          <Chip label={item.is_active ? 'Active' : 'Inactive'} color={item.is_active ? 'success' : 'default'} />
                        </TableCell>
                        <TableCell align="right">
                          <Stack direction="row" spacing={1} justifyContent="flex-end">
                            <IconButton size="small" onClick={() => openEditDialog(item)}>
                              <Edit fontSize="small" />
                            </IconButton>
                            <IconButton size="small" color="error" onClick={() => { setSelectedLocomotive(item); setDeleteDialogOpen(true); }}>
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
        <DialogTitle>{selectedLocomotive ? 'Edit Locomotive' : 'Add Locomotive'}</DialogTitle>
        <DialogContent>
          <Box component="form" id="locomotive-form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
            <Stack spacing={2.2}>
              {formError ? <Alert severity="error">{formError}</Alert> : null}
              <TextField
                label="Locomotive Number"
                value={formValues.loco_number}
                onChange={(event) => setFormValues((current) => ({ ...current, loco_number: event.target.value }))}
                required
              />
              <FormControl fullWidth>
                <InputLabel>Locomotive Model</InputLabel>
                <Select
                  value={formValues.loco_model}
                  label="Locomotive Model"
                  onChange={(event) => setFormValues((current) => ({ ...current, loco_model: event.target.value }))}
                >
                  {modelOptions.map((model) => (
                    <MenuItem key={model} value={model}>{model}</MenuItem>
                  ))}
                </Select>
              </FormControl>
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
          <Button type="submit" form="locomotive-form" variant="contained" disabled={submitting}>
            {submitting ? <Skeleton variant="circular" width={20} height={20} /> : selectedLocomotive ? 'Save Changes' : 'Create Locomotive'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete locomotive</DialogTitle>
        <DialogContent>
          <Typography>Are you sure you want to delete {selectedLocomotive?.loco_number || 'this locomotive'}?</Typography>
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
