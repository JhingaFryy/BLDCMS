import { useEffect, useMemo, useState, type ReactNode } from 'react';
import { Link as RouterLink, useLocation, useNavigate } from 'react-router-dom';
import {
  AppBar,
  Avatar,
  Box,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Stack,
  Toolbar,
  Tooltip,
  Typography,
  alpha,
  useMediaQuery,
  useTheme
} from '@mui/material';
import { motion } from 'framer-motion';
import {
  Assessment,
  ChevronLeftRounded,
  DashboardRounded,
  FactCheck,
  Groups,
  History,
  LibraryBooks,
  LocalShipping,
  Logout,
  Menu as MenuIcon,
  MonitorHeart,
  NotificationsRounded,
  PrecisionManufacturing,
  Settings,
  SettingsRounded,
  TableRows,
  ViewModule,
  VpnKey
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import GlobalSearch from './GlobalSearch';
import PageTransition from './common/PageTransition';
import { gradients } from '../theme/palette';
import logo from '../../logo.png';

const drawerWidth = 280;
const collapsedWidth = 84;
const SIDEBAR_COLLAPSED_KEY = 'rdcms.sidebarCollapsed';

const navItems = [
  { label: 'Dashboard', path: '/dashboard', icon: <DashboardRounded />, adminOnly: false },
  { label: 'Users', path: '/users', icon: <Groups />, adminOnly: true },
  { label: 'Sections', path: '/sections', icon: <ViewModule />, adminOnly: true },
  { label: 'Locomotives', path: '/locomotives', icon: <LocalShipping />, adminOnly: false },
  { label: 'Equipment', path: '/equipment', icon: <PrecisionManufacturing />, adminOnly: false },
  { label: 'Templates', path: '/templates', icon: <LibraryBooks />, adminOnly: false },
  { label: 'Template Fields', path: '/template-fields', icon: <TableRows />, adminOnly: true },
  { label: 'Section–Equipment Mapping', path: '/section-equipment-map', icon: <FactCheck />, adminOnly: true },
  { label: 'Checksheets', path: '/checksheets', icon: <FactCheck />, adminOnly: false },
  { label: 'Reports', path: '/reports', icon: <Assessment />, adminOnly: false },
  { label: 'Settings', path: '/settings', icon: <Settings />, adminOnly: false },
  { label: 'System Health', path: '/system-health', icon: <MonitorHeart />, adminOnly: true },
  // Module 30: Activity Timeline ("Audit Logs") is now Admin-only - a Supervisor previously saw
  // this (section-scoped) per Module 29, but that access is explicitly revoked here.
  { label: 'Activity Timeline', path: '/activity-timeline', icon: <History />, adminOnly: true },
  { label: 'OTP Logs', path: '/otp-logs', icon: <VpnKey />, adminOnly: false }
];

interface AppLayoutProps {
  children: ReactNode;
}

export default function AppLayout({ children }: AppLayoutProps) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(() => localStorage.getItem(SIDEBAR_COLLAPSED_KEY) === 'true');
  const [profileAnchor, setProfileAnchor] = useState<HTMLElement | null>(null);
  const [notifAnchor, setNotifAnchor] = useState<HTMLElement | null>(null);
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    localStorage.setItem(SIDEBAR_COLLAPSED_KEY, String(collapsed));
  }, [collapsed]);

  const currentTitle = useMemo(() => {
    const current = navItems.find((item) => location.pathname === item.path);
    return current?.label ?? 'Dashboard';
  }, [location.pathname]);

  // Hidden completely for non-admins, not merely disabled - a Supervisor never sees these links at
  // all. This is a UX convenience only; the actual access control lives in each route's
  // allowedRoles (see AppRoutes.tsx) and is enforced regardless of what the sidebar shows.
  const visibleNavItems = useMemo(
    () => navItems.filter((item) => !item.adminOnly || user?.role === 'Admin'),
    [user?.role]
  );

  const handleDrawerToggle = () => setMobileOpen((open) => !open);
  const isCollapsed = collapsed && !isMobile;

  const handleLogout = () => {
    setProfileAnchor(null);
    logout();
    setMobileOpen(false);
  };

  const roleBadgeColor = user?.role === 'Admin' ? theme.palette.warning.main : theme.palette.secondary.main;

  const drawerContent = (
    <Box
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        color: '#E7EDFB',
        background: gradients.navy,
        borderRight: `1px solid ${alpha('#22314E', 0.9)}`,
      }}
    >
      <Toolbar sx={{ px: isCollapsed ? 1.5 : 2.5, py: 1.5, justifyContent: isCollapsed ? 'center' : 'flex-start' }}>
        <Stack direction="row" spacing={1.2} alignItems="center" sx={{ overflow: 'hidden' }}>
          <Box component="img" src={logo} alt="BL-DCMS logo" sx={{ width: { xs: 38, sm: 42 }, height: 'auto', objectFit: 'contain', flexShrink: 0 }} />
          {!isCollapsed && (
            <Box sx={{ overflow: 'hidden' }}>
              <Typography variant="subtitle1" fontWeight={800} noWrap>BL-DCMS</Typography>
              <Typography variant="caption" sx={{ opacity: 0.75 }} noWrap>For Admins only</Typography>
            </Box>
          )}
        </Stack>
        {!isMobile && (
          <IconButton
            size="small"
            onClick={() => setCollapsed((c) => !c)}
            sx={{
              ml: 'auto',
              color: 'rgba(255,255,255,0.7)',
              transform: isCollapsed ? 'rotate(180deg)' : 'none',
              transition: 'transform 220ms ease',
              display: isCollapsed ? 'none' : 'inline-flex',
            }}
          >
            <ChevronLeftRounded fontSize="small" />
          </IconButton>
        )}
      </Toolbar>
      <Divider sx={{ borderColor: 'rgba(255,255,255,0.1)' }} />

      {!isCollapsed && (
        <Box sx={{ px: 2.5, py: 2 }}>
          <Stack direction="row" spacing={1.5} alignItems="center">
            <Avatar sx={{ background: gradients.primary, color: '#fff', fontWeight: 700 }}>
              {user?.name?.charAt(0)?.toUpperCase() ?? 'A'}
            </Avatar>
            <Box minWidth={0}>
              <Typography variant="subtitle2" fontWeight={700} noWrap>
                {user?.name ?? 'Administrator'}
              </Typography>
              <Typography variant="caption" sx={{ opacity: 0.7 }} noWrap>
                {user?.role ?? 'Admin'}
              </Typography>
            </Box>
          </Stack>
        </Box>
      )}
      <Divider sx={{ borderColor: 'rgba(255,255,255,0.1)' }} />

      <List sx={{ px: isCollapsed ? 0.75 : 1.2, py: 1, flexGrow: 1, overflowY: 'auto', overflowX: 'hidden' }}>
        {visibleNavItems.map((item) => {
          const selected = location.pathname === item.path || (item.path === '/dashboard' && location.pathname.startsWith('/dashboard'));
          const button = (
            <ListItemButton
              key={item.path}
              component={RouterLink}
              to={item.path}
              selected={selected}
              onClick={() => setMobileOpen(false)}
              sx={{
                position: 'relative',
                borderRadius: 2.5,
                mb: 0.5,
                overflow: 'hidden',
                justifyContent: isCollapsed ? 'center' : 'flex-start',
                px: isCollapsed ? 1.5 : 2,
                color: selected ? '#fff' : 'rgba(231,237,251,0.75)',
                '&:hover': { bgcolor: 'rgba(255,255,255,0.08)' },
                '&.Mui-selected': { bgcolor: 'transparent' },
                '&.Mui-selected:hover': { bgcolor: 'rgba(255,255,255,0.08)' },
              }}
            >
              {selected && (
                <motion.div
                  layoutId="nav-active-pill"
                  transition={{ type: 'spring', stiffness: 420, damping: 34 }}
                  style={{
                    position: 'absolute',
                    inset: 0,
                    borderRadius: 12,
                    background: gradients.primary,
                    boxShadow: '0 4px 18px -4px rgba(47,125,255,0.6)',
                    zIndex: 0,
                  }}
                />
              )}
              <ListItemIcon sx={{ minWidth: isCollapsed ? 0 : 40, color: 'inherit', zIndex: 1, justifyContent: 'center' }}>
                <motion.span whileHover={{ scale: 1.15 }} transition={{ duration: 0.15 }} style={{ display: 'inline-flex' }}>
                  {item.icon}
                </motion.span>
              </ListItemIcon>
              {!isCollapsed && <ListItemText primary={item.label} sx={{ zIndex: 1 }} primaryTypographyProps={{ fontWeight: selected ? 700 : 500, fontSize: '0.9rem' }} />}
            </ListItemButton>
          );
          return isCollapsed ? (
            <Tooltip key={item.path} title={item.label} placement="right">
              {button}
            </Tooltip>
          ) : (
            button
          );
        })}
      </List>

      <Divider sx={{ borderColor: 'rgba(255,255,255,0.1)' }} />
      <Box sx={{ p: 1.5 }}>
        <Tooltip title={isCollapsed ? 'Logout' : ''} placement="right">
          <ListItemButton
            onClick={handleLogout}
            sx={{
              borderRadius: 2.5,
              justifyContent: isCollapsed ? 'center' : 'flex-start',
              px: isCollapsed ? 1.5 : 2,
              color: 'rgba(255,255,255,0.85)',
              '&:hover': { bgcolor: alpha(theme.palette.error.main, 0.18), color: '#fff' },
            }}
          >
            <ListItemIcon sx={{ minWidth: isCollapsed ? 0 : 40, color: 'inherit', justifyContent: 'center' }}>
              <Logout fontSize="small" />
            </ListItemIcon>
            {!isCollapsed && <ListItemText primary="Logout" primaryTypographyProps={{ fontWeight: 600, fontSize: '0.9rem' }} />}
          </ListItemButton>
        </Tooltip>
        {isCollapsed && (
          <IconButton
            size="small"
            onClick={() => setCollapsed(false)}
            sx={{ mt: 1, width: '100%', color: 'rgba(255,255,255,0.7)', transform: 'rotate(180deg)' }}
          >
            <ChevronLeftRounded fontSize="small" />
          </IconButton>
        )}
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      <Box
        component="nav"
        sx={{
          width: { md: isCollapsed ? collapsedWidth : drawerWidth },
          flexShrink: { md: 0 },
          transition: theme.transitions.create('width', { duration: 220, easing: 'ease' }),
        }}
      >
        {isMobile ? (
          <Drawer
            variant="temporary"
            open={mobileOpen}
            onClose={handleDrawerToggle}
            ModalProps={{ keepMounted: true }}
            PaperProps={{ sx: { width: drawerWidth, boxSizing: 'border-box' } }}
          >
            {drawerContent}
          </Drawer>
        ) : (
          <Drawer
            variant="permanent"
            open
            PaperProps={{
              sx: {
                width: isCollapsed ? collapsedWidth : drawerWidth,
                boxSizing: 'border-box',
                transition: theme.transitions.create('width', { duration: 220, easing: 'ease' }),
                overflowX: 'hidden',
              },
            }}
          >
            {drawerContent}
          </Drawer>
        )}
      </Box>

      <Box component="main" sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <AppBar
          position="sticky"
          color="transparent"
          elevation={0}
          sx={{ borderBottom: '1px solid', borderColor: 'divider', bgcolor: 'background.paper', color: 'text.primary' }}
        >
          <Toolbar sx={{ gap: 1.5 }}>
            {isMobile && (
              <IconButton edge="start" color="inherit" aria-label="open drawer" onClick={handleDrawerToggle}>
                <MenuIcon />
              </IconButton>
            )}
            {!isMobile && isCollapsed && (
              <IconButton size="small" onClick={() => setCollapsed(false)} sx={{ transform: 'rotate(180deg)' }}>
                <ChevronLeftRounded />
              </IconButton>
            )}
            <Box sx={{ display: { xs: 'none', sm: 'block' }, minWidth: 0 }}>
              <Typography variant="h6" fontWeight={800} noWrap>{currentTitle}</Typography>
              <Typography variant="caption" color="text.secondary" noWrap>BL- Digital Checksheet Management System</Typography>
            </Box>

            <GlobalSearch />

            <Stack direction="row" spacing={0.5} alignItems="center" sx={{ ml: 'auto' }}>
              <Tooltip title="Notifications">
                <IconButton
                  onClick={(e) => setNotifAnchor(e.currentTarget)}
                  sx={{ transition: 'transform 150ms ease', '&:hover': { transform: 'scale(1.1)' } }}
                >
                  <NotificationsRounded />
                </IconButton>
              </Tooltip>
              <Menu anchorEl={notifAnchor} open={!!notifAnchor} onClose={() => setNotifAnchor(null)} PaperProps={{ sx: { width: 280, p: 1 } }}>
                <Box sx={{ px: 1.5, py: 2, textAlign: 'center' }}>
                  <Typography variant="body2" fontWeight={600}>You're all caught up</Typography>
                  <Typography variant="caption" color="text.secondary">No new notifications right now.</Typography>
                </Box>
              </Menu>

              <Box
                onClick={(e) => setProfileAnchor(e.currentTarget)}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                  cursor: 'pointer',
                  px: 1,
                  py: 0.5,
                  borderRadius: 3,
                  transition: 'background-color 150ms ease',
                  '&:hover': { bgcolor: alpha(theme.palette.text.primary, 0.06) },
                }}
              >
                <Avatar sx={{ width: 34, height: 34, background: gradients.primary, fontSize: '0.9rem', fontWeight: 700 }}>
                  {user?.name?.charAt(0)?.toUpperCase() ?? 'A'}
                </Avatar>
                <Box sx={{ display: { xs: 'none', md: 'block' }, minWidth: 0 }}>
                  <Typography variant="body2" fontWeight={700} noWrap>{user?.name ?? 'Administrator'}</Typography>
                  <Box
                    component="span"
                    sx={{
                      display: 'inline-block',
                      fontSize: '0.68rem',
                      fontWeight: 700,
                      color: roleBadgeColor,
                      bgcolor: alpha(roleBadgeColor, 0.14),
                      px: 0.9,
                      borderRadius: 999,
                      lineHeight: 1.6,
                    }}
                  >
                    {user?.role ?? 'Admin'}
                  </Box>
                </Box>
              </Box>
              <Menu anchorEl={profileAnchor} open={!!profileAnchor} onClose={() => setProfileAnchor(null)} PaperProps={{ sx: { minWidth: 200 } }}>
                <Box sx={{ px: 2, py: 1.25 }}>
                  <Typography variant="subtitle2" fontWeight={700} noWrap>{user?.name ?? 'Administrator'}</Typography>
                  <Typography variant="caption" color="text.secondary" noWrap>{user?.employeeId}</Typography>
                </Box>
                <Divider />
                <MenuItem onClick={() => { setProfileAnchor(null); navigate('/settings'); }}>
                  <SettingsRounded fontSize="small" sx={{ mr: 1.5 }} /> Settings
                </MenuItem>
                <MenuItem onClick={handleLogout} sx={{ color: 'error.main' }}>
                  <Logout fontSize="small" sx={{ mr: 1.5 }} /> Logout
                </MenuItem>
              </Menu>
            </Stack>
          </Toolbar>
        </AppBar>
        <Box sx={{ p: { xs: 2.5, md: 3 }, minWidth: 0 }}>
          <PageTransition>{children}</PageTransition>
        </Box>
      </Box>
    </Box>
  );
}
