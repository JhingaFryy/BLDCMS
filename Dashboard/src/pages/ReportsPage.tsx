import React, { useEffect, useMemo, useState } from 'react';
import {
  Box,
  Button,
  Grid,
  Paper,
  Stack,
  Typography,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  useTheme,
  SelectChangeEvent
} from '@mui/material';
import { DataGrid, GridColDef, GridPaginationModel } from '@mui/x-data-grid';
import { apiService } from '../services/apiService';
import { format } from 'date-fns';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend, LineChart, Line } from 'recharts';
import DownloadIcon from '@mui/icons-material/Download';
import DescriptionRoundedIcon from '@mui/icons-material/DescriptionRounded';
import SendRoundedIcon from '@mui/icons-material/SendRounded';
import CheckCircleRoundedIcon from '@mui/icons-material/CheckCircleRounded';
import CancelRoundedIcon from '@mui/icons-material/CancelRounded';
import AssessmentRoundedIcon from '@mui/icons-material/AssessmentRounded';
import { formatIST } from '../utils/formatDate';
import { useAuth } from '../contexts/AuthContext';
import { cyberColors, gradients, glow } from '../theme/palette';
import { statusMeta } from '../theme/statusMeta';
import StatCard from '../components/common/StatCard';
import StatusChip from '../components/common/StatusChip';

const STATUS_COLORS: Record<string, string> = {
  DRAFT: statusMeta('DRAFT').color,
  SUBMITTED: statusMeta('SUBMITTED').color,
  UNDER_REVIEW: statusMeta('UNDER_REVIEW').color,
  APPROVED: statusMeta('APPROVED').color,
  REJECTED: statusMeta('REJECTED').color
};

