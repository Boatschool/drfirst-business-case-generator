import React from 'react';
import { Typography, Container, Box } from '@mui/material';

const DashboardPage: React.FC = () => {
  return (
    <Container component="main" maxWidth="md">
      <Box sx={{ marginTop: 8, textAlign: 'center' }}>
        <Typography component="h1" variant="h4">
          Dashboard Page (Placeholder)
        </Typography>
        <Typography sx={{ mt: 2 }}>
          Protected content will be here.
        </Typography>
      </Box>
    </Container>
  );
};

export default DashboardPage; 