# DrFirst Business Case Generator - E2E Workflow Test

## Overview

This comprehensive End-to-End (E2E) test script validates the complete "happy path" business case workflow from initiation through final approval. It simulates different user roles performing approval actions at each stage and verifies proper status transitions and data persistence.

## Features

- ✅ **Complete Workflow Testing**: Tests all 12 stages of the business case lifecycle
- 🔐 **Firebase Authentication**: Authenticates as different test users with appropriate roles
- 📊 **Status Verification**: Polls and verifies expected status transitions after each action
- 📝 **Data Validation**: Checks that required data is created/updated at each stage
- 🏷️ **Role-Based Testing**: Simulates approvals by users with correct roles
- 📋 **Comprehensive Logging**: Detailed logging with timestamps and error tracking
- 📄 **Test Reporting**: Generates JSON reports with success/failure details
- ⏱️ **Performance Monitoring**: Tracks timing for each step and overall workflow
- 🔄 **Retry Logic**: Built-in retry mechanisms for network requests
- 🧹 **Error Handling**: Graceful error handling with informative messages

## Workflow Stages Tested

| Stage | Action | User Role | Status Transition |
|-------|--------|-----------|-------------------|
| 1 | Initiate Business Case | Initiator | `INTAKE` → `PRD_DRAFTING` |
| 2 | Submit PRD for Review | Initiator | `PRD_DRAFTING` → `PRD_REVIEW` |
| 3 | Approve PRD | PRD Approver | `PRD_REVIEW` → `SYSTEM_DESIGN_DRAFTING` |
| 4 | Wait for System Design | Developer | `SYSTEM_DESIGN_DRAFTING` → `SYSTEM_DESIGN_DRAFTED` |
| 5 | Submit System Design | Initiator | `SYSTEM_DESIGN_DRAFTED` → `SYSTEM_DESIGN_PENDING_REVIEW` |
| 6 | Approve System Design | Developer | `SYSTEM_DESIGN_PENDING_REVIEW` → `PLANNING_COMPLETE` |
| 7 | Submit Effort Estimate | Initiator | `PLANNING_COMPLETE` → `EFFORT_PENDING_REVIEW` |
| 8 | Approve Effort Estimate | Effort Approver | `EFFORT_PENDING_REVIEW` → `COSTING_PENDING_REVIEW` |
| 9 | Approve Cost Estimate | Finance Approver | `COSTING_PENDING_REVIEW` → `VALUE_PENDING_REVIEW` |
| 10 | Approve Value Projection | Sales Manager | `VALUE_PENDING_REVIEW` → `FINANCIAL_MODEL_COMPLETE` |
| 11 | Submit for Final Approval | Initiator | `FINANCIAL_MODEL_COMPLETE` → `PENDING_FINAL_APPROVAL` |
| 12 | Final Approval | Final Approver | `PENDING_FINAL_APPROVAL` → `APPROVED` |

## Prerequisites

### 1. Python Environment
- Python 3.7 or higher
- Required packages (install with `pip install -r requirements_e2e.txt`)

### 2. Backend API
- DrFirst Business Case Generator backend running on `http://localhost:8000` (or configured URL)
- All API endpoints operational
- Firebase authentication configured

### 3. Test Users Setup
Create test users in Firebase with appropriate roles:

```bash
# Example using Firebase CLI or Admin SDK
# Each user needs the role specified in their custom claims

test.initiator@drfirst.com        # No special role (case initiator)
test.prd.approver@drfirst.com     # PRD approval permissions
test.developer@drfirst.com        # DEVELOPER role
test.effort.approver@drfirst.com  # Effort estimation approval
test.finance@drfirst.com          # FINANCE_APPROVER role
test.sales@drfirst.com            # SALES_MANAGER_APPROVER role
test.final.approver@drfirst.com   # FINAL_APPROVER role
test.admin@drfirst.com            # ADMIN role
```

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements_e2e.txt
   ```

2. **Configure Test Environment**:
   ```bash
   # Copy configuration template
   cp e2e_config_template.yaml e2e_config.yaml
   
   # Edit configuration with your test environment details
   # Update API URLs, Firebase credentials, and test user accounts
   ```

3. **Set Environment Variables** (optional):
   ```bash
   export E2E_API_BASE_URL="http://localhost:8000"
   export E2E_FIREBASE_API_KEY="your_firebase_api_key"
   ```

## Usage

### Basic Execution

```bash
# Run the complete E2E workflow test
python workflow_e2e_tester.py
```

### Advanced Configuration

```bash
# Set custom API URL
E2E_API_BASE_URL="https://your-api.com" python workflow_e2e_tester.py

# Enable debug logging
DEBUG=1 python workflow_e2e_tester.py
```

## Test Configuration

The script uses the `TestConfig` class for configuration. Key settings:

```python
@dataclass
class TestConfig:
    # API Configuration
    api_base_url: str = "http://localhost:8000"
    firebase_api_key: str = "your_api_key"
    firebase_project_id: str = "drfirst-business-case-gen"
    
    # Test User Credentials
    initiator_email: str = "test.initiator@drfirst.com"
    # ... other test user emails
    
    # Timing Configuration
    max_poll_time: int = 300  # 5 minutes max polling
    poll_interval: int = 5    # 5 seconds between polls
    request_timeout: int = 30 # 30 seconds request timeout
