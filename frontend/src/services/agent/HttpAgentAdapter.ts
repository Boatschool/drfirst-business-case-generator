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

// Use environment variable for API base URL
const API_BASE_URL = `${import.meta.env.VITE_API_BASE_URL}/api/${
  import.meta.env.VITE_API_VERSION
}`;

console.log('🔗 HttpAgentAdapter using API_BASE_URL:', API_BASE_URL);

export class HttpAgentAdapter implements AgentService {
  private async getAuthHeaders(): Promise<HeadersInit> {
    console.log('🔑 Getting auth headers...');
    try {
      const token = await authService.getIdToken();
      console.log(
        '🎫 Token received:',
        token ? `${token.substring(0, 20)}...` : 'NULL'
      );

      if (!token) {
        const authError = new Error('Authentication required');
        (authError as any).code = 'auth/no-token';
        throw authError;
      }
      
      return {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      };
    } catch (error) {
      // Enhance auth errors with better context
      if (error instanceof Error) {
        const authError = new Error(error.message || 'Authentication failed');
        (authError as any).code = error.message?.includes('expired') ? 'auth/token-expired' : 'auth/failed';
        throw authError;
      }
      throw error;
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
        
        // Create enhanced error object with status and context
        const error = new Error(errorData?.detail || 'Unknown error');
        (error as any).status = response.status;
        (error as any).endpoint = endpoint;
        (error as any).method = options.method || 'GET';
        
        throw error;
      }
      return response.json() as Promise<T>;
    } catch (error) {
      // Handle network errors and other exceptions
      if (error instanceof TypeError && error.message.includes('fetch')) {
        const networkError = new Error('Network connection failed');
        (networkError as any).name = 'NetworkError';
        (networkError as any).endpoint = endpoint;
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
    await this.fetchWithAuth<any>('/agents/invoke', {
      method: 'POST',
      body: JSON.stringify(requestPayload),
    });
    // If the backend returns a specific structure, we can map it or adjust the return type.
  }

  onAgentUpdate(
    caseId: string,
    _onUpdateCallback: (update: AgentUpdate) => void
  ): () => void {
    console.warn(
      `HttpAgentAdapter.onAgentUpdate for case ${caseId} is not implemented for real-time updates. Polling or WebSocket would be needed.`
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
        console.error("Polling for agent updates failed:", error);
        // Potentially call onUpdateCallback with an error update
      }
    }, 5000); // Poll every 5 seconds
    return () => clearInterval(intervalId);
    */
    return () => {}; // Return a no-op unsubscribe function
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
  ): Promise<{ message: string; updated_system_design: any }> {
    const requestBody = { content_markdown: content };
    return this.fetchWithAuth<{ message: string; updated_system_design: any }>(
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
    console.log('🔄 Requesting PDF export for case:', caseId);

    const authHeaders = await this.getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/cases/${caseId}/export-pdf`, {
      method: 'GET',
      headers: {
        Authorization: (authHeaders as any)['Authorization'],
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

    console.log('✅ PDF export successful, returning blob');
    return response.blob();
  }
}

// Export an instance if you prefer a singleton pattern for services
// export const httpAgentService = new HttpAgentAdapter();
