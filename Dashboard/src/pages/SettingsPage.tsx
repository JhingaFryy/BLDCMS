import { useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Avatar,
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  Paper,
  Stack,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
  CircularProgress
} from '@mui/material';
import {
  Brightness4,
  Brightness7,
  CheckCircle,
  Error as ErrorIcon,
  Logout,
  SettingsBrightness,
  WifiTethering
} from '@mui/icons-material';
import api, { getApiBaseUrlLabel } from '../api/client';
import { authService } from '../services/authService';
import { apiService } from '../services/apiService';
import { useAuth } from '../contexts/AuthContext';
import { useThemeMode } from '../contexts/ThemeModeContext';
import packageJson from '../../package.json';

const DASHBOARD_VERSION = packageJson.version;
const ORGANIZATION_NAME = 'BL- Digital Checksheet Management System';

type ConnectionStatus = 'idle' | 'testing' | 'connected' | 'unreachable';

function GeneralSection() {
  const { preference, setPreference } = useThemeMode();

  return (
    <Card>
      <CardHeader title="General" />
      <Divider />
      <CardContent>
        <Stack spacing={1.5}>
          <Typography variant="subtitle2">Theme</Typography>
          <ToggleButtonGroup
            value={preference}
            exclusive
            onChange={(_, value) => value && setPreference(value)}
            color="primary"
          >
            <ToggleButton value="system">
              <SettingsBrightness sx={{ mr: 1 }} fontSize="small" /> System
            </ToggleButton>
            <ToggleButton value="light">
              <Brightness7 sx={{ mr: 1 }} fontSize="small" /> Light
            </ToggleButton>
            <ToggleButton value="dark">
              <Brightness4 sx={{ mr: 1 }} fontSize="small" /> Dark
            </ToggleButton>
          </ToggleButtonGroup>
          <Typography variant="body2" color="text.secondary">
            "System" follows your device or browser's light/dark preference automatically.
          </Typography>
        </Stack>
      </CardContent>
    </Card>
  );
}