```

## Output and Reporting

### Console Output
- Real-time progress with emoji indicators
- Step-by-step status updates
- Error messages with context
- Final summary with success/failure rates

### Log Files
- Detailed logs saved to `logs/e2e_workflow_YYYYMMDD_HHMMSS.log`
- JSON test reports saved to `logs/e2e_test_report_YYYYMMDD_HHMMSS.json`

### Sample Test Report
```json
{
  "test_summary": {
    "test_case_id": "abc123-def456-ghi789",
    "timestamp": "2025-01-08T19:30:00Z",
    "total_steps": 12,
    "successful_steps": 12,
    "failed_steps": 0,
    "success_rate": 100.0,
    "total_duration_seconds": 245.67,
    "overall_result": "PASS"
  },
  "step_results": [
    {
      "step_name": "1. Initiate Business Case",
      "user_email": "test.initiator@drfirst.com",
      "status": "SUCCESS",
      "duration_seconds": 15.23,
      "timestamp": "2025-01-08T19:25:00Z"
    }
    // ... more steps
  ]
}
```

## Error Handling

The script includes comprehensive error handling:

- **Authentication Failures**: Retries with exponential backoff
- **API Timeouts**: Configurable timeout and retry settings
- **Status Polling**: Polls for expected status with timeout
- **Network Issues**: Automatic retries for transient failures
- **Data Validation**: Verifies required data fields exist

## Customization

### Adding New Test Steps

To add a new workflow step:

```python
def _get_workflow_steps(self) -> List[WorkflowStep]:
    steps = [
        # ... existing steps
        
        # New custom step
        WorkflowStep(
            step_name="Custom Action",
            user_email=self.config.custom_user_email,
            expected_precondition_status=WorkflowStatus.SOME_STATUS,
            api_endpoint="/api/v1/cases/{case_id}/custom-action",
            http_method="POST",
            expected_post_status=WorkflowStatus.NEW_STATUS,
            payload={"custom": "data"},
            description="Perform custom workflow action",
            requires_data_check=True,
            data_field="custom_field"
        )
    ]
    return steps
```

### Custom Test Data

Modify the test case data in `_get_workflow_steps()`:

```python
payload={
    "request_type": "initiate_case",
    "payload": {
        "problemStatement": "Your custom problem statement",
        "projectTitle": "Your Custom Project",
        "relevantLinks": [
            {"name": "Custom Link", "url": "https://example.com"}
        ]
    }
}
```

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Verify Firebase API key is correct
   - Ensure test users exist in Firebase
   - Check user passwords are correct

2. **API Connection Issues**
   - Verify backend is running and accessible
   - Check API base URL configuration
   - Ensure CORS is properly configured

3. **Role Permission Errors**
   - Verify test users have correct roles in Firebase custom claims
   - Check role-based access control configuration

4. **Timeout Issues**
   - Increase polling timeouts for slower environments
   - Check backend performance and agent response times
   - Verify AI services (VertexAI) are responding

### Debug Mode

Enable debug logging by setting environment variable:
```bash
export DEBUG=1
python workflow_e2e_tester.py
```

### Manual Test Steps

If the automated test fails, you can manually verify each step:

1. Check backend logs for errors
2. Verify Firebase authentication is working
3. Test individual API endpoints with curl/Postman
4. Check database state after each step

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: E2E Workflow Test

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  e2e-test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        pip install -r requirements_e2e.txt
        
    - name: Start backend services
      run: |
        docker-compose up -d
        
    - name: Wait for services
      run: |
        sleep 30
        
    - name: Run E2E tests
      env:
        E2E_API_BASE_URL: http://localhost:8000
        E2E_FIREBASE_API_KEY: ${{ secrets.FIREBASE_API_KEY }}
      run: |
        python workflow_e2e_tester.py
        
    - name: Upload test reports
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: e2e-test-reports
        path: logs/
```

## Security Considerations

- **Test Credentials**: Use dedicated test accounts, not production accounts
- **Environment Isolation**: Run tests against test/staging environment only
- **Secret Management**: Store credentials securely (environment variables, secrets manager)
- **Network Security**: Ensure test environment has appropriate network controls
- **Data Cleanup**: Clean up test data after execution

## Performance Guidelines

- **Polling Frequency**: Balance between responsiveness and API load
- **Timeout Values**: Set appropriate timeouts for your environment
- **Parallel Execution**: Consider running multiple test suites in parallel
- **Resource Monitoring**: Monitor backend resource usage during tests

## Support

For issues or questions regarding the E2E test script:

1. Check the troubleshooting section above
2. Review backend and frontend logs
3. Verify test environment configuration
4. Contact the development team with detailed error logs

---

**Version**: 1.0.0  
**Last Updated**: January 2025  
**Compatibility**: Python 3.7+, DrFirst Business Case Generator v1.0+ 