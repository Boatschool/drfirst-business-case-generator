import { authService } from '../auth/authService'; // To get the ID token
import {
  AgentService,
  InitiateCasePayload,
  InitiateCaseResponse,
  ProvideFeedbackPayload,
  AgentUpdate,
  BusinessCaseSummary,
  BusinessCaseDetails,
  UpdatePrdPayload,
  UpdatePrdResponse,
  UpdateStatusPayload,
  UpdateStatusResponse,
  EffortEstimate,
  CostEstimate,
  ValueProjection,
} from './AgentService';
import { AppError, NetworkError, UnknownObject } from '../../types/api';
import Logger from '../../utils/logger';

// Use environment variable for API base URL
const API_BASE_URL = `${import.meta.env.VITE_API_BASE_URL}/api/${
  import.meta.env.VITE_API_VERSION
}`;

// Create logger instance for this service
const logger = Logger.create('HttpAgentAdapter');

logger.debug('Using API_BASE_URL:', API_BASE_URL);

export class HttpAgentAdapter implements AgentService {
  private async getAuthHeaders(): Promise<Record<string, string>> {
    try {
      const idToken = await authService.getIdToken();
      if (!idToken) {
        const authError: AppError = {
          name: 'AuthError',
          message: 'Authentication required - please log in',
          type: 'auth',
          code: 'auth/no-token'
        };
        throw authError;
      }
      return {
        Authorization: `Bearer ${idToken}`,
        'Content-Type': 'application/json',
      };
    } catch (error) {
      // Don't log auth errors as errors - they're expected when not logged in
      if (error && typeof error === 'object' && 'code' in error) {
        logger.debug('[HttpAgentAdapter] Authentication required:', error);
      } else {
        logger.error('[HttpAgentAdapter] Error getting auth headers:', error);
      }
      const authError: AppError = {
        name: 'AuthError',
        message: 'Authentication failed - please log in',
        type: 'auth',
        code: 'auth/failed',
        details: error
      };
      throw authError;
    }
  }