function AccountSection() {
  const { user, logout } = useAuth();
  const [profileOpen, setProfileOpen] = useState(false);

  return (
    <Card>
      <CardHeader title="Account" />
      <Divider />
      <CardContent>
        <Stack spacing={2}>
          <Stack direction="row" spacing={2} alignItems="center">
            <Avatar sx={{ bgcolor: 'primary.main' }}>{user?.name?.charAt(0)?.toUpperCase() ?? 'U'}</Avatar>
            <Box>
              <Typography variant="subtitle1" fontWeight={700}>{user?.name ?? 'User'}</Typography>
              <Typography variant="body2" color="text.secondary">{user?.role} · {user?.employeeId}</Typography>
            </Box>
          </Stack>

          <Stack direction="row" spacing={1.5} flexWrap="wrap" useFlexGap>
            <Button variant="outlined" onClick={() => setProfileOpen(true)}>View Profile</Button>
            <Button variant="outlined" disabled>Change Password</Button>
            <Button variant="outlined" color="error" startIcon={<Logout />} onClick={logout}>Logout</Button>
          </Stack>
          <Typography variant="caption" color="text.secondary">
            Change Password is not available yet - self-service password changes require a backend
            endpoint that does not exist. Contact an administrator to reset your password.
          </Typography>
        </Stack>
      </CardContent>

      <Dialog open={profileOpen} onClose={() => setProfileOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle>My Profile</DialogTitle>
        <DialogContent dividers>
          <Stack spacing={1.5}>
            <ProfileRow label="Name" value={user?.name} />
            <ProfileRow label="Employee ID" value={user?.employeeId} />
            <ProfileRow label="Role" value={user?.role} />
            <ProfileRow label="Email" value={user?.email} />
            <ProfileRow label="Mobile" value={user?.mobile} />
            <ProfileRow label="Section" value={user?.section_name ?? undefined} />
            <ProfileRow label="Status" value={user?.status} />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setProfileOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
}

function ProfileRow({ label, value }: { label: string; value?: string | null }) {
  return (
    <Stack direction="row" justifyContent="space-between">
      <Typography variant="body2" color="text.secondary">{label}</Typography>
      <Typography variant="body2" fontWeight={600}>{value?.trim() ? value : '-'}</Typography>
    </Stack>
  );
}

function SystemSection() {
  const [status, setStatus] = useState<ConnectionStatus>('idle');
  const [backendVersion, setBackendVersion] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    api.get('/openapi.json')
      .then((response) => {
        if (cancelled) return;
        const version = (response.data as { info?: { version?: string } } | undefined)?.info?.version;
        setBackendVersion(typeof version === 'string' && version ? version : null);
      })
      .catch(() => {
        if (!cancelled) setBackendVersion(null);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const testConnection = async () => {
    setStatus('testing');
    try {
      await authService.me();
      setStatus('connected');
    } catch (error) {
      // Any HTTP response (even 401/403/500) still proves the backend itself is reachable - only
      // a network-level failure (no response at all) means it's actually unreachable.
      const hasResponse = typeof error === 'object' && error !== null && 'response' in error && (error as { response?: unknown }).response;
      setStatus(hasResponse ? 'connected' : 'unreachable');
    }
  };

  const statusChip = useMemo(() => {
    switch (status) {
      case 'testing':
        return <Chip icon={<CircularProgress size={14} />} label="Testing..." />;
      case 'connected':
        return <Chip icon={<CheckCircle />} label="Connected" color="success" />;
      case 'unreachable':
        return <Chip icon={<ErrorIcon />} label="Unreachable" color="error" />;
      default:
        return <Chip label="Not tested" variant="outlined" />;
    }
  }, [status]);

  return (
    <Card>
      <CardHeader title="System" />
      <Divider />
      <CardContent>
        <Stack spacing={2}>
          <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap" useFlexGap>
            <Button variant="outlined" startIcon={<WifiTethering />} onClick={testConnection} disabled={status === 'testing'}>
              Test Backend Connection
            </Button>
            {statusChip}
          </Stack>

          <ProfileRow label="Backend URL" value={getApiBaseUrlLabel()} />
          <ProfileRow label="Dashboard Version" value={DASHBOARD_VERSION} />
          <ProfileRow label="Backend Version" value={backendVersion ?? 'Not available'} />
        </Stack>
      </CardContent>
    </Card>
  );
}

const DSC_SETTING_KEYS = {
  caBundlePath: 'dsc.trusted_ca_bundle_path',
  enableRevocationCheck: 'dsc.enable_revocation_check'
} as const;

/**
 * Digital Signature trust configuration. Admin-only, reused entirely off the existing generic
 * system_settings key/value store (same GET/PUT /settings/{key} every other setting uses).
 *
 * Cryptographic signing happens on the supervisor's own Windows PC, against their Class-III DSC
 * on a USB token (ProxKey or another emBridge-compatible token), via eMudhra emBridge/CryptoID -
 * never on this server. These two settings govern only this backend's independent verification of
 * the signed PDF it receives back.
 */
function SignatureTrustSettingsSection() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [values, setValues] = useState<Record<string, string>>({
    [DSC_SETTING_KEYS.caBundlePath]: '',
    [DSC_SETTING_KEYS.enableRevocationCheck]: 'false'
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (user?.role !== 'Admin') return;
    let mounted = true;
    apiService.getSettings()
      .then((res) => {
        if (!mounted) return;
        setValues((current) => {
          const next = { ...current };
          for (const item of res.data.items) {
            if (item.key in next) next[item.key] = item.value ?? '';
          }
          return next;
        });
      })
      .catch(() => setError('Unable to load Digital Signature settings.'))
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [user?.role]);

  if (user?.role !== 'Admin') return null;

  const setField = (key: string, value: string) => {
    setValues((current) => ({ ...current, [key]: value }));
    setSaved(false);
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      await Promise.all(
        Object.entries(values).map(([key, value]) => apiService.updateSetting(key, { value }))
      );
      setSaved(true);
    } catch {
      setError('Unable to save Digital Signature settings.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Card>
      <CardHeader title="Digital Signature Trust Settings" />
      <Divider />
      <CardContent>
        <Stack spacing={2}>
          <Typography variant="body2" color="text.secondary">
            Approving a checksheet always signs it with the supervisor's own Class-III Digital
            Signature Certificate on a USB token (ProxKey or another emBridge-compatible token),
            signed locally on the supervisor's own Windows PC via eMudhra emBridge and CryptoID
            middleware - this server never has access to that token. The settings below govern
            only this backend's independent verification of the signed PDF it receives back.
          </Typography>
          {loading ? (
            <CircularProgress size={22} />
          ) : (
            <Stack spacing={1.5}>
              <TextField
                label="Trusted CA Bundle Path (optional)"
                size="small"
                fullWidth
                value={values[DSC_SETTING_KEYS.caBundlePath]}
                onChange={(e) => setField(DSC_SETTING_KEYS.caBundlePath, e.target.value)}
                helperText="PEM file with your DSC vendor's root/intermediate CA certificates, for full chain-of-trust verification."
              />
              <ToggleButtonGroup
                value={values[DSC_SETTING_KEYS.enableRevocationCheck] === 'true' ? 'on' : 'off'}
                exclusive
                onChange={(_, v) => v && setField(DSC_SETTING_KEYS.enableRevocationCheck, v === 'on' ? 'true' : 'false')}
                size="small"
              >
                <ToggleButton value="off">Revocation Check: Off</ToggleButton>
                <ToggleButton value="on">Revocation Check: On (requires internet)</ToggleButton>
              </ToggleButtonGroup>
              {error ? <Alert severity="error">{error}</Alert> : null}
              {saved ? <Alert severity="success">Digital Signature settings saved.</Alert> : null}
              <Box>
                <Button variant="contained" onClick={handleSave} disabled={saving}>
                  {saving ? <CircularProgress size={18} color="inherit" /> : 'Save'}
                </Button>
              </Box>
            </Stack>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}

function AboutSection() {
  return (
    <Card>
      <CardHeader title="About" />
      <Divider />
      <CardContent>
        <Stack spacing={1.5}>
          <ProfileRow label="Application Version" value={DASHBOARD_VERSION} />
          {/* CHANGE_ME: replace with this deployment's own shed/organization name */}
          <ProfileRow label="Organization Name" value="YOUR_SHED_NAME" />
          <ProfileRow label="Copyright" value={`© ${new Date().getFullYear()} ${ORGANIZATION_NAME}. All rights reserved.`} />
        </Stack>
      </CardContent>
    </Card>
  );
}

function AuthoritiesSection() {
  return (
    <Card>
      <CardHeader title="Authorities" />
      <Divider />
      <CardContent>
        <Stack spacing={2}>
          <Stack spacing={1.5}>
            <Typography variant="subtitle2" color="text.secondary">Approving Authorities</Typography>
            <ProfileRow label="Sr. Divisional Electrical Engineer/TRS/BL" value="Mr. R. C. Meena" />
            <ProfileRow label="Divisional Electrical Engineer" value="Mr. Suresh Kumar" />
          </Stack>
          <Divider />
          <Stack spacing={1.5}>
            <Typography variant="subtitle2" color="text.secondary">Developed By</Typography>
            <ProfileRow label="Tech-III" value="Mr. Jatin Pardeshi" />
            <ProfileRow label="Tech-II" value="Mr. Neelkumar Patel" />
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );
}

export default function SettingsPage() {
  return (
    <Box>
      <Stack spacing={2.5}>
        <Paper sx={{ p: 3, borderRadius: 3 }}>
          <Typography variant="h4" fontWeight={700} mb={1}>Settings</Typography>
          <Typography variant="body1" color="text.secondary">Manage your preferences, account, and view system information.</Typography>
        </Paper>

        <GeneralSection />
        <AccountSection />
        <SignatureTrustSettingsSection />
        <SystemSection />
        <AboutSection />
        <AuthoritiesSection />
      </Stack>
    </Box>
  );
}
