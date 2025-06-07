import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import { vi, beforeEach, afterEach, type MockedFunction } from 'vitest';
import { useContext } from 'react';
import { 
  AgentService, 
  InitiateCasePayload, 
  InitiateCaseResponse,
  BusinessCaseSummary,
  BusinessCaseDetails,
  ProvideFeedbackPayload,
  UpdatePrdPayload,
} from '../../services/agent/AgentService';
import { AgentProvider, AgentContext } from '../AgentContext';

// Mock the HttpAgentAdapter
const mockAgentService = {
  initiateCase: vi.fn() as MockedFunction<AgentService['initiateCase']>,
  provideFeedback: vi.fn() as MockedFunction<AgentService['provideFeedback']>,
  onAgentUpdate: vi.fn() as MockedFunction<AgentService['onAgentUpdate']>,
  listCases: vi.fn() as MockedFunction<AgentService['listCases']>,
  getCaseDetails: vi.fn() as MockedFunction<AgentService['getCaseDetails']>,
  updatePrd: vi.fn() as MockedFunction<AgentService['updatePrd']>,
  updateStatus: vi.fn() as MockedFunction<AgentService['updateStatus']>,
  submitPrdForReview: vi.fn() as MockedFunction<AgentService['submitPrdForReview']>,
  approvePrd: vi.fn() as MockedFunction<AgentService['approvePrd']>,
  rejectPrd: vi.fn() as MockedFunction<AgentService['rejectPrd']>,
  updateSystemDesign: vi.fn() as MockedFunction<AgentService['updateSystemDesign']>,
  submitSystemDesignForReview: vi.fn() as MockedFunction<AgentService['submitSystemDesignForReview']>,
  approveSystemDesign: vi.fn() as MockedFunction<AgentService['approveSystemDesign']>,
  rejectSystemDesign: vi.fn() as MockedFunction<AgentService['rejectSystemDesign']>,
  triggerSystemDesignGeneration: vi.fn() as MockedFunction<AgentService['triggerSystemDesignGeneration']>,
  updateEffortEstimate: vi.fn() as MockedFunction<AgentService['updateEffortEstimate']>,
  submitEffortEstimateForReview: vi.fn() as MockedFunction<AgentService['submitEffortEstimateForReview']>,
  updateCostEstimate: vi.fn() as MockedFunction<AgentService['updateCostEstimate']>,
  submitCostEstimateForReview: vi.fn() as MockedFunction<AgentService['submitCostEstimateForReview']>,
  updateValueProjection: vi.fn() as MockedFunction<AgentService['updateValueProjection']>,
  submitValueProjectionForReview: vi.fn() as MockedFunction<AgentService['submitValueProjectionForReview']>,
  approveEffortEstimate: vi.fn() as MockedFunction<AgentService['approveEffortEstimate']>,
  rejectEffortEstimate: vi.fn() as MockedFunction<AgentService['rejectEffortEstimate']>,
  approveCostEstimate: vi.fn() as MockedFunction<AgentService['approveCostEstimate']>,
  rejectCostEstimate: vi.fn() as MockedFunction<AgentService['rejectCostEstimate']>,
  approveValueProjection: vi.fn() as MockedFunction<AgentService['approveValueProjection']>,
  rejectValueProjection: vi.fn() as MockedFunction<AgentService['rejectValueProjection']>,
  submitCaseForFinalApproval: vi.fn() as MockedFunction<AgentService['submitCaseForFinalApproval']>,
  approveFinalCase: vi.fn() as MockedFunction<AgentService['approveFinalCase']>,
  rejectFinalCase: vi.fn() as MockedFunction<AgentService['rejectFinalCase']>,
  exportCaseToPdf: vi.fn() as MockedFunction<AgentService['exportCaseToPdf']>,
};

// Mock the HttpAgentAdapter module
vi.mock('../../services/agent/HttpAgentAdapter', () => ({
  HttpAgentAdapter: vi.fn().mockImplementation(() => mockAgentService),
}));

// Mock logger
vi.mock('../../utils/logger', () => ({
  default: {
    create: () => ({
      debug: vi.fn(),
      warn: vi.fn(),
      error: vi.fn(),
    }),
  },
}));

