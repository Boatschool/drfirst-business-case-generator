# Firestore Security Rules Testing Recommendations

## Overview

This document provides comprehensive testing strategies for validating the proposed Firestore security rules. Testing should cover all user roles, access patterns, and edge cases to ensure the rules are both secure and functional.

## Testing Environment Setup

### 1. Firestore Emulator Testing (Recommended First Step)

```bash
# Install Firebase CLI if not already installed
npm install -g firebase-tools

# Initialize Firebase emulator
firebase init emulators

# Start Firestore emulator
firebase emulators:start --only firestore

# Run tests against emulator
export FIRESTORE_EMULATOR_HOST="localhost:8080"
```

**Benefits**:
- Fast iteration without cloud costs
- Complete rule testing in isolation
- Easy data reset between test runs
- No risk to production data

### 2. Staging Firebase Project Setup

```bash
# Create separate Firebase project for staging
firebase projects:create drfirst-business-case-staging

# Deploy rules to staging
firebase deploy --only firestore:rules --project drfirst-business-case-staging
```

**Benefits**:
- Real Firebase Auth integration
- Production-like performance testing
- Integration with actual backend APIs
- Cloud function testing

## Testing Strategy

### Phase 1: Unit Testing (Firestore Emulator)

#### Test Framework Setup

```javascript
// Example using Jest + Firebase Testing SDK
const firebase = require('@firebase/rules-unit-testing');
const fs = require('fs');

const PROJECT_ID = 'test-project';
const RULES_FILE = 'proposed_firestore.rules';

describe('Firestore Security Rules', () => {
  let db;
  
  beforeAll(async () => {
    await firebase.loadFirestoreRules({
      projectId: PROJECT_ID,
      rules: fs.readFileSync(RULES_FILE, 'utf8')
    });
  });
  
  afterAll(async () => {
    await firebase.clearFirestoreData({ projectId: PROJECT_ID });
    await Promise.all(firebase.apps().map(app => app.delete()));
  });
});
```

#### Test User Scenarios

Create test users for each role:

```javascript
const testUsers = {
  admin: {
    uid: 'admin-user',
    email: 'admin@drfirst.com',
    token: { systemRole: 'ADMIN' }
  },
  regularUser: {
    uid: 'user-123',
    email: 'user@drfirst.com', 
    token: { systemRole: 'USER' }
  },
  developer: {
    uid: 'dev-456',
    email: 'dev@drfirst.com',
    token: { systemRole: 'DEVELOPER' }
  },
  financeApprover: {
    uid: 'finance-789',
    email: 'finance@drfirst.com',
    token: { systemRole: 'FINANCE_APPROVER' }
  },
  evaluator: {
    uid: 'eval-101',
    email: 'evaluator@drfirst.com',
    token: { systemRole: 'EVALUATOR' }
  },
  serviceAccount: {
    uid: 'service-account',
    token: { 
      firebase: { sign_in_provider: 'custom' }
    }
  },
  unauthenticated: null
};
```

### Phase 2: Role-Based Access Testing

#### 2.1 Users Collection Tests

```javascript
describe('Users Collection', () => {
  test('User can read own profile', async () => {
    const db = firebase.initializeTestApp({
      projectId: PROJECT_ID,
      auth: testUsers.regularUser
    }).firestore();
    
    await firebase.assertSucceeds(
      db.collection('users').doc('user-123').get()
    );
  });
  
  test('User cannot read other profiles', async () => {
    const db = firebase.initializeTestApp({
      projectId: PROJECT_ID,
      auth: testUsers.regularUser
    }).firestore();
    
    await firebase.assertFails(
      db.collection('users').doc('admin-user').get()
    );
  });
  
  test('Admin can read all profiles', async () => {
    const db = firebase.initializeTestApp({
      projectId: PROJECT_ID,
      auth: testUsers.admin
    }).firestore();
    
    await firebase.assertSucceeds(
      db.collection('users').doc('user-123').get()
    );
  });
  
  test('User cannot update role', async () => {
    const db = firebase.initializeTestApp({
      projectId: PROJECT_ID,
      auth: testUsers.regularUser
    }).firestore();
    
    await firebase.assertFails(
      db.collection('users').doc('user-123').update({
        systemRole: 'ADMIN'
      })
    );
  });
});
```

#### 2.2 Business Cases Collection Tests

