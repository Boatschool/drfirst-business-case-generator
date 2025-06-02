import React from 'react';
import { Typography, Container, Box, Alert } from '@mui/material';
import { useLocation } from 'react-router-dom';

const LoginPage: React.FC = () => {
  const location = useLocation();
  const message = location.state?.message;

  return (
    <Container component="main" maxWidth="xs">
      <Box sx={{ marginTop: 8, textAlign: 'center' }}>
        <Typography component="h1" variant="h5">
          Login Page (Placeholder)
        </Typography>
        {message && (
          <Alert severity="success" sx={{ mt: 2 }}>
            {message}
          </Alert>
        )}
        <Typography sx={{ mt: 2 }}>
          Login form will be here.
        </Typography>
      </Box>
    </Container>
  );
};

export default LoginPage; 