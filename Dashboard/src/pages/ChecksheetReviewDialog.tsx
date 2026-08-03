import { useState } from 'react';
import {
  Alert,
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  alpha,
  useTheme
} from '@mui/material';
import { motion } from 'framer-motion';
import ExpandMoreRoundedIcon from '@mui/icons-material/ExpandMoreRounded';
import CheckCircleRoundedIcon from '@mui/icons-material/CheckCircleRounded';
import CancelRoundedIcon from '@mui/icons-material/CancelRounded';
import VerifiedUserRoundedIcon from '@mui/icons-material/VerifiedUserRounded';
import ThumbDownRoundedIcon from '@mui/icons-material/ThumbDownRounded';
import type { ChecksheetItem } from '../types';
import { formatIST } from '../utils/formatDate';
import StatusChip from '../components/common/StatusChip';

interface ChecksheetReviewDialogProps {
  open: boolean;
  checksheet: ChecksheetItem | null;
  loading: boolean;
  actionInProgress: boolean;
  onClose: () => void;
  onReject: () => void;
  onApproveV2: () => void;
}

const FIELD_ROWS: Array<{ label: string; value: (c: ChecksheetItem) => string }> = [
  { label: 'Work Type', value: (c) => c.work_type || '-' },
  // Module 32: only ever set for Traction Motor checksheets - every other equipment shows '-'
  // here, consistent with how every other optional field row already renders.
  { label: 'Traction Motor Number', value: (c) => c.traction_motor_number || '-' },
  { label: 'Maintenance Type', value: (c) => c.maintenance_type || '-' },
  { label: 'Locomotive Number', value: (c) => c.locomotive_number || '-' },
  { label: 'Locomotive Type', value: (c) => c.locomotive_type || '-' },
  { label: 'Technology', value: (c) => c.technology || '-' },
  { label: 'Equipment', value: (c) => c.equipment_name || '-' },
  { label: 'Section', value: (c) => c.section_name || '-' },
  { label: 'Technician Name', value: (c) => c.technician_name || c.technician_mobile || '-' },
  { label: 'Employee ID', value: (c) => c.technician_employee_id || '-' },
  { label: 'Submission Date & Time', value: (c) => formatIST(c.submitted_at) }
];

/**
 * Read-only Supervisor Review screen (Module 29.8) - the only path to Approve/Reject for a
 * Supervisor is through here, replacing the old direct list-row Approve/Reject icon buttons.
 * Work Type is displayed exactly as the technician selected it on Android; nothing here is
 * editable, so there is no textbox for a Supervisor to alter it with.
 */
