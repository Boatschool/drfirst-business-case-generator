import React, { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  Button,
  Stack,
  Box,
  Divider,
  Card,
  CardContent,
  CardActions,
} from '@mui/material';
import {
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import ErrorDisplay, { 
  FormErrorDisplay, 
  LoadingErrorDisplay, 
  PageErrorDisplay 
} from '../components/common/ErrorDisplay';
import { 
  formatErrorMessage, 
  formatAuthError, 
  createGenericError,
  isRetryableError 
} from '../utils/errorFormatting';
import { PAPER_ELEVATION } from '../styles/constants';
import type { ApiError, FirebaseAuthError } from '../types/api';

/**
 * Demo page showcasing the enhanced error handling system
 * This page demonstrates various error types and display patterns
 */
const ErrorDemoPage: React.FC = () => {
  const [currentError, setCurrentError] = useState<any>(null);
  const [retryCount, setRetryCount] = useState(0);

  // Helper function to simulate different error types
  const simulateError = (errorType: string) => {
    switch (errorType) {
      case 'network': {
        const networkError = new Error('Network connection failed');
        (networkError as any).name = 'NetworkError';
        setCurrentError(networkError);
        break;
      }
      
      case 'auth_expired': {
        const authError: ApiError = new Error('Session expired');
        authError.status = 401;
        setCurrentError(authError);
        break;
      }
      
      case 'forbidden': {
        const forbiddenError: ApiError = new Error('Access denied');
        forbiddenError.status = 403;
        setCurrentError(forbiddenError);
        break;
      }
      
      case 'server_error': {
        const serverError: ApiError = new Error('Internal server error');
        serverError.status = 500;
        setCurrentError(serverError);
        break;
      }
      
      case 'validation': {
        const validationError = new Error('Invalid input provided');
        (validationError as any).status = 422;
        setCurrentError(validationError);
        break;
      }
      
      case 'firebase_auth': {
        const firebaseError: FirebaseAuthError = new Error('Invalid credentials') as FirebaseAuthError;
        firebaseError.code = 'auth/wrong-password';
        setCurrentError(firebaseError);
        break;
      }
      
      case 'case_not_found': {
        const notFoundError = new Error('Business case not found');
        (notFoundError as any).status = 404;
        setCurrentError(notFoundError);
        break;
      }
      
      default:
        setCurrentError(new Error('Unknown error occurred'));
    }
  };

  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
    // Simulate clearing error after retry
    setTimeout(() => {
      setCurrentError(null);
    }, 1000);
  };

  const errorButtons = [
    { type: 'network', label: 'Network Error', icon: <ErrorIcon /> },
    { type: 'auth_expired', label: 'Auth Expired', icon: <WarningIcon /> },
    { type: 'forbidden', label: 'Access Denied', icon: <ErrorIcon /> },
    { type: 'server_error', label: 'Server Error', icon: <ErrorIcon /> },
    { type: 'validation', label: 'Validation Error', icon: <WarningIcon /> },
    { type: 'firebase_auth', label: 'Firebase Auth Error', icon: <ErrorIcon /> },
    { type: 'case_not_found', label: 'Case Not Found', icon: <InfoIcon /> },
    { type: 'unknown', label: 'Unknown Error', icon: <ErrorIcon /> },
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom align="center">
        Enhanced Error Handling Demo
      </Typography>
      
      <Typography variant="body1" color="text.secondary" align="center" sx={{ mb: 4 }}>
        This page demonstrates the enhanced error handling system with user-friendly messages,
        actionable advice, and consistent display patterns.
      </Typography>

      {/* Error Generation Section */}
      <Paper elevation={PAPER_ELEVATION.MAIN_CONTENT} sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" gutterBottom>
          Error Generation
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Click any button below to simulate different types of errors and see how they're displayed
          with user-friendly messages and actionable advice.
        </Typography>
        
        <Stack 
          direction="row" 
          spacing={2} 
          flexWrap="wrap" 
          useFlexGap 
          sx={{ mb: 3 }}
        >
          {errorButtons.map(({ type, label, icon }) => (
            <Button
              key={type}
              variant="outlined"
              startIcon={icon}
              onClick={() => simulateError(type)}
              size="small"
            >
              {label}
            </Button>
          ))}
        </Stack>

        <Button 
          variant="contained" 
          color="success" 
          onClick={() => setCurrentError(null)}
          disabled={!currentError}
        >
          Clear Error
        </Button>

        {retryCount > 0 && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Retry attempts: {retryCount}
          </Typography>
        )}
      </Paper>

      {/* Error Display Section */}
      {currentError && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h5" gutterBottom>
            Current Error Display
          </Typography>

          {/* Basic Error Display */}
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Basic Error Display
              </Typography>
              <ErrorDisplay 
                error={currentError}
                showRetry={isRetryableError(currentError)}
                onRetry={handleRetry}
                showClose={true}
                onClose={() => setCurrentError(null)}
              />
            </CardContent>
          </Card>

          {/* Context-Specific Displays */}
          <Stack spacing={2}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Form Error Display (Compact)
                </Typography>
                <FormErrorDisplay 
                  error={currentError}
                  onClose={() => setCurrentError(null)}
                />
              </CardContent>
            </Card>

            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Loading Error Display (With Retry)
                </Typography>
                <LoadingErrorDisplay 
                  error={currentError}
                  context="load_cases"
                  onRetry={handleRetry}
                />
              </CardContent>
            </Card>

            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Page Error Display
                </Typography>
                <PageErrorDisplay 
                  error={currentError}
                  context="save_data"
                  onRetry={handleRetry}
                />
              </CardContent>
            </Card>
          </Stack>
        </Box>
      )}

      {/* Error Information Section */}
      <Paper elevation={PAPER_ELEVATION.MAIN_CONTENT} sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" gutterBottom>
          Error Information
        </Typography>
        
        {currentError ? (
          <Box>
            <Typography variant="h6" gutterBottom>
              Current Error Details:
            </Typography>
            
            <Stack spacing={2}>
              <Box>
                <Typography variant="subtitle2">Original Error:</Typography>
                <Typography variant="body2" sx={{ fontFamily: 'monospace', bgcolor: 'grey.100', p: 1, borderRadius: 1 }}>
                  {JSON.stringify({
                    name: currentError.name,
                    message: currentError.message,
                    status: (currentError as any).status,
                    code: (currentError as any).code,
                  }, null, 2)}
                </Typography>
              </Box>

              <Box>
                <Typography variant="subtitle2">Formatted Error:</Typography>
                <Typography variant="body2" sx={{ fontFamily: 'monospace', bgcolor: 'grey.100', p: 1, borderRadius: 1 }}>
                  {JSON.stringify(formatErrorMessage(currentError), null, 2)}
                </Typography>
              </Box>

              {currentError.code?.startsWith('auth/') && (
                <Box>
                  <Typography variant="subtitle2">Firebase Auth Formatted:</Typography>
                  <Typography variant="body2" sx={{ fontFamily: 'monospace', bgcolor: 'grey.100', p: 1, borderRadius: 1 }}>
                    {JSON.stringify(formatAuthError(currentError), null, 2)}
                  </Typography>
                </Box>
              )}

              <Box>
                <Typography variant="subtitle2">Is Retryable:</Typography>
                <Typography variant="body2">
                  {isRetryableError(currentError) ? 'Yes' : 'No'}
                </Typography>
              </Box>
            </Stack>
          </Box>
        ) : (
          <Typography variant="body2" color="text.secondary">
            No error currently active. Generate an error above to see details.
          </Typography>
        )}
      </Paper>

      {/* Error Handling Features */}
      <Paper elevation={PAPER_ELEVATION.MAIN_CONTENT} sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Enhanced Error Handling Features
        </Typography>
        
        <Stack spacing={2}>
          <Box>
            <Typography variant="h6" gutterBottom>
              ✅ User-Friendly Messages
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Technical error messages are automatically converted to user-friendly language
              that non-technical users can understand.
            </Typography>
          </Box>

          <Divider />

          <Box>
            <Typography variant="h6" gutterBottom>
              🎯 Actionable Advice
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Errors include specific guidance on what users can do next, such as checking
              their internet connection or contacting support.
            </Typography>
          </Box>

          <Divider />

          <Box>
            <Typography variant="h6" gutterBottom>
              🔄 Smart Retry Logic
            </Typography>
            <Typography variant="body2" color="text.secondary">
              System automatically determines which errors are worth retrying and shows
              retry buttons only when appropriate.
            </Typography>
          </Box>

          <Divider />

          <Box>
            <Typography variant="h6" gutterBottom>
              🎨 Consistent Display
            </Typography>
            <Typography variant="body2" color="text.secondary">
              All errors use the same Material-UI Alert components with consistent styling,
              icons, and interaction patterns throughout the application.
            </Typography>
          </Box>

          <Divider />

          <Box>
            <Typography variant="h6" gutterBottom>
              🛡️ Error Boundaries
            </Typography>
            <Typography variant="body2" color="text.secondary">
              React Error Boundaries catch unexpected JavaScript errors and display
              graceful fallback UI instead of crashing the application.
            </Typography>
          </Box>

          <Divider />

          <Box>
            <Typography variant="h6" gutterBottom>
              📱 Context-Aware Messages
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Error messages are customized based on context (login, form submission,
              data loading, etc.) for more specific and helpful guidance.
            </Typography>
          </Box>
        </Stack>
      </Paper>
    </Container>
  );
};

export default ErrorDemoPage; 