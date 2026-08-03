import React, { useEffect, useMemo, useState } from 'react';
import {
  Box,
  Button,
  CircularProgress,
  FormControl,
  IconButton,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  TextField,
  Typography,
  Snackbar,
  Alert,
  Tooltip
} from '@mui/material';
import { apiService } from '../services/apiService';
import type { SectionItem, LocomotiveItem, EquipmentItem, TemplateFieldItem } from '../types';

type FieldValue = { field_id: number; value: string | number | boolean | null };

// Technology is stored in two different vocabularies across the schema: Locomotive.technology and
// ChecksheetTemplate.technology use an underscore/uppercase form ('3_PHASE', 'CONVENTIONAL'), while
// SectionEquipmentMap.technology uses a display-style form ('3-Phase', 'Conventional') - see the
// backend's own `normalize_technology` in app/services/section_equipment_map_service.py, the
// single source of truth this mirrors. Comparing either pair of these directly (as this form used
// to, `t.technology === technology`) never matches, since one side always used the underscore form
// and the other always used the display form - normalizing both before comparing is required.
function normalizeTechnology(value: string | null | undefined): string | null {
  if (!value) return null;
  return value.trim().toUpperCase().replace(/-/g, '_').replace(/ /g, '_');
}

export default function ChecksheetsForm({ currentUser, onSaved, initial }: { currentUser: any; onSaved?: () => void; initial?: any | null }) {
  const [loading, setLoading] = useState(true);
  const [sections, setSections] = useState<SectionItem[]>([]);
  const [locomotives, setLocomotives] = useState<LocomotiveItem[]>([]);
  const [equipment, setEquipment] = useState<EquipmentItem[]>([]);
  const [mappings, setMappings] = useState<any[]>([]);

  const [selectedSection, setSelectedSection] = useState<number | null>(null);
  const [selectedLoco, setSelectedLoco] = useState<number | null>(null);
  const [selectedEquipment, setSelectedEquipment] = useState<number | null>(null);

  const [templateId, setTemplateId] = useState<number | null>(null);
  const [fields, setFields] = useState<TemplateFieldItem[]>([]);
  const [values, setValues] = useState<Record<number, any>>({});
  const [fieldsLoading, setFieldsLoading] = useState(false);
  const [workType, setWorkType] = useState<string>('Inspection');

  const [saving, setSaving] = useState(false);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({ open: false, message: '', severity: 'success' });

  const equipmentOptions = useMemo(() => {
    if (!selectedSection) return [];
    // find equipment available for this section via mappings
    const eqIds = mappings.filter((m) => m.section_id === selectedSection).map((m) => m.equipment_id);
    return equipment.filter((e) => eqIds.includes(e.id));
  }, [equipment, mappings, selectedSection]);

  // Module 36: a section with zero mapped equipment (e.g. M6-HR) - equipment/mappings are both
  // already fully loaded by this point (fetched once on mount), so this is a synchronous
  // derivation, unlike Android's per-technology async fetch.
  const isEquipmentlessSection = selectedSection !== null && equipmentOptions.length === 0;

  useEffect(() => {
    let mounted = true;

    const load = async () => {
      setLoading(true);
      try {
        const [secsRes, locosRes, eqRes, mapRes] = await Promise.all([
          apiService.getSections(),
          apiService.getLocomotives(),
          apiService.getEquipment(),
          apiService.getMappings()
        ]);

        if (!mounted) return;
        setSections(secsRes.data || []);
        setLocomotives(locosRes.data || []);
        setEquipment(eqRes.data || []);
        setMappings(mapRes.data || []);

        // default section: use initial if editing, otherwise currentUser.section_id
        if (initial) {
          setSelectedSection(initial.section_id ?? (currentUser && currentUser.section_id ? currentUser.section_id : null));
          setSelectedLoco(initial.locomotive_id ?? null);
          setSelectedEquipment(initial.equipment_id ?? null);
          setWorkType(initial.work_type ?? 'Inspection');
        } else if (currentUser && currentUser.section_id) {
          setSelectedSection(currentUser.section_id);
        }
      } catch (err) {
        console.error(err);
      } finally {
        if (mounted) setLoading(false);
      }
    };

    load();
    return () => { mounted = false; };
  }, [currentUser]);

  // Loads a template's fields and initializes `values` - from the template's own defaults, or
  // from `initial.values` (the checksheet being edited) wherever a value already exists there.
  const loadFieldsAndValues = async (templateIdToLoad: number) => {
    setFieldsLoading(true);
    try {
      const fieldsRes = await apiService.getTemplateFields(templateIdToLoad);
      setFields(fieldsRes.data || []);

      const init: Record<number, any> = {};
      (fieldsRes.data || []).forEach((f: TemplateFieldItem) => {
        const fid = f.id!;
        let val: any = f.default_value ?? (f.field_type === 'checkbox' ? false : '');
        if (initial && Array.isArray(initial.values)) {
          const foundVal = initial.values.find((v: any) => v.field_id === fid);
          if (foundVal && foundVal.field_value !== undefined && foundVal.field_value !== null) {
            val = foundVal.field_value;
          }
        }
        init[fid] = val;
      });
      setValues(init);
    } finally {
      setFieldsLoading(false);
    }
  };

  useEffect(() => {
    const resolveTemplate = async () => {
      // Editing an existing checksheet: as long as section/equipment still match what the
      // checksheet was originally filed against, its template is already known (initial.template_id)
      // - load it directly instead of re-deriving it from the section+equipment mapping, which can
      // fail (and did - this was the root cause of "Please select section, locomotive, equipment
      // and ensure a template is loaded.") if that mapping or the template was since changed,
      // deactivated, or removed. If the admin deliberately changes section/equipment while editing,
      // this falls through to the normal mapping-based resolution below, same as creating new.
      if (
        initial &&
        initial.template_id &&
        selectedSection === (initial.section_id ?? null) &&
        selectedEquipment === (initial.equipment_id ?? null)
      ) {
        setTemplateId(Number(initial.template_id));
        await loadFieldsAndValues(Number(initial.template_id));
        return;
      }

      setTemplateId(null);
      setFields([]);
      setValues({});

      // Module 36: a section with no equipment mapped at all (e.g. M6-HR) resolves its template
      // by section_id + locomotive technology instead of section_id + equipment_id - the same
      // generic, data-driven distinction Android's FillChecksheetViewModel makes (equipmentOptions
      // for this section came back empty), not a hardcoded section check.
      if (isEquipmentlessSection) {
        if (!selectedSection || !selectedLoco) return;
        const technology = normalizeTechnology(locomotives.find((l) => l.id === selectedLoco)?.technology);
        const templatesRes = await apiService.getTemplates();
        const templates = templatesRes.data || [];
        const found = templates.find((t: any) =>
          t.section_id === selectedSection && t.equipment_id == null &&
          normalizeTechnology(t.technology) === technology && t.is_active
        );
        if (!found || found.id == null) return;
        setTemplateId(Number(found.id));
        await loadFieldsAndValues(Number(found.id));
        return;
      }

      if (!selectedEquipment || !selectedSection) return;

      // find mapping for this section+equipment
      const mapping = mappings.find((m) => m.section_id === selectedSection && m.equipment_id === selectedEquipment);
      const technology = normalizeTechnology(mapping?.technology);

      const templatesRes = await apiService.getTemplates();
      const templates = templatesRes.data || [];

      const found = templates.find((t: any) =>
        t.equipment_id === selectedEquipment && normalizeTechnology(t.technology) === technology && t.is_active
      );
      if (!found || found.id == null) return;
      setTemplateId(Number(found.id));
      await loadFieldsAndValues(Number(found.id));
    };

    resolveTemplate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedEquipment, selectedSection, selectedLoco, mappings, locomotives, isEquipmentlessSection, initial]);

  const handleChangeValue = (fieldId: number | undefined, v: any) => {
    if (fieldId == null) return;
    setValues((cur) => ({ ...cur, [fieldId]: v }));
  };

  const validate = () => {
    for (const f of fields) {
      const fid = f.id!;
      const val = values[fid];
      if (f.required && (val === null || val === '' || (f.field_type === 'checkbox' && val === false))) {
        return `${f.field_label} is required`;
      }
      if (f.field_type === 'number' && val !== '' && val !== null) {
        if (isNaN(Number(val))) return `${f.field_label} must be a number`;
      }
    }
    return null;
  };

  const save = async (status: 'DRAFT' | 'SUBMITTED') => {
    const err = validate();
    if (err) {
      setSnackbar({ open: true, message: err, severity: 'error' });
      return;
    }

    if (!selectedSection || !selectedLoco || !templateId || (!isEquipmentlessSection && !selectedEquipment)) {
      setSnackbar({
        open: true,
        message: isEquipmentlessSection
          ? 'Please select section, locomotive and ensure a template is loaded'
          : 'Please select section, locomotive, equipment and ensure a template is loaded',
        severity: 'error'
      });
      return;
    }

      const payload = {
        locomotive_id: selectedLoco,
        section_id: selectedSection,
        equipment_id: selectedEquipment,
        template_id: templateId,
        work_type: workType,
        status: status === 'SUBMITTED' ? 'SUBMITTED' : 'DRAFT',
        values: fields.map((f) => ({ field_id: f.id, value: values[f.id!] ?? '' }))
      };

    setSaving(true);
    try {
      if (initial && initial.id) {
        await apiService.updateChecksheet(initial.id, payload as any);
        setSnackbar({ open: true, message: status === 'SUBMITTED' ? 'Checksheet submitted (updated)' : 'Draft updated', severity: 'success' });
      } else {
        await apiService.createChecksheet(payload as any);
        setSnackbar({ open: true, message: status === 'SUBMITTED' ? 'Checksheet submitted' : 'Draft saved', severity: 'success' });
      }
      // clear form
      setSelectedLoco(null);
      setSelectedEquipment(null);
      setTemplateId(null);
      setFields([]);
      setValues({});
      if (onSaved) onSaved();
    } catch (e: any) {
      setSnackbar({ open: true, message: e?.response?.data?.detail || 'Unable to save checksheet', severity: 'error' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <Paper sx={{ p: 3, mb: 2 }}><CircularProgress /></Paper>;

  return (
    <Paper sx={{ p: 3, mb: 2 }}>
      <Typography variant="h5" mb={2}>Create Checksheet</Typography>
      <Stack spacing={2}>
        <FormControl fullWidth>
          <InputLabel>Section</InputLabel>
          <Select value={selectedSection ?? ''} label="Section" onChange={(e) => setSelectedSection(e.target.value === '' ? null : Number(e.target.value))}>
            <MenuItem value="">Select section</MenuItem>
            {sections.map((s) => <MenuItem key={s.id} value={s.id}>{s.name}</MenuItem>)}
          </Select>
        </FormControl>

        <FormControl fullWidth>
          <InputLabel>Locomotive</InputLabel>
          <Select value={selectedLoco ?? ''} label="Locomotive" onChange={(e) => setSelectedLoco(e.target.value === '' ? null : Number(e.target.value))}>
            <MenuItem value="">Select locomotive</MenuItem>
            {locomotives.map((l) => <MenuItem key={l.id} value={l.id}>{l.loco_number}</MenuItem>)}
          </Select>
        </FormControl>

        <TextField label="Work Type" value={workType} onChange={(e) => setWorkType(e.target.value)} fullWidth />

        {isEquipmentlessSection ? (
          <Alert severity="info">This section has no equipment - the checksheet template is resolved from section and locomotive technology alone.</Alert>
        ) : (
          <FormControl fullWidth>
            <InputLabel>Equipment</InputLabel>
            <Select value={selectedEquipment ?? ''} label="Equipment" onChange={(e) => setSelectedEquipment(e.target.value === '' ? null : Number(e.target.value))}>
              <MenuItem value="">Select equipment</MenuItem>
              {equipmentOptions.map((eq) => <MenuItem key={eq.id} value={eq.id}>{eq.equipment_name}</MenuItem>)}
            </Select>
          </FormControl>
        )}

        {templateId ? (
          <Box>
            <Typography variant="h6" mb={1}>Inspection Fields</Typography>
            {fieldsLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}><CircularProgress /></Box>
            ) : (
              <Stack spacing={2}>
                {fields.map((f) => (
                  <Paper key={f.id} sx={{ p: 2 }}>
                    <Stack spacing={1}>
                      <Stack direction="row" justifyContent="space-between" alignItems="center">
                        <Typography fontWeight={700}>{f.field_label}{f.required ? ' *' : ''}</Typography>
                        {f.unit ? <Typography color="text.secondary">{f.unit}</Typography> : null}
                      </Stack>
                      <Typography variant="body2" color="text.secondary">{f.help_text}</Typography>

                      {/* Render input based on type */}
                      {f.field_type === 'text' && (
                        <TextField fullWidth value={values[f.id!] ?? ''} onChange={(e) => handleChangeValue(f.id, e.target.value)} />
                      )}
                      {f.field_type === 'textarea' && (
                        <TextField fullWidth multiline minRows={3} value={values[f.id!] ?? ''} onChange={(e) => handleChangeValue(f.id, e.target.value)} />
                      )}
                      {f.field_type === 'number' && (
                        <TextField fullWidth type="number" value={values[f.id!] ?? ''} onChange={(e) => handleChangeValue(f.id, e.target.value)} />
                      )}
                      {f.field_type === 'date' && (
                        <TextField fullWidth type="date" value={values[f.id!] ?? ''} onChange={(e) => handleChangeValue(f.id, e.target.value)} />
                      )}
                      {f.field_type === 'datetime' && (
                        <TextField fullWidth type="datetime-local" value={values[f.id!] ?? ''} onChange={(e) => handleChangeValue(f.id, e.target.value)} />
                      )}
                      {f.field_type === 'select' && (
                        <FormControl fullWidth>
                          <Select value={values[f.id!] ?? ''} onChange={(e) => handleChangeValue(f.id, e.target.value)}>
                            <MenuItem value="">Select</MenuItem>
                            {(f.options || '').split(',').map((opt: string) => <MenuItem key={opt.trim()} value={opt.trim()}>{opt.trim()}</MenuItem>)}
                          </Select>
                        </FormControl>
                      )}
                      {f.field_type === 'radio' && (
                        <FormControl fullWidth>
                          <Select value={values[f.id!] ?? ''} onChange={(e) => handleChangeValue(f.id, e.target.value)}>
                            <MenuItem value="">Select</MenuItem>
                            {(f.options || '').split(',').map((opt: string) => <MenuItem key={opt.trim()} value={opt.trim()}>{opt.trim()}</MenuItem>)}
                          </Select>
                        </FormControl>
                      )}
                      {f.field_type === 'checkbox' && (
                        <FormControl>
                          <Stack direction="row" alignItems="center" spacing={1}>
                            <input type="checkbox" checked={!!values[f.id!]} onChange={(e) => handleChangeValue(f.id, e.target.checked)} />
                            <Typography>{f.help_text}</Typography>
                          </Stack>
                        </FormControl>
                      )}
                    </Stack>
                  </Paper>
                ))}
              </Stack>
            )}
          </Box>
        ) : (
          <Alert severity="info">
            {isEquipmentlessSection ? 'Select a locomotive to load a template and fields.' : 'Select equipment to load a template and fields.'}
          </Alert>
        )}

        <Stack direction="row" spacing={2}>
          <Button variant="outlined" onClick={() => save('DRAFT')} disabled={saving}>{saving ? <CircularProgress size={18} /> : 'Save Draft'}</Button>
          <Button variant="contained" onClick={() => save('SUBMITTED')} disabled={saving}>{saving ? <CircularProgress size={18} /> : 'Submit'}</Button>
        </Stack>
      </Stack>

      <Snackbar open={snackbar.open} autoHideDuration={4000} onClose={() => setSnackbar((s) => ({ ...s, open: false }))}>
        <Alert severity={snackbar.severity}>{snackbar.message}</Alert>
      </Snackbar>
    </Paper>
  );
}
