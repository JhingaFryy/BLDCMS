import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Box,
  Button,
  Grid,
  IconButton,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  TablePagination,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import SendIcon from '@mui/icons-material/Send';
import DownloadIcon from '@mui/icons-material/Download';
import DescriptionRoundedIcon from '@mui/icons-material/DescriptionRounded';
import SendRoundedIcon from '@mui/icons-material/SendRounded';
import CheckCircleRoundedIcon from '@mui/icons-material/CheckCircleRounded';
import CancelRoundedIcon from '@mui/icons-material/CancelRounded';
import ChecksheetsForm from './ChecksheetsForm';
import ChecksheetReviewDialog from './ChecksheetReviewDialog';
import DigitalSignatureDialogV2 from './DigitalSignatureDialogV2';
import { apiService } from '../services/apiService';
import { useAuth } from '../contexts/AuthContext';
import type { ChecksheetItem, StatusDistribution } from '../types';
import { formatIST } from '../utils/formatDate';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import VisibilityIcon from '@mui/icons-material/Visibility';
import { gradients, glow } from '../theme/palette';
import StatCard from '../components/common/StatCard';
import StatusChip from '../components/common/StatusChip';
import SignatureBadge from '../components/common/SignatureBadge';
import LegacyApprovalBadge from '../components/common/LegacyApprovalBadge';
import EmptyState from '../components/common/EmptyState';
import TableSkeleton from '../components/common/TableSkeleton';

const EMPTY_STATUS_COUNTS: StatusDistribution = { DRAFT: 0, SUBMITTED: 0, UNDER_REVIEW: 0, APPROVED: 0, REJECTED: 0 };

