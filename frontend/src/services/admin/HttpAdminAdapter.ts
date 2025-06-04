/**
 * HTTP implementation of AdminService interface
 * Handles authenticated requests to the backend admin endpoints
 */

import { AdminService, RateCard, PricingTemplate } from './AdminService';
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
    const token = await authService.getIdToken();
    if (!token) {
      throw new Error('No authentication token available');
    }
    
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    };
  }

  /**
   * Generic authenticated fetch method
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
      let errorMessage = `HTTP error! status: ${response.status}`;
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch {
        // If response is not JSON, use the default error message
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
   * Fetch all pricing templates from the backend
   */
  async listPricingTemplates(): Promise<PricingTemplate[]> {
    try {
      console.log('[HttpAdminAdapter] Fetching pricing templates...');
      const templates = await this.fetchWithAuth<PricingTemplate[]>(`${this.apiBaseUrl}/admin/pricing-templates`);
      console.log(`[HttpAdminAdapter] Successfully fetched ${templates.length} pricing templates`);
      return templates;
    } catch (error) {
      console.error('[HttpAdminAdapter] Error fetching pricing templates:', error);
      throw error;
    }
  }
} 