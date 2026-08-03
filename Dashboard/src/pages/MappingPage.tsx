import {
  Alert,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
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
import { Add, Delete, Search } from '@mui/icons-material';
import { useEffect, useMemo, useState, type FormEvent } from 'react';
import { apiService } from '../services/apiService';
import type { EquipmentItem, MappingItem, SectionItem } from '../types';

interface MappingFormValues {
  section_id: number | '';
  equipment_id: number | '';
  technology: string;
}

const emptyFormValues: MappingFormValues = {
  section_id: '',
  equipment_id: '',
  technology: ''
};

export default function MappingPage() {
  const [items, setItems] = useState<MappingItem[]>([]);
  const [sections, setSections] = useState<SectionItem[]>([]);
  const [equipment, setEquipment] = useState<EquipmentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [search, setSearch] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedMapping, setSelectedMapping] = useState<MappingItem | null>(null);
  const [formValues, setFormValues] = useState<MappingFormValues>(emptyFormValues);
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success'
  });

  const getErrorMessage = (error: unknown, fallback: string) => {
    if (typeof error === 'object' && error !== null && 'response' in error) {
      const response = (error as { response?: { data?: { detail?: string } } }).response;
      if (response?.data?.detail) {
        return response.data.detail;
      }
    }

    return fallback;
  };

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [mappingsRes, sectionsRes, equipmentRes] = await Promise.all([
        apiService.getMappings(),
        apiService.getSections(),
        apiService.getEquipment()
      ]);

      setItems(mappingsRes.data || []);
      setSections(sectionsRes.data || []);
      setEquipment(equipmentRes.data || []);
    } catch (err) {
      setItems([]);
      setSections([]);
      setEquipment([]);
      setError(getErrorMessage(err, 'Unable to load section-equipment mapping data from the backend.'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let mounted = true;

    const fetchData = async () => {
      if (!mounted) return;
      await loadData();
    };

    fetchData();

    return () => {
      mounted = false;
    };
  }, []);

  const filteredItems = useMemo(() => {
    const term = search.trim().toLowerCase();

    if (!term) return items;

    return items.filter((item) => {
      const haystack = [
        item.section_name,
        item.equipment_name,
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
    sections: new Set(items.map((item) => item.section_id).filter(Boolean)).size,
    equipment: new Set(items.map((item) => item.equipment_id).filter(Boolean)).size
  }), [items]);

  const resetDialog = () => {
    setDialogOpen(false);
    setSelectedMapping(null);
    setFormValues(emptyFormValues);
    setFormError(null);
  };

  const openCreateDialog = () => {
    setSelectedMapping(null);
    setFormValues(emptyFormValues);
    setFormError(null);
    setDialogOpen(true);
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!formValues.section_id) {
      setFormError('Section is required.');
      return;
    }

    if (!formValues.equipment_id) {
      setFormError('Equipment is required.');
      return;
    }

    if (!formValues.technology.trim()) {
      setFormError('Technology is required.');
      return;
    }

    setSubmitting(true);
    setFormError(null);

    try {
      await apiService.createMapping({
        section_id: Number(formValues.section_id),
        equipment_id: Number(formValues.equipment_id),
        technology: formValues.technology.trim()
      });

      setSnackbar({ open: true, message: 'Mapping created successfully.', severity: 'success' });
      resetDialog();
      setPage(0);
      await loadData();
    } catch (error) {
      setFormError(getErrorMessage(error, 'Unable to create mapping.'));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedMapping?.id) return;

    try {
      await apiService.deleteMapping(selectedMapping.id);
      setSnackbar({ open: true, message: 'Mapping deleted successfully.', severity: 'success' });
      setDeleteDialogOpen(false);
      setSelectedMapping(null);
      await loadData();
    } catch (error) {
      setSnackbar({ open: true, message: getErrorMessage(error, 'Unable to delete mapping.'), severity: 'error' });
    }
  };

  return (
    <Box>
      <Stack spacing={2.5}>
        <Paper sx={{ p: 3, borderRadius: 3 }}>
          <Typography variant="h4" fontWeight={700} mb={1}>Section–Equipment Mapping</Typography>
          <Typography variant="body1" color="text.secondary">
            Create, review, and remove section-to-equipment assignments. Use dropdowns for sections and equipment to prevent invalid entries.
          </Typography>
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
              { label: 'Total Mappings', value: stats.total, color: 'primary' as const },
              { label: 'Active Mappings', value: stats.active, color: 'success' as const },
              { label: 'Mapped Sections', value: stats.sections, color: 'info' as const }
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
              placeholder="Search by section, equipment, or technology"
              InputProps={{ startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} /> }}
              sx={{ minWidth: { xs: '100%', md: 320 } }}
            />
            <Button variant="contained" startIcon={<Add />} onClick={openCreateDialog} disabled={loading || sections.length === 0 || equipment.length === 0}>
              Add Mapping
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
              <Typography variant="h6" fontWeight={700} mb={1}>No mappings found</Typography>
              <Typography variant="body2" color="text.secondary" mb={2}>Try changing your search or create a new mapping.</Typography>
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
                      <TableCell>Section</TableCell>
                      <TableCell>Equipment</TableCell>
                      <TableCell>Technology</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {pagedItems.map((item) => (
                      <TableRow key={item.id ?? `${item.section_id}-${item.equipment_id}`} hover>
                        <TableCell>{item.id}</TableCell>
                        <TableCell>{item.section_name || item.section_id}</TableCell>
                        <TableCell>{item.equipment_name || item.equipment_id}</TableCell>
                        <TableCell>{item.technology}</TableCell>
                        <TableCell>{item.is_active ? 'Active' : 'Inactive'}</TableCell>
                        <TableCell align="right">
                          <Button
                            size="small"
                            color="error"
                            onClick={() => {
                              setSelectedMapping(item);
                              setDeleteDialogOpen(true);
                            }}
                          >
                            <Delete fontSize="small" />
                          </Button>
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
        <DialogTitle>Add Mapping</DialogTitle>
        <DialogContent>
          <Box component="form" id="mapping-form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
            <Stack spacing={2.2}>
              {formError ? <Alert severity="error">{formError}</Alert> : null}
              <FormControl fullWidth>
                <InputLabel id="mapping-section-label">Section</InputLabel>
                <Select
                  labelId="mapping-section-label"
                  id="mapping-section"
                  value={formValues.section_id}
                  label="Section"
                  onChange={(event) => setFormValues((current) => ({ ...current, section_id: event.target.value as number }))}
                >
                  {sections.map((section) => (
                    <MenuItem key={section.id} value={section.id}>
                      {section.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <FormControl fullWidth>
                <InputLabel id="mapping-equipment-label">Equipment</InputLabel>
                <Select
                  labelId="mapping-equipment-label"
                  id="mapping-equipment"
                  value={formValues.equipment_id}
                  label="Equipment"
                  onChange={(event) => {
                    setFormValues((current) => ({ ...current, equipment_id: Number(event.target.value) || '', technology: '' }));
                  }}
                >
                  {equipment.map((item) => (
                    <MenuItem key={item.id} value={item.id}>
                      {item.equipment_name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControl fullWidth>
                <TextField
                  label="Technology"
                  value={formValues.technology}
                  onChange={(event) => setFormValues((current) => ({ ...current, technology: String(event.target.value) }))}
                  placeholder="Enter technology"
                  disabled={!formValues.equipment_id}
                  helperText="Enter the technology name for this mapping."
                />
              </FormControl>
            </Stack>
          </Box>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={resetDialog}>Cancel</Button>
          <Button type="submit" form="mapping-form" variant="contained" disabled={submitting}>
            {submitting ? 'Saving...' : 'Create Mapping'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete mapping</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the mapping for <strong>{selectedMapping?.section_name || selectedMapping?.section_id}</strong> to <strong>{selectedMapping?.equipment_name || selectedMapping?.equipment_id}</strong>?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button color="error" variant="contained" onClick={handleDelete}>
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar((current) => ({ ...current, open: false }))}
        message={snackbar.message}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      />
    </Box>
  );
}
