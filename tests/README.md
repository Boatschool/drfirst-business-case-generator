# Tests

This directory contains cross-component and system-wide tests.

## Directory Structure

### 🔄 [E2E (End-to-End)](./e2e/)
- Complete workflow tests
- User journey validation
- Cross-system integration tests
- Automated browser testing

### 🔗 [Integration](./integration/)
- API integration tests
- Database integration tests
- Third-party service integration
- Component interaction tests

### 📋 [Manual](./manual/)
- Manual testing procedures
- User acceptance test scripts
- Exploratory testing guides
- Manual verification steps

### 📊 [Reports](./reports/)
- Test execution reports
- Coverage analysis
- Performance test results
- Quality metrics

## Test Organization

### Backend Tests
Located in `backend/tests/` - includes unit tests for:
- API endpoints
- Services and utilities
- Data models
- Authentication

### Frontend Tests
Located in `frontend/tests/` - includes:
- Component tests
- Integration tests
- User interface tests

## Running Tests

### E2E Tests
```bash
cd tests/e2e
python workflow_e2e_tester.py
```

### All Backend Tests
```bash
cd backend
pytest
```

### All Frontend Tests
```bash
cd frontend
npm test
```

## Test Standards

- Write descriptive test names
- Include both positive and negative test cases
- Maintain test data fixtures
- Keep tests independent and reproducible
- Document complex test scenarios 