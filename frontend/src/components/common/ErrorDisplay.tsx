import React from 'react';
import {
  Alert,
  AlertTitle,
  Box,
  Button,
  IconButton,
  Stack,
  Typography,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { formatErrorMessage, FormattedError } from '../../utils/errorFormatting';

interface ErrorDisplayProps {
  /** The error to display (can be Error object, string, or any object) */
  error?: any;
  /** Context for more specific error messaging */
  context?: string;
  /** Whether to show a retry button */
  showRetry?: boolean;
  /** Callback function for retry action */
  onRetry?: () => void;
  /** Whether to show a close/dismiss button */
  showClose?: boolean;
  /** Callback function for close action */
  onClose?: () => void;
  /** Custom title for the error alert */
  title?: string;
  /** Additional styling for the Alert component */
  sx?: object;
  /** Whether to show the error in a compact format */
  compact?: boolean;
  /** Pre-formatted error object (if you already have a FormattedError) */
  formattedError?: FormattedError;
}

/**
 * Reusable component for displaying user-friendly error messages
 * Uses the error formatting utilities to provide consistent error presentation
 */
const ErrorDisplay: React.FC<ErrorDisplayProps> = ({
  error,
  context,
  showRetry = false,
  onRetry,
  showClose = false,
  onClose,
  title,
  sx = {},
  compact = false,
  formattedError,
}) => {
  // Don't render if no error is provided
  if (!error && !formattedError) {
    return null;
  }

  // Use pre-formatted error or format the error
  const formatted = formattedError || formatErrorMessage(error, context);
  
  // Determine if retry should be shown based on error type
  const shouldShowRetry = showRetry && formatted.retry && onRetry;

  return (
    <Alert
      severity={formatted.severity}
      sx={{
        alignItems: 'flex-start',
        ...sx,
      }}
      action={
        (shouldShowRetry || showClose) ? (
          <Stack direction="row" spacing={0.5}>
            {shouldShowRetry && (
              <Button
                color="inherit"
                size="small"
                startIcon={<RefreshIcon />}
                onClick={onRetry}
                sx={{ 
                  minWidth: 'auto',
                  fontSize: '0.75rem',
                }}
              >
                Try Again
              </Button>
            )}
            {showClose && (
              <IconButton
                aria-label="close"
                color="inherit"
                size="small"
                onClick={onClose}
              >
                <CloseIcon fontSize="inherit" />
              </IconButton>
            )}
          </Stack>
        ) : undefined
      }
    >
      {!compact && (title || formatted.severity === 'error') && (
        <AlertTitle>
          {title || (formatted.severity === 'error' ? 'Error' : 
                    formatted.severity === 'warning' ? 'Warning' : 'Information')}
        </AlertTitle>
      )}
      
      <Box>
        <Typography 
          variant={compact ? "body2" : "body1"} 
          component="div"
          sx={{ mb: formatted.actionable ? 1 : 0 }}
        >
          {formatted.message}
        </Typography>
        
        {formatted.actionable && (
          <Typography 
            variant={compact ? "caption" : "body2"} 
            color="text.secondary"
            component="div"
          >
            {formatted.actionable}
          </Typography>
        )}
      </Box>
    </Alert>
  );
};

export default ErrorDisplay;

/**
 * Specialized error display for form validation errors
 */
export const FormErrorDisplay: React.FC<{
  error?: any;
  onClose?: () => void;
}> = ({ error, onClose }) => (
  <ErrorDisplay
    error={error}
    context="submit_form"
    showClose={true}
    onClose={onClose}
    compact={true}
    sx={{ mb: 2 }}
  />
);

/**
 * Specialized error display for data loading errors with retry
 */
export const LoadingErrorDisplay: React.FC<{
  error?: any;
  onRetry?: () => void;
  context?: string;
}> = ({ error, onRetry, context = "load_data" }) => (
  <ErrorDisplay
    error={error}
    context={context}
    showRetry={true}
    onRetry={onRetry}
    sx={{ width: '100%', mb: 2 }}
  />
);

/**
 * Specialized error display for page-level errors
 */
export const PageErrorDisplay: React.FC<{
  error?: any;
  context?: string;
  onRetry?: () => void;
}> = ({ error, context, onRetry }) => (
  <ErrorDisplay
    error={error}
    context={context}
    showRetry={!!onRetry}
    onRetry={onRetry}
    sx={{ 
      width: '100%', 
      mb: 3,
      '& .MuiAlert-message': {
        width: '100%'
      }
    }}
  />
); 