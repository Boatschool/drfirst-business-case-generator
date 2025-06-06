# Enhanced Logging Strategy Implementation

## Overview

This document describes the comprehensive logging strategy implemented for the DrFirst Business Case Generator backend. The implementation provides structured, contextual logging that's optimized for both local development and cloud production environments.

## Features

### 🏗️ **Structured Logging**
- **JSON format** for production/staging environments (Cloud Run friendly)
- **Human-readable format** for development
- **Contextual information** automatically included in all log messages
- **Proper log levels** (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### 🌍 **Environment-Aware Configuration**
- Automatic format switching based on `ENVIRONMENT` setting
- Configurable log levels via `LOG_LEVEL` environment variable
- Cloud Run optimized output to stdout

### 📊 **Contextual Logging Utilities**
- API request context (request_id, user_id, endpoint, method)
- Business case operations (case_id, user_id, operation)
- Agent operations (agent_name, case_id, operation)
- Error handling with full context and stack traces
- Performance metrics logging

## File Structure

```
backend/app/core/
├── logging_config.py          # Main logging configuration module
├── LOGGING_IMPLEMENTATION.md  # This documentation file
└── config.py                  # Contains LOG_LEVEL and ENVIRONMENT settings

backend/app/utils/
└── logging_examples.py        # Comprehensive usage examples

backend/app/main.py             # Updated to use new logging setup
```

## Configuration

### Environment Variables

| Variable | Description | Default | Examples |
|----------|-------------|---------|----------|
| `LOG_LEVEL` | Logging level | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `ENVIRONMENT` | Application environment | `development` | `development`, `staging`, `production` |

### Logging Formats

**Development (Human-readable):**
```
2024-01-15 10:30:45 - app.agents.orchestrator_agent - INFO - orchestrator_agent.py:handle_request:245 - Business case creation started
```

**Production/Staging (JSON):**
```json
{
  "asctime": "2024-01-15 10:30:45",
  "levelname": "INFO",
  "name": "app.agents.orchestrator_agent",
  "module": "orchestrator_agent",
  "funcName": "handle_request",
  "lineno": 245,
  "message": "Business case creation started",
  "case_id": "case_123",
  "user_id": "user_456",
  "operation": "create_case"
}
```

## Usage Examples

### Basic Logger Setup

```python
import logging
from app.core.logging_config import setup_logging

# In main.py (already implemented)
setup_logging()

# In any module
logger = logging.getLogger(__name__)
logger.info("Module initialized")
```

### Contextual Logging

```python
from app.core.logging_config import get_contextual_logger

# Create logger with persistent context
logger = get_contextual_logger(__name__, {
    'service': 'business_case_generator',
    'version': '1.0.0'
})

logger.info("Operation started", extra={'operation_id': 'op_123'})
```

### API Request Logging

```python
from app.core.logging_config import log_api_request

# In API route handlers
@router.get("/cases/{case_id}")
async def get_case(case_id: str, current_user: dict = Depends(get_current_user)):
    request_logger = log_api_request(
        logger, 
        request_id="req_123", 
        user_id=current_user["uid"], 
        endpoint=f"/cases/{case_id}", 
        method="GET"
    )
    
    request_logger.info("Processing case retrieval request")
    # ... processing logic ...
    request_logger.info("Case retrieved successfully", extra={'case_status': 'ACTIVE'})
```

### Business Case Operations

```python
from app.core.logging_config import log_business_case_operation

case_logger = log_business_case_operation(
    logger, 
    case_id="case_123", 
    user_id="user_456", 
    operation="status_update"
)

case_logger.info("Updating case status", extra={'new_status': 'PRD_REVIEW'})
```

### Agent Operations

```python
from app.core.logging_config import log_agent_operation

agent_logger = log_agent_operation(
    logger, 
    agent_name="ProductManagerAgent", 
    case_id="case_123", 
    operation="draft_prd"
)

agent_logger.info("Starting PRD generation")
agent_logger.info("PRD completed", extra={'draft_length': 2500})
```

### Error Handling

```python
from app.core.logging_config import log_error_with_context

try:
    # Some operation that might fail
    result = await risky_operation()
except Exception as e:
    log_error_with_context(
        logger,
        "Operation failed during processing",
        e,
        {
            'case_id': case_id,
            'user_id': user_id,
            'operation_step': 'validation',
            'input_size': len(input_data)
        }
    )
```

### Performance Metrics

```python
from app.core.logging_config import log_performance_metric
import time

start_time = time.time()
# ... perform operation ...
duration_ms = (time.time() - start_time) * 1000

log_performance_metric(
    logger,
    operation="database_query",
    duration_ms=duration_ms,
    success=True,
    context={
        'query_type': 'business_case_fetch',
        'result_count': 15
    }
)
```

### Function Entry/Exit Tracing

```python
from app.core.logging_config import log_function_entry_exit

@log_function_entry_exit(logger)
async def complex_processing_function(data):
    # This will automatically log entry and exit at DEBUG level
    # ... processing logic ...
    return result
```

## Cloud Run Integration

### Viewing Logs in Google Cloud Console

1. **Navigate to Cloud Logging:**
   - Go to Google Cloud Console → Logging → Logs Explorer

2. **Filter by Service:**
   ```
   resource.type="cloud_run_revision"
   resource.labels.service_name="drfirst-business-case-backend"
   ```

3. **Filter by Log Level:**
   ```
   severity>=WARNING
   ```

4. **Search by Context:**
   ```
   jsonPayload.case_id="case_123"
   jsonPayload.user_id="user_456"
   ```

### Sample Cloud Run Log Queries

**All errors for a specific user:**
```
resource.type="cloud_run_revision"
jsonPayload.user_id="user_456"
severity>=ERROR
```

**Performance metrics:**
```
resource.type="cloud_run_revision"
jsonPayload.metric_type="performance"
```

**Business case operations:**
```
resource.type="cloud_run_revision"
jsonPayload.operation="create_case"
```

## Testing the Logging System

### Local Development Testing

1. **Set environment variables:**
   ```bash
   export LOG_LEVEL=DEBUG
   export ENVIRONMENT=development
   ```

2. **Run the logging examples:**
   ```bash
   cd backend
   python -m app.utils.logging_examples
   ```

3. **Start the application and trigger operations:**
   ```bash
   uvicorn app.main:app --reload
   ```

### Production Testing

1. **Set production environment:**
   ```bash
   export LOG_LEVEL=INFO
   export ENVIRONMENT=production
   ```

2. **Verify JSON output:**
   - Start application
   - Trigger API requests
   - Observe structured JSON logs in stdout

## Best Practices

### 📋 **Log Level Guidelines**

| Level | Usage | Examples |
|-------|-------|----------|
| `DEBUG` | Detailed diagnostic info | Function entry/exit, variable values |
| `INFO` | General operational events | Request processing, status changes |
| `WARNING` | Unexpected but recoverable | Fallback operations, validation warnings |
| `ERROR` | Error conditions | Operation failures, exceptions |
| `CRITICAL` | Critical system failures | Service unavailable, data corruption |

### 🏷️ **Context Guidelines**

**Always Include:**
- `case_id` for business case operations
- `user_id` for user-related operations
- `request_id` for API requests
- `agent_name` for agent operations

**Consider Including:**
- Operation timing information
- Data sizes (number of records, file sizes)
- Status transitions
- Configuration values used

### 🚫 **Security Considerations**

**Never Log:**
- Passwords or authentication tokens
- Credit card numbers or PII
- Full request/response bodies (unless necessary)
- Internal system credentials

**Sanitize:**
- User input before logging
- File paths (remove sensitive directory names)
- Error messages (avoid exposing internal structure)

## Migration from Previous Logging

### Print Statement Replacements

**Before:**
```python
print(f"Processing case {case_id} for user {user_id}")
print(f"Error occurred: {e}")
```

**After:**
```python
case_logger = log_business_case_operation(logger, case_id, user_id, "process")
case_logger.info("Processing case")

# For errors:
log_error_with_context(logger, "Processing failed", e, {'case_id': case_id})
```

### Logger Instantiation

**Before:**
```python
import logging
logger = logging.getLogger(__name__)
logger.info(f"Simple message with {variable}")
```

**After:**
```python
import logging
from app.core.logging_config import log_business_case_operation

logger = logging.getLogger(__name__)
case_logger = log_business_case_operation(logger, case_id, user_id, operation)
case_logger.info("Simple message", extra={'variable': variable})
```

## Monitoring and Alerting

### Recommended Alerts

1. **Error Rate Alert:**
   ```
   Count of ERROR level logs > 10 per minute
   ```

2. **Performance Alert:**
   ```
   95th percentile of operation duration > 5000ms
   ```

3. **Authentication Failures:**
   ```
   Count of authentication errors > 5 per minute
   ```

### Key Metrics to Track

- Error rates by endpoint
- Performance metrics by operation type
- User activity patterns
- Agent processing times
- Database operation latencies

## Troubleshooting

### Common Issues

1. **Logs not appearing in Cloud Run:**
   - Verify logs are going to stdout/stderr
   - Check Cloud Run service logs in Console
   - Ensure proper IAM permissions

2. **JSON formatting issues:**
   - Verify `python-json-logger` is installed
   - Check `ENVIRONMENT` variable setting
   - Review any custom formatting code

3. **Missing context:**
   - Verify contextual loggers are being used
   - Check that context is passed properly
   - Review extra parameters in log calls

4. **Performance impact:**
   - Monitor logging overhead
   - Consider reducing DEBUG level logging in production
   - Use asynchronous logging if needed

## Future Enhancements

### Planned Features

1. **Distributed Tracing:**
   - Request correlation IDs
   - Span tracking across services
   - Integration with Google Cloud Trace

2. **Log Aggregation:**
   - Centralized log analysis
   - Custom dashboards
   - Automated anomaly detection

3. **Enhanced Performance Metrics:**
   - Custom metrics export
   - Integration with monitoring systems
   - Real-time performance dashboards

### Integration Opportunities

- **Error Reporting:** Google Error Reporting integration
- **Metrics:** Google Cloud Monitoring custom metrics
- **Alerting:** PagerDuty or Slack integration
- **Analysis:** BigQuery log exports for analysis

## Conclusion

This logging implementation provides a robust foundation for monitoring and debugging the DrFirst Business Case Generator. The structured approach ensures logs are useful for both development and production operations, while the contextual information makes it easy to trace issues across the system.

For questions or improvements, please refer to the code in `app/core/logging_config.py` or run the examples in `app/utils/logging_examples.py`. 