import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  Container,
  TextField,
  Button,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Link as MuiLink,
  Paper,
  Stack,
  Divider,
} from '@mui/material';
import { Google as GoogleIcon } from '@mui/icons-material';
import { Link as RouterLink } from 'react-router-dom';

const SignUpPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { signUp, signInWithGoogle, currentUser, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (currentUser && !loading) {
      navigate('/main');
    }
  }, [currentUser, loading, navigate]);

  const handleEmailSignUp = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    if (password.length < 6) {
      setError('Password should be at least 6 characters long.');
      return;
    }

    if (!email.trim()) {
      setError('Please enter an email address.');
      return;
    }

    setIsLoading(true);
    try {
      await signUp(email, password);
      navigate('/login', {
        state: { message: 'Sign up successful! Please log in.' },
      });
    } catch (err: any) {
      console.error('Sign up error:', err);
      let errorMessage = 'Failed to sign up. Please try again.';

      if (err.code === 'auth/email-already-in-use') {
        errorMessage = 'An account with this email already exists.';
      } else if (err.code === 'auth/invalid-email') {
        errorMessage = 'Invalid email address.';
      } else if (err.code === 'auth/weak-password') {
        errorMessage =
          'Password is too weak. Please use at least 6 characters.';
      } else if (err.message) {
        errorMessage = err.message;
      }

      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSignUp = async () => {
    setIsLoading(true);
    setError(null);

    try {
      await signInWithGoogle();
    } catch (err: any) {
      console.error('Google sign up error:', err);
      let errorMessage = 'Failed to sign up with Google. Please try again.';

      if (err.code === 'auth/popup-closed-by-user') {
        errorMessage = 'Sign-up was cancelled.';
      } else if (err.code === 'auth/unauthorized-domain') {
        errorMessage = 'This domain is not authorized for Google Sign-In.';
      } else if (err.message) {
        errorMessage = err.message;
      }

      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  if (loading) {
    return (
      <Container component="main" maxWidth="xs">
        <Box
          sx={{
            marginTop: 8,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          <CircularProgress />
          <Typography sx={{ mt: 2 }}>Loading...</Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper elevation={3} sx={{ padding: 4, width: '100%' }}>
          <Typography component="h1" variant="h4" align="center" gutterBottom>
            Sign Up
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box
            component="form"
            onSubmit={handleEmailSignUp}
            noValidate
            sx={{ mt: 1 }}
          >
            <TextField
              margin="normal"
              required
              fullWidth
              id="email"
              label="Email Address"
              name="email"
              autoComplete="email"
              autoFocus
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={isLoading}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type="password"
              id="password"
              autoComplete="new-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isLoading}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="confirmPassword"
              label="Confirm Password"
              type="password"
              id="confirmPassword"
              autoComplete="new-password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              disabled={isLoading}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={
                isLoading ||
                !email.trim() ||
                !password.trim() ||
                !confirmPassword.trim()
              }
            >
              {isLoading ? <CircularProgress size={24} /> : 'Sign Up'}
            </Button>

            <Divider sx={{ my: 2 }}>
              <Typography variant="body2" color="text.secondary">
                OR
              </Typography>
            </Divider>

            <Button
              fullWidth
              variant="outlined"
              startIcon={<GoogleIcon />}
              onClick={handleGoogleSignUp}
              disabled={isLoading}
              sx={{ mb: 2 }}
            >
              Sign up with Google
            </Button>

            <Stack
              direction="row"
              justifyContent="center"
              spacing={1}
              sx={{ mt: 2 }}
            >
              <Typography variant="body2">Already have an account?</Typography>
              <MuiLink component={RouterLink} to="/login" variant="body2">
                Sign In
              </MuiLink>
            </Stack>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default SignUpPage;