  private async fetchWithAuth<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    try {
      const headers = await this.getAuthHeaders();
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: {
          ...headers,
          ...options.headers,
        },
      });

      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
        } catch (e) {
          // If response is not JSON, use status text
          errorData = { detail: response.statusText };
        }
        
        // Extract error message from new standardized backend format
        let errorMessage = 'Unknown error';
        let errorCode: string | undefined;
        let errorDetails: unknown = undefined;
        
        if (errorData?.error) {
          // New standardized format: { error: { message, error_code, details } }
          errorMessage = errorData.error.message || errorMessage;
          errorCode = errorData.error.error_code;
          errorDetails = errorData.error.details;
        } else if (errorData?.detail) {
          // Legacy format: { detail: "message" }
          errorMessage = errorData.detail;
        }
        
        // Create enhanced error object with status and context
        const error: AppError = {
          name: 'ApiError',
          message: errorMessage,
          type: 'api',
          status: response.status,
          details: {
            endpoint,
            method: options.method || 'GET',
            errorCode,
            serverDetails: errorDetails
          }
        };
        
        throw error;
      }
      return response.json() as Promise<T>;
    } catch (error) {
      // Handle network errors and other exceptions
      if (error instanceof TypeError && error.message.includes('fetch')) {
        const networkError: NetworkError = {
          name: 'NetworkError',
          message: 'Network connection failed',
          url: endpoint
        };
        throw networkError;
      }
      
      // Re-throw API errors with additional context
      throw error;
    }
  }

  async initiateCase(
    payload: InitiateCasePayload
  ): Promise<InitiateCaseResponse> {
    // The backend /invoke endpoint expects a generic request_type and payload structure
    const requestPayload = {
      request_type: 'initiate_case', // This type needs to be handled by OrchestratorAgent
      payload: payload,
    };
    // Assuming the direct response from /invoke for 'initiate_case' will match InitiateCaseResponse structure
    // or OrchestratorAgent will return a structure that can be mapped to it.
    return this.fetchWithAuth<InitiateCaseResponse>('/agents/invoke', {
      method: 'POST',
      body: JSON.stringify(requestPayload),
    });
  }

  async provideFeedback(payload: ProvideFeedbackPayload): Promise<void> {
    const requestPayload = {
      request_type: 'provide_feedback', // This type needs to be handled by OrchestratorAgent
      payload: payload,
    };
    // The /invoke endpoint might return a more detailed response. Here we expect it to conform to void or a simple success message.
    await this.fetchWithAuth<UnknownObject>('/agents/invoke', {
      method: 'POST',
      body: JSON.stringify(requestPayload),
    });
    // If the backend returns a specific structure, we can map it or adjust the return type.
  }

  onAgentUpdate(
    caseId: string,
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    _onUpdateCallback: (update: AgentUpdate) => void
  ): () => void {
    logger.warn(
      `onAgentUpdate for case ${caseId} is not implemented for real-time updates. Polling or WebSocket would be needed.`
    );
    // Placeholder: No-op for real-time updates in this basic HTTP adapter
    // In a real scenario, this would set up polling or a WebSocket connection.
    // Example of polling (very basic):
    /*
    const intervalId = setInterval(async () => {
      try {
        // This endpoint needs to be defined in the backend
        const updates = await this.fetchWithAuth<AgentUpdate[]>(`/agents/case/${caseId}/updates`); 
        updates.forEach(onUpdateCallback);
      } catch (error) {
        logger.error("Polling for agent updates failed:", error);
        // Potentially call onUpdateCallback with an error update
      }
    }, 5000); // Poll every 5 seconds
    return () => clearInterval(intervalId);
    */
    return () => {
      // No-op unsubscribe function for HTTP adapter (no real-time updates)
    };
  }

  async listCases(): Promise<BusinessCaseSummary[]> {
    return this.fetchWithAuth<BusinessCaseSummary[]>('/cases', {
      method: 'GET',
    });
  }

  async getCaseDetails(caseId: string): Promise<BusinessCaseDetails> {
    return this.fetchWithAuth<BusinessCaseDetails>(`/cases/${caseId}`, {
      method: 'GET',
    });
  }

  async updatePrd(payload: UpdatePrdPayload): Promise<UpdatePrdResponse> {
    const { caseId, ...requestBody } = payload;
    return this.fetchWithAuth<UpdatePrdResponse>(`/cases/${caseId}/prd`, {
      method: 'PUT',
      body: JSON.stringify(requestBody),
    });
  }

  async updateStatus(
    payload: UpdateStatusPayload
  ): Promise<UpdateStatusResponse> {
    const { caseId, ...requestBody } = payload;
    return this.fetchWithAuth<UpdateStatusResponse>(`/cases/${caseId}/status`, {
      method: 'PUT',
      body: JSON.stringify(requestBody),
    });
  }

  async submitPrdForReview(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }> {
    return this.fetchWithAuth<{
      message: string;
      new_status: string;
      case_id: string;
    }>(`/cases/${caseId}/submit-prd`, {
      method: 'POST',
    });
  }

  async approvePrd(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }> {
    return this.fetchWithAuth<{
      message: string;
      new_status: string;
      case_id: string;
    }>(`/cases/${caseId}/prd/approve`, {
      method: 'POST',
    });
  }

  async rejectPrd(
    caseId: string,
    reason?: string
  ): Promise<{ message: string; new_status: string; case_id: string }> {
    const requestBody = reason ? { reason } : {};
    return this.fetchWithAuth<{
      message: string;
      new_status: string;
      case_id: string;
    }>(`/cases/${caseId}/prd/reject`, {
      method: 'POST',
      body: JSON.stringify(requestBody),
    });
  }

  async updateSystemDesign(
    caseId: string,
    content: string
  ): Promise<{ message: string; updated_system_design: UnknownObject }> {
    const requestBody = { content_markdown: content };
    return this.fetchWithAuth<{ message: string; updated_system_design: UnknownObject }>(
      `/cases/${caseId}/system-design`,
      {
        method: 'PUT',
        body: JSON.stringify(requestBody),
      }
    );
  }

  async submitSystemDesignForReview(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }> {
    return this.fetchWithAuth<{
      message: string;
      new_status: string;
      case_id: string;
    }>(`/cases/${caseId}/system-design/submit`, {
      method: 'POST',
    });
  }

  async approveSystemDesign(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }> {
    return this.fetchWithAuth<{
      message: string;
      new_status: string;
      case_id: string;
    }>(`/cases/${caseId}/system-design/approve`, {
      method: 'POST',
    });
  }

  async rejectSystemDesign(
    caseId: string,
    reason?: string
  ): Promise<{ message: string; new_status: string; case_id: string }> {
    const requestBody = reason ? { reason } : {};
    return this.fetchWithAuth<{
      message: string;
      new_status: string;
      case_id: string;
    }>(`/cases/${caseId}/system-design/reject`, {
      method: 'POST',
      body: JSON.stringify(requestBody),
    });
  }

  async triggerSystemDesignGeneration(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }> {
    return this.fetchWithAuth<{
      message: string;
      new_status: string;
      case_id: string;
    }>(`/cases/${caseId}/trigger-system-design`, {
      method: 'POST',
    });
  }

  async updateEffortEstimate(
    caseId: string,
    data: EffortEstimate
  ): Promise<{ message: string; updated_effort_estimate: EffortEstimate }> {
    return this.fetchWithAuth<{
      message: string;
      updated_effort_estimate: EffortEstimate;
    }>(`/cases/${caseId}/effort-estimate`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async submitEffortEstimateForReview(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }> {
    return this.fetchWithAuth<{
      message: string;
      new_status: string;
      case_id: string;
    }>(`/cases/${caseId}/effort-estimate/submit`, {
      method: 'POST',
    });
  }

  async updateCostEstimate(
    caseId: string,
    data: CostEstimate
  ): Promise<{ message: string; updated_cost_estimate: CostEstimate }> {
    return this.fetchWithAuth<{
      message: string;
      updated_cost_estimate: CostEstimate;
    }>(`/cases/${caseId}/cost-estimate`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async submitCostEstimateForReview(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }> {
    return this.fetchWithAuth<{
      message: string;
      new_status: string;
      case_id: string;
    }>(`/cases/${caseId}/cost-estimate/submit`, {
      method: 'POST',
    });
  }

  async updateValueProjection(
    caseId: string,
    data: ValueProjection
  ): Promise<{ message: string; updated_value_projection: ValueProjection }> {
    return this.fetchWithAuth<{
      message: string;
      updated_value_projection: ValueProjection;
    }>(`/cases/${caseId}/value-projection`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async submitValueProjectionForReview(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }> {
    return this.fetchWithAuth<{
      message: string;
      new_status: string;
      case_id: string;
    }>(`/cases/${caseId}/value-projection/submit`, {
      method: 'POST',
    });
  }

  async approveEffortEstimate(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }> {
    return this.fetchWithAuth<{
      message: string;
      new_status: string;
      case_id: string;
    }>(`/cases/${caseId}/effort-estimate/approve`, {
      method: 'POST',
    });
  }

  async rejectEffortEstimate(
    caseId: string,
    reason?: string
  ): Promise<{ message: string; new_status: string; case_id: string }> {
    const requestBody = reason ? { reason } : {};
    return this.fetchWithAuth<{
      message: string;
      new_status: string;
      case_id: string;
    }>(`/cases/${caseId}/effort-estimate/reject`, {
      method: 'POST',
      body: JSON.stringify(requestBody),
    });
  }

  async approveCostEstimate(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }> {
    return this.fetchWithAuth<{
      message: string;
      new_status: string;
      case_id: string;
    }>(`/cases/${caseId}/cost-estimate/approve`, {
      method: 'POST',
    });
  }

  async rejectCostEstimate(
    caseId: string,
    reason?: string
  ): Promise<{ message: string; new_status: string; case_id: string }> {
    const requestBody = reason ? { reason } : {};
    return this.fetchWithAuth<{
      message: string;
      new_status: string;
      case_id: string;
    }>(`/cases/${caseId}/cost-estimate/reject`, {
      method: 'POST',
      body: JSON.stringify(requestBody),
    });
  }

  async approveValueProjection(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }> {
    return this.fetchWithAuth<{
      message: string;
      new_status: string;
      case_id: string;
    }>(`/cases/${caseId}/value-projection/approve`, {
      method: 'POST',
    });
  }

  async rejectValueProjection(
    caseId: string,
    reason?: string
  ): Promise<{ message: string; new_status: string; case_id: string }> {
    const requestBody = reason ? { reason } : {};
    return this.fetchWithAuth<{
      message: string;
      new_status: string;
      case_id: string;
    }>(`/cases/${caseId}/value-projection/reject`, {
      method: 'POST',
      body: JSON.stringify(requestBody),
    });
  }

  // ============================
  // FINAL BUSINESS CASE APPROVAL METHODS
  // ============================

  async submitCaseForFinalApproval(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }> {
    return this.fetchWithAuth<{
      message: string;
      new_status: string;
      case_id: string;
    }>(`/cases/${caseId}/submit-final`, {
      method: 'POST',
    });
  }

  async approveFinalCase(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }> {
    return this.fetchWithAuth<{
      message: string;
      new_status: string;
      case_id: string;
    }>(`/cases/${caseId}/approve-final`, {
      method: 'POST',
    });
  }

  async rejectFinalCase(
    caseId: string,
    reason?: string
  ): Promise<{ message: string; new_status: string; case_id: string }> {
    const requestBody = reason ? { reason } : {};
    return this.fetchWithAuth<{
      message: string;
      new_status: string;
      case_id: string;
    }>(`/cases/${caseId}/reject-final`, {
      method: 'POST',
      body: JSON.stringify(requestBody),
    });
  }

  async exportCaseToPdf(caseId: string): Promise<Blob> {
    logger.debug('Requesting PDF export for case:', caseId);

    const authHeaders = await this.getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/cases/${caseId}/export-pdf`, {
      method: 'GET',
      headers: {
        Authorization: typeof authHeaders === 'object' && authHeaders && 'Authorization' in authHeaders 
          ? String(authHeaders.Authorization) 
          : '',
      },
    });

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch (e) {
        // If response is not JSON, use status text
        errorData = { detail: response.statusText };
      }
      throw new Error(
        `PDF export failed with status ${response.status}: ${
          errorData?.detail || 'Unknown error'
        }`
      );
    }

    logger.debug('PDF export successful, returning blob');
    return response.blob();
  }

  // ===== ENHANCED AGENT METHODS =====

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  async regeneratePrd(_caseId: string, _feedback?: string): Promise<import('./AgentService').EnhancedAgentResponse> {
    // TODO: Implement PRD regeneration with enhanced error handling
    return {
      success: false,
      message: 'PRD regeneration not yet implemented',
      errors: [{
        code: 'NOT_IMPLEMENTED',
        message: 'This feature is planned for future release'
      }],
      metadata: {
        operation_id: `regen-prd-${Date.now()}`,
        agent_version: '1.0.0'
      }
    };
  }

  async regenerateSystemDesign(
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    _caseId: string,
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    _feedback?: string,
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    _onProgress?: (progress: import('./AgentService').AgentProgress) => void
  ): Promise<import('./AgentService').EnhancedAgentResponse> {
    // TODO: Implement system design regeneration with progress tracking
    return {
      success: false,
      message: 'System design regeneration not yet implemented',
      errors: [{
        code: 'NOT_IMPLEMENTED',
        message: 'This feature is planned for future release'
      }],
      metadata: {
        operation_id: `regen-design-${Date.now()}`,
        agent_version: '1.0.0'
      }
    };
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  async regenerateFinancialEstimates(_caseId: string): Promise<import('./AgentService').EnhancedAgentResponse> {
    // TODO: Implement financial estimates regeneration
    return {
      success: false,
      message: 'Financial estimates regeneration not yet implemented',
      errors: [{
        code: 'NOT_IMPLEMENTED',
        message: 'This feature is planned for future release'
      }],
      metadata: {
        operation_id: `regen-financial-${Date.now()}`,
        agent_version: '1.0.0'
      }
    };
  }

  async getOperationStatus(operationId: string): Promise<import('./AgentService').AgentProgress> {
    // TODO: Implement operation status tracking
    return {
      operation_id: operationId,
      status: 'failed',
      progress_percentage: 0,
      current_step: 'Not implemented',
      error: 'Operation status tracking not yet implemented'
    };
  }

  async cancelOperation(operationId: string): Promise<boolean> {
    // TODO: Implement operation cancellation
    console.warn(`Operation cancellation not yet implemented for operation: ${operationId}`);
    return false;
  }

  async triggerEffortEstimateGeneration(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }> {
    return this.fetchWithAuth<{
      message: string;
      new_status: string;
      case_id: string;
    }>(`/cases/${caseId}/effort-estimate/generate`, {
      method: 'POST',
    });
  }

  async triggerCostAnalysisGeneration(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }> {
    return this.fetchWithAuth<{
      message: string;
      new_status: string;
      case_id: string;
    }>(`/cases/${caseId}/cost-analysis/generate`, {
      method: 'POST',
    });
  }

  async triggerValueAnalysisGeneration(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }> {
    return this.fetchWithAuth<{
      message: string;
      new_status: string;
      case_id: string;
    }>(`/cases/${caseId}/value-analysis/generate`, {
      method: 'POST',
    });
  }

  async triggerFinancialModelGeneration(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }> {
    return this.fetchWithAuth<{
      message: string;
      new_status: string;
      case_id: string;
    }>(`/cases/${caseId}/financial-model/generate`, {
      method: 'POST',
    });
  }

  async submitFinancialModelForReview(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }> {
    return this.fetchWithAuth<{
      message: string;
      new_status: string;
      case_id: string;
    }>(`/cases/${caseId}/financial-model/submit-review`, {
      method: 'POST',
    });
  }

  async approveFinancialModel(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }> {
    return this.fetchWithAuth<{
      message: string;
      new_status: string;
      case_id: string;
    }>(`/cases/${caseId}/financial-model/approve`, {
      method: 'POST',
    });
  }

  async rejectFinancialModel(
    caseId: string,
    reason?: string
  ): Promise<{ message: string; new_status: string; case_id: string }> {
    const body = reason ? JSON.stringify({ reason }) : undefined;
    return this.fetchWithAuth<{
      message: string;
      new_status: string;
      case_id: string;
    }>(`/cases/${caseId}/financial-model/reject`, {
      method: 'POST',
      body,
    });
  }
}

// Export an instance if you prefer a singleton pattern for services
// export const httpAgentService = new HttpAgentAdapter();
