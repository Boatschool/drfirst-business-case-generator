# End-to-End (E2E) Tests

This directory contains comprehensive end-to-end tests that validate complete user workflows across the entire application stack.

## Files

- `workflow_e2e_tester.py` - Main E2E test suite
- `run_e2e_test.sh` - Test execution script
- `e2e_config_template.yaml` - Configuration template
- `requirements_e2e.txt` - Python dependencies for E2E tests

## Setup

1. Install E2E test dependencies:
   ```bash
   pip install -r requirements_e2e.txt
   ```

2. Copy and configure the test config:
   ```bash
   cp e2e_config_template.yaml e2e_config.yaml
   # Edit e2e_config.yaml with your environment details
   ```

3. Ensure both backend and frontend are running:
   - Backend: `http://localhost:8000` (or your configured URL)
   - Frontend: `http://localhost:4000` (or your configured URL)

## Running Tests

### Quick Start
```bash
./run_e2e_test.sh
```

### Manual Execution
```bash
python workflow_e2e_tester.py --config e2e_config.yaml
```

### With Custom Configuration
```bash
python workflow_e2e_tester.py \
  --backend-url https://your-backend.run.app \
  --frontend-url https://your-frontend.web.app \
  --config custom_config.yaml
```

## Test Coverage

The E2E tests cover:

### 🔐 Authentication Flow
- Google OAuth login
- User session management
- Token refresh handling
- Logout functionality

### 📊 Case Management
- Create new business cases
- Edit existing cases
- Delete cases
- Case data persistence

### 🤖 Agent Interactions
- Workflow agent functionality
- Financial calculations
- Cost estimation
- Value projections

### 👥 User Roles
- Admin functionality
- Regular user permissions
- Role-based access control

### 🔄 Complete Workflows
- End-to-end business case creation
- Multi-step form navigation
- Data validation
- Error handling

## Configuration

Edit `e2e_config.yaml` to configure:

```yaml
backend:
  url: "http://localhost:8000"
  health_endpoint: "/health"
  
frontend:
  url: "http://localhost:4000"
  
test_data:
  test_user_email: "test@example.com"
  timeout: 30
  
browser:
  headless: true
  driver: "chrome"
```

## Test Results

Test results are saved in:
- Console output with detailed logs
- JSON reports (if configured)
- Screenshots on failures (if configured)

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure backend/frontend are running
2. **Timeout Errors**: Increase timeout values in config
3. **Authentication Failures**: Check test user credentials
4. **Browser Issues**: Install/update Chrome/Firefox drivers

### Debug Mode
```bash
python workflow_e2e_tester.py --debug --verbose
```

## Contributing

When adding new E2E tests:
1. Follow existing test patterns
2. Use descriptive test names
3. Include proper cleanup
4. Document test scenarios
5. Update this README if needed 