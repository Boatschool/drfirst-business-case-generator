/**
 * Firestore Security Rules Tests - Evaluation Collections
 * Tests evaluation system access controls for human and automated evaluations
 */

describe('Evaluation Collections Security Rules', () => {

  describe('Human Evaluation Results Collection', () => {
    
    beforeEach(async () => {
      // Setup test evaluation data
      const adminContext = getAuthenticatedContext(testUsers.admin);
      await adminContext.firestore()
        .collection('humanEvaluationResults')
        .doc('test-eval-123')
        .set({
          evaluator_id: 'eval-141',
          eval_id: 'EVAL_20250101_TEST',
          agent_name: 'ProductManagerAgent',
          scores: { quality: 4, relevance: 5 },
          comments: 'Good output quality',
          timestamp: new Date()
        });
    });

    describe('Read Permissions', () => {
      test('admin can read human evaluation results', async () => {
        const adminContext = getAuthenticatedContext(testUsers.admin);
        
        await expectFirestoreSuccess(
          adminContext.firestore()
            .collection('humanEvaluationResults')
            .doc('test-eval-123')
            .get()
        );
      });

      test('evaluator can read human evaluation results', async () => {
        const evaluatorContext = getAuthenticatedContext(testUsers.evaluator);
        
        await expectFirestoreSuccess(
          evaluatorContext.firestore()
            .collection('humanEvaluationResults')
            .doc('test-eval-123')
            .get()
        );
      });

      test('regular user cannot read human evaluation results', async () => {
        const userContext = getAuthenticatedContext(testUsers.regularUser);
        
        await expectFirestorePermissionDenied(
          userContext.firestore()
            .collection('humanEvaluationResults')
            .doc('test-eval-123')
            .get()
        );
      });

      test('developer cannot read human evaluation results', async () => {
        const devContext = getAuthenticatedContext(testUsers.developer);
        
        await expectFirestorePermissionDenied(
          devContext.firestore()
            .collection('humanEvaluationResults')
            .doc('test-eval-123')
            .get()
        );
      });

      test('unauthenticated user cannot read human evaluation results', async () => {
        const unauthenticatedContext = getAuthenticatedContext(null);
        
        await expectFirestorePermissionDenied(
          unauthenticatedContext.firestore()
            .collection('humanEvaluationResults')
            .doc('test-eval-123')
            .get()
        );
      });
    });

    describe('Create Permissions', () => {
      test('evaluator can create their own evaluation', async () => {
        const evaluatorContext = getAuthenticatedContext(testUsers.evaluator);
        
        await expectFirestoreSuccess(
          evaluatorContext.firestore()
            .collection('humanEvaluationResults')
            .doc('new-eval-456')
            .set({
              evaluator_id: 'eval-141',
              eval_id: 'EVAL_20250101_NEW',
              agent_name: 'ArchitectAgent',
              scores: { quality: 3, clarity: 4 },
              comments: 'Architecture needs improvement',
              timestamp: new Date()
            })
        );
      });

      test('admin can create evaluation for any evaluator', async () => {
        const adminContext = getAuthenticatedContext(testUsers.admin);
        
        await expectFirestoreSuccess(
          adminContext.firestore()
            .collection('humanEvaluationResults')
            .doc('admin-eval-789')
            .set({
              evaluator_id: 'different-evaluator',
              eval_id: 'EVAL_20250101_ADMIN',
              agent_name: 'PlannerAgent',
              scores: { quality: 5 },
              comments: 'Admin created evaluation',
              timestamp: new Date()
            })
        );
      });

      test('evaluator cannot create evaluation for different evaluator', async () => {
        const evaluatorContext = getAuthenticatedContext(testUsers.evaluator);
        
        await expectFirestorePermissionDenied(
          evaluatorContext.firestore()
            .collection('humanEvaluationResults')
            .doc('unauthorized-eval')
            .set({
              evaluator_id: 'different-evaluator',
              eval_id: 'EVAL_20250101_UNAUTHORIZED',
              agent_name: 'TestAgent',
              scores: { quality: 3 },
              timestamp: new Date()
            })
        );
      });

      test('regular user cannot create evaluation', async () => {
        const userContext = getAuthenticatedContext(testUsers.regularUser);
        
        await expectFirestorePermissionDenied(
          userContext.firestore()
            .collection('humanEvaluationResults')
            .doc('user-eval')
            .set({
              evaluator_id: 'user-123',
              eval_id: 'EVAL_20250101_USER',
              agent_name: 'TestAgent',
              scores: { quality: 4 },
              timestamp: new Date()
            })
        );
      });
    });

    describe('Update Permissions', () => {
      test('evaluator can update their own evaluation', async () => {
        const evaluatorContext = getAuthenticatedContext(testUsers.evaluator);
        
        await expectFirestoreSuccess(
          evaluatorContext.firestore()
            .collection('humanEvaluationResults')
            .doc('test-eval-123')
            .update({
              scores: { quality: 5, relevance: 4 },
              comments: 'Updated evaluation'
            })
        );
      });

      test('admin can update any evaluation', async () => {
        const adminContext = getAuthenticatedContext(testUsers.admin);
        
        await expectFirestoreSuccess(
          adminContext.firestore()
            .collection('humanEvaluationResults')
            .doc('test-eval-123')
            .update({
              scores: { quality: 3 },
              comments: 'Admin updated evaluation'
            })
        );
      });

      test('evaluator cannot update other evaluator\'s evaluation', async () => {
        // Create evaluation by different evaluator
        const adminContext = getAuthenticatedContext(testUsers.admin);
        await adminContext.firestore()
          .collection('humanEvaluationResults')
          .doc('other-eval-456')
          .set({
            evaluator_id: 'different-evaluator',
            eval_id: 'EVAL_20250101_OTHER',
            agent_name: 'TestAgent',
            scores: { quality: 3 },
            timestamp: new Date()
          });

        const evaluatorContext = getAuthenticatedContext(testUsers.evaluator);
        
        await expectFirestorePermissionDenied(
          evaluatorContext.firestore()
            .collection('humanEvaluationResults')
            .doc('other-eval-456')
            .update({
              scores: { quality: 5 }
            })
        );
      });

      test('regular user cannot update evaluations', async () => {
        const userContext = getAuthenticatedContext(testUsers.regularUser);
        
        await expectFirestorePermissionDenied(
          userContext.firestore()
            .collection('humanEvaluationResults')
            .doc('test-eval-123')
            .update({
              scores: { quality: 1 }
            })
        );
      });
    });

    describe('Delete Permissions', () => {
      test('admin can delete evaluation results', async () => {
        const adminContext = getAuthenticatedContext(testUsers.admin);
        
        await expectFirestoreSuccess(
          adminContext.firestore()
            .collection('humanEvaluationResults')
            .doc('test-eval-123')
            .delete()
        );
      });

      test('evaluator cannot delete their own evaluation', async () => {
        const evaluatorContext = getAuthenticatedContext(testUsers.evaluator);
        
        await expectFirestorePermissionDenied(
          evaluatorContext.firestore()
            .collection('humanEvaluationResults')
            .doc('test-eval-123')
            .delete()
        );
      });

      test('regular user cannot delete evaluations', async () => {
        const userContext = getAuthenticatedContext(testUsers.regularUser);
        
        await expectFirestorePermissionDenied(
          userContext.firestore()
            .collection('humanEvaluationResults')
            .doc('test-eval-123')
            .delete()
        );
      });
    });
  });

  describe('Automated Evaluation Results Collection', () => {
    
    beforeEach(async () => {
      // Setup test automated evaluation data
      const serviceContext = getAuthenticatedContext(testUsers.serviceAccount);
      await serviceContext.firestore()
        .collection('automatedEvaluationResults')
        .doc('auto-eval-123')
        .set({
          eval_run_id: 'run-uuid-123',
          agent_name: 'ProductManagerAgent',
          golden_dataset_inputId: 'test_input_001',
          validation_results: { syntax_valid: true, completeness: false },
          overall_automated_eval_passed: false,
          execution_time_ms: 1500,
          timestamp: new Date()
        });
    });

    describe('Read Permissions', () => {
      test('admin can read automated evaluation results', async () => {
        const adminContext = getAuthenticatedContext(testUsers.admin);
        
        await expectFirestoreSuccess(
          adminContext.firestore()
            .collection('automatedEvaluationResults')
            .doc('auto-eval-123')
            .get()
        );
      });

      test('regular user cannot read automated evaluation results', async () => {
        const userContext = getAuthenticatedContext(testUsers.regularUser);
        
        await expectFirestorePermissionDenied(
          userContext.firestore()
            .collection('automatedEvaluationResults')
            .doc('auto-eval-123')
            .get()
        );
      });

      test('evaluator cannot read automated evaluation results', async () => {
        const evaluatorContext = getAuthenticatedContext(testUsers.evaluator);
        
        await expectFirestorePermissionDenied(
          evaluatorContext.firestore()
            .collection('automatedEvaluationResults')
            .doc('auto-eval-123')
            .get()
        );
      });

      test('developer cannot read automated evaluation results', async () => {
        const devContext = getAuthenticatedContext(testUsers.developer);
        
        await expectFirestorePermissionDenied(
          devContext.firestore()
            .collection('automatedEvaluationResults')
            .doc('auto-eval-123')
            .get()
        );
      });
    });

    describe('Write Permissions', () => {
      test('service account can create automated evaluation results', async () => {
        const serviceContext = getAuthenticatedContext(testUsers.serviceAccount);
        
        await expectFirestoreSuccess(
          serviceContext.firestore()
            .collection('automatedEvaluationResults')
            .doc('new-auto-eval-456')
            .set({
              eval_run_id: 'run-uuid-456',
              agent_name: 'ArchitectAgent',
              golden_dataset_inputId: 'test_input_002',
              validation_results: { architecture_valid: true },
              overall_automated_eval_passed: true,
              execution_time_ms: 2500,
              timestamp: new Date()
            })
        );
      });

      test('service account can update automated evaluation results', async () => {
        const serviceContext = getAuthenticatedContext(testUsers.serviceAccount);
        
        await expectFirestoreSuccess(
          serviceContext.firestore()
            .collection('automatedEvaluationResults')
            .doc('auto-eval-123')
            .update({
              validation_results: { syntax_valid: true, completeness: true },
              overall_automated_eval_passed: true
            })
        );
      });

      test('service account can delete automated evaluation results', async () => {
        const serviceContext = getAuthenticatedContext(testUsers.serviceAccount);
        
        await expectFirestoreSuccess(
          serviceContext.firestore()
            .collection('automatedEvaluationResults')
            .doc('auto-eval-123')
            .delete()
        );
      });

      test('admin cannot write automated evaluation results', async () => {
        const adminContext = getAuthenticatedContext(testUsers.admin);
        
        await expectFirestorePermissionDenied(
          adminContext.firestore()
            .collection('automatedEvaluationResults')
            .doc('admin-auto-eval')
            .set({
              eval_run_id: 'admin-run',
              agent_name: 'TestAgent',
              validation_results: { admin_created: true },
              timestamp: new Date()
            })
        );
      });

      test('regular user cannot write automated evaluation results', async () => {
        const userContext = getAuthenticatedContext(testUsers.regularUser);
        
        await expectFirestorePermissionDenied(
          userContext.firestore()
            .collection('automatedEvaluationResults')
            .doc('user-auto-eval')
            .set({
              eval_run_id: 'user-run',
              agent_name: 'TestAgent',
              validation_results: { user_created: true },
              timestamp: new Date()
            })
        );
      });
    });
  });

  describe('Automated Evaluation Runs Collection', () => {
    
    beforeEach(async () => {
      // Setup test evaluation run data
      const serviceContext = getAuthenticatedContext(testUsers.serviceAccount);
      await serviceContext.firestore()
        .collection('automatedEvaluationRuns')
        .doc('run-123')
        .set({
          eval_run_id: 'run-uuid-123',
          total_examples: 21,
          successful_runs: 18,
          validation_passed: 15,
          start_time: new Date(),
          end_time: new Date(),
          summary: { success_rate: 85.7, validation_rate: 71.4 }
        });
    });

    describe('Read Permissions', () => {
      test('admin can read evaluation runs', async () => {
        const adminContext = getAuthenticatedContext(testUsers.admin);
        
        await expectFirestoreSuccess(
          adminContext.firestore()
            .collection('automatedEvaluationRuns')
            .doc('run-123')
            .get()
        );
      });

      test('regular user cannot read evaluation runs', async () => {
        const userContext = getAuthenticatedContext(testUsers.regularUser);
        
        await expectFirestorePermissionDenied(
          userContext.firestore()
            .collection('automatedEvaluationRuns')
            .doc('run-123')
            .get()
        );
      });

      test('evaluator cannot read evaluation runs', async () => {
        const evaluatorContext = getAuthenticatedContext(testUsers.evaluator);
        
        await expectFirestorePermissionDenied(
          evaluatorContext.firestore()
            .collection('automatedEvaluationRuns')
            .doc('run-123')
            .get()
        );
      });
    });

    describe('Write Permissions', () => {
      test('service account can create evaluation runs', async () => {
        const serviceContext = getAuthenticatedContext(testUsers.serviceAccount);
        
        await expectFirestoreSuccess(
          serviceContext.firestore()
            .collection('automatedEvaluationRuns')
            .doc('new-run-456')
            .set({
              eval_run_id: 'run-uuid-456',
              total_examples: 15,
              successful_runs: 12,
              validation_passed: 10,
              start_time: new Date(),
              end_time: new Date(),
              summary: { success_rate: 80.0, validation_rate: 66.7 }
            })
        );
      });

      test('service account can update evaluation runs', async () => {
        const serviceContext = getAuthenticatedContext(testUsers.serviceAccount);
        
        await expectFirestoreSuccess(
          serviceContext.firestore()
            .collection('automatedEvaluationRuns')
            .doc('run-123')
            .update({
              end_time: new Date(),
              summary: { success_rate: 90.0, validation_rate: 80.0 }
            })
        );
      });

      test('admin cannot write evaluation runs', async () => {
        const adminContext = getAuthenticatedContext(testUsers.admin);
        
        await expectFirestorePermissionDenied(
          adminContext.firestore()
            .collection('automatedEvaluationRuns')
            .doc('admin-run')
            .set({
              eval_run_id: 'admin-run-uuid',
              total_examples: 5,
              summary: { admin_created: true }
            })
        );
      });

      test('regular user cannot write evaluation runs', async () => {
        const userContext = getAuthenticatedContext(testUsers.regularUser);
        
        await expectFirestorePermissionDenied(
          userContext.firestore()
            .collection('automatedEvaluationRuns')
            .doc('user-run')
            .set({
              eval_run_id: 'user-run-uuid',
              total_examples: 1,
              summary: { user_created: true }
            })
        );
      });
    });
  });

  describe('List/Query Permissions', () => {
    test('admin can query all evaluation collections', async () => {
      const adminContext = getAuthenticatedContext(testUsers.admin);
      
      await expectFirestoreSuccess(
        adminContext.firestore()
          .collection('humanEvaluationResults')
          .get()
      );
      
      await expectFirestoreSuccess(
        adminContext.firestore()
          .collection('automatedEvaluationResults')
          .get()
      );
      
      await expectFirestoreSuccess(
        adminContext.firestore()
          .collection('automatedEvaluationRuns')
          .get()
      );
    });

    test('evaluator can query human evaluation results', async () => {
      const evaluatorContext = getAuthenticatedContext(testUsers.evaluator);
      
      await expectFirestoreSuccess(
        evaluatorContext.firestore()
          .collection('humanEvaluationResults')
          .get()
      );
    });

    test('evaluator cannot query automated evaluation collections', async () => {
      const evaluatorContext = getAuthenticatedContext(testUsers.evaluator);
      
      await expectFirestorePermissionDenied(
        evaluatorContext.firestore()
          .collection('automatedEvaluationResults')
          .get()
      );
      
      await expectFirestorePermissionDenied(
        evaluatorContext.firestore()
          .collection('automatedEvaluationRuns')
          .get()
      );
    });

    test('regular user cannot query any evaluation collections', async () => {
      const userContext = getAuthenticatedContext(testUsers.regularUser);
      
      await expectFirestorePermissionDenied(
        userContext.firestore()
          .collection('humanEvaluationResults')
          .get()
      );
      
      await expectFirestorePermissionDenied(
        userContext.firestore()
          .collection('automatedEvaluationResults')
          .get()
      );
      
      await expectFirestorePermissionDenied(
        userContext.firestore()
          .collection('automatedEvaluationRuns')
          .get()
      );
    });
  });
}); 