/**
 * Error formatting utilities for user-friendly error messages
 * Provides consistent, actionable error messages throughout the application
 */

export interface FormattedError {
  message: string;
  severity: 'error' | 'warning' | 'info';
  actionable?: string;
  retry?: boolean;
}

/**
 * Maps common error types to user-friendly messages with actionable advice
 */
const ERROR_MESSAGES = {
  // Network errors
  NETWORK_ERROR: {
    message: 'Unable to connect to our servers',
    actionable: 'Please check your internet connection and try again',
    retry: true,
  },
  TIMEOUT_ERROR: {
    message: 'The request is taking longer than expected',
    actionable: 'Please try again in a few moments',
    retry: true,
  },
  
  // Authentication errors
  AUTH_EXPIRED: {
    message: 'Your session has expired',
    actionable: 'Please sign out and sign back in to continue',
    retry: false,
  },
  AUTH_UNAUTHORIZED: {
    message: 'You are not authorized to perform this action',
    actionable: 'Please contact your administrator if you believe this is an error',
    retry: false,
  },
  AUTH_FORBIDDEN: {
    message: 'You do not have permission to access this resource',
    actionable: 'Please contact your administrator for access',
    retry: false,
  },
  
  // Server errors
  SERVER_ERROR: {
    message: 'Our servers are experiencing a temporary issue',
    actionable: 'Please try again in a few minutes. If the problem persists, contact support',
    retry: true,
  },
  SERVICE_UNAVAILABLE: {
    message: 'Service is temporarily unavailable',
    actionable: 'We are working to resolve this issue. Please try again shortly',
    retry: true,
  },
  
  // Validation errors
  VALIDATION_ERROR: {
    message: 'Please check your input and try again',
    actionable: 'Make sure all required fields are filled correctly',
    retry: true,
  },
  
  // Business logic errors
  CASE_NOT_FOUND: {
    message: 'The requested business case could not be found',
    actionable: 'Please check the case ID or return to the dashboard',
    retry: false,
  },
  CASE_ACCESS_DENIED: {
    message: 'You do not have access to this business case',
    actionable: 'Please contact the case owner for access',
    retry: false,
  },
  
  // Generic fallbacks
  UNKNOWN_ERROR: {
    message: 'An unexpected error occurred',
    actionable: 'Please try again. If the problem continues, contact support',
    retry: true,
  },
};

/**
 * Determines error type based on error object or HTTP status code
 */
function getErrorType(error: unknown): keyof typeof ERROR_MESSAGES {
  // Handle different error object structures
  const errorObj = error && typeof error === 'object' ? error as Record<string, unknown> : {};
  const status = errorObj.status || (errorObj.response as Record<string, unknown>)?.status || errorObj.code;
  const message = String(errorObj.message || errorObj.detail || '');
  
  // Network errors
  if (errorObj.name === 'TypeError' && message.includes('fetch')) {
    return 'NETWORK_ERROR';
  }
  if (errorObj.name === 'AbortError' || message.includes('timeout')) {
    return 'TIMEOUT_ERROR';
  }
  
  // HTTP status codes
  switch (status) {
    case 401:
      return 'AUTH_EXPIRED';
    case 403:
      return 'AUTH_FORBIDDEN';
    case 404:
      if (message.toLowerCase().includes('case')) {
        return 'CASE_NOT_FOUND';
      }
      return 'UNKNOWN_ERROR';
    case 422:
      return 'VALIDATION_ERROR';
    case 500:
    case 502:
      return 'SERVER_ERROR';
    case 503:
      return 'SERVICE_UNAVAILABLE';
  }
  
  // Firebase Auth errors
  if (typeof errorObj.code === 'string' && errorObj.code.startsWith('auth/')) {
    switch (errorObj.code) {
      case 'auth/user-not-found':
      case 'auth/wrong-password':
      case 'auth/invalid-email':
        return 'VALIDATION_ERROR';
      case 'auth/unauthorized-domain':
      case 'auth/operation-not-allowed':
        return 'AUTH_FORBIDDEN';
      case 'auth/too-many-requests':
        return 'SERVER_ERROR';
      default:
        return 'AUTH_UNAUTHORIZED';
    }
  }
  
  // Business logic checks
  if (message.toLowerCase().includes('not found')) {
    return 'CASE_NOT_FOUND';
  }
  if (message.toLowerCase().includes('unauthorized') || message.toLowerCase().includes('forbidden')) {
    return 'AUTH_UNAUTHORIZED';
  }
  if (message.toLowerCase().includes('access denied')) {
    return 'CASE_ACCESS_DENIED';
  }
  
  return 'UNKNOWN_ERROR';
}

