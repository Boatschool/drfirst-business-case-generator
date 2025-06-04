/**
 * Admin Service Interface for DrFirst Business Case Generator
 * Handles admin operations for rate cards and pricing templates
 */

// Rate Card Interface
export interface RateCard {
  id: string;
  name: string;
  description: string;
  isActive: boolean;
  defaultOverallRate: number;
  roles: Array<{
    roleName: string;
    hourlyRate: number;
  }>;
  created_at: string;
  updated_at: string;
}

// Pricing Template Interface
export interface PricingTemplate {
  id: string;
  name: string;
  description: string;
  version: string;
  structureDefinition: {
    type: string;
    scenarios?: Array<{
      case: string;
      value: number;
      description: string;
    }>;
    [key: string]: any; // Allow additional properties
  };
  created_at: string;
  updated_at: string;
}

// Request types for Rate Card operations
export interface CreateRateCardRequest {
  name: string;
  description: string;
  isActive: boolean;
  defaultOverallRate: number;
  roles: Array<{
    roleName: string;
    hourlyRate: number;
  }>;
}

export interface UpdateRateCardRequest {
  name?: string;
  description?: string;
  isActive?: boolean;
  defaultOverallRate?: number;
  roles?: Array<{
    roleName: string;
    hourlyRate: number;
  }>;
}

/**
 * AdminService interface defines the contract for admin operations
 */
export interface AdminService {
  /**
   * Fetch all rate cards from the backend
   * @returns Promise<RateCard[]> List of rate cards
   */
  listRateCards(): Promise<RateCard[]>;

  /**
   * Create a new rate card
   * @param data Rate card data to create
   * @returns Promise<RateCard> Created rate card with ID
   */
  createRateCard(data: CreateRateCardRequest): Promise<RateCard>;

  /**
   * Update an existing rate card
   * @param cardId ID of the rate card to update
   * @param data Partial rate card data to update
   * @returns Promise<RateCard> Updated rate card
   */
  updateRateCard(cardId: string, data: UpdateRateCardRequest): Promise<RateCard>;

  /**
   * Delete a rate card
   * @param cardId ID of the rate card to delete
   * @returns Promise<void>
   */
  deleteRateCard(cardId: string): Promise<void>;

  /**
   * Fetch all pricing templates from the backend
   * @returns Promise<PricingTemplate[]> List of pricing templates
   */
  listPricingTemplates(): Promise<PricingTemplate[]>;
} 