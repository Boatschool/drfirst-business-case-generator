/**
 * HTTP implementation of AdminService interface
 * Handles authenticated requests to the backend admin endpoints
 */

import {
  AdminService,
  RateCard,
  PricingTemplate,
  CreateRateCardRequest,
  UpdateRateCardRequest,
  CreatePricingTemplateRequest,
  UpdatePricingTemplateRequest,
  User,
} from './AdminService';
import { authService } from '../auth/authService';

export class HttpAdminAdapter implements AdminService {
  private readonly apiBaseUrl: string;

  constructor() {
    // Use environment variable with fallback for development
    this.apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
  }

  /**
   * Get authentication headers with Firebase ID token
   */
  private async getAuthHeaders(): Promise<Record<string, string>> {
    try {
      const idToken = await authService.getIdToken();
      if (!idToken) {
        const authError = new Error('Authentication required');
        (authError as any).code = 'auth/no-token';
        throw authError;
      }
      return {
        Authorization: `Bearer ${idToken}`,
        'Content-Type': 'application/json',
      };
    } catch (error) {
      console.error('[HttpAdminAdapter] Error getting auth headers:', error);
      const authError = new Error('Authentication failed');
      (authError as any).code = 'auth/failed';
      (authError as any).originalError = error;
      throw authError;
    }
  }

  /**
   * Generic method to make authenticated requests
   */
  private async fetchWithAuth<T>(
    url: string,
    options: RequestInit = {}
  ): Promise<T> {
    try {
      const headers = await this.getAuthHeaders();

      const response = await fetch(url, {
        ...options,
        headers: {
          ...headers,
          ...options.headers,
        },
      });

      if (!response.ok) {
        let errorMessage = response.statusText || 'Unknown error';
        try {
          const errorData = await response.json();
          if (errorData.detail) {
            errorMessage = errorData.detail;
          }
        } catch (parseError) {
          // If we can't parse the error response, use the status text
          console.warn(
            '[HttpAdminAdapter] Could not parse error response:',
            parseError
          );
        }
        
        // Create enhanced error object with status and context
        const error = new Error(errorMessage);
        (error as any).status = response.status;
        (error as any).url = url;
        (error as any).method = options.method || 'GET';
        
        throw error;
      }

      return response.json();
    } catch (error) {
      // Handle network errors and other exceptions
      if (error instanceof TypeError && error.message.includes('fetch')) {
        const networkError = new Error('Network connection failed');
        (networkError as any).name = 'NetworkError';
        (networkError as any).url = url;
        throw networkError;
      }
      
      // Re-throw errors with additional context
      throw error;
    }
  }

  /**
   * Fetch all rate cards from the backend
   */
  async listRateCards(): Promise<RateCard[]> {
    try {
      console.log('[HttpAdminAdapter] Fetching rate cards...');
      const rateCards = await this.fetchWithAuth<RateCard[]>(
        `${this.apiBaseUrl}/admin/rate-cards`
      );
      console.log(
        `[HttpAdminAdapter] Successfully fetched ${rateCards.length} rate cards`
      );
      return rateCards;
    } catch (error) {
      console.error('[HttpAdminAdapter] Error fetching rate cards:', error);
      throw error;
    }
  }

  /**
   * Create a new rate card
   */
  async createRateCard(data: CreateRateCardRequest): Promise<RateCard> {
    try {
      console.log('[HttpAdminAdapter] Creating rate card:', data.name);
      const createdRateCard = await this.fetchWithAuth<RateCard>(
        `${this.apiBaseUrl}/admin/rate-cards`,
        {
          method: 'POST',
          body: JSON.stringify(data),
        }
      );
      console.log(
        `[HttpAdminAdapter] Successfully created rate card: ${createdRateCard.id}`
      );
      return createdRateCard;
    } catch (error) {
      console.error('[HttpAdminAdapter] Error creating rate card:', error);
      throw error;
    }
  }

  /**
   * Update an existing rate card
   */
  async updateRateCard(
    cardId: string,
    data: UpdateRateCardRequest
  ): Promise<RateCard> {
    try {
      console.log('[HttpAdminAdapter] Updating rate card:', cardId);
      const updatedRateCard = await this.fetchWithAuth<RateCard>(
        `${this.apiBaseUrl}/admin/rate-cards/${cardId}`,
        {
          method: 'PUT',
          body: JSON.stringify(data),
        }
      );
      console.log(
        `[HttpAdminAdapter] Successfully updated rate card: ${cardId}`
      );
      return updatedRateCard;
    } catch (error) {
      console.error('[HttpAdminAdapter] Error updating rate card:', error);
      throw error;
    }
  }

  /**
   * Delete a rate card
   */
  async deleteRateCard(cardId: string): Promise<void> {
    try {
      console.log('[HttpAdminAdapter] Deleting rate card:', cardId);
      await this.fetchWithAuth<{ message: string; deleted_id: string }>(
        `${this.apiBaseUrl}/admin/rate-cards/${cardId}`,
        {
          method: 'DELETE',
        }
      );
      console.log(
        `[HttpAdminAdapter] Successfully deleted rate card: ${cardId}`
      );
    } catch (error) {
      console.error('[HttpAdminAdapter] Error deleting rate card:', error);
      throw error;
    }
  }

