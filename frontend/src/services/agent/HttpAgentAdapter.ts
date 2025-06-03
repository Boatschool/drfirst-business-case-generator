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
} from './AgentService';

// Use environment variable for API base URL
const API_BASE_URL = `${import.meta.env.VITE_API_BASE_URL}/api/${import.meta.env.VITE_API_VERSION}`;

console.log('🔗 HttpAgentAdapter using API_BASE_URL:', API_BASE_URL);

export class HttpAgentAdapter implements AgentService {
  private async getAuthHeaders(): Promise<HeadersInit> {
    console.log('🔑 Getting auth headers...');
    const token = await authService.getIdToken();
    console.log('🎫 Token received:', token ? `${token.substring(0, 20)}...` : 'NULL');
    
    if (!token) {
      throw new Error('User not authenticated. Cannot make API call.');
    }
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    };
  }

  private async fetchWithAuth<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
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
      throw new Error(
        `API request failed with status ${response.status}: ${errorData?.detail || 'Unknown error'}`
      );
    }
    return response.json() as Promise<T>;
  }

  async initiateCase(payload: InitiateCasePayload): Promise<InitiateCaseResponse> {
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

  async updateStatus(payload: UpdateStatusPayload): Promise<UpdateStatusResponse> {
    const { caseId, ...requestBody } = payload;
    return this.fetchWithAuth<UpdateStatusResponse>(`/cases/${caseId}/status`, {
      method: 'PUT',
      body: JSON.stringify(requestBody),
    });
  }

  async submitPrdForReview(caseId: string): Promise<{ message: string; new_status: string; case_id: string }> {
    return this.fetchWithAuth<{ message: string; new_status: string; case_id: string }>(`/cases/${caseId}/submit-prd`, {
      method: 'POST',
    });
  }
}

// Export an instance if you prefer a singleton pattern for services
// export const httpAgentService = new HttpAgentAdapter(); 