// Test component to access context
const TestConsumer: React.FC<{ onContextValue?: (value: any) => void }> = ({ onContextValue }) => {
  const context = useContext(AgentContext);
  
  if (onContextValue) {
    onContextValue(context);
  }
  
  if (!context) {
    return <div>No context</div>;
  }

  return (
    <div>
      <div data-testid="loading">{context.isLoading ? 'loading' : 'not-loading'}</div>
      <div data-testid="cases-loading">{context.isLoadingCases ? 'cases-loading' : 'cases-not-loading'}</div>
      <div data-testid="case-details-loading">{context.isLoadingCaseDetails ? 'case-details-loading' : 'case-details-not-loading'}</div>
      <div data-testid="error">{context.error?.message || 'no-error'}</div>
      <div data-testid="cases-error">{context.casesError?.message || 'no-cases-error'}</div>
      <div data-testid="case-details-error">{context.caseDetailsError?.message || 'no-case-details-error'}</div>
      <div data-testid="current-case-id">{context.currentCaseId || 'no-current-case'}</div>
      <div data-testid="cases-count">{context.cases.length}</div>
      <div data-testid="messages-count">{context.messages.length}</div>
      <div data-testid="current-case-details">{context.currentCaseDetails?.title || 'no-details'}</div>
    </div>
  );
};

