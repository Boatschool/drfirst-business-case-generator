/**
 * Common API types to replace 'any' types throughout the application
 */

export interface ApiError extends Error {
  status?: number;
  code?: string;
  details?: unknown;
}

export interface ApiResponse<T = unknown> {
  data?: T;
  message?: string;
  error?: string;
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

// HTTP Response wrapper
export interface HttpResponse<T = unknown> {
  status: number;
  statusText: string;
  data: T;
  headers: Record<string, string>;
}

// Generic form field change event
export type FormFieldChangeEvent = React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>;

// Common event handler types
export type ClickHandler = (event: React.MouseEvent<HTMLElement>) => void;
export type SubmitHandler = (event: React.FormEvent<HTMLFormElement>) => void;
export type KeyboardHandler = (event: React.KeyboardEvent<HTMLElement>) => void; 