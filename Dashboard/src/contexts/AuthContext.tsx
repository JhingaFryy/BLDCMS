import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { flushSync } from 'react-dom';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { authService } from '../services/authService';
import { storage } from '../utils/storage';
import type { LoginPayload, UserProfile, UserRole } from '../types';

interface AuthContextValue {
  user: UserProfile | null;
  role: UserRole | null;
  loading: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  logout: () => void;
  isAuthorized: (roles: UserRole[]) => boolean;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const normalizeRole = (role: unknown): UserRole => {
  if (typeof role === 'string') {
    const normalized = role.toLowerCase();
    if (normalized === 'admin') return 'Admin';
    if (normalized === 'supervisor') return 'Supervisor';
  }
  return 'Technician';
};

const normalizeUserProfile = (payload: unknown): UserProfile => {
  const raw = (payload && typeof payload === 'object' && 'user' in payload ? (payload as { user?: unknown }).user : payload) as Record<string, unknown> | null;
  const source = raw ?? {};

  const employeeId = [source.employee_id, source.employeeId, source.id, source.employee_number, source.username]
    .find((value): value is string => typeof value === 'string' && value.length > 0) ?? '';

  const nameValue = [source.name, source.full_name, source.fullName]
    .find((value): value is string => typeof value === 'string' && value.length > 0);

  const firstName = typeof source.first_name === 'string' ? source.first_name : '';
  const lastName = typeof source.last_name === 'string' ? source.last_name : '';
  const computedName = [nameValue, [firstName, lastName].filter(Boolean).join(' ').trim() || undefined, employeeId || undefined]
    .find((value): value is string => typeof value === 'string' && value.length > 0) ?? 'User';

  return {
    id: String(source.id ?? employeeId ?? ''),
    employeeId: String(employeeId),
    name: String(computedName),
    email: typeof source.email === 'string' ? source.email : '',
    mobile: typeof source.mobile === 'string' ? source.mobile : (typeof source.phone === 'string' ? source.phone : ''),
    role: normalizeRole(source.role),
    status: (typeof source.status === 'string' && ['Active', 'Inactive', 'Pending'].includes(source.status) ? source.status : 'Active') as UserProfile['status'],
    section_id: typeof source.section_id === 'number' ? source.section_id : (typeof source.sectionId === 'number' ? source.sectionId : (typeof source.section_id === 'string' ? Number(source.section_id) : undefined)),
    section_name: typeof source.section_name === 'string' ? source.section_name : (typeof source.sectionName === 'string' ? source.sectionName : undefined)
  };
};

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const storedUser = storage.getUser();
    if (storedUser) {
      setUser(storedUser as UserProfile);
    }
    setLoading(false);
  }, []);

  const login = async (payload: LoginPayload) => {
    setLoading(true);
    try {
      const response = await authService.login({ employee_id: payload.employee_id, password: payload.password });
      const token = response.data.access_token || response.data.accessToken;

      if (!token) {
        throw new Error('No access token received from backend');
      }

      storage.setToken(token);

      const meResponse = await authService.me();
      const authUser = normalizeUserProfile(meResponse.data);

      if (authUser.role === 'Technician') {
        // No dashboard session is created for Technicians - undo the token we just stored and
        // leave the user on the login screen (we're already there; there is nothing to navigate).
        storage.clearToken();
        storage.clearUser();
        setLoading(false);
        toast.error('Dashboard access is restricted to Administrators and Supervisors.');
        return;
      }

      flushSync(() => {
        storage.setUser(authUser);
        setUser(authUser);
        setLoading(false);
      });

      toast.success(`Welcome back, ${authUser.name || payload.employee_id}`);
      navigate('/dashboard');
    } catch {
      setLoading(false);
      toast.error('Unable to sign in. Please verify the backend service.');
    }
  };

  const logout = () => {
    storage.clearToken();
    storage.clearUser();
    setUser(null);
    navigate('/login');
  };

  const role = user?.role ?? null;
  const isAuthorized = (roles: UserRole[]) => !!user && roles.includes(user.role);

  const value = useMemo(() => ({ user, role, loading, login, logout, isAuthorized }), [user, role, loading]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}
