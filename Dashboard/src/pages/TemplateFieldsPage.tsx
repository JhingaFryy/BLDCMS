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
import { useEffect, useMemo, useState, type FormEvent } from 'react';
import { apiService } from '../services/apiService';
import type {
  TemplateFieldCreatePayload,
  TemplateFieldItem,
  TemplateFieldFormValues,
  TemplateFieldUpdatePayload,
  TemplateItem
} from '../types';

const fieldTypes = [
  'text',
  'textarea',
  'number',
  'numeric_range',
  'group',
  'boolean',
  'select',
  'radio',
  'checkbox',
  'date',
  'datetime'
] as const;

const emptyFormValues: TemplateFieldFormValues = {
  template_id: '',
  display_order: 1,
  field_label: '',
  field_key: '',
  field_type: 'text',
  required: true,
  unit: '',
  default_value: '',
  options: '',
  help_text: '',
  is_active: true,
  min_value: '',
  max_value: '',
  decimal_precision: '',
  standard_value: '',
  authority_reference: '',
  parent_field_id: '',
  page_number: 1
};

export default function TemplateFieldsPage() {
  const [items, setItems] = useState<TemplateFieldItem[]>([]);
  const [templates, setTemplates] = useState<TemplateItem[]>([]);
  const [selectedTemplateId, setSelectedTemplateId] = useState<number | ''>('');
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [search, setSearch] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedField, setSelectedField] = useState<TemplateFieldItem | null>(null);
  const [formValues, setFormValues] = useState<TemplateFieldFormValues>(emptyFormValues);
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
      const response = await apiService.getTemplates();
      const payload = response.data || [];
      setTemplates(payload);
      if (selectedTemplateId === '' && payload.length > 0) {
        setSelectedTemplateId(payload[0].id ?? '');
      }
      setError(null);
    } catch (err) {
      const response = (err as { response?: { data?: { detail?: string; message?: string } } }).response;
      setError(response?.data?.detail || response?.data?.message || 'Unable to load templates from the backend.');
      setTemplates([]);
    } finally {
      setLoading(false);
    }
  };

  const loadFields = async (templateId: number) => {
    setLoading(true);
    try {
      const response = await apiService.getTemplateFields(templateId);
      setItems(response.data || []);
      setError(null);
    } catch (err) {
      const response = (err as { response?: { data?: { detail?: string; message?: string } } }).response;
      setError(response?.data?.detail || response?.data?.message || 'Unable to load template fields from the backend.');
      setItems([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let mounted = true;
    const fetchTemplates = async () => {
      if (!mounted) return;
      await loadTemplates();
    };
    fetchTemplates();
    return () => { mounted = false; };
  }, []);

  useEffect(() => {
    if (selectedTemplateId === '') {
      setItems([]);
      return;
    }
    loadFields(selectedTemplateId);
  }, [selectedTemplateId]);

  const templateOptions = useMemo(
    () => templates.map((template) => ({
      id: template.id,
      label: template.template_name || template.template_code || `Template ${template.id}`
    })),
    [templates]
  );

  const filteredItems = useMemo(() => {
    const term = search.trim().toLowerCase();
    if (!term) return items;

    return items.filter((item) => {
      const haystack = [
        item.display_order?.toString(),
        item.field_label,
        item.field_key,
        item.field_type,
        item.unit,
        item.default_value,
        item.options,
        item.help_text,
        item.required ? 'required' : 'optional',
        item.is_active ? 'active' : 'inactive',
        item.standard_value,
        item.authority_reference,
        item.page_number != null ? `page ${item.page_number}` : undefined
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

  const stats = useMemo(
    () => ({
      total: items.length,
      required: items.filter((item) => item.required).length,
      optional: items.filter((item) => !item.required).length
    }),
    [items]
  );

  const resetDialog = () => {
    setDialogOpen(false);
    setSelectedField(null);
    setFormValues((current) => ({
      ...emptyFormValues,
      template_id: selectedTemplateId || ''
    }));
    setFormError(null);
  };

  const openCreateDialog = () => {
    setSelectedField(null);
    setFormValues({
      ...emptyFormValues,
      template_id: selectedTemplateId || ''
    });
    setFormError(null);
    setDialogOpen(true);
  };

  const openEditDialog = (field: TemplateFieldItem) => {
    setSelectedField(field);
    setFormValues({
      template_id: (field.template_id ?? selectedTemplateId) || '',
      display_order: field.display_order ?? 1,
      field_label: field.field_label ?? '',
      field_key: field.field_key ?? '',
      field_type: field.field_type ?? 'text',
      required: field.required ?? true,
      unit: field.unit ?? '',
      default_value: field.default_value ?? '',
      options: field.options ?? '',
      help_text: field.help_text ?? '',
      is_active: field.is_active ?? true,
      min_value: field.min_value != null ? String(field.min_value) : '',
      max_value: field.max_value != null ? String(field.max_value) : '',
      decimal_precision: field.decimal_precision != null ? String(field.decimal_precision) : '',
      standard_value: field.standard_value ?? '',
      authority_reference: field.authority_reference ?? '',
      parent_field_id: field.parent_field_id ?? '',
      page_number: field.page_number ?? 1
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

  const validateDisplayOrder = async (templateId: number, displayOrder: number, ignoreId?: number) => {
    const fields = templateId === selectedTemplateId ? items : (await apiService.getTemplateFields(templateId)).data || [];
    return fields.some((field) => field.display_order === displayOrder && field.id !== ignoreId);
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const templateId = Number(formValues.template_id);
    if (!templateId) {
      setFormError('Template selection is required.');
      return;
    }
    if (!(formValues.display_order > 0)) {
      setFormError('Display order must be a positive number.');
      return;
    }
    if (!formValues.field_label.trim()) {
      setFormError('Field label is required.');
      return;
    }
    if (!formValues.field_key.trim()) {
      setFormError('Field key is required.');
      return;
    }
    if (!formValues.field_type.trim()) {
      setFormError('Field type is required.');
      return;
    }
    if ((formValues.field_type === 'select' || formValues.field_type === 'radio') && !formValues.options.trim()) {
      setFormError('Options are required for select and radio fields.');
      return;
    }
    if (formValues.field_type === 'numeric_range') {
      const min = formValues.min_value.trim() ? Number(formValues.min_value) : null;
      const max = formValues.max_value.trim() ? Number(formValues.max_value) : null;
      if (formValues.min_value.trim() && Number.isNaN(min)) {
        setFormError('Minimum value must be a valid number.');
        return;
      }
      if (formValues.max_value.trim() && Number.isNaN(max)) {
        setFormError('Maximum value must be a valid number.');
        return;
      }
      if (min != null && max != null && min > max) {
        setFormError('Minimum value cannot be greater than maximum value.');
        return;
      }
    }

    setSubmitting(true);
    setFormError(null);

    try {
      const hasDuplicate = await validateDisplayOrder(templateId, formValues.display_order, selectedField?.id);
      if (hasDuplicate) {
        setFormError('Display order already exists for this template.');
        setSubmitting(false);
        return;
      }

      const payload: TemplateFieldCreatePayload | TemplateFieldUpdatePayload = {
        template_id: templateId,
        display_order: Number(formValues.display_order),
        field_label: formValues.field_label.trim(),
        field_key: formValues.field_key.trim(),
        field_type: formValues.field_type,
        required: formValues.required,
        unit: formValues.unit.trim() || undefined,
        default_value: formValues.default_value.trim() || undefined,
        options: formValues.options.trim() || undefined,
        help_text: formValues.help_text.trim() || undefined,
        min_value: formValues.min_value.trim() ? Number(formValues.min_value) : undefined,
        max_value: formValues.max_value.trim() ? Number(formValues.max_value) : undefined,
        decimal_precision: formValues.decimal_precision.trim() ? Number(formValues.decimal_precision) : undefined,
        standard_value: formValues.standard_value.trim() || undefined,
        authority_reference: formValues.authority_reference.trim() || undefined,
        parent_field_id: formValues.parent_field_id ? Number(formValues.parent_field_id) : undefined,
        page_number: Number(formValues.page_number) || 1
      };

      let targetTemplateId = templateId;
      if (selectedField) {
        await apiService.updateTemplateField(selectedField.id as number, {
          ...payload,
          is_active: formValues.is_active
        });
        setSnackbar({ open: true, message: 'Field updated successfully.', severity: 'success' });
      } else {
        const response = await apiService.createTemplateField(payload as TemplateFieldCreatePayload);
        if (!formValues.is_active) {
          await apiService.updateTemplateField(response.data.id as number, { is_active: false });
        }
        setSnackbar({ open: true, message: 'Field created successfully.', severity: 'success' });
      }

      resetDialog();
      setSelectedTemplateId(targetTemplateId);
      await loadFields(targetTemplateId);
    } catch (error) {
      setFormError(getErrorMessage(error, 'Unable to save field.'));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedField?.id) return;

    try {
      // The backend archives (rather than hard-deletes) a field still referenced by historical
      // checksheet_value rows, and returns a user-friendly message explaining that outcome instead
      // of a raw ForeignKeyViolation - surface it as-is rather than assuming "deleted" every time.
      const response = await apiService.deleteTemplateField(selectedField.id);
      setSnackbar({
        open: true,
        message: response.data?.message ?? 'Field deleted successfully.',
        severity: 'success'
      });
      setDeleteDialogOpen(false);
      setSelectedField(null);
      if (selectedTemplateId !== '') {
        await loadFields(selectedTemplateId);
      }
    } catch (error) {
      setSnackbar({ open: true, message: getErrorMessage(error, 'Unable to delete field.'), severity: 'error' });
    }
  };

  return (
    <Box>
      <Stack spacing={2.5}>
        <Paper sx={{ p: 3, borderRadius: 3 }}>
          <Typography variant="h4" fontWeight={700} mb={1}>Template Fields</Typography>
          <Typography variant="body1" color="text.secondary">Manage template field definitions with backend CRUD, filtering, and field-level metadata.</Typography>
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
              { label: 'Total Fields', value: stats.total, color: 'primary' as const },
              { label: 'Required Fields', value: stats.required, color: 'success' as const },
              { label: 'Optional Fields', value: stats.optional, color: 'warning' as const }
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
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ width: '100%' }}>
              <FormControl sx={{ minWidth: 220 }}>
                <InputLabel id="template-filter-label">Template</InputLabel>
                <Select
                  labelId="template-filter-label"
                  value={selectedTemplateId.toString()}
                  label="Template"
                  onChange={(event: SelectChangeEvent<string>) => {
                    const value = Number(event.target.value);
                    setSelectedTemplateId(Number.isNaN(value) ? '' : value);
                    setPage(0);
                  }}
                >
                  {templateOptions.map((template) => (
                    <MenuItem key={template.id} value={template.id}>{template.label}</MenuItem>
                  ))}
                </Select>
              </FormControl>
              <TextField
                value={search}
                onChange={(event) => { setSearch(event.target.value); setPage(0); }}
                placeholder="Search fields"
                InputProps={{ startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} /> }}
                sx={{ width: '100%' }}
              />
            </Stack>
            <Button variant="contained" startIcon={<Add />} onClick={openCreateDialog} disabled={templates.length === 0}>
              Add Field
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
              <Typography variant="h6" fontWeight={700} mb={1}>No fields found</Typography>
              <Typography variant="body2" color="text.secondary" mb={2}>Select a template or adjust your search to view fields.</Typography>
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
                      <TableCell>Page</TableCell>
                      <TableCell>Display Order</TableCell>
                      <TableCell>Field Label</TableCell>
                      <TableCell>Field Key</TableCell>
                      <TableCell>Field Type</TableCell>
                      <TableCell>Required</TableCell>
                      <TableCell>Unit</TableCell>
                      <TableCell>Default Value</TableCell>
                      <TableCell>Active</TableCell>
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {pagedItems.map((item) => (
                      <TableRow key={item.id ?? item.field_key} hover>
                        <TableCell>{item.page_number ?? 1}</TableCell>
                        <TableCell>{item.display_order}</TableCell>
                        <TableCell>{item.field_label}</TableCell>
                        <TableCell>{item.field_key}</TableCell>
                        <TableCell>{item.field_type}</TableCell>
                        <TableCell>{item.required ? 'Yes' : 'No'}</TableCell>
                        <TableCell>{item.unit || '—'}</TableCell>
                        <TableCell>{item.default_value || '—'}</TableCell>
                        <TableCell>
                          <Chip label={item.is_active ? 'Active' : 'Inactive'} color={item.is_active ? 'success' : 'default'} />
                        </TableCell>
                        <TableCell align="right">
                          <Stack direction="row" spacing={1} justifyContent="flex-end">
                            <IconButton size="small" onClick={() => openEditDialog(item)}>
                              <Edit fontSize="small" />
                            </IconButton>
                            <IconButton size="small" color="error" onClick={() => { setSelectedField(item); setDeleteDialogOpen(true); }}>
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
        <DialogTitle>{selectedField ? 'Edit Field' : 'Add Field'}</DialogTitle>
        <DialogContent>
          <Box component="form" id="template-field-form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
            <Stack spacing={2.2}>
              {formError ? <Alert severity="error">{formError}</Alert> : null}
              <FormControl fullWidth required>
                <InputLabel id="field-template-label">Template</InputLabel>
                <Select
                  labelId="field-template-label"
                  value={formValues.template_id.toString()}
                  label="Template"
                  onChange={(event: SelectChangeEvent<string>) => {
                    const value = Number(event.target.value);
                    setFormValues((current) => ({ ...current, template_id: Number.isNaN(value) ? '' : value }));
                  }}
                >
                  {templateOptions.map((template) => (
                    <MenuItem key={template.id} value={template.id}>{template.label}</MenuItem>
                  ))}
                </Select>
              </FormControl>
              <TextField
                label="Display Order"
                type="number"
                value={formValues.display_order}
                onChange={(event) => setFormValues((current) => ({ ...current, display_order: Number(event.target.value) }))}
                required
                fullWidth
              />
              <TextField
                label="Page Number"
                type="number"
                value={formValues.page_number}
                onChange={(event) => setFormValues((current) => ({ ...current, page_number: Number(event.target.value) }))}
                helperText="Which page of the template this field appears on."
                required
                fullWidth
              />
              <TextField
                label="Field Label"
                value={formValues.field_label}
                onChange={(event) => setFormValues((current) => ({ ...current, field_label: event.target.value }))}
                required
                fullWidth
              />
              <TextField
                label="Field Key"
                value={formValues.field_key}
                onChange={(event) => setFormValues((current) => ({ ...current, field_key: event.target.value }))}
                required
                fullWidth
              />
              <FormControl fullWidth required>
                <InputLabel id="field-type-label">Field Type</InputLabel>
                <Select
                  labelId="field-type-label"
                  value={formValues.field_type}
                  label="Field Type"
                  onChange={(event: SelectChangeEvent<string>) => setFormValues((current) => ({ ...current, field_type: event.target.value }))}
                >
                  {fieldTypes.map((type) => (
                    <MenuItem key={type} value={type}>{type}</MenuItem>
                  ))}
                </Select>
              </FormControl>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={formValues.required}
                    onChange={(event) => setFormValues((current) => ({ ...current, required: event.target.checked }))}
                  />
                }
                label="Required"
              />
              <TextField
                label="Unit"
                value={formValues.unit}
                onChange={(event) => setFormValues((current) => ({ ...current, unit: event.target.value }))}
                fullWidth
              />
              <TextField
                label="Default Value"
                value={formValues.default_value}
                onChange={(event) => setFormValues((current) => ({ ...current, default_value: event.target.value }))}
                fullWidth
              />
              <TextField
                label="Options"
                value={formValues.options}
                onChange={(event) => setFormValues((current) => ({ ...current, options: event.target.value }))}
                fullWidth
                multiline
                minRows={2}
                disabled={formValues.field_type !== 'select' && formValues.field_type !== 'radio'}
                helperText={formValues.field_type === 'select' || formValues.field_type === 'radio' ? 'Enter comma-separated options.' : 'Options are only available for select and radio fields.'}
              />
              {formValues.field_type === 'numeric_range' ? (
                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                  <TextField
                    label="Minimum Value"
                    type="number"
                    value={formValues.min_value}
                    onChange={(event) => setFormValues((current) => ({ ...current, min_value: event.target.value }))}
                    fullWidth
                  />
                  <TextField
                    label="Maximum Value"
                    type="number"
                    value={formValues.max_value}
                    onChange={(event) => setFormValues((current) => ({ ...current, max_value: event.target.value }))}
                    fullWidth
                  />
                  <TextField
                    label="Decimal Precision"
                    type="number"
                    value={formValues.decimal_precision}
                    onChange={(event) => setFormValues((current) => ({ ...current, decimal_precision: event.target.value }))}
                    fullWidth
                  />
                </Stack>
              ) : null}
              <TextField
                label="Standard"
                value={formValues.standard_value}
                onChange={(event) => setFormValues((current) => ({ ...current, standard_value: event.target.value }))}
                fullWidth
                helperText="The prescribed/expected value shown as a read-only reference column, e.g. 'Normal', '1 - 1000 MOhm'."
              />
              <TextField
                label="Authority"
                value={formValues.authority_reference}
                onChange={(event) => setFormValues((current) => ({ ...current, authority_reference: event.target.value }))}
                fullWidth
                helperText="The manual/standard clause this check is drawn from."
              />
              <FormControl fullWidth>
                <InputLabel id="parent-field-label">Parent Group</InputLabel>
                <Select
                  labelId="parent-field-label"
                  value={formValues.parent_field_id.toString()}
                  label="Parent Group"
                  onChange={(event: SelectChangeEvent<string>) => {
                    const value = Number(event.target.value);
                    setFormValues((current) => ({ ...current, parent_field_id: Number.isNaN(value) ? '' : value }));
                  }}
                >
                  <MenuItem value="">No parent (top-level field)</MenuItem>
                  {items
                    .filter((candidate) => candidate.field_type === 'group' && candidate.id !== selectedField?.id)
                    .map((candidate) => (
                      <MenuItem key={candidate.id} value={candidate.id ?? ''}>
                        {candidate.field_label}
                      </MenuItem>
                    ))}
                </Select>
              </FormControl>
              <TextField
                label="Help Text"
                value={formValues.help_text}
                onChange={(event) => setFormValues((current) => ({ ...current, help_text: event.target.value }))}
                fullWidth
                multiline
                minRows={2}
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
          <Button type="submit" form="template-field-form" variant="contained" disabled={submitting}>
            {selectedField ? 'Save Changes' : 'Create Field'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete field</DialogTitle>
        <DialogContent>
          <Typography>Are you sure you want to delete <strong>{selectedField?.field_label || 'this field'}</strong>?</Typography>
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
