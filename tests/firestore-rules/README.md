# Firestore Security Rules Testing Framework

This directory contains the comprehensive testing framework for validating Firestore security rules for the DrFirst Agentic Business Case Generator.

## 🎯 **Purpose**

The testing framework ensures that Firestore security rules:
- Enforce proper access controls for all user roles
- Implement the principle of least privilege
- Protect sensitive data from unauthorized access
- Support the business case workflow correctly
- Handle edge cases and potential security vulnerabilities

## 📁 **Directory Structure**

```
tests/firestore-rules/
├── __tests__/                    # Test files
│   ├── users.test.js             # Users collection tests
│   ├── business-cases.test.js    # Business cases collection tests
│   └── evaluations.test.js       # Evaluation collections tests
├── package.json                  # Test dependencies
├── jest.setup.js                 # Test environment setup
├── run-tests.sh                  # Test runner script
└── README.md                     # This file
```

## 🚀 **Quick Start**

### 1. Install Dependencies

```bash
cd tests/firestore-rules
./run-tests.sh install
```

### 2. Run All Tests

```bash
./run-tests.sh test
```

### 3. Run Tests with Coverage

```bash
./run-tests.sh test:coverage
```

## 📋 **Available Commands**

| Command | Description |
|---------|-------------|
| `./run-tests.sh install` | Install test dependencies |
| `./run-tests.sh test` | Run all tests with emulator |
| `./run-tests.sh test:watch` | Run tests in watch mode |
| `./run-tests.sh test:coverage` | Run tests with coverage report |
| `./run-tests.sh test:users` | Run only users collection tests |
| `./run-tests.sh test:cases` | Run only business cases tests |
| `./run-tests.sh test:eval` | Run only evaluation collections tests |
| `./run-tests.sh emulator` | Start emulator only (for manual testing) |
| `./run-tests.sh clean` | Clean up test artifacts |

### Command Options

- `-v, --verbose`: Enable verbose output
- `--keep-alive`: Keep emulator running after tests
- `-h, --help`: Show help message

## 🧪 **Test Coverage**

The test suite covers the following collections and scenarios:

### **Users Collection (`users`)**
- ✅ Self-profile read access
- ✅ Admin read access to all profiles
- ✅ Role-based create restrictions
- ✅ Self-update permissions with field restrictions
- ✅ System role protection
- ✅ Delete permissions

### **Business Cases Collection (`businessCases`)**
- ✅ Owner-based read access
- ✅ Workflow stage-specific approver access
- ✅ Shareable case access controls
- ✅ Creation with ownership validation
- ✅ Stage-based update permissions
- ✅ Approver action validation
- ✅ Field-level update restrictions

### **Evaluation Collections**
- ✅ `humanEvaluationResults` - Admin/evaluator access
- ✅ `automatedEvaluationResults` - Admin read, service account write
- ✅ `automatedEvaluationRuns` - Admin read, service account write
- ✅ Role-based query permissions

### **Edge Cases & Security**
- ✅ Unauthenticated access denial
- ✅ Privilege escalation prevention
- ✅ Cross-user data access prevention
- ✅ Required field validation
- ✅ System field protection

## 👥 **Test User Roles**

The test suite uses predefined user accounts with different roles:

```javascript
{
  admin: { uid: 'admin-user', systemRole: 'ADMIN' },
  regularUser: { uid: 'user-123', systemRole: 'USER' },
  developer: { uid: 'dev-456', systemRole: 'DEVELOPER' },
  financeApprover: { uid: 'finance-789', systemRole: 'FINANCE_APPROVER' },
  salesManager: { uid: 'sales-101', systemRole: 'SALES_MANAGER' },
  productOwner: { uid: 'po-112', systemRole: 'PRODUCT_OWNER' },
  finalApprover: { uid: 'final-131', systemRole: 'FINAL_APPROVER' },
  evaluator: { uid: 'eval-141', systemRole: 'EVALUATOR' },
  serviceAccount: { uid: 'service-account', provider_id: 'firebase' }
}
```

## 🛠 **Test Utilities**

### **Global Helper Functions**

```javascript
// Authentication contexts
getAuthenticatedContext(user)        // Get Firebase context for user
expectFirestorePermissionDenied()    // Assert permission denied
expectFirestoreSuccess()             // Assert operation success

// Data setup
setupTestBusinessCase(caseData)      // Create test business case
setupTestUser(userData)              // Create test user

// Test users
testUsers.admin                      // Admin user
testUsers.regularUser                // Regular user
testUsers.developer                  // Developer user
// ... other roles
```

### **Example Test Structure**

```javascript
describe('Collection Security Rules', () => {
  beforeEach(async () => {
    await setupTestData();
  });

  describe('Read Permissions', () => {
    test('authorized user can read', async () => {
      const context = getAuthenticatedContext(testUsers.admin);
      
      await expectFirestoreSuccess(
        context.firestore()
          .collection('collectionName')
          .doc('documentId')
          .get()
      );
    });

    test('unauthorized user cannot read', async () => {
      const context = getAuthenticatedContext(testUsers.regularUser);
      
      await expectFirestorePermissionDenied(
        context.firestore()
          .collection('collectionName')
          .doc('documentId')
          .get()
      );
    });
  });
});
```

## 🔧 **Configuration**

### **Firebase Emulator Settings**

- **Host**: `localhost:8080`
- **Project**: `demo-project`
- **Rules File**: `../../config/firebase/proposed_firestore.rules`

### **Jest Configuration**

```json
{
  "testEnvironment": "node",
  "testTimeout": 30000,
  "setupFilesAfterEnv": ["./jest.setup.js"]
}
```

## 📊 **Coverage Reports**

Coverage reports are generated in the `coverage/` directory:

- **HTML Report**: `coverage/lcov-report/index.html`
- **LCOV File**: `coverage/lcov.info`
- **JSON Summary**: `coverage/coverage-summary.json`

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Emulator Won't Start**
   ```bash
   # Kill existing emulator processes
   pkill -f "firebase.*emulators"
   
   # Check if port 8080 is in use
   lsof -i :8080
   ```

2. **Tests Timeout**
   - Increase Jest timeout in `jest.setup.js`
   - Check emulator connectivity
   - Verify rules file syntax

3. **Permission Denied on All Tests**
   - Verify rules file path in configuration
   - Check if emulator is using correct rules file
   - Validate rules syntax with `firebase firestore:rules:check`

4. **Node Modules Issues**
   ```bash
   ./run-tests.sh clean --full
   ./run-tests.sh install
   ```

### **Debug Mode**

Run tests with verbose output:
```bash
./run-tests.sh test -v
```

Keep emulator running for manual testing:
```bash
./run-tests.sh test --keep-alive
```

## 🔄 **Integration with CI/CD**

The testing framework can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Test Firestore Rules
  run: |
    cd tests/firestore-rules
    ./run-tests.sh install
    ./run-tests.sh test:coverage
```

## 📚 **Dependencies**

- **@firebase/rules-unit-testing**: ^3.0.3
- **jest**: ^29.7.0
- **firebase-tools**: ^12.7.0
- **Node.js**: >=16.0.0

## 🤝 **Contributing**

When adding new tests:

1. Follow the existing test structure
2. Use descriptive test names
3. Include both positive and negative test cases
4. Test all user roles where applicable
5. Add documentation for new test utilities

## 📖 **Further Reading**

- [Firebase Security Rules Documentation](https://firebase.google.com/docs/firestore/security/get-started)
- [Firebase Rules Unit Testing](https://firebase.google.com/docs/rules/unit-tests)
- [Jest Testing Framework](https://jestjs.io/docs/getting-started) 