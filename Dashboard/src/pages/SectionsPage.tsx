import {
  Alert,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
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
import { useEffect, useMemo, useRef, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { apiService } from '../services/apiService';
import type { SectionFormValues, SectionItem } from '../types';
import { formatIST } from '../utils/formatDate';

const emptyFormValues: SectionFormValues = {
  name: ''
};

export default function SectionsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const deepLinkHandled = useRef(false);

  const [sections, setSections] = useState<SectionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedSection, setSelectedSection] = useState<SectionItem | null>(null);
  const [formValues, setFormValues] = useState<SectionFormValues>(emptyFormValues);
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success'
  });

  useEffect(() => {
    const timer = window.setTimeout(() => setDebouncedSearch(search.trim()), 300);
    return () => window.clearTimeout(timer);
  }, [search]);

  const loadSections = async (searchOverride?: string) => {
    setLoading(true);

    try {
      const response = await apiService.getSections();
      const source = response.data || [];
      const term = ((searchOverride ?? debouncedSearch) || '').toLowerCase();
      const filtered = source.filter((item) => {
        if (!term) return true;
        return String(item.name || '').toLowerCase().includes(term);
      });
      setSections(filtered);
      setError(null);
    } catch (err) {
      setSections([]);
      setError(getErrorMessage(err, 'Unable to load sections from the backend.'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let mounted = true;

    const fetchSections = async () => {
      if (!mounted) return;
      await loadSections(debouncedSearch);
    };

    fetchSections();

    return () => {
      mounted = false;
    };
  }, [debouncedSearch]);

  // Global Search (Module 28) deep-links here as /sections?id=<id> - once the list has loaded,
  // resolve and open that record's existing edit dialog exactly once.
  useEffect(() => {
    if (deepLinkHandled.current || loading) return;
    const idParam = searchParams.get('id');
    if (!idParam) return;

    const match = sections.find((section) => String(section.id) === idParam);
    if (match) {
      deepLinkHandled.current = true;
      openEditDialog(match);
      searchParams.delete('id');
      setSearchParams(searchParams, { replace: true });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sections, loading, searchParams]);

  const filteredSections = useMemo(() => {
    const startIndex = page * rowsPerPage;
    return sections.slice(startIndex, startIndex + rowsPerPage);
  }, [page, rowsPerPage, sections]);

  const resetDialog = () => {
    setDialogOpen(false);
    setSelectedSection(null);
    setFormValues(emptyFormValues);
    setFormError(null);
  };

  const openCreateDialog = () => {
    setSelectedSection(null);
    setFormValues(emptyFormValues);
    setFormError(null);
    setDialogOpen(true);
  };

  const openEditDialog = (section: SectionItem) => {
    setSelectedSection(section);
    setFormValues({ name: section.name || '' });
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

    if (!formValues.name.trim()) {
      setFormError('Section name is required.');
      return;
    }

    setSubmitting(true);
    setFormError(null);

    try {
      if (selectedSection) {
        await apiService.updateSection(selectedSection.id as number, { name: formValues.name.trim() });
      } else {
        await apiService.createSection({ name: formValues.name.trim() });
      }

      setSnackbar({
        open: true,
        message: selectedSection ? 'Section updated successfully.' : 'Section created successfully.',
        severity: 'success'
      });
      resetDialog();
      await loadSections(search.trim());
    } catch (error) {
      setFormError(getErrorMessage(error, 'The section could not be saved.'));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedSection) return;

    try {
      await apiService.deleteSection(selectedSection.id as number);
      setSnackbar({ open: true, message: 'Section deleted successfully.', severity: 'success' });
      setDeleteDialogOpen(false);
      setSelectedSection(null);
      await loadSections(search.trim());
    } catch (error) {
      setSnackbar({ open: true, message: getErrorMessage(error, 'Unable to delete section.'), severity: 'error' });
    }
  };

  return (
    <Box>
      <Stack spacing={2.5}>
        <Paper sx={{ p: 3, borderRadius: 3 }}>
          <Typography variant="h4" fontWeight={700} mb={1}>Sections</Typography>
          <Typography variant="body1" color="text.secondary">Manage railway operational sections with search, lifecycle actions, and backend-backed updates.</Typography>
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
              { label: 'Total Sections', value: sections.length, color: 'primary' as const },
              { label: 'Visible Sections', value: filteredSections.length, color: 'info' as const },
              { label: 'Search Results', value: sections.length, color: 'success' as const }
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
              placeholder="Search by section name"
              InputProps={{ startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} /> }}
              sx={{ minWidth: { xs: '100%', md: 320 } }}
            />
            <Button variant="contained" startIcon={<Add />} onClick={openCreateDialog}>
              Add Section
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
          ) : sections.length === 0 ? (
            <Box sx={{ p: 5, textAlign: 'center' }}>
              <Typography variant="h6" fontWeight={700} mb={1}>No sections found</Typography>
              <Typography variant="body2" color="text.secondary" mb={2}>Try changing your search or create a new section.</Typography>
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
                      <TableCell>Name</TableCell>
                      <TableCell>Created</TableCell>
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filteredSections.map((section) => (
                      <TableRow key={section.id ?? section.name} hover>
                        <TableCell>{section.id}</TableCell>
                        <TableCell>{section.name}</TableCell>
                        <TableCell>{formatIST(section.created_at as string | undefined)}</TableCell>
                        <TableCell align="right">
                          <Stack direction="row" spacing={1} justifyContent="flex-end">
                            <IconButton size="small" onClick={() => openEditDialog(section)}>
                              <Edit fontSize="small" />
                            </IconButton>
                            <IconButton size="small" color="error" onClick={() => { setSelectedSection(section); setDeleteDialogOpen(true); }}>
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
                count={sections.length}
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
        <DialogTitle>{selectedSection ? 'Edit Section' : 'Add Section'}</DialogTitle>
        <DialogContent>
          <Box component="form" id="section-form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
            <Stack spacing={2.2}>
              {formError ? <Alert severity="error">{formError}</Alert> : null}
              <TextField
                label="Section Name"
                value={formValues.name}
                onChange={(event) => setFormValues((current) => ({ ...current, name: event.target.value }))}
                required
              />
            </Stack>
          </Box>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={resetDialog}>Cancel</Button>
          <Button type="submit" form="section-form" variant="contained" disabled={submitting}>
            {submitting ? <Skeleton variant="circular" width={20} height={20} /> : selectedSection ? 'Save Changes' : 'Create Section'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete section</DialogTitle>
        <DialogContent>
          <Typography>Are you sure you want to delete {selectedSection?.name || 'this section'}?</Typography>
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
