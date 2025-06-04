/**
 * HTTP implementation of AdminService interface
 * Handles authenticated requests to the backend admin endpoints
 */

import { AdminService, RateCard, PricingTemplate, CreateRateCardRequest, UpdateRateCardRequest, CreatePricingTemplateRequest, UpdatePricingTemplateRequest } from './AdminService';
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
      return {
        'Authorization': `Bearer ${idToken}`,
        'Content-Type': 'application/json',
      };
    } catch (error) {
      console.error('[HttpAdminAdapter] Error getting auth headers:', error);
      throw new Error('Authentication required. Please sign in again.');
    }
  }

  /**
   * Generic method to make authenticated requests
   */
  private async fetchWithAuth<T>(url: string, options: RequestInit = {}): Promise<T> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(url, {
      ...options,
      headers: {
        ...headers,
        ...options.headers,
      },
    });

    if (!response.ok) {
      let errorMessage = `HTTP Error: ${response.status} ${response.statusText}`;
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = errorData.detail;
        }
      } catch (parseError) {
        // If we can't parse the error response, use the status text
        console.warn('[HttpAdminAdapter] Could not parse error response:', parseError);
      }
      throw new Error(errorMessage);
    }

    return response.json();
  }

  /**
   * Fetch all rate cards from the backend
   */
  async listRateCards(): Promise<RateCard[]> {
    try {
      console.log('[HttpAdminAdapter] Fetching rate cards...');
      const rateCards = await this.fetchWithAuth<RateCard[]>(`${this.apiBaseUrl}/admin/rate-cards`);
      console.log(`[HttpAdminAdapter] Successfully fetched ${rateCards.length} rate cards`);
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
      const createdRateCard = await this.fetchWithAuth<RateCard>(`${this.apiBaseUrl}/admin/rate-cards`, {
        method: 'POST',
        body: JSON.stringify(data),
      });
      console.log(`[HttpAdminAdapter] Successfully created rate card: ${createdRateCard.id}`);
      return createdRateCard;
    } catch (error) {
      console.error('[HttpAdminAdapter] Error creating rate card:', error);
      throw error;
    }
  }

  /**
   * Update an existing rate card
   */
  async updateRateCard(cardId: string, data: UpdateRateCardRequest): Promise<RateCard> {
    try {
      console.log('[HttpAdminAdapter] Updating rate card:', cardId);
      const updatedRateCard = await this.fetchWithAuth<RateCard>(`${this.apiBaseUrl}/admin/rate-cards/${cardId}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
      console.log(`[HttpAdminAdapter] Successfully updated rate card: ${cardId}`);
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
      await this.fetchWithAuth<{ message: string; deleted_id: string }>(`${this.apiBaseUrl}/admin/rate-cards/${cardId}`, {
        method: 'DELETE',
      });
      console.log(`[HttpAdminAdapter] Successfully deleted rate card: ${cardId}`);
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
      const pricingTemplates = await this.fetchWithAuth<PricingTemplate[]>(`${this.apiBaseUrl}/admin/pricing-templates`);
      console.log(`[HttpAdminAdapter] Successfully fetched ${pricingTemplates.length} pricing templates`);
      return pricingTemplates;
    } catch (error) {
      console.error('[HttpAdminAdapter] Error fetching pricing templates:', error);
      throw error;
    }
  }

  /**
   * Create a new pricing template
   */
  async createPricingTemplate(data: CreatePricingTemplateRequest): Promise<PricingTemplate> {
    try {
      console.log('[HttpAdminAdapter] Creating pricing template:', data.name);
      const createdTemplate = await this.fetchWithAuth<PricingTemplate>(`${this.apiBaseUrl}/admin/pricing-templates`, {
        method: 'POST',
        body: JSON.stringify(data),
      });
      console.log(`[HttpAdminAdapter] Successfully created pricing template: ${createdTemplate.id}`);
      return createdTemplate;
    } catch (error) {
      console.error('[HttpAdminAdapter] Error creating pricing template:', error);
      throw error;
    }
  }

  /**
   * Update an existing pricing template
   */
  async updatePricingTemplate(templateId: string, data: UpdatePricingTemplateRequest): Promise<PricingTemplate> {
    try {
      console.log('[HttpAdminAdapter] Updating pricing template:', templateId);
      const updatedTemplate = await this.fetchWithAuth<PricingTemplate>(`${this.apiBaseUrl}/admin/pricing-templates/${templateId}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
      console.log(`[HttpAdminAdapter] Successfully updated pricing template: ${templateId}`);
      return updatedTemplate;
    } catch (error) {
      console.error('[HttpAdminAdapter] Error updating pricing template:', error);
      throw error;
    }
  }

  /**
   * Delete a pricing template
   */
  async deletePricingTemplate(templateId: string): Promise<void> {
    try {
      console.log('[HttpAdminAdapter] Deleting pricing template:', templateId);
      await this.fetchWithAuth<{ message: string; deleted_id: string }>(`${this.apiBaseUrl}/admin/pricing-templates/${templateId}`, {
        method: 'DELETE',
      });
      console.log(`[HttpAdminAdapter] Successfully deleted pricing template: ${templateId}`);
    } catch (error) {
      console.error('[HttpAdminAdapter] Error deleting pricing template:', error);
      throw error;
    }
  }
} 