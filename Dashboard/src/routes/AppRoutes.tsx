import { Navigate, Route, Routes } from 'react-router-dom';
import LoginPage from '../pages/LoginPage';
import DashboardPage from '../pages/DashboardPage';
import ProtectedRoute from '../components/ProtectedRoute';
import NotFoundPage from '../pages/NotFoundPage';
import ForbiddenPage from '../pages/ForbiddenPage';
import AppLayout from '../components/AppLayout';
import UsersPage from '../pages/UsersPage';
import SectionsPage from '../pages/SectionsPage';
import LocomotivesPage from '../pages/LocomotivesPage';
import EquipmentPage from '../pages/EquipmentPage';
import TemplatesPage from '../pages/TemplatesPage';
import TemplateFieldsPage from '../pages/TemplateFieldsPage';
import MappingPage from '../pages/MappingPage';
import ChecksheetsPage from '../pages/ChecksheetsPage';
import ReportsPage from '../pages/ReportsPage';
import SettingsPage from '../pages/SettingsPage';
import SystemHealthPage from '../pages/SystemHealthPage';
import ActivityTimelinePage from '../pages/ActivityTimelinePage';
import OtpLogsPage from '../pages/OtpLogsPage';
import type { UserRole } from '../types';

// The default for every dashboard route - a Technician is never given a session at all (see
// AuthContext.login), but this is enforced again here at the route level as defense in depth per
// Requirement 5: hiding a sidebar link is not access control, only this is.
const STAFF_ROLES: UserRole[] = ['Admin', 'Supervisor'];
const ADMIN_ONLY: UserRole[] = ['Admin'];

const ProtectedLayout = ({ children, allowedRoles = STAFF_ROLES }: { children: React.ReactNode; allowedRoles?: UserRole[] }) => (
  <ProtectedRoute allowedRoles={allowedRoles}>
    <AppLayout>{children}</AppLayout>
  </ProtectedRoute>
);

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/forbidden" element={<ForbiddenPage />} />
      <Route path="/dashboard" element={<ProtectedLayout><DashboardPage /></ProtectedLayout>} />
      <Route path="/users" element={<ProtectedLayout allowedRoles={ADMIN_ONLY}><UsersPage /></ProtectedLayout>} />
      <Route path="/sections" element={<ProtectedLayout allowedRoles={ADMIN_ONLY}><SectionsPage /></ProtectedLayout>} />
      <Route path="/locomotives" element={<ProtectedLayout><LocomotivesPage /></ProtectedLayout>} />
      <Route path="/equipment" element={<ProtectedLayout><EquipmentPage /></ProtectedLayout>} />
      <Route path="/templates" element={<ProtectedLayout><TemplatesPage /></ProtectedLayout>} />
      <Route path="/template-fields" element={<ProtectedLayout allowedRoles={ADMIN_ONLY}><TemplateFieldsPage /></ProtectedLayout>} />
      <Route path="/section-equipment-map" element={<ProtectedLayout allowedRoles={ADMIN_ONLY}><MappingPage /></ProtectedLayout>} />
      <Route path="/checksheets" element={<ProtectedLayout><ChecksheetsPage /></ProtectedLayout>} />
      <Route path="/reports" element={<ProtectedLayout><ReportsPage /></ProtectedLayout>} />
      <Route path="/settings" element={<ProtectedLayout><SettingsPage /></ProtectedLayout>} />
      <Route path="/system-health" element={<ProtectedLayout allowedRoles={ADMIN_ONLY}><SystemHealthPage /></ProtectedLayout>} />
      {/* Module 30: Admin-only ("Audit Logs") - a Supervisor previously saw this section-scoped
          per Module 29, but that access is explicitly revoked here. */}
      <Route path="/activity-timeline" element={<ProtectedLayout allowedRoles={ADMIN_ONLY}><ActivityTimelinePage /></ProtectedLayout>} />
      <Route path="/otp-logs" element={<ProtectedLayout><OtpLogsPage /></ProtectedLayout>} />
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
