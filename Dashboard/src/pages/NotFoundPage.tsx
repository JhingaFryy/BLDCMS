import { Box, Button, Paper, Typography } from '@mui/material';
import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', p: 3 }}>
      <Paper sx={{ p: 6, textAlign: 'center', maxWidth: 480 }}>
        <Typography variant="h3" fontWeight={700} mb={2}>404</Typography>
        <Typography variant="h6" mb={1}>Page not found</Typography>
        <Typography color="text.secondary" mb={3}>The requested screen could not be found.</Typography>
        <Button component={Link} to="/dashboard" variant="contained">Return Home</Button>
      </Paper>
    </Box>
  );
}
