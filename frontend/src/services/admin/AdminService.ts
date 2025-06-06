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
    [key: string]: unknown; // Allow additional properties
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

// Request types for Pricing Template operations
export interface CreatePricingTemplateRequest {
  name: string;
  description: string;
  version: string;
  structureDefinition: {
    type?: string;
    scenarios?: Array<{
      case: string;
      value: number;
      description: string;
    }>;
    [key: string]: unknown; // Allow additional properties
  };
}

export interface UpdatePricingTemplateRequest {
  name?: string;
  description?: string;
  version?: string;
  structureDefinition?: {
    type?: string;
    scenarios?: Array<{
      case: string;
      value: number;
      description: string;
    }>;
    [key: string]: unknown; // Allow additional properties
  };
}

// Add User interface near the top with other interfaces
export interface User {
  uid: string;
  email: string;
  display_name?: string;
  systemRole?: string;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
  last_login?: string;
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
  updateRateCard(
    cardId: string,
    data: UpdateRateCardRequest
  ): Promise<RateCard>;

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

  /**
   * Create a new pricing template
   * @param data Pricing template data to create
   * @returns Promise<PricingTemplate> Created pricing template with ID
   */
  createPricingTemplate(
    data: CreatePricingTemplateRequest
  ): Promise<PricingTemplate>;

  /**
   * Update an existing pricing template
   * @param templateId ID of the pricing template to update
   * @param data Partial pricing template data to update
   * @returns Promise<PricingTemplate> Updated pricing template
   */
  updatePricingTemplate(
    templateId: string,
    data: UpdatePricingTemplateRequest
  ): Promise<PricingTemplate>;

  /**
   * Delete a pricing template
   * @param templateId ID of the pricing template to delete
   * @returns Promise<void>
   */
  deletePricingTemplate(templateId: string): Promise<void>;

  /**
   * Fetch all users from the backend (admin only)
   * @returns Promise<User[]> List of users with their system roles
   */
  listUsers(): Promise<User[]>;

  /**
   * Get the global final approver role setting
   * @returns Promise<{ finalApproverRoleName: string }> Current final approver role configuration
   */
  getFinalApproverRoleSetting(): Promise<{ finalApproverRoleName: string; updatedAt?: string; description?: string }>;

  /**
   * Set the global final approver role setting
   * @param roleName System role name to use for final approvals
   * @returns Promise<{ finalApproverRoleName: string }> Updated final approver role configuration
   */
  setFinalApproverRoleSetting(roleName: string): Promise<{ finalApproverRoleName: string; updatedAt?: string; description?: string }>;
}
