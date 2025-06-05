import React, { Component, ErrorInfo, ReactNode } from 'react';
import {
  Container,
  Box,
  Typography,
  Button,
  Alert,
  AlertTitle,
  Stack,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Home as HomeIcon,
  BugReport as BugReportIcon,
} from '@mui/icons-material';
import { formatErrorMessage } from '../../utils/errorFormatting';

interface Props {
  children: ReactNode;
  /** Custom fallback component to render when an error occurs */
  fallback?: ReactNode;
  /** Whether to show technical error details (for development) */
  showDetails?: boolean;
  /** Custom title for the error boundary */
  title?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * Error Boundary component that catches JavaScript errors anywhere in the child component tree
 * and displays a fallback UI instead of crashing the entire application
 */
class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error, errorInfo: null };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log the error details
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    // Update state with error info
    this.setState({
      error,
      errorInfo,
    });

    // In production, you might want to log this to an error reporting service
    // Example: errorReportingService.captureException(error, { extra: errorInfo });
  }

  handleReload = () => {
    // Reload the page to recover from the error
    window.location.reload();
  };

  handleGoHome = () => {
    // Navigate to home page
    window.location.href = '/';
  };

  handleReset = () => {
    // Reset the error boundary state to try rendering again
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      const formatted = formatErrorMessage(this.state.error, 'unknown');
      const isDevelopment = process.env.NODE_ENV === 'development';

      return (
        <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
          <Box
            display="flex"
            flexDirection="column"
            alignItems="center"
            justifyContent="center"
            minHeight="60vh"
            textAlign="center"
          >
            <BugReportIcon 
              sx={{ 
                fontSize: 64, 
                color: 'error.main', 
                mb: 2 
              }} 
            />
            
            <Typography variant="h4" component="h1" gutterBottom>
              {this.props.title || 'Something went wrong'}
            </Typography>
            
            <Alert 
              severity="error" 
              sx={{ 
                width: '100%', 
                maxWidth: 600, 
                mb: 3,
                textAlign: 'left'
              }}
            >
              <AlertTitle>Application Error</AlertTitle>
              <Typography variant="body1" sx={{ mb: 1 }}>
                {formatted.message}
              </Typography>
              {formatted.actionable && (
                <Typography variant="body2" color="text.secondary">
                  {formatted.actionable}
                </Typography>
              )}
            </Alert>

            <Stack 
              direction={{ xs: 'column', sm: 'row' }} 
              spacing={2} 
              sx={{ mb: 3 }}
            >
              <Button
                variant="contained"
                startIcon={<RefreshIcon />}
                onClick={this.handleReload}
                size="large"
              >
                Reload Page
              </Button>
              
              <Button
                variant="outlined"
                startIcon={<HomeIcon />}
                onClick={this.handleGoHome}
                size="large"
              >
                Go to Home
              </Button>
              
              {isDevelopment && (
                <Button
                  variant="text"
                  onClick={this.handleReset}
                  size="large"
                >
                  Try Again
                </Button>
              )}
            </Stack>

            {/* Show technical details in development mode or if explicitly requested */}
            {(isDevelopment || this.props.showDetails) && this.state.error && (
              <Alert 
                severity="warning" 
                sx={{ 
                  width: '100%', 
                  maxWidth: 800, 
                  textAlign: 'left',
                  '& .MuiAlert-message': {
                    width: '100%'
                  }
                }}
              >
                <AlertTitle>Technical Details (Development Only)</AlertTitle>
                <Box sx={{ mt: 1 }}>
                  <Typography variant="subtitle2" sx={{ mb: 1 }}>
                    Error Message:
                  </Typography>
                  <Typography 
                    variant="body2" 
                    component="pre" 
                    sx={{ 
                      whiteSpace: 'pre-wrap',
                      fontFamily: 'monospace',
                      fontSize: '0.8rem',
                      mb: 2,
                      p: 1,
                      bgcolor: 'grey.100',
                      borderRadius: 1,
                    }}
                  >
                    {this.state.error.toString()}
                  </Typography>
                  
                  {this.state.errorInfo && (
                    <>
                      <Typography variant="subtitle2" sx={{ mb: 1 }}>
                        Component Stack:
                      </Typography>
                      <Typography 
                        variant="body2" 
                        component="pre" 
                        sx={{ 
                          whiteSpace: 'pre-wrap',
                          fontFamily: 'monospace',
                          fontSize: '0.8rem',
                          p: 1,
                          bgcolor: 'grey.100',
                          borderRadius: 1,
                        }}
                      >
                        {this.state.errorInfo.componentStack}
                      </Typography>
                    </>
                  )}
                </Box>
              </Alert>
            )}
          </Box>
        </Container>
      );
    }

    // Normal rendering when no error
    return this.props.children;
  }
}

export default ErrorBoundary;

/**
 * Higher-order component to wrap any component with error boundary
 */
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  errorBoundaryProps?: Omit<Props, 'children'>
) {
  const WrappedComponent = (props: P) => (
    <ErrorBoundary {...errorBoundaryProps}>
      <Component {...props} />
    </ErrorBoundary>
  );
  
  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`;
  
  return WrappedComponent;
} 