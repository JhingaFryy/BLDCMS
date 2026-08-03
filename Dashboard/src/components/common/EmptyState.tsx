import { Box, Button, Stack, Typography, alpha, useTheme } from '@mui/material';
import { motion } from 'framer-motion';
import InboxRoundedIcon from '@mui/icons-material/InboxRounded';
import type { SvgIconComponent } from '@mui/icons-material';

interface EmptyStateProps {
  title: string;
  message?: string;
  icon?: SvgIconComponent;
  actionLabel?: string;
  onAction?: () => void;
}

/**
 * Module 33: shared empty-state panel - icon "illustration" (no external illustration asset
 * library is bundled with this app, so a large themed icon stands in for one), message, and an
 * optional primary action. Replaces each page's own ad hoc centered-Typography empty block.
 */
export default function EmptyState({ title, message, icon: Icon = InboxRoundedIcon, actionLabel, onAction }: EmptyStateProps) {
  const theme = useTheme();
  return (
    <Box sx={{ py: 7, px: 3, textAlign: 'center' }}>
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: 'easeOut' }}
      >
        <Stack alignItems="center" spacing={1.5}>
          <Box
            sx={{
              width: 72,
              height: 72,
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              bgcolor: alpha(theme.palette.primary.main, theme.palette.mode === 'dark' ? 0.14 : 0.08),
              border: `1px solid ${alpha(theme.palette.primary.main, 0.25)}`,
            }}
          >
            <Icon sx={{ fontSize: 34, color: 'primary.main' }} />
          </Box>
          <Typography variant="h6" fontWeight={700}>
            {title}
          </Typography>
          {message ? (
            <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 380 }}>
              {message}
            </Typography>
          ) : null}
          {actionLabel && onAction ? (
            <Button variant="outlined" onClick={onAction} sx={{ mt: 1 }}>
              {actionLabel}
            </Button>
          ) : null}
        </Stack>
      </motion.div>
    </Box>
  );
}