```javascript
describe('Business Cases Collection', () => {
  beforeEach(async () => {
    // Setup test business case
    const adminDb = firebase.initializeTestApp({
      projectId: PROJECT_ID,
      auth: testUsers.admin
    }).firestore();
    
    await adminDb.collection('businessCases').doc('case-123').set({
      user_id: 'user-123',
      title: 'Test Case',
      problem_statement: 'Test problem',
      status: 'INTAKE',
      created_at: new Date(),
      updated_at: new Date()
    });
  });
  
  test('Owner can read own case', async () => {
    const db = firebase.initializeTestApp({
      projectId: PROJECT_ID,
      auth: testUsers.regularUser
    }).firestore();
    
    await firebase.assertSucceeds(
      db.collection('businessCases').doc('case-123').get()
    );
  });
  
  test('Non-owner cannot read case in INTAKE status', async () => {
    const db = firebase.initializeTestApp({
      projectId: PROJECT_ID,
      auth: testUsers.developer
    }).firestore();
    
    await firebase.assertFails(
      db.collection('businessCases').doc('case-123').get()
    );
  });
  
  test('Developer can read case in SYSTEM_DESIGN_PENDING_REVIEW', async () => {
    // Update case status
    const adminDb = firebase.initializeTestApp({
      projectId: PROJECT_ID,
      auth: testUsers.admin
    }).firestore();
    
    await adminDb.collection('businessCases').doc('case-123').update({
      status: 'SYSTEM_DESIGN_PENDING_REVIEW',
      updated_at: new Date()
    });
    
    const db = firebase.initializeTestApp({
      projectId: PROJECT_ID,
      auth: testUsers.developer
    }).firestore();
    
    await firebase.assertSucceeds(
      db.collection('businessCases').doc('case-123').get()
    );
  });
  
  test('User must set themselves as owner on create', async () => {
    const db = firebase.initializeTestApp({
      projectId: PROJECT_ID,
      auth: testUsers.regularUser
    }).firestore();
    
    await firebase.assertFails(
      db.collection('businessCases').add({
        user_id: 'different-user',
        title: 'Test Case',
        problem_statement: 'Test problem',
        status: 'INTAKE',
        created_at: new Date()
      })
    );
  });
  
  test('Owner cannot update case in approved status', async () => {
    // Set case to approved status
    const adminDb = firebase.initializeTestApp({
      projectId: PROJECT_ID,
      auth: testUsers.admin
    }).firestore();
    
    await adminDb.collection('businessCases').doc('case-123').update({
      status: 'APPROVED',
      updated_at: new Date()
    });
    
    const db = firebase.initializeTestApp({
      projectId: PROJECT_ID,
      auth: testUsers.regularUser
    }).firestore();
    
    await firebase.assertFails(
      db.collection('businessCases').doc('case-123').update({
        title: 'Updated Title',
        updated_at: new Date()
      })
    );
  });
});
```

#### 2.3 Evaluation Collections Tests

```javascript
describe('Evaluation Collections', () => {
  test('Only admin can read automated evaluation results', async () => {
    const userDb = firebase.initializeTestApp({
      projectId: PROJECT_ID,
      auth: testUsers.regularUser
    }).firestore();
    
    await firebase.assertFails(
      userDb.collection('automatedEvaluationResults').get()
    );
    
    const adminDb = firebase.initializeTestApp({
      projectId: PROJECT_ID,
      auth: testUsers.admin
    }).firestore();
    
    await firebase.assertSucceeds(
      adminDb.collection('automatedEvaluationResults').get()
    );
  });
  
  test('Service account can write automated evaluation results', async () => {
    const serviceDb = firebase.initializeTestApp({
      projectId: PROJECT_ID,
      auth: testUsers.serviceAccount
    }).firestore();
    
    await firebase.assertSucceeds(
      serviceDb.collection('automatedEvaluationResults').add({
        eval_run_id: 'test-run',
        agent_name: 'TestAgent',
        timestamp: new Date()
      })
    );
  });
  
  test('Evaluator can create human evaluation result', async () => {
    const evalDb = firebase.initializeTestApp({
      projectId: PROJECT_ID,
      auth: testUsers.evaluator
    }).firestore();
    
    await firebase.assertSucceeds(
      evalDb.collection('humanEvaluationResults').add({
        evaluator_id: 'eval-101',
        eval_id: 'test-eval',
        scores: { quality: 4 }
      })
    );
  });
});
```

### Phase 3: Edge Case Testing

#### 3.1 Concurrent Modification Protection

```javascript
test('Concurrent modification protection', async () => {
  const db1 = firebase.initializeTestApp({
    projectId: PROJECT_ID,
    auth: testUsers.regularUser
  }).firestore();
  
  const db2 = firebase.initializeTestApp({
    projectId: PROJECT_ID,
    auth: testUsers.regularUser
  }).firestore();
  
  // Both users try to update without changing updated_at
  await firebase.assertFails(
    db1.collection('businessCases').doc('case-123').update({
      title: 'Update 1'
      // Missing updated_at change
    })
  );
});
```

#### 3.2 Field Validation Tests

```javascript
test('Required fields validation on create', async () => {
  const db = firebase.initializeTestApp({
    projectId: PROJECT_ID,
    auth: testUsers.regularUser
  }).firestore();
  
  await firebase.assertFails(
    db.collection('businessCases').add({
      user_id: 'user-123',
      title: 'Test Case'
      // Missing required fields: problem_statement, status, created_at
    })
  );
});
```

