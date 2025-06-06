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
import { AppError, NetworkError } from '../../types/api';
import Logger from '../../utils/logger';

export class HttpAdminAdapter implements AdminService {
  private readonly apiBaseUrl: string;
  private logger = Logger.create('HttpAdminAdapter');

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
        const authError: AppError = {
          name: 'AuthError',
          message: 'Authentication required',
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
      this.logger.error('[HttpAdminAdapter] Error getting auth headers:', error);
      const authError: AppError = {
        name: 'AuthError',
        message: 'Authentication failed',
        type: 'auth',
        code: 'auth/failed',
        details: error
      };
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
        let errorCode: string | undefined;
        let errorDetails: any = undefined;
        
        try {
          const errorData = await response.json();
          
          if (errorData?.error) {
            // New standardized format: { error: { message, error_code, details } }
            errorMessage = errorData.error.message || errorMessage;
            errorCode = errorData.error.error_code;
            errorDetails = errorData.error.details;
          } else if (errorData?.detail) {
            // Legacy format: { detail: "message" }
            errorMessage = errorData.detail;
          }
        } catch (parseError) {
          // If we can't parse the error response, use the status text
         this.logger.warn(
            '[HttpAdminAdapter] Could not parse error response:',
            parseError
          );
        }
        
        // Create enhanced error object with status and context
        const error: AppError = {
          name: 'ApiError',
          message: errorMessage,
          type: 'api',
          status: response.status,
          details: {
            url,
            method: options.method || 'GET',
            errorCode,
            serverDetails: errorDetails
          }
        };
        
        throw error;
      }

