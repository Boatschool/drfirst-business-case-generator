/* eslint-disable @typescript-eslint/no-explicit-any */
/**
 * Prompt Service Admin for managing agent prompts
 * Handles admin operations for agent prompts and versions
 */

import { auth } from '../../config/firebase';

// AgentPromptVersion Interface
export interface AgentPromptVersion {
  version: string;
  prompt_template: string;
  description: string;
  created_at: string;
  created_by: string;
  is_active: boolean;
  performance_notes?: string;
}

// AgentPrompt Interface
export interface AgentPrompt {
  prompt_id: string;
  agent_name: string;
  agent_function: string;
  current_version: string;
  versions: AgentPromptVersion[];
  title: string;
  description: string;
  category: string;
  placeholders: string[];
  ai_model_config: Record<string, any>;
  is_enabled: boolean;
  created_at: string;
  updated_at: string;
  created_by: string;
  last_updated_by: string;
  usage_count: number;
  last_used_at?: string;
}

// Request types for Prompt operations
export interface AgentPromptCreatePayload {
  agent_name: string;
  agent_function: string;
  title: string;
  description: string;
  prompt_template: string;
  category?: string;
  placeholders?: string[];
  ai_model_config?: Record<string, any>;
  version_description?: string;
}

export interface AgentPromptUpdatePayload {
  title?: string;
  description?: string;
  category?: string;
  is_enabled?: boolean;
  ai_model_config?: Record<string, any>;
}

export interface AgentPromptVersionCreatePayload {
  prompt_template: string;
  description: string;
  placeholders?: string[];
  ai_model_config?: Record<string, any>;
  make_active?: boolean;
}

export interface SetActiveVersionPayload {
  version: string;
}

/**
 * PromptServiceAdmin interface defines the contract for prompt admin operations
 */
export interface PromptServiceAdmin {
  /**
   * Fetch all prompts, optionally filtered by agent name
   * @param agentName Optional agent name filter
   * @returns Promise<AgentPrompt[]> List of agent prompts
   */
  listPrompts(agentName?: string): Promise<AgentPrompt[]>;

  /**
   * Get a specific prompt by ID
   * @param promptId ID of the prompt to fetch
   * @returns Promise<AgentPrompt> The agent prompt
   */
  getPrompt(promptId: string): Promise<AgentPrompt>;

  /**
   * Create a new agent prompt
   * @param data Prompt data to create
   * @returns Promise<{ prompt_id: string }> Created prompt response
   */
  createPrompt(data: AgentPromptCreatePayload): Promise<{ prompt_id: string }>;

  /**
   * Update an existing agent prompt
   * @param promptId ID of the prompt to update
   * @param data Partial prompt data to update
   * @returns Promise<void>
   */
  updatePrompt(promptId: string, data: AgentPromptUpdatePayload): Promise<void>;

  /**
   * Add a new version to an existing prompt
   * @param promptId ID of the prompt to add version to
   * @param data Version data to create
   * @returns Promise<void>
   */
  addPromptVersion(
    promptId: string,
    data: AgentPromptVersionCreatePayload
  ): Promise<void>;

  /**
   * Set the active version for a prompt
   * @param promptId ID of the prompt
   * @param version Version string to set as active
   * @returns Promise<void>  
   */
  setActivePromptVersion(promptId: string, version: string): Promise<void>;
}

/**
 * HTTP implementation of PromptServiceAdmin
 */
export class HttpPromptServiceAdmin implements PromptServiceAdmin {
  private readonly baseUrl: string;

  constructor() {
    this.baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  }

  private async getAuthHeaders(): Promise<Record<string, string>> {
    const user = auth.currentUser;
    if (!user) {
      throw new Error('User not authenticated');
    }

    const token = await user.getIdToken();
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    };
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorText = await response.text();
      let errorMessage: string;
      
      try {
        const errorJson = JSON.parse(errorText);
        errorMessage = errorJson.detail || errorJson.message || 'An error occurred';
      } catch {
        errorMessage = errorText || `HTTP ${response.status}: ${response.statusText}`;
      }
      
      throw new Error(errorMessage);
    }

    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return response.json();
    }
    
    return {} as T;
  }

  async listPrompts(agentName?: string): Promise<AgentPrompt[]> {
    const headers = await this.getAuthHeaders();
    const url = new URL(`${this.baseUrl}/api/v1/prompts/`);
    
    if (agentName) {
      url.searchParams.append('agent_name', agentName);
    }

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers,
    });

    return this.handleResponse<AgentPrompt[]>(response);
  }

  async getPrompt(promptId: string): Promise<AgentPrompt> {
    const headers = await this.getAuthHeaders();
    const response = await fetch(`${this.baseUrl}/api/v1/prompts/${promptId}`, {
      method: 'GET',
      headers,
    });

    return this.handleResponse<AgentPrompt>(response);
  }

  async createPrompt(data: AgentPromptCreatePayload): Promise<{ prompt_id: string }> {
    const headers = await this.getAuthHeaders();
    const response = await fetch(`${this.baseUrl}/api/v1/prompts/`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    });

    return this.handleResponse<{ prompt_id: string }>(response);
  }

  async updatePrompt(promptId: string, data: AgentPromptUpdatePayload): Promise<void> {
    const headers = await this.getAuthHeaders();
    const response = await fetch(`${this.baseUrl}/api/v1/prompts/${promptId}`, {
      method: 'PUT',
      headers,
      body: JSON.stringify(data),
    });

    await this.handleResponse<void>(response);
  }

  async addPromptVersion(
    promptId: string,
    data: AgentPromptVersionCreatePayload
  ): Promise<void> {
    const headers = await this.getAuthHeaders();
    const response = await fetch(`${this.baseUrl}/api/v1/prompts/${promptId}/versions`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    });

    await this.handleResponse<void>(response);
  }

  async setActivePromptVersion(promptId: string, version: string): Promise<void> {
    // Since the backend doesn't have a dedicated endpoint for setting active version directly,
    // and the update endpoint doesn't support changing current_version or version.is_active,
    // we need to use the add_prompt_version endpoint with make_active: true
    // to reactivate an existing version
    
    // First get the current prompt to find the target version
    const currentPrompt = await this.getPrompt(promptId);
    
    // Find the target version
    const targetVersion = currentPrompt.versions.find(v => v.version === version);
    if (!targetVersion) {
      throw new Error(`Version ${version} not found for prompt ${promptId}`);
    }

    // If it's already active, no need to do anything
    if (targetVersion.is_active && currentPrompt.current_version === version) {
      return;
    }

    // Re-add the version with make_active: true
    // This will deactivate other versions and set this one as active
    await this.addPromptVersion(promptId, {
      prompt_template: targetVersion.prompt_template,
      description: `Reactivated version ${version}`,
      placeholders: currentPrompt.placeholders,
      ai_model_config: currentPrompt.ai_model_config,
      make_active: true,
    });
  }
} 