### Phase 4: Integration Testing (Staging Environment)

#### 4.1 Authentication Integration Tests

```javascript
// Test with actual Firebase Auth tokens
describe('Auth Integration Tests', () => {
  test('Custom claims integration', async () => {
    // Test that custom claims are properly read
    // Test fallback to Firestore when claims are unavailable
  });
  
  test('Service account detection', async () => {
    // Test backend service account authentication
    // Verify service account operations work correctly
  });
});
```

#### 4.2 Backend API Integration

```javascript
describe('Backend API Integration', () => {
  test('Status transitions via API', async () => {
    // Test that backend APIs can perform status changes
    // Verify that client-side status changes are blocked
  });
  
  test('Role assignment via admin API', async () => {
    // Test admin role assignment functionality
    // Verify role changes are reflected in rules
  });
});
```

### Phase 5: Performance Testing

#### 5.1 Rule Evaluation Performance

```javascript
describe('Performance Tests', () => {
  test('Large dataset query performance', async () => {
    // Create large number of test documents
    // Measure query performance with rules
    // Ensure acceptable response times
  });
  
  test('Complex rule evaluation time', async () => {
    // Test performance of complex rules like canApproveForStage
    // Measure rule evaluation overhead
  });
});
```

## Testing Checklist

### Security Validation

- [ ] **Unauthenticated users cannot access any data**
- [ ] **Users cannot access other users' business cases**
- [ ] **Role escalation is prevented (users cannot change their role)**
- [ ] **System fields are protected (user_id, created_at)**
- [ ] **Approved cases are not publicly readable (unless shareable flag set)**
- [ ] **Evaluation data is admin/evaluator restricted**
- [ ] **Agent prompts are admin-only**
- [ ] **Service account operations work correctly**

### Functionality Validation

- [ ] **Users can create business cases**
- [ ] **Owners can edit cases in draft status**
- [ ] **Approvers can read cases in their approval stage**
- [ ] **Admins have full access to all collections**
- [ ] **Configuration data is readable by authenticated users**
- [ ] **Comments system works with proper permissions**
- [ ] **Audit logs are protected from client access**

### Workflow Validation

- [ ] **Business case lifecycle permissions work correctly**
- [ ] **Status-based access control functions properly**
- [ ] **Cross-role approval handoffs work**
- [ ] **Concurrent modification protection works**
- [ ] **Field validation prevents invalid data**

## Automated Testing Setup

### Continuous Integration

```yaml
# GitHub Actions example
name: Firestore Rules Testing
on: [push, pull_request]

jobs:
  test-rules:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '16'
      - run: npm install -g firebase-tools
      - run: npm install
      - run: firebase emulators:exec --only firestore "npm test"
```

### Test Data Management

```javascript
// Helper function to create test data
async function setupTestData(projectId) {
  const adminDb = firebase.initializeTestApp({
    projectId,
    auth: testUsers.admin
  }).firestore();
  
  // Create test users
  await adminDb.collection('users').doc('user-123').set({
    uid: 'user-123',
    email: 'user@drfirst.com',
    systemRole: 'USER'
  });
  
  // Create test business cases in various statuses
  await adminDb.collection('businessCases').doc('case-intake').set({
    user_id: 'user-123',
    status: 'INTAKE',
    title: 'Test Case - Intake',
    // ... other fields
  });
  
  // Create test configuration
  await adminDb.collection('systemConfiguration').doc('approvalSettings').set({
    stageApproverRoles: {
      PRD: 'PRODUCT_OWNER',
      SystemDesign: 'DEVELOPER'
    }
  });
}
```

## Production Deployment Testing

### Pre-deployment Validation

1. **Backup current rules**:
   ```bash
   firebase firestore:rules --output current_rules_backup.txt
   ```

2. **Deploy to staging first**:
   ```bash
   firebase deploy --only firestore:rules --project staging
   ```

3. **Run full test suite against staging**

4. **Monitor staging for 24-48 hours**

### Deployment Rollback Plan

```bash
# Quick rollback command
firebase deploy --only firestore:rules --project production
# (with previous rules file)
```

### Post-deployment Monitoring

1. **Monitor application logs** for permission denied errors
2. **Check user feedback** for access issues
3. **Review Firebase console** for rule evaluation metrics
4. **Validate all user workflows** still function correctly

## Troubleshooting Common Issues

### Permission Denied Errors

1. **Check user authentication status**
2. **Verify role assignments**
3. **Validate document ownership**
4. **Test rule conditions in emulator**

### Performance Issues

1. **Optimize complex rule conditions**
2. **Reduce document lookups in rules**
3. **Consider backend authorization for complex logic**

### Testing Environment Issues

1. **Ensure emulator is running latest rules**
2. **Clear emulator data between tests**
3. **Verify test user setup**
4. **Check for race conditions in tests**

This comprehensive testing approach ensures that the new Firestore security rules are both secure and functional before production deployment. 