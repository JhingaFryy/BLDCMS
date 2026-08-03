import { Box, Button, Paper, Typography } from '@mui/material';
import { Link } from 'react-router-dom';

export default function ForbiddenPage() {
  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', p: 3 }}>
      <Paper sx={{ p: 6, textAlign: 'center', maxWidth: 480 }}>
        <Typography variant="h3" fontWeight={700} mb={2}>403</Typography>
        <Typography variant="h6" mb={1}>Access denied</Typography>
        <Typography color="text.secondary" mb={3}>
          You do not have permission to view this page.
        </Typography>
        <Button component={Link} to="/dashboard" variant="contained">Return Home</Button>
      </Paper>
    </Box>
  );
}
