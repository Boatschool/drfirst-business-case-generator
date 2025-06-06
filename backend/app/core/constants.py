"""
Core constants for the DrFirst Business Case Generator Backend.

This module centralizes magic numbers, hardcoded strings, and configuration values
to improve code maintainability and reduce the risk of inconsistencies.
"""

from typing import List

# ============================================================================
# HTTP Status Codes (for consistency)
# ============================================================================

class HTTPStatus:
    """Common HTTP status codes used throughout the application."""
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500

# ============================================================================
# Application Limits and Timeouts
# ============================================================================

class Limits:
    """Application limits and constraints."""
    MAX_BUSINESS_CASE_TITLE_LENGTH = 500
    MAX_BUSINESS_CASE_DESCRIPTION_LENGTH = 10000
    MAX_UPLOAD_SIZE_BYTES = 5_000_000  # 5MB
    MAX_PAGINATION_LIMIT = 100
    DEFAULT_PAGINATION_LIMIT = 20
    
    # Agent processing limits
    MAX_AGENT_RETRY_ATTEMPTS = 3
    AGENT_TIMEOUT_SECONDS = 300  # 5 minutes
    MAX_CONCURRENT_AGENTS = 5

class Timeouts:
    """Timeout values in seconds."""
    DATABASE_OPERATION = 30
    EXTERNAL_API_CALL = 60
    FILE_UPLOAD = 120
    BUSINESS_CASE_GENERATION = 1800  # 30 minutes
    
    # Vertex AI specific timeouts
    VERTEX_AI_REQUEST = 120
    VERTEX_AI_STREAMING = 300

# ============================================================================
# Business Logic Constants
# ============================================================================

class BusinessRules:
    """Business logic constants and rules."""
    
    # Cost analysis constants
    DEFAULT_HOURLY_RATE = 100.0
    MIN_EFFORT_HOURS = 1
    MAX_EFFORT_HOURS = 10000
    
    # Value analysis constants
    MIN_ROI_PERCENTAGE = -100.0  # Can have negative ROI
    MAX_ROI_PERCENTAGE = 1000.0  # 1000% ROI cap for validation
    
    # Financial model constants
    DEFAULT_DISCOUNT_RATE = 0.08  # 8% discount rate
    MAX_PROJECT_DURATION_YEARS = 10
    
    # Planning constants
    DEFAULT_SPRINT_LENGTH_WEEKS = 2
    MIN_PROJECT_DURATION_WEEKS = 1
    MAX_PROJECT_DURATION_WEEKS = 260  # 5 years

# ============================================================================
# Message Types and Sources
# ============================================================================

class MessageTypes:
    """Standard message types for business case history."""
    STATUS_UPDATE = "STATUS_UPDATE"
    PRD_SUBMISSION = "PRD_SUBMISSION"
    PRD_APPROVAL = "PRD_APPROVAL"
    PRD_REJECTION = "PRD_REJECTION"
    SYSTEM_DESIGN_GENERATED = "SYSTEM_DESIGN_GENERATED"
    EFFORT_ESTIMATE_GENERATED = "EFFORT_ESTIMATE_GENERATED"
    COST_ESTIMATE_GENERATED = "COST_ESTIMATE_GENERATED"
    VALUE_ANALYSIS_GENERATED = "VALUE_ANALYSIS_GENERATED"
    FINANCIAL_MODEL_GENERATED = "FINANCIAL_MODEL_GENERATED"
    FINAL_SUBMISSION = "FINAL_SUBMISSION"
    FINAL_APPROVAL = "FINAL_APPROVAL"
    FINAL_REJECTION = "FINAL_REJECTION"
    AGENT_ERROR = "AGENT_ERROR"
    USER_COMMENT = "USER_COMMENT"

class MessageSources:
    """Standard message sources for business case history."""
    USER = "USER"
    SYSTEM = "SYSTEM"
    ORCHESTRATOR_AGENT = "ORCHESTRATOR_AGENT"
    PRD_AGENT = "PRD_AGENT"
    ARCHITECT_AGENT = "ARCHITECT_AGENT"
    PLANNER_AGENT = "PLANNER_AGENT"
    COST_ANALYST_AGENT = "COST_ANALYST_AGENT"
    SALES_VALUE_ANALYST_AGENT = "SALES_VALUE_ANALYST_AGENT"
    FINANCIAL_ANALYST_AGENT = "FINANCIAL_ANALYST_AGENT"

# ============================================================================
# Default Values
# ============================================================================

class Defaults:
    """Default values used throughout the application."""
    
    # Pagination
    PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # Business case defaults
    DEFAULT_PRIORITY = "medium"
    DEFAULT_CASE_TITLE = "Untitled Business Case"
    
    # Agent configuration
    VERTEX_AI_TEMPERATURE = 0.6
    VERTEX_AI_MAX_TOKENS = 4096
    VERTEX_AI_TOP_P = 0.9
    VERTEX_AI_TOP_K = 40
    
    # Export configuration
    PDF_MAX_FILE_SIZE_MB = 50
    EXPORT_TIMEOUT_MINUTES = 10

# ============================================================================
# Validation Patterns
# ============================================================================

class ValidationPatterns:
    """Regular expressions and validation patterns."""
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    FIREBASE_UID_PATTERN = r'^[a-zA-Z0-9]{28}$'
    
    # Business case validation
    CASE_ID_PATTERN = r'^[a-zA-Z0-9_-]+$'
    CASE_TITLE_PATTERN = r'^[a-zA-Z0-9\s\-_.,()]+$'

# ============================================================================
# Collection Names (Firestore)
# ============================================================================

class Collections:
    """Firestore collection names."""
    USERS = "users"
    BUSINESS_CASES = "business_cases"
    JOBS = "jobs"
    RATE_CARDS = "rateCards"  # Note: camelCase to match existing Firestore collection
    GLOBAL_CONFIG = "global_config"
    AUDIT_LOGS = "audit_logs"

# ============================================================================
# Error Messages
# ============================================================================

class ErrorMessages:
    """Standard error messages used throughout the application."""
    
    # Authentication errors
    USER_ID_NOT_FOUND = "User ID not found in token."
    INSUFFICIENT_PERMISSIONS = "You do not have permission to perform this action."
    INVALID_TOKEN = "Invalid or expired authentication token."
    
    # Business case errors
    BUSINESS_CASE_NOT_FOUND = "Business case not found."
    INVALID_STATUS_TRANSITION = "Invalid status transition."
    PRD_CONTENT_MISSING = "PRD content is required."
    
    # Validation errors
    INVALID_EMAIL = "Invalid email address format."
    INVALID_INPUT = "Invalid input provided."
    REQUIRED_FIELD_MISSING = "Required field is missing."
    
    # System errors
    INTERNAL_SERVER_ERROR = "An internal server error occurred."
    DATABASE_ERROR = "Database operation failed."
    EXTERNAL_SERVICE_ERROR = "External service is currently unavailable."

# ============================================================================
# Success Messages
# ============================================================================

class SuccessMessages:
    """Standard success messages."""
    BUSINESS_CASE_CREATED = "Business case created successfully."
    STATUS_UPDATED = "Status updated successfully."
    PRD_APPROVED = "PRD approved successfully."
    PRD_REJECTED = "PRD rejected successfully."
    FINAL_APPROVAL_GRANTED = "Business case approved successfully."
    FINAL_APPROVAL_REJECTED = "Business case rejected." 