/**
 * Formats any error into a user-friendly message with actionable advice
 * @param error - The error object (can be Error, string, or any object)
 * @param context - Optional context for more specific messaging
 * @returns Formatted error object with user-friendly message
 */
export function formatErrorMessage(
  error: unknown,
  context?: string
): FormattedError {
  const errorType = getErrorType(error);
  const template = ERROR_MESSAGES[errorType];
  
  // Context-specific message adjustments
  let contextualMessage = template.message;
  if (context) {
    switch (context) {
      case 'login':
        contextualMessage = contextualMessage.replace('An unexpected error occurred', 'Unable to sign in');
        break;
      case 'signup':
        contextualMessage = contextualMessage.replace('An unexpected error occurred', 'Unable to create account');
        break;
      case 'load_cases':
        contextualMessage = contextualMessage.replace('An unexpected error occurred', 'Unable to load business cases');
        break;
      case 'save_data':
        contextualMessage = contextualMessage.replace('An unexpected error occurred', 'Unable to save changes');
        break;
      case 'submit_form':
        contextualMessage = contextualMessage.replace('An unexpected error occurred', 'Unable to submit form');
        break;
      case 'delete_item':
        contextualMessage = contextualMessage.replace('An unexpected error occurred', 'Unable to delete item');
        break;
      case 'export_pdf':
        contextualMessage = contextualMessage.replace('An unexpected error occurred', 'Unable to generate PDF');
        break;
    }
  }
  
  return {
    message: contextualMessage,
    severity: 'error',
    actionable: template.actionable,
    retry: template.retry,
  };
}

/**
 * Formats Firebase Auth errors with specific user-friendly messages
 */
export function formatAuthError(error: unknown): FormattedError {
  const errorObj = error && typeof error === 'object' ? error as Record<string, unknown> : {};
  const code = String(errorObj.code || '');
  
  switch (code) {
    case 'auth/user-not-found':
      return {
        message: 'No account found with this email address',
        severity: 'error',
        actionable: 'Please check your email or create a new account',
        retry: true,
      };
    case 'auth/wrong-password':
      return {
        message: 'Incorrect password',
        severity: 'error',
        actionable: 'Please try again or reset your password',
        retry: true,
      };
    case 'auth/invalid-email':
      return {
        message: 'Invalid email address format',
        severity: 'error',
        actionable: 'Please enter a valid email address',
        retry: true,
      };
    case 'auth/too-many-requests':
      return {
        message: 'Too many failed sign-in attempts',
        severity: 'warning',
        actionable: 'Please wait a few minutes before trying again',
        retry: true,
      };
    case 'auth/popup-closed-by-user':
      return {
        message: 'Sign-in was cancelled',
        severity: 'info',
        actionable: 'Please try signing in again',
        retry: true,
      };
    case 'auth/unauthorized-domain':
      return {
        message: 'This domain is not authorized for sign-in',
        severity: 'error',
        actionable: 'Please contact your administrator',
        retry: false,
      };
    default:
      return formatErrorMessage(error, 'login');
  }
}

/**
 * Formats validation errors for form fields
 */
export function formatValidationError(
  fieldName: string,
  error: unknown
): FormattedError {
  const errorObj = error && typeof error === 'object' ? error as Record<string, unknown> : {};
  const message = String(errorObj.message || error || 'Invalid input');
  
  return {
    message: `${fieldName}: ${message}`,
    severity: 'error',
    actionable: 'Please correct the highlighted fields and try again',
    retry: true,
  };
}

/**
 * Creates a generic error message for unexpected errors
 */
export function createGenericError(context?: string): FormattedError {
  return formatErrorMessage(new Error('Unknown error'), context);
}

/**
 * Checks if an error indicates a temporary issue that the user should retry
 */
export function isRetryableError(error: unknown): boolean {
  const errorType = getErrorType(error);
  return ERROR_MESSAGES[errorType].retry;
}

/**
 * Extracts a user-friendly message from various error object structures
 * Legacy function for backward compatibility - prefer formatErrorMessage
 */
export function getUserFriendlyMessage(error: unknown): string {
  const formatted = formatErrorMessage(error);
  return formatted.actionable 
    ? `${formatted.message}. ${formatted.actionable}`
    : formatted.message;
} 