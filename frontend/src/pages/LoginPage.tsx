import React, { useState, useEffect } from 'react';
import {
  Typography,
  Container,
  Box,
  Alert,
  TextField,
  Stack,
  Divider,
  Link as MuiLink,
  Paper,
  CircularProgress,
} from '@mui/material';
import { Google as GoogleIcon } from '@mui/icons-material';
import { useLocation, useNavigate, Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { LoadingButton } from '../components/common/LoadingIndicators';
import { PAPER_ELEVATION, STANDARD_STYLES } from '../styles/constants';
import { formatAuthError } from '../utils/errorFormatting';
import ErrorDisplay from '../components/common/ErrorDisplay';

const LoginPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { signIn, signInWithGoogle, currentUser, loading } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<any>(null);
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
      setError(err);
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
      setError(err);
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
          <Typography id="login-title" component="h1" variant="h4" align="center" gutterBottom>
            Sign In
          </Typography>

          {message && (
            <Alert severity="success" sx={{ mb: 2 }} role="status">
              {message}
            </Alert>
          )}

          <ErrorDisplay 
            error={error}
            formattedError={error ? formatAuthError(error) : undefined}
            showClose={true}
            onClose={() => setError(null)}
            sx={{ mb: 2 }}
          />

          <Box component="form" onSubmit={handleEmailLogin} sx={{ mt: 1 }} role="form" aria-labelledby="login-title">
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
              aria-describedby={error ? 'login-error' : undefined}
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
              aria-describedby={error ? 'login-error' : undefined}
            />

            <LoadingButton
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={!email.trim() || !password.trim()}
              loading={isLoading}
              loadingText="Signing In..."
              aria-describedby="login-help"
            >
              Sign In
            </LoadingButton>

            <Divider sx={{ my: 2 }}>
              <Typography variant="body2" color="text.secondary">
                OR
              </Typography>
            </Divider>

            <LoadingButton
              fullWidth
              variant="outlined"
              startIcon={<GoogleIcon />}
              onClick={handleGoogleLogin}
              loading={isLoading}
              loadingText="Signing In..."
              sx={{ mb: 2 }}
              aria-label="Sign in with Google account"
            >
              Sign in with Google
            </LoadingButton>

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
