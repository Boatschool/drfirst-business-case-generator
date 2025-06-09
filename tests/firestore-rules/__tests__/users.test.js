/**
 * Firestore Security Rules Tests - Users Collection
 * Tests user document access controls and role-based permissions
 */

describe('Users Collection Security Rules', () => {
  
  beforeEach(async () => {
    // Setup test user data
    await setupTestUser();
  });

  describe('Read Permissions', () => {
    test('user can read their own profile', async () => {
      const userContext = getAuthenticatedContext(testUsers.regularUser);
      
      await expectFirestoreSuccess(
        userContext.firestore()
          .collection('users')
          .doc('user-123')
          .get()
      );
    });

    test('user cannot read other user profiles', async () => {
      const userContext = getAuthenticatedContext(testUsers.regularUser);
      
      await expectFirestorePermissionDenied(
        userContext.firestore()
          .collection('users')
          .doc('admin-user')
          .get()
      );
    });

    test('admin can read any user profile', async () => {
      const adminContext = getAuthenticatedContext(testUsers.admin);
      
      await expectFirestoreSuccess(
        adminContext.firestore()
          .collection('users')
          .doc('user-123')
          .get()
      );
    });

    test('developer can read user profiles with limited fields', async () => {
      const devContext = getAuthenticatedContext(testUsers.developer);
      
      // This tests the rule logic - in practice, field filtering happens client-side
      await expectFirestoreSuccess(
        devContext.firestore()
          .collection('users')
          .doc('user-123')
          .get()
      );
    });

    test('unauthenticated user cannot read any profiles', async () => {
      const unauthenticatedContext = getAuthenticatedContext(null);
      
      await expectFirestorePermissionDenied(
        unauthenticatedContext.firestore()
          .collection('users')
          .doc('user-123')
          .get()
      );
    });
  });

  describe('Create Permissions', () => {
    test('admin can create user documents', async () => {
      const adminContext = getAuthenticatedContext(testUsers.admin);
      
      await expectFirestoreSuccess(
        adminContext.firestore()
          .collection('users')
          .doc('new-user-456')
          .set({
            uid: 'new-user-456',
            email: 'newuser@drfirst.com',
            systemRole: 'USER',
            created_at: new Date()
          })
      );
    });

    test('service account can create user documents', async () => {
      const serviceContext = getAuthenticatedContext(testUsers.serviceAccount);
      
      await expectFirestoreSuccess(
        serviceContext.firestore()
          .collection('users')
          .doc('service-created-user')
          .set({
            uid: 'service-created-user',
            email: 'service@drfirst.com',
            systemRole: 'USER',
            created_at: new Date()
          })
      );
    });

    test('regular user cannot create user documents', async () => {
      const userContext = getAuthenticatedContext(testUsers.regularUser);
      
      await expectFirestorePermissionDenied(
        userContext.firestore()
          .collection('users')
          .doc('unauthorized-user')
          .set({
            uid: 'unauthorized-user',
            email: 'unauthorized@drfirst.com',
            systemRole: 'USER'
          })
      );
    });
  });

  describe('Update Permissions', () => {
    test('user can update basic fields of their own document', async () => {
      const userContext = getAuthenticatedContext(testUsers.regularUser);
      
      await expectFirestoreSuccess(
        userContext.firestore()
          .collection('users')
          .doc('user-123')
          .update({
            displayName: 'Updated Name',
            uid: 'user-123' // Must match auth uid
          })
      );
    });

    test('user cannot update their system role', async () => {
      const userContext = getAuthenticatedContext(testUsers.regularUser);
      
      await expectFirestorePermissionDenied(
        userContext.firestore()
          .collection('users')
          .doc('user-123')
          .update({
            systemRole: 'ADMIN' // Privilege escalation attempt
          })
      );
    });

    test('user cannot update uid field', async () => {
      const userContext = getAuthenticatedContext(testUsers.regularUser);
      
      await expectFirestorePermissionDenied(
        userContext.firestore()
          .collection('users')
          .doc('user-123')
          .update({
            uid: 'different-user-id'
          })
      );
    });

    test('user cannot update created_at field', async () => {
      const userContext = getAuthenticatedContext(testUsers.regularUser);
      
      await expectFirestorePermissionDenied(
        userContext.firestore()
          .collection('users')
          .doc('user-123')
          .update({
            created_at: new Date()
          })
      );
    });

    test('admin can update any user document', async () => {
      const adminContext = getAuthenticatedContext(testUsers.admin);
      
      await expectFirestoreSuccess(
        adminContext.firestore()
          .collection('users')
          .doc('user-123')
          .update({
            systemRole: 'DEVELOPER',
            displayName: 'Admin Updated Name'
          })
      );
    });

    test('user cannot update other user documents', async () => {
      const userContext = getAuthenticatedContext(testUsers.regularUser);
      
      // Setup another user
      await setupTestUser({
        uid: 'other-user-456',
        email: 'other@drfirst.com'
      });
      
      await expectFirestorePermissionDenied(
        userContext.firestore()
          .collection('users')
          .doc('other-user-456')
          .update({
            displayName: 'Unauthorized Update'
          })
      );
    });
  });

  describe('Delete Permissions', () => {
    test('admin can delete user documents', async () => {
      const adminContext = getAuthenticatedContext(testUsers.admin);
      
      await expectFirestoreSuccess(
        adminContext.firestore()
          .collection('users')
          .doc('user-123')
          .delete()
      );
    });

    test('user cannot delete their own document', async () => {
      const userContext = getAuthenticatedContext(testUsers.regularUser);
      
      await expectFirestorePermissionDenied(
        userContext.firestore()
          .collection('users')
          .doc('user-123')
          .delete()
      );
    });

    test('user cannot delete other user documents', async () => {
      const userContext = getAuthenticatedContext(testUsers.regularUser);
      
      await expectFirestorePermissionDenied(
        userContext.firestore()
          .collection('users')
          .doc('admin-user')
          .delete()
      );
    });
  });

  describe('List/Query Permissions', () => {
    test('admin can list all users', async () => {
      const adminContext = getAuthenticatedContext(testUsers.admin);
      
      await expectFirestoreSuccess(
        adminContext.firestore()
          .collection('users')
          .get()
      );
    });

    test('regular user cannot list all users', async () => {
      const userContext = getAuthenticatedContext(testUsers.regularUser);
      
      await expectFirestorePermissionDenied(
        userContext.firestore()
          .collection('users')
          .get()
      );
    });
  });
}); 