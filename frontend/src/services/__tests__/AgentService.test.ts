import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { HttpAgentAdapter } from '../agent/HttpAgentAdapter';
import { authService } from '../auth/authService';
import {
  InitiateCasePayload,
  InitiateCaseResponse,
  ProvideFeedbackPayload,
  BusinessCaseSummary,
  BusinessCaseDetails,
  UpdatePrdPayload,
  UpdateStatusPayload,
} from '../agent/AgentService';
import { AppError, NetworkError } from '../../types/api';

// Mock the auth service
const mockGetIdToken = vi.fn();
vi.mock('../auth/authService', () => ({
  authService: {
    getIdToken: mockGetIdToken,
  },
}));

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Mock environment variables
vi.mock('../../utils/logger', () => ({
  default: {
    create: () => ({
      debug: vi.fn(),
      warn: vi.fn(),
      error: vi.fn(),
    }),
  },
}));

describe('HttpAgentAdapter', () => {
  let agentAdapter: HttpAgentAdapter;
  const mockToken = 'mock-jwt-token';
  const mockApiBaseUrl = 'http://localhost:8000/api/v1';

  beforeEach(() => {
    agentAdapter = new HttpAgentAdapter();
    
    // Setup default mocks
    mockGetIdToken.mockResolvedValue(mockToken);
    
    // Clear all mocks
    vi.clearAllMocks();
    mockFetch.mockClear();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('Authentication', () => {
    it('should include auth headers in requests', async () => {
      const mockResponse = { success: true };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      await agentAdapter.listCases();

      expect(authService.getIdToken).toHaveBeenCalled();
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/cases'),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': `Bearer ${mockToken}`,
            'Content-Type': 'application/json',
          }),
        })
      );
    });

    it('should throw auth error when token is not available', async () => {
      mockGetIdToken.mockResolvedValue(null);

      await expect(agentAdapter.listCases()).rejects.toEqual(
        expect.objectContaining({
          name: 'AuthError',
          message: 'Authentication required',
          type: 'auth',
          code: 'auth/no-token',
        })
      );
    });

    it('should handle auth service errors', async () => {
      const authError = new Error('Token expired');
      mockGetIdToken.mockRejectedValue(authError);

      await expect(agentAdapter.listCases()).rejects.toEqual(
        expect.objectContaining({
          name: 'AuthError',
          message: 'Token expired',
          type: 'auth',
          code: 'auth/token-expired',
        })
      );
    });
  });

  describe('Error Handling', () => {
    beforeEach(() => {
      mockGetIdToken.mockResolvedValue(mockToken);
    });

    it('should handle network errors', async () => {
      mockFetch.mockRejectedValue(new TypeError('Failed to fetch'));

      await expect(agentAdapter.listCases()).rejects.toEqual(
        expect.objectContaining({
          name: 'NetworkError',
          message: 'Network connection failed',
          url: '/cases',
        })
      );
    });

    it('should handle API errors with standardized format', async () => {
      const errorResponse = {
        error: {
          message: 'Case not found',
          error_code: 'CASE_NOT_FOUND',
          details: { caseId: 'invalid-id' }
        }
      };

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: () => Promise.resolve(errorResponse),
      });

      await expect(agentAdapter.getCaseDetails('invalid-id')).rejects.toEqual(
        expect.objectContaining({
          name: 'ApiError',
          message: 'Case not found',
          type: 'api',
          status: 404,
          details: expect.objectContaining({
            endpoint: '/cases/invalid-id',
            method: 'GET',
            errorCode: 'CASE_NOT_FOUND',
            serverDetails: { caseId: 'invalid-id' }
          })
        })
      );
    });

    it('should handle legacy error format', async () => {
      const errorResponse = { detail: 'Invalid request' };

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: () => Promise.resolve(errorResponse),
      });

      await expect(agentAdapter.listCases()).rejects.toEqual(
        expect.objectContaining({
          name: 'ApiError',
          message: 'Invalid request',
          type: 'api',
          status: 400,
        })
      );
    });

    it('should handle non-JSON error responses', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: () => Promise.reject(new Error('Not JSON')),
      });

      await expect(agentAdapter.listCases()).rejects.toEqual(
        expect.objectContaining({
          name: 'ApiError',
          message: 'Unknown error',
          type: 'api',
          status: 500,
        })
      );
    });
  });

  describe('Case Management Operations', () => {
    beforeEach(() => {
      mockGetIdToken.mockResolvedValue(mockToken);
    });

    describe('initiateCase', () => {
      it('should successfully initiate a new case', async () => {
        const payload: InitiateCasePayload = {
          problemStatement: 'Test Problem',
          projectTitle: 'Test Project',
          relevantLinks: []
        };

        const expectedResponse: InitiateCaseResponse = {
          caseId: 'test-case-id',
          initialMessage: 'Case initiated successfully'
        };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(expectedResponse),
        });

        const result = await agentAdapter.initiateCase(payload);

        expect(result).toEqual(expectedResponse);
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/agents/invoke'),
          expect.objectContaining({
            method: 'POST',
            body: JSON.stringify({
              request_type: 'initiate_case',
              payload: payload,
            }),
          })
        );
      });
    });

    describe('listCases', () => {
      it('should successfully fetch user cases', async () => {
        const mockCases: BusinessCaseSummary[] = [
          {
            case_id: 'case-1',
            user_id: 'user-1',
            title: 'Project 1',
            status: 'PRD_DRAFTED',
            created_at: '2023-01-01T00:00:00Z',
            updated_at: '2023-01-01T00:00:00Z'
          },
          {
            case_id: 'case-2',
            user_id: 'user-2',
            title: 'Project 2',
            status: 'IN_PROGRESS',
            created_at: '2023-01-02T00:00:00Z',
            updated_at: '2023-01-02T00:00:00Z'
          }
        ];

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockCases),
        });

        const result = await agentAdapter.listCases();

        expect(result).toEqual(mockCases);
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/cases'),
          expect.objectContaining({
            method: 'GET',
          })
        );
      });
    });

    describe('getCaseDetails', () => {
      it('should successfully fetch case details', async () => {
        const caseId = 'test-case-id';
        const mockDetails: BusinessCaseDetails = {
          case_id: caseId,
          user_id: 'test-user-id',
          title: 'Test Project',
          problem_statement: 'Test Problem',
          status: 'PRD_DRAFTED',
          created_at: '2023-01-01T00:00:00Z',
          updated_at: '2023-01-01T00:00:00Z',
          history: [],
          relevant_links: []
        };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockDetails),
        });

        const result = await agentAdapter.getCaseDetails(caseId);

        expect(result).toEqual(mockDetails);
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining(`/cases/${caseId}`),
          expect.objectContaining({
            method: 'GET',
          })
        );
      });
    });

    describe('provideFeedback', () => {
      it('should successfully send feedback', async () => {
        const payload: ProvideFeedbackPayload = {
          caseId: 'test-case-id',
          message: 'Test feedback'
        };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({}),
        });

        await agentAdapter.provideFeedback(payload);

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/agents/invoke'),
          expect.objectContaining({
            method: 'POST',
            body: JSON.stringify({
              request_type: 'provide_feedback',
              payload: payload,
            }),
          })
        );
      });
    });

    describe('updatePrd', () => {
      it('should successfully update PRD', async () => {
        const payload: UpdatePrdPayload = {
          caseId: 'test-case-id',
          content_markdown: 'Updated PRD content'
        };

        const expectedResponse = {
          message: 'PRD updated successfully',
          updated_prd_draft: {
            title: 'Test PRD',
            content_markdown: payload.content_markdown,
            version: '1.0'
          }
        };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(expectedResponse),
        });

        const result = await agentAdapter.updatePrd(payload);

        expect(result).toEqual(expectedResponse);
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining(`/cases/${payload.caseId}/prd`),
          expect.objectContaining({
            method: 'PUT',
            body: JSON.stringify({ content_markdown: payload.content_markdown }),
          })
        );
      });
    });

    describe('Status Management', () => {
      it('should submit PRD for review', async () => {
        const caseId = 'test-case-id';
        const expectedResponse = {
          message: 'PRD submitted for review',
          new_status: 'PRD_UNDER_REVIEW',
          case_id: caseId
        };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(expectedResponse),
        });

        const result = await agentAdapter.submitPrdForReview(caseId);

        expect(result).toEqual(expectedResponse);
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining(`/cases/${caseId}/prd/submit`),
          expect.objectContaining({
            method: 'POST',
          })
        );
      });

      it('should approve PRD', async () => {
        const caseId = 'test-case-id';
        const expectedResponse = {
          message: 'PRD approved',
          new_status: 'PRD_APPROVED',
          case_id: caseId
        };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(expectedResponse),
        });

        const result = await agentAdapter.approvePrd(caseId);

        expect(result).toEqual(expectedResponse);
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining(`/cases/${caseId}/prd/approve`),
          expect.objectContaining({
            method: 'POST',
          })
        );
      });

      it('should reject PRD with reason', async () => {
        const caseId = 'test-case-id';
        const reason = 'Needs more detail';
        const expectedResponse = {
          message: 'PRD rejected',
          new_status: 'PRD_REJECTED',
          case_id: caseId
        };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(expectedResponse),
        });

        const result = await agentAdapter.rejectPrd(caseId, reason);

        expect(result).toEqual(expectedResponse);
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining(`/cases/${caseId}/prd/reject`),
          expect.objectContaining({
            method: 'POST',
            body: JSON.stringify({ reason }),
          })
        );
      });
    });

    describe('Export Functionality', () => {
      it('should export case to PDF', async () => {
        const caseId = 'test-case-id';
        const mockBlob = new Blob(['PDF content'], { type: 'application/pdf' });

        mockFetch.mockResolvedValueOnce({
          ok: true,
          blob: () => Promise.resolve(mockBlob),
          headers: new Headers({
            'content-type': 'application/pdf'
          })
        });

        const result = await agentAdapter.exportCaseToPdf(caseId);

        expect(result).toBeInstanceOf(Blob);
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining(`/cases/${caseId}/export/pdf`),
          expect.objectContaining({
            method: 'GET',
          })
        );
      });
    });
  });

  describe('Real-time Updates', () => {
    it('should return a no-op unsubscribe function for onAgentUpdate', () => {
      const mockCallback = vi.fn();
      const unsubscribe = agentAdapter.onAgentUpdate('test-case-id', mockCallback);
      
      expect(typeof unsubscribe).toBe('function');
      
      // Should not throw when called
      expect(() => unsubscribe()).not.toThrow();
      
      // Callback should not have been called (no real-time implementation)
      expect(mockCallback).not.toHaveBeenCalled();
    });
  });
});
