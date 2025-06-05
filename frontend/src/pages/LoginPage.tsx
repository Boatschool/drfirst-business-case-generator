import React, { useState, useEffect } from 'react';
import {
  Typography,
  Container,
  Box,
  Alert,
  TextField,
  Button,
  Stack,
  Divider,
  Link as MuiLink,
  Paper,
  CircularProgress,
} from '@mui/material';
import { Google as GoogleIcon } from '@mui/icons-material';
import { useLocation, useNavigate, Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { PAPER_ELEVATION, STANDARD_STYLES } from '../styles/constants';

const LoginPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { signIn, signInWithGoogle, currentUser, loading } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const message = location.state?.message;

  // Redirect if already logged in
  useEffect(() => {
    if (currentUser && !loading) {
      navigate('/main');
    }
  }, [currentUser, loading, navigate]);

  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      setError('Please enter both email and password.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      await signIn(email, password);
      // Navigation will happen automatically via useEffect when currentUser updates
    } catch (err: any) {
      console.error('Login error:', err);
      // Firebase error messages can be quite technical, so let's provide user-friendly messages
      let errorMessage = 'Failed to log in. Please try again.';

      if (err.code === 'auth/user-not-found') {
        errorMessage = 'No account found with this email address.';
      } else if (err.code === 'auth/wrong-password') {
        errorMessage = 'Incorrect password.';
      } else if (err.code === 'auth/invalid-email') {
        errorMessage = 'Invalid email address.';
      } else if (err.code === 'auth/too-many-requests') {
        errorMessage = 'Too many failed attempts. Please try again later.';
      } else if (err.message) {
        errorMessage = err.message;
      }

      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setIsLoading(true);
    setError(null);

    try {
      await signInWithGoogle();
      // Navigation will happen automatically via useEffect when currentUser updates
    } catch (err: any) {
      console.error('Google login error:', err);
      let errorMessage = 'Failed to log in with Google. Please try again.';

      if (err.code === 'auth/popup-closed-by-user') {
        errorMessage = 'Sign-in was cancelled.';
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

  // Show loading spinner while checking auth state
  if (loading) {
    return (
      <Container component="main" maxWidth="xs">
        <Box sx={STANDARD_STYLES.authPageContainer}>
          <CircularProgress />
          <Typography sx={{ mt: 2 }}>Loading...</Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container component="main" maxWidth="xs">
      <Box sx={STANDARD_STYLES.authPageContainer}>
        <Paper elevation={PAPER_ELEVATION.AUTH_FORM} sx={{ ...STANDARD_STYLES.authFormPaper, width: '100%' }}>
          <Typography component="h1" variant="h4" align="center" gutterBottom>
            Sign In
          </Typography>

          {message && (
            <Alert severity="success" sx={{ mb: 2 }}>
              {message}
            </Alert>
          )}

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleEmailLogin} sx={{ mt: 1 }}>
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
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isLoading}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={isLoading || !email.trim() || !password.trim()}
            >
              {isLoading ? <CircularProgress size={24} /> : 'Sign In'}
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
              onClick={handleGoogleLogin}
              disabled={isLoading}
              sx={{ mb: 2 }}
            >
              Sign in with Google
            </Button>

            <Stack
              direction="row"
              justifyContent="center"
              spacing={1}
              sx={{ mt: 2 }}
            >
              <Typography variant="body2">Don't have an account?</Typography>
              <MuiLink component={RouterLink} to="/signup" variant="body2">
                Sign up
              </MuiLink>
            </Stack>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default LoginPage;