export default function ChecksheetReviewDialog({
  open,
  checksheet,
  loading,
  actionInProgress,
  onClose,
  onReject,
  onApproveV2
}: ChecksheetReviewDialogProps) {
  const theme = useTheme();
  const [detailsOpen, setDetailsOpen] = useState(true);
  const [pointsOpen, setPointsOpen] = useState(true);

  const checkingPoints = (checksheet?.values || [])
    .filter((v) => v.field_type !== 'group')
    .sort((a, b) => a.display_order - b.display_order);

  // Existing data only - `required` + presence of `field_value` is the one signal already carried
  // by ChecksheetValueDetailItem, so "missing a required observation" is the one badge that can be
  // shown honestly without fabricating a pass/fail verdict the backend never computed.
  const missingCount = checkingPoints.filter((p) => p.required && !p.field_value).length;

  const canDecide = checksheet?.status === 'SUBMITTED' || checksheet?.status === 'UNDER_REVIEW';

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="md">
      <DialogTitle>
        <Stack direction="row" alignItems="center" spacing={1.5}>
          <span>Review Checksheet{checksheet?.id ? ` #${checksheet.id}` : ''}</span>
          {checksheet ? <StatusChip status={checksheet.status} /> : null}
        </Stack>
      </DialogTitle>
      <DialogContent dividers>
        {loading || !checksheet ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Box>
            <Accordion
              expanded={detailsOpen}
              onChange={(_, exp) => setDetailsOpen(exp)}
              disableGutters
              sx={{ '&:before': { display: 'none' } }}
            >
              <AccordionSummary expandIcon={<ExpandMoreRoundedIcon />}>
                <Typography variant="subtitle1" fontWeight={700}>Checksheet Details</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  {FIELD_ROWS.map((row) => (
                    <Grid item xs={12} sm={6} key={row.label}>
                      <Typography variant="caption" color="text.secondary">{row.label}</Typography>
                      <Typography variant="body2" fontWeight={600}>{row.value(checksheet)}</Typography>
                    </Grid>
                  ))}
                </Grid>
              </AccordionDetails>
            </Accordion>

            <Accordion
              expanded={pointsOpen}
              onChange={(_, exp) => setPointsOpen(exp)}
              disableGutters
              sx={{ '&:before': { display: 'none' }, mt: 1.5 }}
            >
              <AccordionSummary expandIcon={<ExpandMoreRoundedIcon />}>
                <Stack direction="row" alignItems="center" spacing={1.5}>
                  <Typography variant="subtitle1" fontWeight={700}>Checking Points</Typography>
                  {missingCount > 0 ? (
                    <Box
                      component="span"
                      sx={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 0.5,
                        px: 1,
                        py: 0.2,
                        borderRadius: 999,
                        fontSize: '0.7rem',
                        fontWeight: 700,
                        color: theme.palette.error.main,
                        bgcolor: alpha(theme.palette.error.main, theme.palette.mode === 'dark' ? 0.16 : 0.1),
                        border: `1px solid ${alpha(theme.palette.error.main, 0.35)}`
                      }}
                    >
                      <CancelRoundedIcon sx={{ fontSize: 13 }} /> {missingCount} missing
                    </Box>
                  ) : (
                    <Box
                      component="span"
                      sx={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 0.5,
                        px: 1,
                        py: 0.2,
                        borderRadius: 999,
                        fontSize: '0.7rem',
                        fontWeight: 700,
                        color: theme.palette.success.main,
                        bgcolor: alpha(theme.palette.success.main, theme.palette.mode === 'dark' ? 0.16 : 0.1),
                        border: `1px solid ${alpha(theme.palette.success.main, 0.35)}`
                      }}
                    >
                      <CheckCircleRoundedIcon sx={{ fontSize: 13 }} /> All complete
                    </Box>
                  )}
                </Stack>
              </AccordionSummary>
              <AccordionDetails>
                {checkingPoints.length === 0 ? (
                  <Alert severity="info">No checking points recorded for this checksheet.</Alert>
                ) : (
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Sr. No.</TableCell>
                          <TableCell>Checking Point Details</TableCell>
                          <TableCell>Standard</TableCell>
                          <TableCell>Authority</TableCell>
                          <TableCell>Observation</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {checkingPoints.map((point, index) => {
                          const missing = point.required && !point.field_value;
                          return (
                            <motion.tr
                              key={point.field_id}
                              initial={{ opacity: 0, y: 4 }}
                              animate={{ opacity: 1, y: 0 }}
                              transition={{ duration: 0.2, delay: Math.min(index * 0.015, 0.3) }}
                              style={{
                                display: 'table-row',
                                backgroundColor: missing ? alpha(theme.palette.error.main, theme.palette.mode === 'dark' ? 0.08 : 0.05) : 'transparent'
                              }}
                            >
                              <TableCell>{point.display_order}</TableCell>
                              <TableCell>{point.field_label}</TableCell>
                              <TableCell>{point.standard_value || '-'}</TableCell>
                              <TableCell>{point.authority_reference || '-'}</TableCell>
                              <TableCell sx={{ color: missing ? 'error.main' : undefined, fontWeight: missing ? 700 : undefined }}>
                                {point.field_value || (missing ? 'Missing' : '-')}
                              </TableCell>
                            </motion.tr>
                          );
                        })}
                      </TableBody>
                    </Table>
                  </TableContainer>
                )}
              </AccordionDetails>
            </Accordion>

            {checksheet.status === 'REJECTED' && checksheet.rejection_reason ? (
              <Alert severity="error" sx={{ mt: 2 }}>Rejection reason: {checksheet.rejection_reason}</Alert>
            ) : null}
          </Box>
        )}
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 3 }}>
        <Button onClick={onClose} disabled={actionInProgress}>Close</Button>
        {canDecide ? (
          <>
            <motion.div whileHover={{ scale: actionInProgress || loading ? 1 : 1.03 }} whileTap={{ scale: actionInProgress || loading ? 1 : 0.97 }}>
              <Button color="error" variant="outlined" startIcon={<ThumbDownRoundedIcon />} onClick={onReject} disabled={actionInProgress || loading}>
                Reject
              </Button>
            </motion.div>
            <motion.div whileHover={{ scale: actionInProgress || loading ? 1 : 1.03 }} whileTap={{ scale: actionInProgress || loading ? 1 : 0.97 }}>
              <Button color="primary" variant="contained" startIcon={<VerifiedUserRoundedIcon />} onClick={onApproveV2} disabled={actionInProgress || loading}>
                Approve &amp; Sign (emBridge)
              </Button>
            </motion.div>
          </>
        ) : null}
      </DialogActions>
    </Dialog>
  );
}