describe('AgentContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('Provider Setup', () => {
    it('should provide context to children', () => {
      render(
        <AgentProvider>
          <TestConsumer />
        </AgentProvider>
      );

      expect(screen.getByTestId('loading')).toHaveTextContent('not-loading');
      expect(screen.getByTestId('cases-loading')).toHaveTextContent('cases-not-loading');
      expect(screen.getByTestId('case-details-loading')).toHaveTextContent('case-details-not-loading');
      expect(screen.getByTestId('error')).toHaveTextContent('no-error');
      expect(screen.getByTestId('current-case-id')).toHaveTextContent('no-current-case');
      expect(screen.getByTestId('cases-count')).toHaveTextContent('0');
    });

    it('should have all required methods in context', () => {
      let contextValue: any;
      
      render(
        <AgentProvider>
          <TestConsumer onContextValue={(value) => contextValue = value} />
        </AgentProvider>
      );

      expect(contextValue).toBeDefined();
      expect(typeof contextValue.initiateBusinessCase).toBe('function');
      expect(typeof contextValue.sendFeedbackToAgent).toBe('function');
      expect(typeof contextValue.fetchUserCases).toBe('function');
      expect(typeof contextValue.fetchCaseDetails).toBe('function');
      expect(typeof contextValue.updatePrdDraft).toBe('function');
      expect(typeof contextValue.clearAgentState).toBe('function');
      expect(typeof contextValue.clearError).toBe('function');
    });
  });

  describe('Case Initiation', () => {
    it('should successfully initiate a business case', async () => {
      const mockResponse: InitiateCaseResponse = {
        caseId: 'test-case-123',
        initialMessage: 'Case initiated successfully'
      };
      
      mockAgentService.initiateCase.mockResolvedValue(mockResponse);

      let contextValue: any;
      render(
        <AgentProvider>
          <TestConsumer onContextValue={(value) => contextValue = value} />
        </AgentProvider>
      );

      const payload: InitiateCasePayload = {
        problemStatement: 'Test problem statement',
        projectTitle: 'Test Project',
        relevantLinks: []
      };

      await act(async () => {
        const result = await contextValue.initiateBusinessCase(payload);
        expect(result).toEqual(mockResponse);
      });

      expect(mockAgentService.initiateCase).toHaveBeenCalledWith(payload);
      expect(screen.getByTestId('current-case-id')).toHaveTextContent('test-case-123');
      expect(screen.getByTestId('loading')).toHaveTextContent('not-loading');
    });

    it('should handle initiate case errors', async () => {
      const mockError = new Error('Failed to initiate case');
      mockAgentService.initiateCase.mockRejectedValue(mockError);

      let contextValue: any;
      render(
        <AgentProvider>
          <TestConsumer onContextValue={(value) => contextValue = value} />
        </AgentProvider>
      );

      const payload: InitiateCasePayload = {
        problemStatement: 'Test problem statement'
      };

      await act(async () => {
        const result = await contextValue.initiateBusinessCase(payload);
        expect(result).toBeUndefined();
      });

      await waitFor(() => {
        expect(screen.getByTestId('error')).toHaveTextContent('Failed to initiate case');
        expect(screen.getByTestId('loading')).toHaveTextContent('not-loading');
      });
    });

    it('should set loading state during initiation', async () => {
      const mockResponse: InitiateCaseResponse = {
        caseId: 'test-case-123'
      };

      // Make the promise hang to test loading state
      let resolvePromise: (value: InitiateCaseResponse) => void;
      const pendingPromise = new Promise<InitiateCaseResponse>((resolve) => {
        resolvePromise = resolve;
      });
      
      mockAgentService.initiateCase.mockReturnValue(pendingPromise);

      let contextValue: any;
      render(
        <AgentProvider>
          <TestConsumer onContextValue={(value) => contextValue = value} />
        </AgentProvider>
      );

      const payload: InitiateCasePayload = {
        problemStatement: 'Test problem statement'
      };

      // Start the async operation
      act(() => {
        contextValue.initiateBusinessCase(payload);
      });

      // Check loading state is set
      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('loading');
      });

      // Resolve the promise
      await act(async () => {
        resolvePromise!(mockResponse);
      });

      // Check loading state is cleared
      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('not-loading');
      });
    });
  });

  describe('Cases Management', () => {
    it('should fetch user cases successfully', async () => {
      const mockCases: BusinessCaseSummary[] = [
        {
          case_id: 'case-1',
          user_id: 'user-1',
          title: 'Project Alpha',
          status: 'PRD_DRAFTED',
          created_at: '2023-01-01T00:00:00Z',
          updated_at: '2023-01-01T00:00:00Z'
        },
        {
          case_id: 'case-2',
          user_id: 'user-1',
          title: 'Project Beta',
          status: 'IN_PROGRESS',
          created_at: '2023-01-02T00:00:00Z',
          updated_at: '2023-01-02T00:00:00Z'
        }
      ];

      mockAgentService.listCases.mockResolvedValue(mockCases);

      let contextValue: any;
      render(
        <AgentProvider>
          <TestConsumer onContextValue={(value) => contextValue = value} />
        </AgentProvider>
      );

      await act(async () => {
        await contextValue.fetchUserCases();
      });

      expect(mockAgentService.listCases).toHaveBeenCalled();
      expect(screen.getByTestId('cases-count')).toHaveTextContent('2');
      expect(screen.getByTestId('cases-loading')).toHaveTextContent('cases-not-loading');
    });

    it('should handle fetch cases errors', async () => {
      const mockError = new Error('Failed to fetch cases');
      mockAgentService.listCases.mockRejectedValue(mockError);

      let contextValue: any;
      render(
        <AgentProvider>
          <TestConsumer onContextValue={(value) => contextValue = value} />
        </AgentProvider>
      );

      await act(async () => {
        await contextValue.fetchUserCases();
      });

      await waitFor(() => {
        expect(screen.getByTestId('cases-error')).toHaveTextContent('Failed to fetch cases');
        expect(screen.getByTestId('cases-loading')).toHaveTextContent('cases-not-loading');
      });
    });

    it('should fetch case details successfully', async () => {
      const mockDetails: BusinessCaseDetails = {
        case_id: 'case-123',
        user_id: 'user-1',
        title: 'Test Project Details',
        problem_statement: 'Test problem',
        status: 'PRD_DRAFTED',
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z',
        relevant_links: [],
        history: [
          {
            caseId: 'case-123',
            timestamp: '2023-01-01T00:00:00Z',
            source: 'AGENT',
            messageType: 'TEXT',
            content: 'Welcome to your business case!'
          }
        ]
      };

      mockAgentService.getCaseDetails.mockResolvedValue(mockDetails);

      let contextValue: any;
      render(
        <AgentProvider>
          <TestConsumer onContextValue={(value) => contextValue = value} />
        </AgentProvider>
      );

      await act(async () => {
        await contextValue.fetchCaseDetails('case-123');
      });

      expect(mockAgentService.getCaseDetails).toHaveBeenCalledWith('case-123');
      expect(screen.getByTestId('current-case-details')).toHaveTextContent('Test Project Details');
      expect(screen.getByTestId('current-case-id')).toHaveTextContent('case-123');
      expect(screen.getByTestId('messages-count')).toHaveTextContent('1');
      expect(screen.getByTestId('case-details-loading')).toHaveTextContent('case-details-not-loading');
    });

    it('should handle fetch case details errors', async () => {
      const mockError = new Error('Case not found');
      mockAgentService.getCaseDetails.mockRejectedValue(mockError);

      let contextValue: any;
      render(
        <AgentProvider>
          <TestConsumer onContextValue={(value) => contextValue = value} />
        </AgentProvider>
      );

      await act(async () => {
        await contextValue.fetchCaseDetails('invalid-case');
      });

      await waitFor(() => {
        expect(screen.getByTestId('case-details-error')).toHaveTextContent('Case not found');
        expect(screen.getByTestId('case-details-loading')).toHaveTextContent('case-details-not-loading');
      });
    });
  });

  describe('Feedback Management', () => {
    it('should send feedback successfully', async () => {
      mockAgentService.provideFeedback.mockResolvedValue();

      let contextValue: any;
      render(
        <AgentProvider>
          <TestConsumer onContextValue={(value) => contextValue = value} />
        </AgentProvider>
      );

      const payload: ProvideFeedbackPayload = {
        caseId: 'case-123',
        message: 'This looks great!'
      };

      await act(async () => {
        await contextValue.sendFeedbackToAgent(payload);
      });

      expect(mockAgentService.provideFeedback).toHaveBeenCalledWith(payload);
      expect(screen.getByTestId('loading')).toHaveTextContent('not-loading');
    });

    it('should handle feedback errors', async () => {
      const mockError = new Error('Failed to send feedback');
      mockAgentService.provideFeedback.mockRejectedValue(mockError);

      let contextValue: any;
      render(
        <AgentProvider>
          <TestConsumer onContextValue={(value) => contextValue = value} />
        </AgentProvider>
      );

      const payload: ProvideFeedbackPayload = {
        caseId: 'case-123',
        message: 'Test feedback'
      };

      await act(async () => {
        await contextValue.sendFeedbackToAgent(payload);
      });

      await waitFor(() => {
        expect(screen.getByTestId('error')).toHaveTextContent('Failed to send feedback');
        expect(screen.getByTestId('loading')).toHaveTextContent('not-loading');
      });
    });

    it('should add user message to messages before sending feedback', async () => {
      mockAgentService.provideFeedback.mockResolvedValue();

      let contextValue: any;
      render(
        <AgentProvider>
          <TestConsumer onContextValue={(value) => contextValue = value} />
        </AgentProvider>
      );

      const payload: ProvideFeedbackPayload = {
        caseId: 'case-123',
        message: 'Test user message'
      };

      await act(async () => {
        await contextValue.sendFeedbackToAgent(payload);
      });

      // The user message should be added to the messages array
      expect(screen.getByTestId('messages-count')).toHaveTextContent('1');
    });
  });

  describe('PRD Management', () => {
    it('should update PRD draft successfully', async () => {
      const mockResponse = {
        message: 'PRD updated successfully',
        updated_prd_draft: {
          title: 'Updated PRD',
          content_markdown: 'Updated content',
          version: '1.1'
        }
      };

      mockAgentService.updatePrd.mockResolvedValue(mockResponse);

      let contextValue: any;
      render(
        <AgentProvider>
          <TestConsumer onContextValue={(value) => contextValue = value} />
        </AgentProvider>
      );

      const payload: UpdatePrdPayload = {
        caseId: 'case-123',
        content_markdown: 'Updated PRD content'
      };

      let result: boolean;
      await act(async () => {
        result = await contextValue.updatePrdDraft(payload);
      });

      expect(result!).toBe(true);
      expect(mockAgentService.updatePrd).toHaveBeenCalledWith(payload);
    });

    it('should handle PRD update errors', async () => {
      const mockError = new Error('Failed to update PRD');
      mockAgentService.updatePrd.mockRejectedValue(mockError);

      let contextValue: any;
      render(
        <AgentProvider>
          <TestConsumer onContextValue={(value) => contextValue = value} />
        </AgentProvider>
      );

      const payload: UpdatePrdPayload = {
        caseId: 'case-123',
        content_markdown: 'Updated PRD content'
      };

      let result: boolean;
      await act(async () => {
        result = await contextValue.updatePrdDraft(payload);
      });

      expect(result!).toBe(false);
    });

    it('should submit PRD for review successfully', async () => {
      const mockResponse = {
        message: 'PRD submitted for review',
        new_status: 'PRD_UNDER_REVIEW',
        case_id: 'case-123'
      };

      mockAgentService.submitPrdForReview.mockResolvedValue(mockResponse);

      let contextValue: any;
      render(
        <AgentProvider>
          <TestConsumer onContextValue={(value) => contextValue = value} />
        </AgentProvider>
      );

      let result: boolean;
      await act(async () => {
        result = await contextValue.submitPrdForReview('case-123');
      });

      expect(result!).toBe(true);
      expect(mockAgentService.submitPrdForReview).toHaveBeenCalledWith('case-123');
    });
  });

  describe('Error Management', () => {
    it('should clear general errors', async () => {
      // First set an error
      const mockError = new Error('Test error');
      mockAgentService.initiateCase.mockRejectedValue(mockError);

      let contextValue: any;
      render(
        <AgentProvider>
          <TestConsumer onContextValue={(value) => contextValue = value} />
        </AgentProvider>
      );

      // Trigger an error
      await act(async () => {
        await contextValue.initiateBusinessCase({ problemStatement: 'test' });
      });

      // Verify error is set
      await waitFor(() => {
        expect(screen.getByTestId('error')).toHaveTextContent('Test error');
      });

      // Clear the error
      await act(async () => {
        contextValue.clearError('general');
      });

      // Verify error is cleared
      expect(screen.getByTestId('error')).toHaveTextContent('no-error');
    });

    it('should clear cases errors', async () => {
      const mockError = new Error('Cases error');
      mockAgentService.listCases.mockRejectedValue(mockError);

      let contextValue: any;
      render(
        <AgentProvider>
          <TestConsumer onContextValue={(value) => contextValue = value} />
        </AgentProvider>
      );

      // Trigger an error
      await act(async () => {
        await contextValue.fetchUserCases();
      });

      // Verify error is set
      await waitFor(() => {
        expect(screen.getByTestId('cases-error')).toHaveTextContent('Cases error');
      });

      // Clear the error
      await act(async () => {
        contextValue.clearError('cases');
      });

      // Verify error is cleared
      expect(screen.getByTestId('cases-error')).toHaveTextContent('no-cases-error');
    });

    it('should clear all errors when no type specified', async () => {
      // Set multiple errors
      const mockError1 = new Error('General error');
      const mockError2 = new Error('Cases error');
      
      mockAgentService.initiateCase.mockRejectedValue(mockError1);
      mockAgentService.listCases.mockRejectedValue(mockError2);

      let contextValue: any;
      render(
        <AgentProvider>
          <TestConsumer onContextValue={(value) => contextValue = value} />
        </AgentProvider>
      );

      // Trigger errors
      await act(async () => {
        await contextValue.initiateBusinessCase({ problemStatement: 'test' });
        await contextValue.fetchUserCases();
      });

      // Verify errors are set
      await waitFor(() => {
        expect(screen.getByTestId('error')).toHaveTextContent('General error');
        expect(screen.getByTestId('cases-error')).toHaveTextContent('Cases error');
      });

      // Clear all errors
      await act(async () => {
        contextValue.clearError();
      });

      // Verify all errors are cleared
      expect(screen.getByTestId('error')).toHaveTextContent('no-error');
      expect(screen.getByTestId('cases-error')).toHaveTextContent('no-cases-error');
    });
  });

  describe('State Management', () => {
    it('should clear agent state', async () => {
      // First set some state
      const mockCases: BusinessCaseSummary[] = [
        {
          case_id: 'case-1',
          user_id: 'user-1',
          title: 'Project Alpha',
          status: 'PRD_DRAFTED',
          created_at: '2023-01-01T00:00:00Z',
          updated_at: '2023-01-01T00:00:00Z'
        }
      ];

      mockAgentService.listCases.mockResolvedValue(mockCases);

      let contextValue: any;
      render(
        <AgentProvider>
          <TestConsumer onContextValue={(value) => contextValue = value} />
        </AgentProvider>
      );

      // Set some state
      await act(async () => {
        await contextValue.fetchUserCases();
      });

      expect(screen.getByTestId('cases-count')).toHaveTextContent('1');

      // Clear state
      await act(async () => {
        contextValue.clearAgentState();
      });

      // Verify state is cleared
      expect(screen.getByTestId('cases-count')).toHaveTextContent('0');
      expect(screen.getByTestId('current-case-id')).toHaveTextContent('no-current-case');
      expect(screen.getByTestId('messages-count')).toHaveTextContent('0');
    });

    it('should clear current case details', async () => {
      // First set case details
      const mockDetails: BusinessCaseDetails = {
        case_id: 'case-123',
        user_id: 'user-1',
        title: 'Test Project',
        problem_statement: 'Test problem',
        status: 'PRD_DRAFTED',
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z',
        relevant_links: [],
        history: []
      };

      mockAgentService.getCaseDetails.mockResolvedValue(mockDetails);

      let contextValue: any;
      render(
        <AgentProvider>
          <TestConsumer onContextValue={(value) => contextValue = value} />
        </AgentProvider>
      );

      // Set case details
      await act(async () => {
        await contextValue.fetchCaseDetails('case-123');
      });

      expect(screen.getByTestId('current-case-details')).toHaveTextContent('Test Project');

      // Clear current case details
      await act(async () => {
        contextValue.clearCurrentCaseDetails();
      });

      // Verify case details are cleared
      expect(screen.getByTestId('current-case-details')).toHaveTextContent('no-details');
    });
  });
}); 