  /**
   * Fetch all pricing templates from the backend
   */
  async listPricingTemplates(): Promise<PricingTemplate[]> {
    try {
      console.log('[HttpAdminAdapter] Fetching pricing templates...');
      const pricingTemplates = await this.fetchWithAuth<PricingTemplate[]>(
        `${this.apiBaseUrl}/admin/pricing-templates`
      );
      console.log(
        `[HttpAdminAdapter] Successfully fetched ${pricingTemplates.length} pricing templates`
      );
      return pricingTemplates;
    } catch (error) {
      console.error(
        '[HttpAdminAdapter] Error fetching pricing templates:',
        error
      );
      throw error;
    }
  }

  /**
   * Create a new pricing template
   */
  async createPricingTemplate(
    data: CreatePricingTemplateRequest
  ): Promise<PricingTemplate> {
    try {
      console.log('[HttpAdminAdapter] Creating pricing template:', data.name);
      const createdTemplate = await this.fetchWithAuth<PricingTemplate>(
        `${this.apiBaseUrl}/admin/pricing-templates`,
        {
          method: 'POST',
          body: JSON.stringify(data),
        }
      );
      console.log(
        `[HttpAdminAdapter] Successfully created pricing template: ${createdTemplate.id}`
      );
      return createdTemplate;
    } catch (error) {
      console.error(
        '[HttpAdminAdapter] Error creating pricing template:',
        error
      );
      throw error;
    }
  }

  /**
   * Update an existing pricing template
   */
  async updatePricingTemplate(
    templateId: string,
    data: UpdatePricingTemplateRequest
  ): Promise<PricingTemplate> {
    try {
      console.log('[HttpAdminAdapter] Updating pricing template:', templateId);
      const updatedTemplate = await this.fetchWithAuth<PricingTemplate>(
        `${this.apiBaseUrl}/admin/pricing-templates/${templateId}`,
        {
          method: 'PUT',
          body: JSON.stringify(data),
        }
      );
      console.log(
        `[HttpAdminAdapter] Successfully updated pricing template: ${templateId}`
      );
      return updatedTemplate;
    } catch (error) {
      console.error(
        '[HttpAdminAdapter] Error updating pricing template:',
        error
      );
      throw error;
    }
  }

  /**
   * Delete a pricing template
   */
  async deletePricingTemplate(templateId: string): Promise<void> {
    try {
      console.log('[HttpAdminAdapter] Deleting pricing template:', templateId);
      await this.fetchWithAuth<{ message: string; deleted_id: string }>(
        `${this.apiBaseUrl}/admin/pricing-templates/${templateId}`,
        {
          method: 'DELETE',
        }
      );
      console.log(
        `[HttpAdminAdapter] Successfully deleted pricing template: ${templateId}`
      );
    } catch (error) {
      console.error(
        '[HttpAdminAdapter] Error deleting pricing template:',
        error
      );
      throw error;
    }
  }

  /**
   * Fetch all users from the backend (admin only)
   */
  async listUsers(): Promise<User[]> {
    try {
      console.log('[HttpAdminAdapter] Fetching users...');
      const users = await this.fetchWithAuth<User[]>(
        `${this.apiBaseUrl}/admin/users`
      );
      console.log(
        `[HttpAdminAdapter] Successfully fetched ${users.length} users`
      );
      return users;
    } catch (error) {
      console.error('[HttpAdminAdapter] Error fetching users:', error);
      throw error;
    }
  }

  /**
   * Get the global final approver role setting
   */
  async getFinalApproverRoleSetting(): Promise<{ finalApproverRoleName: string; updatedAt?: string; description?: string }> {
    try {
      console.log('[HttpAdminAdapter] Fetching final approver role setting...');
      const config = await this.fetchWithAuth<{ finalApproverRoleName: string; updatedAt?: string; description?: string }>(
        `${this.apiBaseUrl}/admin/config/final-approver-role`
      );
      console.log(
        `[HttpAdminAdapter] Successfully fetched final approver role: ${config.finalApproverRoleName}`
      );
      return config;
    } catch (error) {
      console.error('[HttpAdminAdapter] Error fetching final approver role setting:', error);
      throw error;
    }
  }

  /**
   * Set the global final approver role setting
   */
  async setFinalApproverRoleSetting(roleName: string): Promise<{ finalApproverRoleName: string; updatedAt?: string; description?: string }> {
    try {
      console.log('[HttpAdminAdapter] Setting final approver role to:', roleName);
      const config = await this.fetchWithAuth<{ finalApproverRoleName: string; updatedAt?: string; description?: string }>(
        `${this.apiBaseUrl}/admin/config/final-approver-role`,
        {
          method: 'PUT',
          body: JSON.stringify({ finalApproverRoleName: roleName }),
        }
      );
      console.log(
        `[HttpAdminAdapter] Successfully set final approver role to: ${config.finalApproverRoleName}`
      );
      return config;
    } catch (error) {
      console.error('[HttpAdminAdapter] Error setting final approver role:', error);
      throw error;
    }
  }
}
