import { Box, Button, Stack, Typography, alpha, useTheme } from '@mui/material';
import { motion } from 'framer-motion';
import ErrorOutlineRoundedIcon from '@mui/icons-material/ErrorOutlineRounded';
import RefreshRoundedIcon from '@mui/icons-material/RefreshRounded';

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
  retryLabel?: string;
}

/**
 * Module 33: shared error panel - icon, meaningful message, retry button with a small spin
 * animation on click (visual feedback that the retry actually registered, not a real loading
 * spinner - the caller's own `loading` state drives the actual refetch). Replaces the plain
 * `Alert severity="error"` blocks (and a few native `alert()` calls) scattered across pages.
 */
export default function ErrorState({ message, onRetry, retryLabel = 'Retry' }: ErrorStateProps) {
  const theme = useTheme();

  return (
    <Box sx={{ py: 5, px: 3, textAlign: 'center' }}>
      <motion.div initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.25 }}>
        <Stack alignItems="center" spacing={1.5}>
          <Box
            sx={{
              width: 64,
              height: 64,
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              bgcolor: alpha(theme.palette.error.main, theme.palette.mode === 'dark' ? 0.16 : 0.1),
              border: `1px solid ${alpha(theme.palette.error.main, 0.35)}`,
            }}
          >
            <ErrorOutlineRoundedIcon sx={{ fontSize: 30, color: 'error.main' }} />
          </Box>
          <Typography variant="body1" fontWeight={600} sx={{ maxWidth: 420 }}>
            {message}
          </Typography>
          {onRetry ? (
            <Button
              variant="contained"
              color="error"
              startIcon={
                <motion.span
                  key={message}
                  initial={{ rotate: 0 }}
                  animate={{ rotate: 0 }}
                  whileTap={{ rotate: 220 }}
                  style={{ display: 'inline-flex' }}
                >
                  <RefreshRoundedIcon fontSize="small" />
                </motion.span>
              }
              onClick={onRetry}
            >
              {retryLabel}
            </Button>
          ) : null}
        </Stack>
      </motion.div>
    </Box>
  );
}
