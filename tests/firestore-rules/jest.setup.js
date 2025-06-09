/**
 * Jest setup for Firestore Rules Testing
 * Configures test environment and global utilities
 */

const { initializeTestEnvironment } = require('@firebase/rules-unit-testing');
const fs = require('fs');
const path = require('path');

// Test configuration
const PROJECT_ID = 'drfirst-test-project';
const RULES_FILE = path.join(__dirname, '../../config/firebase/proposed_firestore.rules');

// Global test environment
let testEnv;

// Setup before all tests
beforeAll(async () => {
  // Read the rules file
  const rulesContent = fs.readFileSync(RULES_FILE, 'utf8');
  
  // Initialize test environment
  testEnv = await initializeTestEnvironment({
    projectId: PROJECT_ID,
    firestore: {
      rules: rulesContent,
      host: 'localhost',
      port: 8080
    }
  });
  
  // Store in global for access in tests
  global.testEnv = testEnv;
  global.PROJECT_ID = PROJECT_ID;
});

// Cleanup after each test
afterEach(async () => {
  if (testEnv) {
    await testEnv.clearFirestore();
  }
});

// Cleanup after all tests
afterAll(async () => {
  if (testEnv) {
    await testEnv.cleanup();
  }
});

// Global test utilities
global.testUsers = {
  admin: {
    uid: 'admin-user',
    email: 'admin@drfirst.com',
    custom_claims: { systemRole: 'ADMIN' }
  },
  regularUser: {
    uid: 'user-123',
    email: 'user@drfirst.com',
    custom_claims: { systemRole: 'USER' }
  },
  developer: {
    uid: 'dev-456',
    email: 'dev@drfirst.com',
    custom_claims: { systemRole: 'DEVELOPER' }
  },
  financeApprover: {
    uid: 'finance-789',
    email: 'finance@drfirst.com',
    custom_claims: { systemRole: 'FINANCE_APPROVER' }
  },
  salesManager: {
    uid: 'sales-101',
    email: 'sales@drfirst.com',
    custom_claims: { systemRole: 'SALES_MANAGER' }
  },
  productOwner: {
    uid: 'po-112',
    email: 'po@drfirst.com',
    custom_claims: { systemRole: 'PRODUCT_OWNER' }
  },
  finalApprover: {
    uid: 'final-131',
    email: 'final@drfirst.com',
    custom_claims: { systemRole: 'FINAL_APPROVER' }
  },
  evaluator: {
    uid: 'eval-141',
    email: 'evaluator@drfirst.com',
    custom_claims: { systemRole: 'EVALUATOR' }
  },
  serviceAccount: {
    uid: 'service-account',
    provider_id: 'firebase',
    custom_claims: { 
      firebase: { 
        sign_in_provider: 'custom' 
      } 
    }
  },
  unauthenticated: null
};

// Helper function to get authenticated context
global.getAuthenticatedContext = (user) => {
  if (!user) {
    return testEnv.unauthenticatedContext();
  }
  return testEnv.authenticatedContext(user.uid, user.custom_claims);
};

// Helper function to setup test data
global.setupTestBusinessCase = async (caseData = {}) => {
  const adminContext = testEnv.authenticatedContext(
    global.testUsers.admin.uid, 
    global.testUsers.admin.custom_claims
  );
  
  const defaultCase = {
    user_id: 'user-123',
    title: 'Test Business Case',
    problem_statement: 'Test problem statement',
    status: 'INTAKE',
    created_at: new Date(),
    updated_at: new Date(),
    ...caseData
  };
  
  await adminContext.firestore()
    .collection('businessCases')
    .doc('test-case-123')
    .set(defaultCase);
    
  return defaultCase;
};

// Helper function to setup test user
global.setupTestUser = async (userData = {}) => {
  const adminContext = testEnv.authenticatedContext(
    global.testUsers.admin.uid, 
    global.testUsers.admin.custom_claims
  );
  
  const defaultUser = {
    uid: 'user-123',
    email: 'user@drfirst.com',
    systemRole: 'USER',
    displayName: 'Test User',
    created_at: new Date(),
    ...userData
  };
  
  await adminContext.firestore()
    .collection('users')
    .doc(defaultUser.uid)
    .set(defaultUser);
    
  return defaultUser;
};

// Custom assertion helpers
global.expectFirestorePermissionDenied = async (promise) => {
  let error;
  try {
    await promise;
  } catch (err) {
    error = err;
  }
  
  expect(error).toBeDefined();
  expect(error.code).toBe('permission-denied');
};

global.expectFirestoreSuccess = async (promise) => {
  let error;
  try {
    await promise;
  } catch (err) {
    error = err;
  }
  
  expect(error).toBeUndefined();
}; 