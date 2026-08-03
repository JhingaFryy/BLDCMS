import { Box, Paper, Stack, Typography } from '@mui/material';

interface PlaceholderPageProps {
  title: string;
  description: string;
}

export default function PlaceholderPage({ title, description }: PlaceholderPageProps) {
  return (
    <Box>
      <Paper sx={{ p: { xs: 3, md: 4 }, borderRadius: 3 }}>
        <Stack spacing={1.5}>
          <Typography variant="h4" fontWeight={700}>{title}</Typography>
          <Typography variant="body1" color="text.secondary">{description}</Typography>
        </Stack>
      </Paper>
    </Box>
  );
}
