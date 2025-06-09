/**
 * Firestore Security Rules Tests - Business Cases Collection
 * Tests business case access controls, workflow permissions, and role-based approvals
 */

describe('Business Cases Collection Security Rules', () => {

  beforeEach(async () => {
    // Setup test user and business case data
    await setupTestUser();
    await setupTestBusinessCase();
  });

  describe('Read Permissions - Ownership', () => {
    test('case owner can read their own case', async () => {
      const userContext = getAuthenticatedContext(testUsers.regularUser);
      
      await expectFirestoreSuccess(
        userContext.firestore()
          .collection('businessCases')
          .doc('test-case-123')
          .get()
      );
    });

    test('non-owner cannot read case in INTAKE status', async () => {
      const devContext = getAuthenticatedContext(testUsers.developer);
      
      await expectFirestorePermissionDenied(
        devContext.firestore()
          .collection('businessCases')
          .doc('test-case-123')
          .get()
      );
    });

    test('admin can read any case', async () => {
      const adminContext = getAuthenticatedContext(testUsers.admin);
      
      await expectFirestoreSuccess(
        adminContext.firestore()
          .collection('businessCases')
          .doc('test-case-123')
          .get()
      );
    });

    test('unauthenticated user cannot read any case', async () => {
      const unauthenticatedContext = getAuthenticatedContext(null);
      
      await expectFirestorePermissionDenied(
        unauthenticatedContext.firestore()
          .collection('businessCases')
          .doc('test-case-123')
          .get()
      );
    });
  });

  describe('Read Permissions - Workflow Stage Access', () => {
    test('developer can read case in SYSTEM_DESIGN_PENDING_REVIEW', async () => {
      // Update case to system design review status
      await setupTestBusinessCase({
        status: 'SYSTEM_DESIGN_PENDING_REVIEW'
      });

      const devContext = getAuthenticatedContext(testUsers.developer);
      
      await expectFirestoreSuccess(
        devContext.firestore()
          .collection('businessCases')
          .doc('test-case-123')
          .get()
      );
    });

    test('finance approver can read case in COSTING_PENDING_REVIEW', async () => {
      await setupTestBusinessCase({
        status: 'COSTING_PENDING_REVIEW'
      });

      const financeContext = getAuthenticatedContext(testUsers.financeApprover);
      
      await expectFirestoreSuccess(
        financeContext.firestore()
          .collection('businessCases')
          .doc('test-case-123')
          .get()
      );
    });

    test('sales manager can read case in VALUE_PENDING_REVIEW', async () => {
      await setupTestBusinessCase({
        status: 'VALUE_PENDING_REVIEW'
      });

      const salesContext = getAuthenticatedContext(testUsers.salesManager);
      
      await expectFirestoreSuccess(
        salesContext.firestore()
          .collection('businessCases')
          .doc('test-case-123')
          .get()
      );
    });

    test('final approver can read case in PENDING_FINAL_APPROVAL', async () => {
      await setupTestBusinessCase({
        status: 'PENDING_FINAL_APPROVAL'
      });

      const finalContext = getAuthenticatedContext(testUsers.finalApprover);
      
      await expectFirestoreSuccess(
        finalContext.firestore()
          .collection('businessCases')
          .doc('test-case-123')
          .get()
      );
    });

    test('product owner can read case in PRD_REVIEW', async () => {
      await setupTestBusinessCase({
        status: 'PRD_REVIEW'
      });

      const poContext = getAuthenticatedContext(testUsers.productOwner);
      
      await expectFirestoreSuccess(
        poContext.firestore()
          .collection('businessCases')
          .doc('test-case-123')
          .get()
      );
    });

    test('non-relevant approver cannot read case in wrong stage', async () => {
      await setupTestBusinessCase({
        status: 'COSTING_PENDING_REVIEW'
      });

      const salesContext = getAuthenticatedContext(testUsers.salesManager);
      
      await expectFirestorePermissionDenied(
        salesContext.firestore()
          .collection('businessCases')
          .doc('test-case-123')
          .get()
      );
    });
  });

  describe('Read Permissions - Shareable Cases', () => {
    test('authenticated user can read approved case with shareable flag', async () => {
      await setupTestBusinessCase({
        status: 'APPROVED',
        shareable: true
      });

      const randomUserContext = getAuthenticatedContext(testUsers.developer);
      
      await expectFirestoreSuccess(
        randomUserContext.firestore()
          .collection('businessCases')
          .doc('test-case-123')
          .get()
      );
    });

    test('authenticated user cannot read approved case without shareable flag', async () => {
      await setupTestBusinessCase({
        status: 'APPROVED',
        shareable: false
      });

      const randomUserContext = getAuthenticatedContext(testUsers.developer);
      
      await expectFirestorePermissionDenied(
        randomUserContext.firestore()
          .collection('businessCases')
          .doc('test-case-123')
          .get()
      );
    });

    test('authenticated user cannot read approved case with no shareable field', async () => {
      await setupTestBusinessCase({
        status: 'APPROVED'
        // No shareable field - defaults to false
      });

      const randomUserContext = getAuthenticatedContext(testUsers.developer);
      
      await expectFirestorePermissionDenied(
        randomUserContext.firestore()
          .collection('businessCases')
          .doc('test-case-123')
          .get()
      );
    });
  });

  describe('Create Permissions', () => {
    test('authenticated user can create business case with themselves as owner', async () => {
      const userContext = getAuthenticatedContext(testUsers.regularUser);
      
      await expectFirestoreSuccess(
        userContext.firestore()
          .collection('businessCases')
          .doc('new-case-456')
          .set({
            user_id: 'user-123',
            title: 'New Test Case',
            problem_statement: 'New problem statement',
            status: 'INTAKE',
            created_at: new Date()
          })
      );
    });

    test('user cannot create case with different user as owner', async () => {
      const userContext = getAuthenticatedContext(testUsers.regularUser);
      
      await expectFirestorePermissionDenied(
        userContext.firestore()
          .collection('businessCases')
          .doc('invalid-case')
          .set({
            user_id: 'different-user-789',
            title: 'Invalid Case',
            problem_statement: 'Problem statement',
            status: 'INTAKE',
            created_at: new Date()
          })
      );
    });

    test('user cannot create case without required fields', async () => {
      const userContext = getAuthenticatedContext(testUsers.regularUser);
      
      await expectFirestorePermissionDenied(
        userContext.firestore()
          .collection('businessCases')
          .doc('incomplete-case')
          .set({
            user_id: 'user-123',
            title: 'Incomplete Case'
            // Missing problem_statement, status, created_at
          })
      );
    });

    test('user cannot create case with non-INTAKE status', async () => {
      const userContext = getAuthenticatedContext(testUsers.regularUser);
      
      await expectFirestorePermissionDenied(
        userContext.firestore()
          .collection('businessCases')
          .doc('invalid-status-case')
          .set({
            user_id: 'user-123',
            title: 'Invalid Status Case',
            problem_statement: 'Problem statement',
            status: 'APPROVED', // Should be INTAKE for new cases
            created_at: new Date()
          })
      );
    });

    test('unauthenticated user cannot create business case', async () => {
      const unauthenticatedContext = getAuthenticatedContext(null);
      
      await expectFirestorePermissionDenied(
        unauthenticatedContext.firestore()
          .collection('businessCases')
          .doc('unauthorized-case')
          .set({
            user_id: 'user-123',
            title: 'Unauthorized Case',
            problem_statement: 'Problem statement',
            status: 'INTAKE',
            created_at: new Date()
          })
      );
    });
  });

  describe('Update Permissions - Owner Editable Stages', () => {
    test('owner can update case content in INTAKE status', async () => {
      const userContext = getAuthenticatedContext(testUsers.regularUser);
      
      await expectFirestoreSuccess(
        userContext.firestore()
          .collection('businessCases')
          .doc('test-case-123')
          .update({
            title: 'Updated Title',
            problem_statement: 'Updated problem statement',
            updated_at: new Date()
          })
      );
    });

    test('owner can update case content in PRD_DRAFTING status', async () => {
      await setupTestBusinessCase({ status: 'PRD_DRAFTING' });
      
      const userContext = getAuthenticatedContext(testUsers.regularUser);
      
      await expectFirestoreSuccess(
        userContext.firestore()
          .collection('businessCases')
          .doc('test-case-123')
          .update({
            title: 'Updated in PRD Drafting',
            updated_at: new Date()
          })
      );
    });

    test('owner cannot update case in APPROVED status', async () => {
      await setupTestBusinessCase({ status: 'APPROVED' });
      
      const userContext = getAuthenticatedContext(testUsers.regularUser);
      
      await expectFirestorePermissionDenied(
        userContext.firestore()
          .collection('businessCases')
          .doc('test-case-123')
          .update({
            title: 'Unauthorized Update',
            updated_at: new Date()
          })
      );
    });

    test('owner cannot update system fields', async () => {
      const userContext = getAuthenticatedContext(testUsers.regularUser);
      
      await expectFirestorePermissionDenied(
        userContext.firestore()
          .collection('businessCases')
          .doc('test-case-123')
          .update({
            user_id: 'different-user',
            updated_at: new Date()
          })
      );
    });

    test('owner cannot update without changing updated_at', async () => {
      const userContext = getAuthenticatedContext(testUsers.regularUser);
      
      await expectFirestorePermissionDenied(
        userContext.firestore()
          .collection('businessCases')
          .doc('test-case-123')
          .update({
            title: 'No Timestamp Update'
            // Missing updated_at change
          })
      );
    });
  });

  describe('Update Permissions - Approver Actions', () => {
    test('developer can update approval fields for system design review', async () => {
      await setupTestBusinessCase({ status: 'SYSTEM_DESIGN_PENDING_REVIEW' });
      
      const devContext = getAuthenticatedContext(testUsers.developer);
      
      await expectFirestoreSuccess(
        devContext.firestore()
          .collection('businessCases')
          .doc('test-case-123')
          .update({
            status: 'SYSTEM_DESIGN_APPROVED',
            history: [{ action: 'approved', by: 'dev-456', timestamp: new Date() }],
            updated_at: new Date()
          })
      );
    });

    test('finance approver can update status for cost review', async () => {
      await setupTestBusinessCase({ status: 'COSTING_PENDING_REVIEW' });
      
      const financeContext = getAuthenticatedContext(testUsers.financeApprover);
      
      await expectFirestoreSuccess(
        financeContext.firestore()
          .collection('businessCases')
          .doc('test-case-123')
          .update({
            status: 'COSTING_APPROVED',
            updated_at: new Date()
          })
      );
    });

    test('approver cannot update non-approval fields', async () => {
      await setupTestBusinessCase({ status: 'SYSTEM_DESIGN_PENDING_REVIEW' });
      
      const devContext = getAuthenticatedContext(testUsers.developer);
      
      await expectFirestorePermissionDenied(
        devContext.firestore()
          .collection('businessCases')
          .doc('test-case-123')
          .update({
            title: 'Unauthorized Title Change',
            status: 'SYSTEM_DESIGN_APPROVED',
            updated_at: new Date()
          })
      );
    });

    test('approver for wrong stage cannot update status', async () => {
      await setupTestBusinessCase({ status: 'COSTING_PENDING_REVIEW' });
      
      const devContext = getAuthenticatedContext(testUsers.developer);
      
      await expectFirestorePermissionDenied(
        devContext.firestore()
          .collection('businessCases')
          .doc('test-case-123')
          .update({
            status: 'COSTING_APPROVED',
            updated_at: new Date()
          })
      );
    });
  });

  describe('Update Permissions - Admin Override', () => {
    test('admin can update any case in any status', async () => {
      await setupTestBusinessCase({ status: 'APPROVED' });
      
      const adminContext = getAuthenticatedContext(testUsers.admin);
      
      await expectFirestoreSuccess(
        adminContext.firestore()
          .collection('businessCases')
          .doc('test-case-123')
          .update({
            title: 'Admin Updated Title',
            status: 'REJECTED',
            updated_at: new Date()
          })
      );
    });
  });

  describe('Delete Permissions', () => {
    test('admin can delete business cases', async () => {
      const adminContext = getAuthenticatedContext(testUsers.admin);
      
      await expectFirestoreSuccess(
        adminContext.firestore()
          .collection('businessCases')
          .doc('test-case-123')
          .delete()
      );
    });

    test('case owner cannot delete their own case', async () => {
      const userContext = getAuthenticatedContext(testUsers.regularUser);
      
      await expectFirestorePermissionDenied(
        userContext.firestore()
          .collection('businessCases')
          .doc('test-case-123')
          .delete()
      );
    });

    test('approver cannot delete business case', async () => {
      await setupTestBusinessCase({ status: 'SYSTEM_DESIGN_PENDING_REVIEW' });
      
      const devContext = getAuthenticatedContext(testUsers.developer);
      
      await expectFirestorePermissionDenied(
        devContext.firestore()
          .collection('businessCases')
          .doc('test-case-123')
          .delete()
      );
    });
  });

  describe('List/Query Permissions', () => {
    test('admin can query all business cases', async () => {
      const adminContext = getAuthenticatedContext(testUsers.admin);
      
      await expectFirestoreSuccess(
        adminContext.firestore()
          .collection('businessCases')
          .get()
      );
    });

    test('user can query their own business cases', async () => {
      const userContext = getAuthenticatedContext(testUsers.regularUser);
      
      await expectFirestoreSuccess(
        userContext.firestore()
          .collection('businessCases')
          .where('user_id', '==', 'user-123')
          .get()
      );
    });

    test('user cannot query all business cases without constraints', async () => {
      const userContext = getAuthenticatedContext(testUsers.regularUser);
      
      await expectFirestorePermissionDenied(
        userContext.firestore()
          .collection('businessCases')
          .get()
      );
    });
  });
}); 