export default function ChecksheetsPage() {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const deepLinkHandled = useRef(false);

  const [items, setItems] = useState<ChecksheetItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string | ''>('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [selected, setSelected] = useState<ChecksheetItem | null>(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [actionInProgress, setActionInProgress] = useState(false);
  const [rejectDialogOpen, setRejectDialogOpen] = useState(false);
  const [rejectReason, setRejectReason] = useState('');

  // Module 29.8: Supervisor Review screen - the only path to Approve/Reject for a Supervisor.
  // reviewChecksheet holds the freshly-fetched full detail (with values[]), not just the row's
  // summary data, so the dialog always shows the complete, current checking-point list.
  const [reviewDialogOpen, setReviewDialogOpen] = useState(false);
  const [reviewChecksheet, setReviewChecksheet] = useState<ChecksheetItem | null>(null);
  const [reviewLoading, setReviewLoading] = useState(false);

  // Module 40: "Approve & Sign" opens this instead of calling the status-change API directly -
  // signTargetV2 holds the checksheet being signed while the emBridge signing dialog is open.
  const [signDialogOpenV2, setSignDialogOpenV2] = useState(false);
  const [signTargetV2, setSignTargetV2] = useState<ChecksheetItem | null>(null);

  const [statusCounts, setStatusCounts] = useState<StatusDistribution>(EMPTY_STATUS_COUNTS);
  const [statsLoading, setStatsLoading] = useState(false);

  const loadChecksheets = async (opts?: any) => {
    setLoading(true);
    try {
      const params: any = {
        skip: (opts?.page ?? page) * (opts?.limit ?? rowsPerPage),
        limit: opts?.limit ?? rowsPerPage,
      };
      if ((opts?.search ?? search) && (opts?.search ?? search).length > 0) params.search = opts?.search ?? search;
      if ((opts?.status ?? statusFilter) && (opts?.status ?? statusFilter) !== '') params.status = opts?.status ?? statusFilter;
      const res = await apiService.getChecksheets(params);
      setItems(res.data.items || []);
      setTotal(res.data.total || 0);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Totals across every checksheet, independent of the table's own status filter/pagination -
  // reused from the existing analytics endpoint rather than a new one.
  const loadStats = async () => {
    setStatsLoading(true);
    try {
      const res = await apiService.getChecksheetAnalytics();
      setStatusCounts(res.data.status_distribution);
    } catch (err) {
      console.error(err);
    } finally {
      setStatsLoading(false);
    }
  };

  useEffect(() => { loadChecksheets({ page, limit: rowsPerPage }); }, [page, rowsPerPage, statusFilter]);
  useEffect(() => { loadStats(); }, []);

  // Global Search (Module 28) deep-links here as /checksheets?id=<id> - openEdit() already
  // re-fetches the full record by id regardless of what's currently loaded/filtered in the table.
  useEffect(() => {
    if (deepLinkHandled.current) return;
    const idParam = searchParams.get('id');
    if (!idParam) return;

    deepLinkHandled.current = true;
    openEdit({ id: Number(idParam) } as ChecksheetItem).finally(() => {
      searchParams.delete('id');
      setSearchParams(searchParams, { replace: true });
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  const refresh = () => loadChecksheets({ page, limit: rowsPerPage });
  // Used after any create/edit/delete/status-change action, so the stat cards never go stale.
  const refreshAll = () => { refresh(); loadStats(); };

  const openEdit = async (item: ChecksheetItem) => {
    setActionInProgress(true);
    try {
      const res = await apiService.getChecksheet(item.id!);
      setSelected(res.data);
      setEditDialogOpen(true);
    } catch (e) {
      console.error(e);
    } finally {
      setActionInProgress(false);
    }
  };

  const handleDelete = async (item: ChecksheetItem) => {
    if (!confirm('Delete this checksheet? This cannot be undone.')) return;
    setActionInProgress(true);
    try {
      await apiService.deleteChecksheet(item.id!);
      refreshAll();
    } catch (e: any) {
      alert(e?.response?.data?.detail || 'Unable to delete checksheet.');
      console.error(e);
    } finally { setActionInProgress(false); }
  };

  const handleSubmit = async (item: ChecksheetItem) => {
    if (!confirm('Submit this draft?')) return;
    setActionInProgress(true);
    try {
      await apiService.changeChecksheetStatus(item.id!, { status: 'SUBMITTED' });
      refreshAll();
    } catch (e: any) {
      alert(e?.response?.data?.detail || 'Unable to submit checksheet.');
      console.error(e);
    } finally { setActionInProgress(false); }
  };

  // The backend's status machine requires SUBMITTED checksheets to pass through UNDER_REVIEW
  // before APPROVED/REJECTED (VALID_STATUS_TRANSITIONS in checksheet_service.py) - there is no
  // separate "start review" action anywhere in this UI, so Approve/Reject silently drive both
  // steps as one action. Previously this second step was skipped entirely, so the backend
  // rejected the direct SUBMITTED->APPROVED/REJECTED request with a 400 that was never surfaced
  // to the user (see handleApprove/confirmReject's old bare `catch (e) { console.error(e); }`),
  // which is why the Dashboard appeared to do nothing after clicking Approve.
  const advanceToUnderReview = async (item: ChecksheetItem) => {
    if (item.status === 'SUBMITTED') {
      await apiService.changeChecksheetStatus(item.id!, { status: 'UNDER_REVIEW' });
    }
  };

  // No native confirm() here anymore - the Supervisor Review dialog (Module 29.8) that Approve is
  // now only ever reachable from already IS the "are you sure" step, since it requires actually
  // reviewing the checksheet's full content first.
  //
  // "Approve" no longer directly changes status - it advances to UNDER_REVIEW (as before) and then
  // opens the emBridge signing dialog. The actual APPROVED transition only ever happens inside
  // DigitalSignatureDialogV2's onSigned callback, once the checksheet has genuinely been digitally
  // signed.
  const handleApproveV2 = async (item: ChecksheetItem) => {
    setActionInProgress(true);
    try {
      await advanceToUnderReview(item);
      setSignTargetV2({ ...item, status: 'UNDER_REVIEW' });
      setSignDialogOpenV2(true);
    } catch (e: any) {
      alert(e?.response?.data?.detail || 'Unable to move checksheet to review.');
      console.error(e);
    } finally { setActionInProgress(false); }
  };

  const handleSignedV2 = (_updated: ChecksheetItem) => {
    setSignDialogOpenV2(false);
    setSignTargetV2(null);
    closeReview();
    refreshAll();
  };

  const closeSignDialogV2 = () => {
    setSignDialogOpenV2(false);
    setSignTargetV2(null);
  };

  const handleReject = (item: ChecksheetItem) => {
    setSelected(item);
    setRejectReason('');
    setRejectDialogOpen(true);
  };

  const confirmReject = async () => {
    if (!selected) return;
    if (!rejectReason || !rejectReason.trim()) { alert('Rejection reason is required'); return; }
    setActionInProgress(true);
    try {
      await advanceToUnderReview(selected);
      await apiService.changeChecksheetStatus(selected.id!, { status: 'REJECTED', rejection_reason: rejectReason });
      setRejectDialogOpen(false);
      closeReview();
      refreshAll();
    } catch (e: any) {
      alert(e?.response?.data?.detail || 'Unable to reject checksheet.');
      console.error(e);
    } finally { setActionInProgress(false); }
  };

  // Module 29.8: opens the read-only Supervisor Review dialog with the checksheet's full detail
  // (including values[] with Standard/Authority/Observation) - this is the only entry point to
  // Approve/Reject for a Supervisor now; there is no direct list-row shortcut anymore.
  const openReview = async (item: ChecksheetItem) => {
    setReviewDialogOpen(true);
    setReviewLoading(true);
    try {
      const res = await apiService.getChecksheet(item.id!);
      setReviewChecksheet(res.data);
    } catch (e) {
      console.error(e);
      alert('Unable to load checksheet for review.');
      setReviewDialogOpen(false);
    } finally {
      setReviewLoading(false);
    }
  };

  const closeReview = () => {
    setReviewDialogOpen(false);
    setReviewChecksheet(null);
  };

  const handleEditSaved = () => {
    setEditDialogOpen(false);
    setSelected(null);
    refreshAll();
  };

  const handleViewPdf = async (item: ChecksheetItem) => {
    if (!item.id) return;
    try {
      const res = await apiService.previewChecksheetPdf(item.id);
      const blobUrl = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      window.open(blobUrl, '_blank', 'noopener,noreferrer');
      setTimeout(() => window.URL.revokeObjectURL(blobUrl), 10000);
    } catch (e) {
      console.error(e);
    }
  };

  const handleDownloadPdf = async (item: ChecksheetItem) => {
    if (!item.id) return;
    try {
      const res = await apiService.downloadChecksheetPdf(item.id);
      const blob = new Blob([res.data], { type: 'application/pdf' });
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = `checksheet_${item.id}.pdf`;
      link.click();
      window.URL.revokeObjectURL(link.href);
    } catch (e) {
      console.error(e);
    }
  };

  const handleRegeneratePdf = async (item: ChecksheetItem) => {
    if (!item.id) return;
    setActionInProgress(true);
    try {
      await apiService.generateChecksheetPdf(item.id);
      refresh();
    } catch (e) {
      console.error(e);
    } finally {
      setActionInProgress(false);
    }
  };

  return (
    <Box>
      <Stack spacing={2.5}>
        <Paper sx={{ p: 3, borderRadius: 3 }}>
          <Typography variant="h4" fontWeight={700} mb={1}>Checksheet Dashboard</Typography>
          <Typography variant="body1" color="text.secondary">List, manage and review checksheets.</Typography>
        </Paper>

        <Grid container spacing={2}>
          <Grid item xs={12} md={3}>
            <Paper sx={{ p: 2.5, height: '100%' }}>
              <Stack spacing={1.2}>
                <Typography variant="subtitle1" fontWeight={700}>Search</Typography>
                <TextField fullWidth size="small" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search technician, work type, template" />
                <Button variant="contained" onClick={() => { setPage(0); loadChecksheets({ page: 0, search }); }}>Search</Button>
              </Stack>
            </Paper>
          </Grid>
          <Grid item xs={12} md={9}>
            <Grid container spacing={2}>
              <Grid item xs={6} sm={3}>
                <StatCard label="Draft" value={statusCounts.DRAFT} icon={DescriptionRoundedIcon} gradient={gradients.navy} glowColor={glow.primary} loading={statsLoading} />
              </Grid>
              <Grid item xs={6} sm={3}>
                <StatCard label="Submitted" value={statusCounts.SUBMITTED} icon={SendRoundedIcon} gradient={gradients.primary} glowColor={glow.primary} loading={statsLoading} />
              </Grid>
              <Grid item xs={6} sm={3}>
                <StatCard label="Approved" value={statusCounts.APPROVED} icon={CheckCircleRoundedIcon} gradient={gradients.success} glowColor={glow.success} loading={statsLoading} />
              </Grid>
              <Grid item xs={6} sm={3}>
                <StatCard label="Rejected" value={statusCounts.REJECTED} icon={CancelRoundedIcon} gradient={gradients.error} glowColor={glow.error} loading={statsLoading} />
              </Grid>
            </Grid>
          </Grid>
        </Grid>

        <Paper sx={{ p: 2 }}>
          <Stack spacing={2}>
            <Stack direction="row" spacing={2} alignItems="center">
              <FormControl sx={{ minWidth: 160 }}>
                <InputLabel>Status</InputLabel>
                <Select value={statusFilter} label="Status" onChange={(e) => { setStatusFilter(e.target.value as string); setPage(0); }}>
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="DRAFT">Draft</MenuItem>
                  <MenuItem value="SUBMITTED">Submitted</MenuItem>
                  <MenuItem value="UNDER_REVIEW">Under Review</MenuItem>
                  <MenuItem value="APPROVED">Approved</MenuItem>
                  <MenuItem value="REJECTED">Rejected</MenuItem>
                </Select>
              </FormControl>
            </Stack>

            <>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>ID</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Technician</TableCell>
                      <TableCell>Section</TableCell>
                      <TableCell>Equipment</TableCell>
                      <TableCell>Created</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  {loading ? (
                    <TableSkeleton rows={rowsPerPage > 10 ? 10 : rowsPerPage} columns={7} />
                  ) : items.length === 0 ? (
                    <TableBody>
                      <TableRow>
                        <TableCell colSpan={7} sx={{ border: 0 }}>
                          <EmptyState title="No checksheets found" message="Try adjusting the search or status filter." />
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  ) : (
                  <TableBody>
                    {items.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell>{item.id}</TableCell>
                        <TableCell>
                          <Box>
                            <StatusChip status={item.status} label={item.digital_signature ? 'Digitally Signed' : undefined} />
                            {item.digital_signature ? (
                              <Box sx={{ mt: 0.5 }}>
                                <SignatureBadge signature={item.digital_signature} />
                                <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.4 }}>
                                  {item.digital_signature.supervisor_name} · {formatIST(item.digital_signature.signing_timestamp)}
                                </Typography>
                              </Box>
                            ) : item.status === 'APPROVED' ? (
                              <Box sx={{ mt: 0.5 }}>
                                <LegacyApprovalBadge />
                              </Box>
                            ) : null}
                          </Box>
                        </TableCell>
                        <TableCell>{item.technician_name || item.technician_mobile}</TableCell>
                        <TableCell>{item.section_name ?? item.section_id}</TableCell>
                        <TableCell>{item.equipment_name ?? item.equipment_id}</TableCell>
                        <TableCell>{formatIST(item.created_at)}</TableCell>
                        <TableCell>
                          <Stack direction="row" spacing={1}>
                            {user?.role === 'Technician' && item.status === 'DRAFT' && (
                              <>
                                <IconButton size="small" onClick={() => openEdit(item)}><EditIcon /></IconButton>
                                <IconButton size="small" onClick={() => handleDelete(item)}><DeleteIcon /></IconButton>
                                <IconButton size="small" onClick={() => handleSubmit(item)}><SendIcon /></IconButton>
                              </>
                            )}
                            {user?.role === 'Supervisor' && (item.status === 'SUBMITTED' || item.status === 'UNDER_REVIEW') && (
                              <IconButton size="small" title="Review" onClick={() => openReview(item)}><VisibilityIcon /></IconButton>
                            )}
                            {user?.role === 'Admin' && (
                              <>
                                <IconButton size="small" onClick={() => openEdit(item)}><EditIcon /></IconButton>
                                {(item.status === 'DRAFT' || item.status === 'SUBMITTED' || item.status === 'UNDER_REVIEW') && (
                                  <IconButton size="small" onClick={() => handleDelete(item)}><DeleteIcon /></IconButton>
                                )}
                              </>
                            )}
                            {/* View/Download are available for every row regardless of status - the
                                backend generates the PDF on first request if one doesn't exist yet. */}
                            <IconButton size="small" title="View PDF" onClick={() => handleViewPdf(item)}><PictureAsPdfIcon /></IconButton>
                            <IconButton size="small" title="Download PDF" onClick={() => handleDownloadPdf(item)}><DownloadIcon /></IconButton>
                            {item.status === 'APPROVED' && (
                              <IconButton size="small" title="Regenerate PDF" onClick={() => handleRegeneratePdf(item)}><PictureAsPdfIcon /></IconButton>
                            )}
                          </Stack>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                  )}
                </Table>

                <TablePagination component="div" count={total} page={page} onPageChange={(_, p) => setPage(p)} rowsPerPage={rowsPerPage} onRowsPerPageChange={(e) => { setRowsPerPage(Number(e.target.value)); setPage(0); }} />
              </>
          </Stack>
        </Paper>

        <Dialog open={editDialogOpen} fullWidth maxWidth="md" onClose={() => setEditDialogOpen(false)}>
          <DialogTitle>Edit Checksheet</DialogTitle>
          <DialogContent>
            {selected ? <ChecksheetsForm currentUser={user} initial={selected} onSaved={handleEditSaved} /> : <CircularProgress />}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setEditDialogOpen(false)}>Close</Button>
          </DialogActions>
        </Dialog>

        <Dialog open={rejectDialogOpen} onClose={() => setRejectDialogOpen(false)}>
          <DialogTitle>Reject Checksheet</DialogTitle>
          <DialogContent>
            <TextField fullWidth multiline minRows={3} value={rejectReason} onChange={(e) => setRejectReason(e.target.value)} placeholder="Enter rejection reason" />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setRejectDialogOpen(false)}>Cancel</Button>
            <Button variant="contained" onClick={confirmReject}>Reject</Button>
          </DialogActions>
        </Dialog>

        <ChecksheetReviewDialog
          open={reviewDialogOpen}
          checksheet={reviewChecksheet}
          loading={reviewLoading}
          actionInProgress={actionInProgress}
          onClose={closeReview}
          onReject={() => reviewChecksheet && handleReject(reviewChecksheet)}
          onApproveV2={() => reviewChecksheet && handleApproveV2(reviewChecksheet)}
        />

        <DigitalSignatureDialogV2
          open={signDialogOpenV2}
          checksheet={signTargetV2}
          onClose={closeSignDialogV2}
          onSigned={handleSignedV2}
        />
      </Stack>
    </Box>
  );
}