      return response.json();
    } catch (error) {
      // Handle network errors and other exceptions
      if (error instanceof TypeError && error.message.includes('fetch')) {
        const networkError: NetworkError = {
          name: 'NetworkError',
          message: 'Network connection failed',
          url
        };
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
     this.logger.debug('[HttpAdminAdapter] Fetching rate cards...');
      const rateCards = await this.fetchWithAuth<RateCard[]>(
        `${this.apiBaseUrl}/admin/rate-cards`
      );
     this.logger.debug(
        `[HttpAdminAdapter] Successfully fetched ${rateCards.length} rate cards`
      );
      return rateCards;
    } catch (error) {
     this.logger.error('[HttpAdminAdapter] Error fetching rate cards:', error);
      throw error;
    }
  }

  /**
   * Create a new rate card
   */
  async createRateCard(data: CreateRateCardRequest): Promise<RateCard> {
    try {
     this.logger.debug('[HttpAdminAdapter] Creating rate card:', data.name);
      const createdRateCard = await this.fetchWithAuth<RateCard>(
        `${this.apiBaseUrl}/admin/rate-cards`,
        {
          method: 'POST',
          body: JSON.stringify(data),
        }
      );
     this.logger.debug(
        `[HttpAdminAdapter] Successfully created rate card: ${createdRateCard.id}`
      );
      return createdRateCard;
    } catch (error) {
     this.logger.error('[HttpAdminAdapter] Error creating rate card:', error);
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
     this.logger.debug('[HttpAdminAdapter] Updating rate card:', cardId);
      const updatedRateCard = await this.fetchWithAuth<RateCard>(
        `${this.apiBaseUrl}/admin/rate-cards/${cardId}`,
        {
          method: 'PUT',
          body: JSON.stringify(data),
        }
      );
     this.logger.debug(
        `[HttpAdminAdapter] Successfully updated rate card: ${cardId}`
      );
      return updatedRateCard;
    } catch (error) {
     this.logger.error('[HttpAdminAdapter] Error updating rate card:', error);
      throw error;
    }
  }

  /**
   * Delete a rate card
   */
  async deleteRateCard(cardId: string): Promise<void> {
    try {
     this.logger.debug('[HttpAdminAdapter] Deleting rate card:', cardId);
      await this.fetchWithAuth<{ message: string; deleted_id: string }>(
        `${this.apiBaseUrl}/admin/rate-cards/${cardId}`,
        {
          method: 'DELETE',
        }
      );
     this.logger.debug(
        `[HttpAdminAdapter] Successfully deleted rate card: ${cardId}`
      );
    } catch (error) {
     this.logger.error('[HttpAdminAdapter] Error deleting rate card:', error);
      throw error;
    }
  }

  /**
   * Fetch all pricing templates from the backend
   */
  async listPricingTemplates(): Promise<PricingTemplate[]> {
    try {
     this.logger.debug('[HttpAdminAdapter] Fetching pricing templates...');
      const pricingTemplates = await this.fetchWithAuth<PricingTemplate[]>(
        `${this.apiBaseUrl}/admin/pricing-templates`
      );
     this.logger.debug(
        `[HttpAdminAdapter] Successfully fetched ${pricingTemplates.length} pricing templates`
      );
      return pricingTemplates;
    } catch (error) {
     this.logger.error(
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
     this.logger.debug('[HttpAdminAdapter] Creating pricing template:', data.name);
      const createdTemplate = await this.fetchWithAuth<PricingTemplate>(
        `${this.apiBaseUrl}/admin/pricing-templates`,
        {
          method: 'POST',
          body: JSON.stringify(data),
        }
      );
     this.logger.debug(
        `[HttpAdminAdapter] Successfully created pricing template: ${createdTemplate.id}`
      );
      return createdTemplate;
    } catch (error) {
     this.logger.error(
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
     this.logger.debug('[HttpAdminAdapter] Updating pricing template:', templateId);
      const updatedTemplate = await this.fetchWithAuth<PricingTemplate>(
        `${this.apiBaseUrl}/admin/pricing-templates/${templateId}`,
        {
          method: 'PUT',
          body: JSON.stringify(data),
        }
      );
     this.logger.debug(
        `[HttpAdminAdapter] Successfully updated pricing template: ${templateId}`
      );
      return updatedTemplate;
    } catch (error) {
     this.logger.error(
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
     this.logger.debug('[HttpAdminAdapter] Deleting pricing template:', templateId);
      await this.fetchWithAuth<{ message: string; deleted_id: string }>(
        `${this.apiBaseUrl}/admin/pricing-templates/${templateId}`,
        {
          method: 'DELETE',
        }
      );
     this.logger.debug(
        `[HttpAdminAdapter] Successfully deleted pricing template: ${templateId}`
      );
    } catch (error) {
     this.logger.error(
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
     this.logger.debug('[HttpAdminAdapter] Fetching users...');
      const users = await this.fetchWithAuth<User[]>(
        `${this.apiBaseUrl}/admin/users`
      );
     this.logger.debug(
        `[HttpAdminAdapter] Successfully fetched ${users.length} users`
      );
      return users;
    } catch (error) {
     this.logger.error('[HttpAdminAdapter] Error fetching users:', error);
      throw error;
    }
  }

  /**
   * Get the global final approver role setting
   */
  async getFinalApproverRoleSetting(): Promise<{ finalApproverRoleName: string; updatedAt?: string; description?: string }> {
    try {
     this.logger.debug('[HttpAdminAdapter] Fetching final approver role setting...');
      const config = await this.fetchWithAuth<{ finalApproverRoleName: string; updatedAt?: string; description?: string }>(
        `${this.apiBaseUrl}/admin/config/final-approver-role`
      );
     this.logger.debug(
        `[HttpAdminAdapter] Successfully fetched final approver role: ${config.finalApproverRoleName}`
      );
      return config;
    } catch (error) {
     this.logger.error('[HttpAdminAdapter] Error fetching final approver role setting:', error);
      throw error;
    }
  }

  /**
   * Set the global final approver role setting
   */
  async setFinalApproverRoleSetting(roleName: string): Promise<{ finalApproverRoleName: string; updatedAt?: string; description?: string }> {
    try {
     this.logger.debug('[HttpAdminAdapter] Setting final approver role to:', roleName);
      const config = await this.fetchWithAuth<{ finalApproverRoleName: string; updatedAt?: string; description?: string }>(
        `${this.apiBaseUrl}/admin/config/final-approver-role`,
        {
          method: 'PUT',
          body: JSON.stringify({ finalApproverRoleName: roleName }),
        }
      );
     this.logger.debug(
        `[HttpAdminAdapter] Successfully set final approver role to: ${config.finalApproverRoleName}`
      );
      return config;
    } catch (error) {
     this.logger.error('[HttpAdminAdapter] Error setting final approver role:', error);
      throw error;
    }
  }
}
