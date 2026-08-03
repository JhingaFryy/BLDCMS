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
  SelectChangeEvent,
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
import type {
  EquipmentItem,
  SectionItem,
  TemplateCreatePayload,
  TemplateItem,
  TemplateFormValues,
  TemplateUpdatePayload
} from '../types';

const initialFormValues: TemplateFormValues = {
  template_code: '',
  version: 1,
  template_kind: 'equipment',
  equipment_id: '',
  section_id: '',
  technology: '',
  template_name: '',
  description: '',
  is_active: true
};

const defaultTechnologies = ['CONVENTIONAL', '3_PHASE'];

export default function TemplatesPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const deepLinkHandled = useRef(false);

  const [items, setItems] = useState<TemplateItem[]>([]);
  const [equipment, setEquipment] = useState<EquipmentItem[]>([]);
  const [sections, setSections] = useState<SectionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [search, setSearch] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<TemplateItem | null>(null);
  const [formValues, setFormValues] = useState<TemplateFormValues>(initialFormValues);
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success'
  });

  const loadTemplates = async () => {
    setLoading(true);

    try {
      const [templatesResponse, equipmentResponse, sectionsResponse] = await Promise.all([
        apiService.getTemplates(),
        apiService.getEquipment(),
        apiService.getSections()
      ]);

      setItems(templatesResponse.data || []);
      setEquipment(equipmentResponse.data || []);
      setSections(sectionsResponse.data || []);
      setError(null);
    } catch (error) {
      const response = (error as { response?: { data?: { detail?: string; message?: string } } }).response;
      setError(response?.data?.detail || response?.data?.message || 'Unable to load templates from the backend.');
      setItems([]);
      setEquipment([]);
      setSections([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let mounted = true;
    const fetchData = async () => {
      if (!mounted) return;
      await loadTemplates();
    };

    fetchData();

    return () => { mounted = false; };
  }, []);

  // Global Search (Module 28) deep-links here as /templates?id=<id> - once the list has loaded,
  // resolve and open that record's existing edit dialog exactly once.
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

  const equipmentMap = useMemo(
    () => Object.fromEntries(equipment.map((item) => [item.id, item.equipment_name ?? ''])),
    [equipment]
  );

  const sectionMap = useMemo(
    () => Object.fromEntries(sections.map((item) => [item.id, item.name ?? ''])),
    [sections]
  );

  const scopeLabel = (item: TemplateItem) => {
    if (item.equipment_id != null) return equipmentMap[item.equipment_id] || 'Unknown equipment';
    if (item.section_id != null) return `Section Common: ${sectionMap[item.section_id] || 'Unknown section'}`;
    return 'Unassigned';
  };

  const technologyOptions = useMemo(() => {
    const unique = Array.from(new Set(items.map((item) => item.technology).filter(Boolean) as string[]));
    return unique.length ? unique : defaultTechnologies;
  }, [items]);

  const filteredItems = useMemo(() => {
    const term = search.trim().toLowerCase();
    if (!term) return items;

    return items.filter((item) => {
      const haystack = [
        item.template_code,
        item.template_name,
        item.technology,
        item.is_active ? 'active' : 'inactive',
        scopeLabel(item)
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase();

      return haystack.includes(term);
    });
  }, [items, search, equipmentMap, sectionMap]);

  const pagedItems = useMemo(() => {
    const startIndex = page * rowsPerPage;
    return filteredItems.slice(startIndex, startIndex + rowsPerPage);
  }, [filteredItems, page, rowsPerPage]);

  const stats = useMemo(
    () => ({
      total: items.length,
      active: items.filter((item) => item.is_active).length,
      inactive: items.filter((item) => !item.is_active).length
    }),
    [items]
  );

  const resetDialog = () => {
    setDialogOpen(false);
    setSelectedTemplate(null);
    setFormValues(initialFormValues);
    setFormError(null);
  };

  const openCreateDialog = () => {
    setSelectedTemplate(null);
    setFormValues(initialFormValues);
    setFormError(null);
    setDialogOpen(true);
  };

  const openEditDialog = (template: TemplateItem) => {
    setSelectedTemplate(template);
    setFormValues({
      template_code: template.template_code ?? '',
      version: template.version ?? 1,
      template_kind: template.equipment_id == null && template.section_id != null ? 'common' : 'equipment',
      equipment_id: template.equipment_id ?? '',
      section_id: template.section_id ?? '',
      technology: template.technology ?? '',
      template_name: template.template_name ?? '',
      description: template.description ?? '',
      is_active: template.is_active ?? true
    });
    setFormError(null);
    setDialogOpen(true);
  };

  const getErrorMessage = (error: unknown, fallback: string) => {
    if (typeof error === 'object' && error !== null && 'response' in error) {
      const response = (error as { response?: { data?: { detail?: string; message?: string } } }).response;
      if (response?.data?.detail) return response.data.detail;
      if (response?.data?.message) return response.data.message;
    }
    return fallback;
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!formValues.template_code.trim()) {
      setFormError('Template code is required.');
      return;
    }

    if (!(formValues.version > 0)) {
      setFormError('Version must be a positive number.');
      return;
    }

    if (formValues.template_kind === 'equipment' && !formValues.equipment_id) {
      setFormError('Equipment selection is required.');
      return;
    }

    if (formValues.template_kind === 'common' && !formValues.section_id) {
      setFormError('Section selection is required for a section-wide common page template.');
      return;
    }

    if (!formValues.technology.trim()) {
      setFormError('Technology is required.');
      return;
    }

    if (!formValues.template_name.trim()) {
      setFormError('Template name is required.');
      return;
    }

    setSubmitting(true);
    setFormError(null);

    try {
      const payload: TemplateCreatePayload | TemplateUpdatePayload = {
        template_code: formValues.template_code.trim(),
        version: Number(formValues.version),
        technology: formValues.technology.trim(),
        template_name: formValues.template_name.trim(),
        description: formValues.description.trim() || undefined,
        ...(formValues.template_kind === 'equipment'
          ? { equipment_id: Number(formValues.equipment_id) }
          : { section_id: Number(formValues.section_id) })
      };

      if (selectedTemplate) {
        await apiService.updateTemplate(selectedTemplate.id as number, {
          ...payload,
          is_active: formValues.is_active
        });
        setSnackbar({ open: true, message: 'Template updated successfully.', severity: 'success' });
      } else {
        const createResponse = await apiService.createTemplate(payload as TemplateCreatePayload);
        if (!formValues.is_active) {
          await apiService.updateTemplate(createResponse.data.id as number, { is_active: false });
        }
        setSnackbar({ open: true, message: 'Template created successfully.', severity: 'success' });
      }

      resetDialog();
      await loadTemplates();
    } catch (error) {
      setFormError(getErrorMessage(error, 'Unable to save template.'));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedTemplate?.id) return;

    try {
      await apiService.deleteTemplate(selectedTemplate.id);
      setSnackbar({ open: true, message: 'Template deleted successfully.', severity: 'success' });
      setDeleteDialogOpen(false);
      setSelectedTemplate(null);
      await loadTemplates();
    } catch (error) {
      setSnackbar({ open: true, message: getErrorMessage(error, 'Unable to delete template.'), severity: 'error' });
    }
  };

  return (
    <Box>
      <Stack spacing={2.5}>
        <Paper sx={{ p: 3, borderRadius: 3 }}>
          <Typography variant="h4" fontWeight={700} mb={1}>Templates</Typography>
          <Typography variant="body1" color="text.secondary">Manage templates with equipment mapping, versioning, and backend-powered operations.</Typography>
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
              { label: 'Total Templates', value: stats.total, color: 'primary' as const },
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
              onChange={(event) => { setSearch(event.target.value); setPage(0); }}
              placeholder="Search by code, name, equipment, or technology"
              InputProps={{ startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} /> }}
              sx={{ minWidth: { xs: '100%', md: 360 } }}
            />
            <Button variant="contained" startIcon={<Add />} onClick={openCreateDialog}>
              Add Template
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
              <Typography variant="h6" fontWeight={700} mb={1}>No templates found</Typography>
              <Typography variant="body2" color="text.secondary" mb={2}>Adjust your search or create a new template to get started.</Typography>
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
                      <TableCell>Template Code</TableCell>
                      <TableCell>Version</TableCell>
                      <TableCell>Template Name</TableCell>
                      <TableCell>Scope</TableCell>
                      <TableCell>Technology</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {pagedItems.map((item) => (
                      <TableRow key={item.id ?? item.template_code} hover>
                        <TableCell>{item.template_code}</TableCell>
                        <TableCell>{item.version}</TableCell>
                        <TableCell>{item.template_name}</TableCell>
                        <TableCell>{scopeLabel(item)}</TableCell>
                        <TableCell>{item.technology}</TableCell>
                        <TableCell>
                          <Chip label={item.is_active ? 'Active' : 'Inactive'} color={item.is_active ? 'success' : 'default'} />
                        </TableCell>
                        <TableCell align="right">
                          <Stack direction="row" spacing={1} justifyContent="flex-end">
                            <IconButton size="small" onClick={() => openEditDialog(item)}>
                              <Edit fontSize="small" />
                            </IconButton>
                            <IconButton size="small" color="error" onClick={() => { setSelectedTemplate(item); setDeleteDialogOpen(true); }}>
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
                onRowsPerPageChange={(event) => { setRowsPerPage(parseInt(event.target.value, 10)); setPage(0); }}
                rowsPerPageOptions={[5, 10, 25]}
              />
            </>
          )}
        </Paper>
      </Stack>

      <Dialog open={dialogOpen} onClose={resetDialog} maxWidth="sm" fullWidth>
        <DialogTitle>{selectedTemplate ? 'Edit Template' : 'Add Template'}</DialogTitle>
        <DialogContent>
          <Box component="form" id="template-form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
            <Stack spacing={2.2}>
              {formError ? <Alert severity="error">{formError}</Alert> : null}
              <TextField
                label="Template Code"
                value={formValues.template_code}
                onChange={(event) => setFormValues((current) => ({ ...current, template_code: event.target.value }))}
                required
              />
              <TextField
                label="Version"
                type="number"
                value={formValues.version}
                onChange={(event) => setFormValues((current) => ({ ...current, version: Number(event.target.value) }))}
                required
              />
              <FormControl required>
                <InputLabel id="template-kind-label">Template Type</InputLabel>
                <Select
                  labelId="template-kind-label"
                  value={formValues.template_kind}
                  label="Template Type"
                  onChange={(event: SelectChangeEvent<string>) => {
                    const kind = event.target.value as 'equipment' | 'common';
                    setFormValues((current) => ({ ...current, template_kind: kind }));
                  }}
                >
                  <MenuItem value="equipment">Equipment-specific</MenuItem>
                  <MenuItem value="common">Section-wide common page</MenuItem>
                </Select>
              </FormControl>
              {formValues.template_kind === 'equipment' ? (
                <FormControl required>
                  <InputLabel id="equipment-select-label">Equipment</InputLabel>
                  <Select
                    labelId="equipment-select-label"
                    value={formValues.equipment_id.toString()}
                    label="Equipment"
                    onChange={(event: SelectChangeEvent<string>) => {
                      const value = Number(event.target.value);
                      setFormValues((current) => ({ ...current, equipment_id: Number.isNaN(value) ? '' : value }));
                    }}
                  >
                    <MenuItem value="">Select equipment</MenuItem>
                    {equipment.map((item) => (
                      <MenuItem key={item.id} value={item.id ?? ''}>
                        {item.equipment_name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              ) : (
                <FormControl required>
                  <InputLabel id="section-select-label">Section</InputLabel>
                  <Select
                    labelId="section-select-label"
                    value={formValues.section_id.toString()}
                    label="Section"
                    onChange={(event: SelectChangeEvent<string>) => {
                      const value = Number(event.target.value);
                      setFormValues((current) => ({ ...current, section_id: Number.isNaN(value) ? '' : value }));
                    }}
                  >
                    <MenuItem value="">Select section</MenuItem>
                    {sections.map((item) => (
                      <MenuItem key={item.id} value={item.id ?? ''}>
                        {item.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              )}
              <FormControl required>
                <InputLabel id="technology-select-label">Technology</InputLabel>
                <Select
                  labelId="technology-select-label"
                  value={formValues.technology}
                  label="Technology"
                  onChange={(event: SelectChangeEvent<string>) => setFormValues((current) => ({ ...current, technology: event.target.value }))}
                >
                  <MenuItem value="">Select technology</MenuItem>
                  {technologyOptions.map((technology) => (
                    <MenuItem key={technology} value={technology}>
                      {technology}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <TextField
                label="Template Name"
                value={formValues.template_name}
                onChange={(event) => setFormValues((current) => ({ ...current, template_name: event.target.value }))}
                required
              />
              <TextField
                label="Description"
                multiline
                minRows={3}
                value={formValues.description}
                onChange={(event) => setFormValues((current) => ({ ...current, description: event.target.value }))}
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
          <Button onClick={resetDialog} disabled={submitting}>Cancel</Button>
          <Button type="submit" form="template-form" variant="contained" disabled={submitting}>
            {selectedTemplate ? 'Save Changes' : 'Create Template'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete template</DialogTitle>
        <DialogContent>
          <Typography>Are you sure you want to delete <strong>{selectedTemplate?.template_code || 'this template'}</strong>?</Typography>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={() => setDeleteDialogOpen(false)} disabled={submitting}>Cancel</Button>
          <Button color="error" variant="contained" onClick={handleDelete} disabled={submitting}>
            Delete
          </Button>
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
