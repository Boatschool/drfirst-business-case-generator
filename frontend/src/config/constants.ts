/**
 * Core constants for the DrFirst Business Case Generator Frontend.
 * 
 * This module centralizes magic numbers, hardcoded strings, and configuration values
 * to improve code maintainability and reduce the risk of inconsistencies.
 */

// ============================================================================
// Application Limits and Constraints
// ============================================================================

export const APP_LIMITS = {
  // File upload limits
  MAX_UPLOAD_SIZE_BYTES: 5_000_000, // 5MB
  MAX_UPLOAD_SIZE_MB: 5,
  
  // Text input limits
  MAX_TITLE_LENGTH: 500,
  MAX_DESCRIPTION_LENGTH: 10000,
  MAX_COMMENT_LENGTH: 2000,
  
  // Pagination
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,
  MIN_PAGE_SIZE: 5,
  
  // UI constraints
  MAX_BREADCRUMB_ITEMS: 5,
  MAX_TOAST_MESSAGES: 3,
  MAX_RECENT_ITEMS: 10,
} as const;

// ============================================================================
// Timeouts and Delays
// ============================================================================

export const TIMEOUTS = {
  // API request timeouts (milliseconds)
  API_REQUEST_TIMEOUT: 30_000, // 30 seconds
  UPLOAD_TIMEOUT: 120_000, // 2 minutes
  GENERATION_TIMEOUT: 1_800_000, // 30 minutes
  
  // UI timeouts
  TOAST_AUTO_HIDE: 5_000, // 5 seconds
  DEBOUNCE_SEARCH: 300, // 300ms
  LOADING_SPINNER_DELAY: 200, // 200ms before showing spinner
  
  // Polling intervals
  STATUS_POLL_INTERVAL: 2_000, // 2 seconds
  HEARTBEAT_INTERVAL: 30_000, // 30 seconds
  
  // Cache expiry
  CACHE_EXPIRE_SHORT: 300_000, // 5 minutes
  CACHE_EXPIRE_LONG: 3_600_000, // 1 hour
} as const;

// ============================================================================
// UI Constants
// ============================================================================

export const UI_CONSTANTS = {
  // Layout dimensions
  HEADER_HEIGHT: 64, // pixels
  SIDEBAR_WIDTH: 280, // pixels
  SIDEBAR_COLLAPSED_WIDTH: 72, // pixels
  FOOTER_HEIGHT: 48, // pixels
  
  // Table settings
  DEFAULT_ROWS_PER_PAGE: 10,
  ROWS_PER_PAGE_OPTIONS: [5, 10, 25, 50] as const,
  
  // Card/Modal dimensions
  MODAL_MAX_WIDTH: 800, // pixels
  CARD_MIN_HEIGHT: 200, // pixels
  
  // Animation durations (milliseconds)
  TRANSITION_FAST: 150,
  TRANSITION_NORMAL: 250,
  TRANSITION_SLOW: 400,
  
  // Z-index values
  Z_INDEX: {
    DROPDOWN: 1000,
    MODAL: 1300,
    TOOLTIP: 1500,
    TOAST: 2000,
  },
} as const;

// ============================================================================
// Local Storage Keys
// ============================================================================

export const STORAGE_KEYS = {
  // User preferences
  THEME_PREFERENCE: 'drfirst_theme',
  SIDEBAR_COLLAPSED: 'drfirst_sidebar_collapsed',
  TABLE_DENSITY: 'drfirst_table_density',
  
  // Application state
  LAST_ROUTE: 'drfirst_last_route',
  FILTER_PREFERENCES: 'drfirst_filters',
  SORT_PREFERENCES: 'drfirst_sort',
  
  // Cache keys
  USER_PROFILE_CACHE: 'drfirst_user_profile',
  BUSINESS_CASES_CACHE: 'drfirst_business_cases',
  
  // Authentication
  AUTH_REDIRECT_PATH: 'drfirst_auth_redirect',
} as const;

// ============================================================================
// API Constants
// ============================================================================

export const API_CONSTANTS = {
  // Retry configuration
  MAX_RETRY_ATTEMPTS: 3,
  RETRY_DELAY_BASE: 1000, // 1 second
  RETRY_DELAY_MULTIPLIER: 2,
  
  // Request headers
  CONTENT_TYPE_JSON: 'application/json',
  CONTENT_TYPE_MULTIPART: 'multipart/form-data',
  
  // Response status codes
  HTTP_STATUS: {
    OK: 200,
    CREATED: 201,
    BAD_REQUEST: 400,
    UNAUTHORIZED: 401,
    FORBIDDEN: 403,
    NOT_FOUND: 404,
    CONFLICT: 409,
    INTERNAL_SERVER_ERROR: 500,
  },
} as const;