export default function ReportsPage() {
  const { user } = useAuth();
  const theme = useTheme();
  const gridColor = theme.palette.divider;
  const tickColor = theme.palette.text.secondary;
  const tooltipStyle = {
    backgroundColor: theme.palette.background.paper,
    border: `1px solid ${theme.palette.divider}`,
    borderRadius: 8,
    color: theme.palette.text.primary
  };
  // The backend enforces this unconditionally regardless of what section_id is sent (see
  // Module 27.5) - the picker is hidden for Supervisors rather than merely disabled, matching
  // "Reports should automatically be filtered to the supervisor's section - no manual filtering
  // required" instead of showing a control that would silently have no effect.
  const isSupervisor = user?.role === 'Supervisor';

  const [loading, setLoading] = useState(false);
  const [items, setItems] = useState<any[]>([]);
  const [total, setTotal] = useState(0);

  const [sections, setSections] = useState<any[]>([]);
  const [locomotives, setLocomotives] = useState<any[]>([]);
  const [equipment, setEquipment] = useState<any[]>([]);
  const [templates, setTemplates] = useState<any[]>([]);
  const [technicians, setTechnicians] = useState<any[]>([]);
  const [supervisors, setSupervisors] = useState<any[]>([]);

  // filters
  const [dateFrom, setDateFrom] = useState<string>('');
  const [dateTo, setDateTo] = useState<string>('');
  const [sectionId, setSectionId] = useState<number | ''>('');
  const [locomotiveId, setLocomotiveId] = useState<number | ''>('');
  const [equipmentId, setEquipmentId] = useState<number | ''>('');
  const [technicianId, setTechnicianId] = useState<number | ''>('');
  const [supervisorId, setSupervisorId] = useState<number | ''>('');
  const [status, setStatus] = useState<string | ''>('');
  const [technology, setTechnology] = useState<string | ''>('');
  const [workType, setWorkType] = useState<string | ''>('');

  // pagination / grid
  const [paginationModel, setPaginationModel] = useState<GridPaginationModel>({ page: 0, pageSize: 10 });

  useEffect(() => {
    let mounted = true;
    const loadLookups = async () => {
      try {
        const [secs, locos, eqs, tmpls] = await Promise.all([
          apiService.getSections(),
          apiService.getLocomotives(),
          apiService.getEquipment(),
          apiService.getTemplates()
        ]);
        if (!mounted) return;
        setSections(secs.data || []);
        setLocomotives(locos.data || []);
        setEquipment(eqs.data || []);
        setTemplates(tmpls.data || []);

        // load technicians and supervisors (first 1000)
        const techResp = await apiService.getUsers({ skip: 0, limit: 1000, role: 'Technician' });
        const supResp = await apiService.getUsers({ skip: 0, limit: 1000, role: 'Supervisor' });
        setTechnicians(techResp.data.items || []);
        setSupervisors(supResp.data.items || []);
      } catch (e) {
        console.error(e);
      }
    };
    loadLookups();
    return () => { mounted = false; };
  }, []);

  const safeDate = (value?: string | null) => {
    if (!value) return null;
    const date = new Date(value);
    return Number.isFinite(date.getTime()) ? date : null;
  };

  const buildParams = () => {
    const params: any = { skip: paginationModel.page * paginationModel.pageSize, limit: paginationModel.pageSize };
    if (dateFrom) params.date_from = dateFrom;
    if (dateTo) params.date_to = dateTo;
    if (sectionId) params.section_id = sectionId;
    if (locomotiveId) params.locomotive_id = locomotiveId;
    if (equipmentId) params.equipment_id = equipmentId;
    if (status) params.status = status;
    if (technology) params.technology = technology;
    if (workType) params.work_type = workType;
    if (technicianId) params.search = technicians.find((t: { id?: number; mobile?: string }) => t.id === technicianId)?.mobile || undefined;
    return params;
  };

  const loadData = async (opts?: any) => {
    setLoading(true);
    try {
      const params = buildParams();
      if (opts?.all) { params.skip = 0; params.limit = 10000; }
      const res = await apiService.getChecksheets(params);
      setItems(res.data.items || []);
      setTotal(res.data.total || 0);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  useEffect(() => { loadData(); }, [paginationModel.page, paginationModel.pageSize, dateFrom, dateTo, sectionId, locomotiveId, equipmentId, status, technology, workType]);

  // KPIs computed from current result set by requesting all matching rows (limit large)
  const [kpiCounts, setKpiCounts] = useState<any>({});
  const refreshKpis = async () => {
    try {
      const params = buildParams();
      params.skip = 0; params.limit = 10000;
      const res = await apiService.getChecksheets(params);
      const rows = res.data.items || [];
      const counts: any = { total: rows.length, DRAFT: 0, SUBMITTED: 0, APPROVED: 0, REJECTED: 0, today: 0, week: 0, month: 0 };
      const today = format(new Date(), 'yyyy-MM-dd');
      const startOfWeek = new Date(); startOfWeek.setDate(startOfWeek.getDate() - startOfWeek.getDay());
      const startOfMonth = new Date(new Date().getFullYear(), new Date().getMonth(), 1);
      rows.forEach((r: any) => {
        counts[r.status] = (counts[r.status] || 0) + 1;
        const created = safeDate(r.created_at);
        if (created) {
          const d = format(created, 'yyyy-MM-dd');
          if (d === today) counts.today++;
          if (created >= startOfWeek) counts.week++;
          if (created >= startOfMonth) counts.month++;
        }
      });
      setKpiCounts(counts);
    } catch (e) { console.error(e); }
  };

  useEffect(() => { refreshKpis(); }, [dateFrom, dateTo, sectionId, locomotiveId, equipmentId, status, technology, workType]);

  const exportCsv = () => {
    const header = ['id','status','technician_mobile','section_name','equipment_name','template_name','created_at'];
    const rows = items.map((it: any) => header.map(h => String(it[h] ?? '')).join(','));
    const csv = [header.join(','), ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = `checksheets_${Date.now()}.csv`; a.click(); URL.revokeObjectURL(url);
  };

  const exportPdf = async () => {
    try {
      const params = buildParams();
      const res = await apiService.exportReportPdf(params);
      const blob = new Blob([res.data], { type: 'application/pdf' });
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = 'checksheets_report.pdf';
      link.click();
      window.URL.revokeObjectURL(link.href);
    } catch (e) {
      console.error(e);
    }
  };

  // charts data
  const statusData = useMemo(() => Object.keys(kpiCounts).filter(k => ['DRAFT','SUBMITTED','APPROVED','REJECTED'].includes(k)).map(k => ({ name: k, value: kpiCounts[k] || 0 })), [kpiCounts]);
  const sectionData = useMemo(() => {
    const map = new Map<string, number>();
    items.forEach((r:any) => { const key = r.section_name || 'Unknown'; map.set(key, (map.get(key) || 0) + 1); });
    return Array.from(map.entries()).map(([name, value]) => ({ name, value }));
  }, [items]);
  const equipmentData = useMemo(() => {
    const map = new Map<string, number>();
    items.forEach((r:any) => { const key = r.equipment_name || 'Unknown'; map.set(key, (map.get(key) || 0) + 1); });
    return Array.from(map.entries()).map(([name, value]) => ({ name, value }));
  }, [items]);
  const monthlyTrend = useMemo(() => {
    const map = new Map<string, number>();
    items.forEach((r:any) => {
      const created = safeDate(r.created_at);
      if (created) {
        const m = format(created, 'yyyy-MM');
        map.set(m, (map.get(m) || 0) + 1);
      }
    });
    return Array.from(map.entries()).sort().map(([name, value]) => ({ name, value }));
  }, [items]);

  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 80 },
    { field: 'status', headerName: 'Status', width: 140, renderCell: (params) => <StatusChip status={params.value as string} /> },
    { field: 'technician_mobile', headerName: 'Technician', width: 160 },
    { field: 'section_name', headerName: 'Section', width: 140 },
    { field: 'equipment_name', headerName: 'Equipment', width: 160 },
    { field: 'template_name', headerName: 'Template', width: 220 },
    { field: 'created_at', headerName: 'Created', width: 200, valueFormatter: (value) => formatIST(value as string | undefined) }
  ];

  return (
    <Box>
      <Stack spacing={2.5}>
        <Paper sx={{ p: 3, borderRadius: 3 }}>
          <Typography variant="h4" fontWeight={700} mb={1}>Reports</Typography>
          <Typography variant="body1" color="text.secondary">Operational checksheet reports and analytics.</Typography>
        </Paper>

        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={2.4}>
            <StatCard label="Total Checksheets" value={kpiCounts.total ?? 0} icon={AssessmentRoundedIcon} gradient={gradients.navy} glowColor={glow.cyan} />
          </Grid>
          <Grid item xs={12} sm={6} md={2.4}>
            <StatCard label="Draft" value={kpiCounts.DRAFT ?? 0} icon={DescriptionRoundedIcon} gradient={gradients.navy} glowColor={glow.primary} />
          </Grid>
          <Grid item xs={12} sm={6} md={2.4}>
            <StatCard label="Submitted" value={kpiCounts.SUBMITTED ?? 0} icon={SendRoundedIcon} gradient={gradients.primary} glowColor={glow.primary} />
          </Grid>
          <Grid item xs={12} sm={6} md={2.4}>
            <StatCard label="Approved" value={kpiCounts.APPROVED ?? 0} icon={CheckCircleRoundedIcon} gradient={gradients.success} glowColor={glow.success} />
          </Grid>
          <Grid item xs={12} sm={6} md={2.4}>
            <StatCard label="Rejected" value={kpiCounts.REJECTED ?? 0} icon={CancelRoundedIcon} gradient={gradients.error} glowColor={glow.error} />
          </Grid>
        </Grid>

        <Paper sx={{ p: 2 }}>
          <Stack spacing={2}>
            <Stack direction="row" spacing={2} alignItems="center">
              <TextField label="From" type="date" InputLabelProps={{ shrink: true }} value={dateFrom} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setDateFrom(e.target.value)} />
              <TextField label="To" type="date" InputLabelProps={{ shrink: true }} value={dateTo} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setDateTo(e.target.value)} />
              {isSupervisor ? null : (
                <FormControl sx={{ minWidth: 160 }}><InputLabel>Section</InputLabel><Select value={sectionId} label="Section" onChange={(e: SelectChangeEvent<number | ''>) => setSectionId(e.target.value as number | '')}><MenuItem value="">All</MenuItem>{sections.map(s=> <MenuItem key={s.id} value={s.id}>{s.name}</MenuItem>)}</Select></FormControl>
              )}
              <FormControl sx={{ minWidth: 160 }}><InputLabel>Locomotive</InputLabel><Select value={locomotiveId} label="Locomotive" onChange={(e: SelectChangeEvent<number | ''>) => setLocomotiveId(e.target.value as number | '')}><MenuItem value="">All</MenuItem>{locomotives.map(l=> <MenuItem key={l.id} value={l.id}>{l.loco_number}</MenuItem>)}</Select></FormControl>
              <FormControl sx={{ minWidth: 160 }}><InputLabel>Equipment</InputLabel><Select value={equipmentId} label="Equipment" onChange={(e: SelectChangeEvent<number | ''>) => setEquipmentId(e.target.value as number | '')}><MenuItem value="">All</MenuItem>{equipment.map(eq=> <MenuItem key={eq.id} value={eq.id}>{eq.equipment_name}</MenuItem>)}</Select></FormControl>
            </Stack>

            <Stack direction="row" spacing={2} alignItems="center">
              <FormControl sx={{ minWidth: 160 }}><InputLabel>Technician</InputLabel><Select value={technicianId} label="Technician" onChange={(e: SelectChangeEvent<number | ''>) => setTechnicianId(e.target.value as number | '')}><MenuItem value="">All</MenuItem>{technicians.map((t: any)=> <MenuItem key={t.id} value={t.id}>{t.name}</MenuItem>)}</Select></FormControl>
              <FormControl sx={{ minWidth: 160 }}><InputLabel>Supervisor</InputLabel><Select value={supervisorId} label="Supervisor" onChange={(e: SelectChangeEvent<number | ''>) => setSupervisorId(e.target.value as number | '')}><MenuItem value="">All</MenuItem>{supervisors.map((s: any)=> <MenuItem key={s.id} value={s.id}>{s.name}</MenuItem>)}</Select></FormControl>
              <FormControl sx={{ minWidth: 160 }}><InputLabel>Status</InputLabel><Select value={status} label="Status" onChange={(e: SelectChangeEvent<string>) => setStatus(e.target.value as string)}><MenuItem value="">All</MenuItem><MenuItem value="DRAFT">Draft</MenuItem><MenuItem value="SUBMITTED">Submitted</MenuItem><MenuItem value="UNDER_REVIEW">Under Review</MenuItem><MenuItem value="APPROVED">Approved</MenuItem><MenuItem value="REJECTED">Rejected</MenuItem></Select></FormControl>
              <FormControl sx={{ minWidth: 160 }}><InputLabel>Technology</InputLabel><Select value={technology} label="Technology" onChange={(e: SelectChangeEvent<string>) => setTechnology(e.target.value as string)}><MenuItem value="">All</MenuItem>{Array.from(new Set(templates.map((t: any)=>t.technology))).map(z=> <MenuItem key={z} value={z}>{z}</MenuItem>)}</Select></FormControl>
              <TextField label="Work Type" value={workType} onChange={(e: React.ChangeEvent<HTMLInputElement>)=>setWorkType(e.target.value)} />
              <Button variant="contained" onClick={()=> { setPaginationModel((current: GridPaginationModel) => ({ ...current, page: 0 })); refreshKpis(); }}>Apply</Button>
              <Button startIcon={<DownloadIcon />} onClick={exportCsv}>Export CSV</Button>
              <Button startIcon={<DownloadIcon />} onClick={exportPdf}>Export PDF</Button>
            </Stack>

            <Stack spacing={2}>
              <Typography variant="h6">Analytics</Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6} style={{ height: 240 }}>
                  <Paper sx={{ p: 1.5, height: '100%' }}>
                    <Typography variant="subtitle2" fontWeight={700} mb={0.5}>Checksheets by Status</Typography>
                    <ResponsiveContainer width="100%" height={180}>
                      <PieChart>
                        <Pie data={statusData} dataKey="value" nameKey="name" outerRadius={60} label>
                          {statusData.map((entry: any, idx: number) => (<Cell key={idx} fill={STATUS_COLORS[entry.name] || cyberColors.purple} />))}
                        </Pie>
                        <Tooltip contentStyle={tooltipStyle} />
                      </PieChart>
                    </ResponsiveContainer>
                  </Paper>
                </Grid>

                <Grid item xs={12} md={6} style={{ height: 240 }}>
                  <Paper sx={{ p: 1.5, height: '100%' }}>
                    <Typography variant="subtitle2" fontWeight={700} mb={0.5}>Checksheets by Section</Typography>
                    <ResponsiveContainer width="100%" height={180}>
                      <BarChart data={sectionData}>
                        <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
                        <XAxis dataKey="name" stroke={tickColor} tick={{ fill: tickColor, fontSize: 12 }} />
                        <YAxis stroke={tickColor} tick={{ fill: tickColor, fontSize: 12 }} />
                        <Tooltip contentStyle={tooltipStyle} />
                        <Bar dataKey="value" fill={cyberColors.electricBlue} radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </Paper>
                </Grid>

                <Grid item xs={12} md={6} style={{ height: 240 }}>
                  <Paper sx={{ p: 1.5, height: '100%' }}>
                    <Typography variant="subtitle2" fontWeight={700} mb={0.5}>Monthly Trend</Typography>
                    <ResponsiveContainer width="100%" height={180}>
                      <LineChart data={monthlyTrend}>
                        <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
                        <XAxis dataKey="name" stroke={tickColor} tick={{ fill: tickColor, fontSize: 12 }} />
                        <YAxis stroke={tickColor} tick={{ fill: tickColor, fontSize: 12 }} />
                        <Tooltip contentStyle={tooltipStyle} />
                        <Line type="monotone" dataKey="value" stroke={cyberColors.purple} strokeWidth={2.5} dot={false} activeDot={{ r: 5, fill: cyberColors.purpleLight }} />
                      </LineChart>
                    </ResponsiveContainer>
                  </Paper>
                </Grid>

                <Grid item xs={12} md={6} style={{ height: 240 }}>
                  <Paper sx={{ p: 1.5, height: '100%' }}>
                    <Typography variant="subtitle2" fontWeight={700} mb={0.5}>Equipment-wise Inspection Count</Typography>
                    <ResponsiveContainer width="100%" height={180}>
                      <BarChart data={equipmentData}>
                        <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
                        <XAxis dataKey="name" stroke={tickColor} tick={{ fill: tickColor, fontSize: 12 }} />
                        <YAxis stroke={tickColor} tick={{ fill: tickColor, fontSize: 12 }} />
                        <Tooltip contentStyle={tooltipStyle} />
                        <Bar dataKey="value" fill={cyberColors.neonGreen} radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </Paper>
                </Grid>
              </Grid>
            </Stack>

            <div style={{ height: 520, width: '100%' }}>
              <DataGrid
                rows={items}
                columns={columns}
                paginationModel={paginationModel}
                onPaginationModelChange={(model) => setPaginationModel(model)}
                pageSizeOptions={[5, 10, 25, 50]}
                paginationMode="server"
                rowCount={total}
                loading={loading}
              />
            </div>

          </Stack>
        </Paper>
      </Stack>
    </Box>
  );
}
