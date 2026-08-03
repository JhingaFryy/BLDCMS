import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import type { UserRole } from '../types';

interface ProtectedRouteProps {
  children: React.ReactNode;
  /**
   * When provided, the current user's role must be included or they are redirected to /forbidden.
   * This is the server-of-truth check behind every protected route - the sidebar only hides menu
   * items as a UX convenience, it is never the only thing standing between a role and a route.
   */
  allowedRoles?: UserRole[];
}

export default function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const { user, loading } = useAuth();

  if (loading) return null;
  if (!user) return <Navigate to="/login" replace />;
  if (allowedRoles && !allowedRoles.includes(user.role)) return <Navigate to="/forbidden" replace />;

  return <>{children}</>;
}
