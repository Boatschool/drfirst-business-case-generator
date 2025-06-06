/**
 * Comprehensive API types to replace 'any' types throughout the application
 */

// ================================
// ERROR TYPES
// ================================

export interface ApiError extends Error {
  status?: number;
  code?: string;
  details?: unknown;
  response?: {
    data?: unknown;
    status?: number;
    statusText?: string;
  };
}

export interface ValidationError {
  field: string;
  message: string;
  code?: string;
}

export interface ApiValidationErrorResponse {
  message: string;
  errors: ValidationError[];
  status: number;
}

// Firebase Auth error interface
export interface FirebaseAuthError extends Error {
  code: string;
  customData?: {
    email?: string;
    credential?: unknown;
  };
}

// Network/HTTP errors
export interface NetworkError extends Error {
  status?: number;
  statusText?: string;
  url?: string;
}

// Service-level errors
export interface ServiceError extends Error {
  service: string;
  operation: string;
  timestamp: string;
  details?: unknown;
}

// Generic app error for unknown error types
export interface AppError extends Error {
  type: 'api' | 'validation' | 'network' | 'service' | 'auth' | 'unknown';
  code?: string;
  status?: number;
  details?: unknown;
}

// ================================
// API RESPONSE TYPES
// ================================

export interface ApiResponse<T = unknown> {
  data?: T;
  message?: string;
  error?: string;
  success?: boolean;
}

export interface PaginatedResponse<T = unknown> {
  data: T[];
  total: number;
  page: number;
  per_page: number;
  has_next: boolean;
  has_prev: boolean;
}

// HTTP Response wrapper
export interface HttpResponse<T = unknown> {
  status: number;
  statusText: string;
  data: T;
  headers: Record<string, string>;
}

// Service method responses
export interface ServiceResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: AppError;
  message?: string;
}

// ================================
// REACT EVENT TYPES
// ================================

// Generic form field change event
export type FormFieldChangeEvent = React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>;

// Specific input events
export type InputChangeEvent = React.ChangeEvent<HTMLInputElement>;
export type TextAreaChangeEvent = React.ChangeEvent<HTMLTextAreaElement>;
export type SelectChangeEvent = React.ChangeEvent<HTMLSelectElement>;

// Common event handler types
export type ClickHandler = (event: React.MouseEvent<HTMLElement>) => void;
export type SubmitHandler = (event: React.FormEvent<HTMLFormElement>) => void;
export type KeyboardHandler = (event: React.KeyboardEvent<HTMLElement>) => void;
export type FocusHandler = (event: React.FocusEvent<HTMLElement>) => void;

// Button-specific handlers
export type ButtonClickHandler = (event: React.MouseEvent<HTMLButtonElement>) => void;

// ================================
// UTILITY TYPES
// ================================

// For gradual migration from 'any' to specific types
export type UnknownObject = Record<string, unknown>;
export type UnknownArray = unknown[];

// JSON-serializable data
export type JsonValue = string | number | boolean | null | JsonObject | JsonArray;
export interface JsonObject { [key: string]: JsonValue }
export type JsonArray = Array<JsonValue>;

// Component props
export interface BaseComponentProps {
  className?: string;
  'data-testid'?: string;
}

// ================================
// ERROR HANDLING UTILITIES
// ================================

// Type guard for Error objects
export const isError = (error: unknown): error is Error => {
  return error instanceof Error;
};

// Type guard for API errors
export const isApiError = (error: unknown): error is ApiError => {
  return isError(error) && 'status' in error;
};

// Type guard for Firebase auth errors
export const isFirebaseAuthError = (error: unknown): error is FirebaseAuthError => {
  return isError(error) && 'code' in error && typeof (error as FirebaseAuthError).code === 'string';
};

// Convert unknown error to AppError
export const toAppError = (error: unknown, type: AppError['type'] = 'unknown'): AppError => {
  if (isError(error)) {
    return {
      ...error,
      type,
      name: error.name,
      message: error.message,
    };
  }
  
  return {
    name: 'AppError',
    message: typeof error === 'string' ? error : 'An unexpected error occurred',
    type,
  };
};

// ================================
// LOADING AND ASYNC STATES
// ================================

export interface LoadingState {
  isLoading: boolean;
  error: AppError | null;
}

export interface AsyncState<T> extends LoadingState {
  data: T | null;
}

// ================================
// FORM TYPES
// ================================

export interface FormState<T = UnknownObject> {
  values: T;
  errors: Record<string, string>;
  touched: Record<string, boolean>;
  isSubmitting: boolean;
  isValid: boolean;
}

export interface FormFieldProps {
  name: string;
  value: unknown;
  onChange: (event: FormFieldChangeEvent) => void;
  onBlur?: (event: React.FocusEvent<HTMLElement>) => void;
  error?: string;
  disabled?: boolean;
  required?: boolean;
} 