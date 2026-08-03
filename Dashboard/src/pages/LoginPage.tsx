import { Box, Button, Checkbox, FormControlLabel, Stack, TextField, Typography, CircularProgress, alpha, useTheme } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '../contexts/AuthContext';
import GlassCard from '../components/common/GlassCard';
import ParticlesBackground from '../components/common/ParticlesBackground';
import { gradients } from '../theme/palette';
import trainImage from '../../image.jpeg';
import logo from '../../logo.png';

const schema = z.object({
  employeeId: z.string().min(1, 'Employee ID is required'),
  password: z.string().min(6, 'Password is required'),
  rememberMe: z.boolean().optional()
});

export default function LoginPage() {
  const { login, loading } = useAuth();
  const { register, handleSubmit, formState: { errors } } = useForm({ resolver: zodResolver(schema) });
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';

  return (
    <Box
      sx={{
        minHeight: '100vh',
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden',
        p: 2,
      }}
    >
      {/* Railway locomotive photo backdrop, tinted by the same cyber gradient used before this
          image existed - kept as a separate layer (rather than a CSS background-image on the
          outer Box) so its brightness/saturation can be tuned independently of the gradient tint
          that sits on top of it for text contrast. */}
      <Box
        aria-hidden
        sx={{
          position: 'absolute',
          inset: 0,
          backgroundImage: `url(${trainImage})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          filter: isDark ? 'brightness(0.5) saturate(1.05)' : 'brightness(0.95) saturate(1.05)',
        }}
      />
      <Box
        aria-hidden
        sx={{
          position: 'absolute',
          inset: 0,
          background: isDark ? gradients.loginBackdrop : gradients.loginBackdropLight,
          opacity: isDark ? 0.86 : 0.82,
        }}
      />
      <ParticlesBackground />

      <motion.div
        initial={{ opacity: 0, y: 18, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.45, ease: 'easeOut' }}
        style={{ width: '100%', maxWidth: 460, position: 'relative', zIndex: 1 }}
      >
        <GlassCard>
          <Stack spacing={1} alignItems="center" mb={3.5}>
            <motion.div
              initial={{ opacity: 0, scale: 0.6, rotate: -8 }}
              animate={{ opacity: 1, scale: 1, rotate: 0 }}
              transition={{ duration: 0.5, ease: 'easeOut', delay: 0.1 }}
            >
              <Box
                component="img"
                src={logo}
                alt="BL-DCMS logo"
                sx={{
                  width: 84,
                  height: 84,
                  objectFit: 'contain',
                  filter: 'drop-shadow(0 8px 24px rgba(47,125,255,0.45))',
                  mb: 0.5,
                }}
              />
            </motion.div>
            <Box textAlign="center">
              <Typography variant="h5" fontWeight={800} sx={{ letterSpacing: -0.3 }}>
                BL-DCMS
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                BL- Digital Checksheet Management System
              </Typography>
            </Box>
          </Stack>

          <form onSubmit={handleSubmit((data) => login({ employee_id: data.employeeId, password: data.password, rememberMe: data.rememberMe }))}>
            <Stack spacing={2.2}>
              <TextField
                label="Employee ID"
                fullWidth
                autoFocus
                {...register('employeeId')}
                error={!!errors.employeeId}
                helperText={typeof errors.employeeId?.message === 'string' ? errors.employeeId.message : undefined}
              />
              <TextField
                label="Password"
                type="password"
                fullWidth
                {...register('password')}
                error={!!errors.password}
                helperText={typeof errors.password?.message === 'string' ? errors.password.message : undefined}
              />
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <FormControlLabel control={<Checkbox {...register('rememberMe')} />} label="Remember me" />
                <Typography variant="body2" color="primary" sx={{ cursor: 'pointer', fontWeight: 600 }}>
                  Forgot password?
                </Typography>
              </Box>
              <motion.div whileHover={{ scale: loading ? 1 : 1.015 }} whileTap={{ scale: loading ? 1 : 0.98 }}>
                <Button type="submit" variant="contained" size="large" fullWidth disabled={loading} sx={{ height: 50 }}>
                  <AnimatePresence mode="wait" initial={false}>
                    {loading ? (
                      <motion.span
                        key="loading"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        style={{ display: 'inline-flex' }}
                      >
                        <CircularProgress size={22} color="inherit" />
                      </motion.span>
                    ) : (
                      <motion.span key="label" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                        Sign In
                      </motion.span>
                    )}
                  </AnimatePresence>
                </Button>
              </motion.div>
            </Stack>
          </form>
        </GlassCard>

        <Typography variant="caption" sx={{ display: 'block', textAlign: 'center', mt: 2.5, color: alpha(theme.palette.text.secondary, 0.8) }}>
          Secure access · Authorized railway personnel only
        </Typography>
      </motion.div>
    </Box>
  );
}
