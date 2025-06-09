import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { HttpAgentAdapter } from '../agent/HttpAgentAdapter';

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Mock authService
vi.mock('../auth/authService', () => ({
  authService: {
    getIdToken: vi.fn().mockResolvedValue('mock-auth-token'),
  },
}));

describe.skip('HttpAgentAdapter', () => {
  let adapter: HttpAgentAdapter;

  beforeEach(() => {
    adapter = new HttpAgentAdapter();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('initiateCase', () => {
    it('should successfully initiate a case', async () => {
      const mockResponse = {
        caseId: 'test-case-id',
        initialMessage: 'Case initiated successfully',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const caseData = {
        problemStatement: 'Test problem statement',
        projectTitle: 'Test Project',
        relevantLinks: [{ name: 'Test Link', url: 'https://example.com' }],
      };

      const result = await adapter.initiateCase(caseData);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/agents/invoke'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-auth-token',
            'Content-Type': 'application/json',
          }),
          body: JSON.stringify({
            request_type: 'initiate_case',
            payload: caseData,
          }),
        })
      );

      expect(result).toEqual(mockResponse);
    });

    it('should handle API errors gracefully', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: () => Promise.resolve({ detail: 'Bad Request' }),
      });

      const caseData = {
        problemStatement: 'Test problem statement',
      };

      await expect(adapter.initiateCase(caseData))
        .rejects.toThrow('Bad Request');
    });

    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new TypeError('fetch error'));

      const caseData = {
        problemStatement: 'Test problem statement',
      };

      await expect(adapter.initiateCase(caseData))
        .rejects.toThrow('Network connection failed');
    });
  });

  describe('updatePrd', () => {
    it('should successfully update PRD', async () => {
      const mockResponse = {
        message: 'PRD updated successfully',
        updated_prd_draft: {
          title: 'Updated PRD',
          content_markdown: '# Updated PRD',
          version: 'v2',
        },
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const updateData = {
        caseId: 'case-id',
        content_markdown: '# Updated PRD',
      };

      const result = await adapter.updatePrd(updateData);

      expect(result).toEqual(mockResponse);
    });
  });

  describe('approvePrd', () => {
    it('should successfully approve PRD', async () => {
      const mockResponse = {
        message: 'PRD approved successfully',
        new_status: 'PRD_APPROVED',
        case_id: 'case-id',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await adapter.approvePrd('case-id');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/cases/case-id/prd/approve'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-auth-token',
          }),
        })
      );

      expect(result).toEqual(mockResponse);
    });
  });

  describe('rejectPrd', () => {
    it('should successfully reject PRD with reason', async () => {
      const mockResponse = {
        message: 'PRD rejected',
        new_status: 'PRD_REJECTED',
        case_id: 'case-id',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const rejectionReason = 'Needs more details';
      const result = await adapter.rejectPrd('case-id', rejectionReason);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/cases/case-id/prd/reject'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-auth-token',
            'Content-Type': 'application/json',
          }),
          body: JSON.stringify({ reason: rejectionReason }),
        })
      );

      expect(result).toEqual(mockResponse);
    });
  });

  describe('triggerSystemDesignGeneration', () => {
    it('should successfully trigger system design generation', async () => {
      const mockResponse = {
        message: 'System design generation initiated successfully',
        new_status: 'SYSTEM_DESIGN_DRAFTING',
        case_id: 'case-id',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await adapter.triggerSystemDesignGeneration('case-id');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/cases/case-id/trigger-system-design'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-auth-token',
          }),
        })
      );

      expect(result).toEqual(mockResponse);
    });
  });

  describe('getCaseDetails', () => {
    it('should successfully fetch case details', async () => {
      const mockCaseDetails = {
        case_id: 'case-id',
        title: 'Test Case',
        status: 'PRD_APPROVED',
        user_id: 'user-123',
        problem_statement: 'Test problem',
        relevant_links: [],
        history: [],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        prd_draft: {
          title: 'PRD Title',
          content_markdown: '# PRD Content',
          version: 'v1',
        },
        system_design_v1_draft: {
          content_markdown: '# System Design',
          generated_by: 'ArchitectAgent',
          version: 'v1',
          generated_at: '2024-01-01T00:00:00Z',
        },
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockCaseDetails),
      });

      const result = await adapter.getCaseDetails('case-id');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/cases/case-id'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-auth-token',
          }),
        })
      );

      expect(result).toEqual(mockCaseDetails);
    });
  });

  describe('error handling', () => {
    it('should handle 401 unauthorized errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: () => Promise.resolve({ detail: 'Unauthorized' }),
      });

      await expect(adapter.getCaseDetails('case-id'))
        .rejects.toThrow('Unauthorized');
    });

    it('should handle 403 forbidden errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 403,
        json: () => Promise.resolve({ detail: 'Forbidden' }),
      });

      await expect(adapter.getCaseDetails('case-id'))
        .rejects.toThrow('Forbidden');
    });

    it('should handle 404 not found errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: () => Promise.resolve({ detail: 'Not Found' }),
      });

      await expect(adapter.getCaseDetails('non-existent-case'))
        .rejects.toThrow('Not Found');
    });

    it('should handle 500 server errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ detail: 'Internal Server Error' }),
      });

      await expect(adapter.getCaseDetails('case-id'))
        .rejects.toThrow('Internal Server Error');
    });

    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new TypeError('fetch error'));

      await expect(adapter.getCaseDetails('case-id'))
        .rejects.toThrow('Network connection failed');
    });
  });
}); 