// ============================================================================
// Form Constants
// ============================================================================

export const FORM_CONSTANTS = {
  // Validation
  MIN_PASSWORD_LENGTH: 8,
  MIN_TITLE_LENGTH: 3,
  MIN_DESCRIPTION_LENGTH: 10,
  
  // Input types
  ACCEPTED_FILE_TYPES: [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
  ] as const,
  
  ACCEPTED_IMAGE_TYPES: [
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
  ] as const,
  
  // Default values
  DEFAULT_PRIORITY: 'medium' as const,
  DEFAULT_STATUS_FILTER: 'all' as const,
} as const;

// ============================================================================
// Error Messages
// ============================================================================

export const ERROR_MESSAGES = {
  // Network errors
  NETWORK_ERROR: 'Network error. Please check your connection and try again.',
  TIMEOUT_ERROR: 'Request timed out. Please try again.',
  SERVER_ERROR: 'Server error. Please try again later.',
  
  // Authentication errors
  UNAUTHORIZED: 'You are not authorized to perform this action.',
  SESSION_EXPIRED: 'Your session has expired. Please sign in again.',
  
  // Validation errors
  REQUIRED_FIELD: 'This field is required.',
  INVALID_EMAIL: 'Please enter a valid email address.',
  INVALID_FILE_TYPE: 'Invalid file type. Please select a supported file.',
  FILE_TOO_LARGE: 'File is too large. Maximum size is 5MB.',
  
  // Business logic errors
  BUSINESS_CASE_NOT_FOUND: 'Business case not found.',
  INVALID_STATUS_TRANSITION: 'Invalid status transition.',
  
  // Generic errors
  UNEXPECTED_ERROR: 'An unexpected error occurred. Please try again.',
  FEATURE_NOT_AVAILABLE: 'This feature is not available at the moment.',
} as const;

// ============================================================================
// Success Messages
// ============================================================================

export const SUCCESS_MESSAGES = {
  // CRUD operations
  SAVED_SUCCESSFULLY: 'Saved successfully.',
  DELETED_SUCCESSFULLY: 'Deleted successfully.',
  UPDATED_SUCCESSFULLY: 'Updated successfully.',
  
  // Business case operations
  BUSINESS_CASE_CREATED: 'Business case created successfully.',
  PRD_SUBMITTED: 'PRD submitted for review successfully.',
  STATUS_UPDATED: 'Status updated successfully.',
  
  // File operations
  FILE_UPLOADED: 'File uploaded successfully.',
  EXPORT_COMPLETED: 'Export completed successfully.',
  
  // User actions
  SETTINGS_SAVED: 'Settings saved successfully.',
  PASSWORD_CHANGED: 'Password changed successfully.',
} as const;

// ============================================================================
// Route Constants
// ============================================================================

export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  DASHBOARD: '/dashboard',
  BUSINESS_CASES: '/business-cases',
  BUSINESS_CASE_DETAIL: '/business-cases/:id',
  BUSINESS_CASE_CREATE: '/business-cases/create',
  PROFILE: '/profile',
  SETTINGS: '/settings',
  ADMIN: '/admin',
  NOT_FOUND: '/404',
} as const;

// ============================================================================
// Feature Flags
// ============================================================================

export const FEATURE_FLAGS = {
  ENABLE_DARK_MODE: true,
  ENABLE_EXPORT_PDF: true,
  ENABLE_ADVANCED_FILTERS: true,
  ENABLE_BULK_OPERATIONS: false,
  ENABLE_REAL_TIME_UPDATES: true,
  ENABLE_NOTIFICATIONS: true,
} as const;

// ============================================================================
// Environment Constants
// ============================================================================

export const ENV_CONSTANTS = {
  DEVELOPMENT: 'development',
  STAGING: 'staging',
  PRODUCTION: 'production',
} as const;

// ============================================================================
// Business Constants
// ============================================================================

export const BUSINESS_CONSTANTS = {
  // Priority levels
  PRIORITY_LEVELS: ['low', 'medium', 'high', 'critical'] as const,
  
  // Default values for calculations
  DEFAULT_HOURLY_RATE: 100,
  DEFAULT_SPRINT_LENGTH_WEEKS: 2,
  DEFAULT_DISCOUNT_RATE: 0.08, // 8%
  
  // Validation ranges
  MIN_EFFORT_HOURS: 1,
  MAX_EFFORT_HOURS: 10000,
  MIN_ROI_PERCENTAGE: -100,
  MAX_ROI_PERCENTAGE: 1000,
} as const; 