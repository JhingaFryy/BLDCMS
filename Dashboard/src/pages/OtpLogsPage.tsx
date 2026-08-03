import { useEffect, useState } from 'react';
import {
  Alert,
  Box,
  Chip,
  CircularProgress,
  Paper,
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
import { Search } from '@mui/icons-material';
import { apiService } from '../services/apiService';
import { useAuth } from '../contexts/AuthContext';
import { formatIST } from '../utils/formatDate';
import type { OtpLogItem } from '../types';

const PAGE_SIZE_OPTIONS = [10, 25, 50];

export default function OtpLogsPage() {
  const { user } = useAuth();
  const [items, setItems] = useState<OtpLogItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [search, setSearch] = useState('');

  const load = async (skip: number, limit: number, searchTerm: string) => {
    setLoading(true);
    try {
      // Module 30: no section_id is ever sent from here - a Supervisor is restricted to their own
      // section entirely on the backend (see app/services/otp_service.get_otp_logs), so there is
      // nothing for the Dashboard to additionally filter or hide.
      const response = await apiService.getOtpLogs({ skip, limit, search: searchTerm || undefined });
      setItems(response.data.items);
      setTotal(response.data.total);
      setError(null);
    } catch (err) {
      const response = (err as { response?: { data?: { detail?: string } } }).response;
      setError(response?.data?.detail || 'Unable to load OTP logs from the backend.');
      setItems([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load(page * rowsPerPage, rowsPerPage, search);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, rowsPerPage]);

  useEffect(() => {
    const timeout = setTimeout(() => {
      setPage(0);
      load(0, rowsPerPage, search);
    }, 300);
    return () => clearTimeout(timeout);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search]);

  return (
    <Box>
      <Stack spacing={2.5}>
        <Paper sx={{ p: 3, borderRadius: 3 }}>
          <Typography variant="h4" fontWeight={700} mb={1}>OTP Logs</Typography>
          <Typography variant="body1" color="text.secondary">
            {user?.role === 'Supervisor'
              ? 'OTP generation and verification history for users in your section. The OTP code is shown here so it can be relayed directly, without a separate SMS service.'
              : 'OTP generation and verification history for all users. The OTP code is shown here so it can be relayed directly, without a separate SMS service.'}
          </Typography>
        </Paper>

        <Paper sx={{ p: 2 }}>
          <TextField
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search by employee ID or name"
            size="small"
            InputProps={{ startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} fontSize="small" /> }}
            sx={{ width: { xs: '100%', sm: 360 } }}
          />
        </Paper>

        {error ? <Alert severity="error">{error}</Alert> : null}

        <Paper sx={{ borderRadius: 3, overflow: 'hidden' }}>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}>
              <CircularProgress />
            </Box>
          ) : items.length === 0 ? (
            <Box sx={{ p: 5, textAlign: 'center' }}>
              <Typography variant="h6" fontWeight={700} mb={1}>No OTP logs found</Typography>
              <Typography variant="body2" color="text.secondary">
                {user?.role === 'Supervisor' ? 'No OTP activity for your section yet.' : 'Adjust your search to see results.'}
              </Typography>
            </Box>
          ) : (
            <>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Employee ID</TableCell>
                      <TableCell>Name</TableCell>
                      <TableCell>Section</TableCell>
                      <TableCell>OTP</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Attempts</TableCell>
                      <TableCell>Generated At (IST)</TableCell>
                      <TableCell>Expires At (IST)</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {items.map((item) => (
                      <TableRow key={item.id} hover>
                        <TableCell>{item.employee_id ?? '—'}</TableCell>
                        <TableCell>{item.user_name ?? '—'}</TableCell>
                        <TableCell>{item.section_name ?? '—'}</TableCell>
                        <TableCell>
                          {item.otp ? (
                            <Typography component="span" fontFamily="monospace" fontWeight={700} letterSpacing={1}>
                              {item.otp}
                            </Typography>
                          ) : '—'}
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={item.is_verified ? 'Verified' : 'Pending'}
                            color={item.is_verified ? 'success' : 'default'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{item.attempts}</TableCell>
                        <TableCell>{formatIST(item.created_at)}</TableCell>
                        <TableCell>{formatIST(item.expires_at)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              <TablePagination
                component="div"
                count={total}
                page={page}
                rowsPerPage={rowsPerPage}
                onPageChange={(_, nextPage) => setPage(nextPage)}
                onRowsPerPageChange={(event) => { setRowsPerPage(parseInt(event.target.value, 10)); setPage(0); }}
                rowsPerPageOptions={PAGE_SIZE_OPTIONS}
              />
            </>
          )}
        </Paper>
      </Stack>
    </Box>
  );
}
