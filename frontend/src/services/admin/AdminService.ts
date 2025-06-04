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
   * Fetch all pricing templates from the backend
   * @returns Promise<PricingTemplate[]> List of pricing templates
   */
  listPricingTemplates(): Promise<PricingTemplate[]>;
} 