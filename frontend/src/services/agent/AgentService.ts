/**
 * Represents the payload for initiating a new business case.
 */
export interface InitiateCasePayload {
  problemStatement: string;
  // Optional: Add other initial details like project title, relevant links (Confluence, Jira), etc.
  projectTitle?: string;
  relevantLinks?: Array<{ name: string; url: string }>;
}

/**
 * Represents the response from initiating a new business case.
 */
export interface InitiateCaseResponse {
  caseId: string; // Unique identifier for the newly created case
  initialMessage?: string; // Optional initial message from the agent
  // other relevant details about the created case
}

/**
 * Represents the payload for providing feedback or further input to an agent.
 */
export interface ProvideFeedbackPayload {
  caseId: string;
  message: string;
  // Optional: Add other structured data as needed for feedback
  // e.g., approvalStatus, editedField, etc.
}

/**
 * Represents an update or message from an agent during the business case lifecycle.
 */
export interface AgentUpdate {
  caseId: string;
  timestamp: string; // ISO 8601 timestamp
  source: 'USER' | 'AGENT'; // Who sent the message/update
  messageType:
    | 'TEXT'
    | 'PROMPT'
    | 'PRD_DRAFT'
    | 'SYSTEM_DESIGN_DRAFT'
    | 'STATUS_UPDATE'
    | 'ERROR'; // Type of update
  content: string | object; // Flexible content based on messageType (string for TEXT, object for DRAFT)
  requiresResponse?: boolean; // Does this update require user input?
}

/**
 * Represents a summary of a business case, typically for list views.
 */
export interface BusinessCaseSummary {
  case_id: string;
  user_id: string;
  title: string;
  status: string; // Matches the BusinessCaseStatus enum values from backend
  created_at: string; // ISO 8601 timestamp string
  updated_at: string; // ISO 8601 timestamp string
}

/**
 * Effort Estimate structure from PlannerAgent
 */
export interface EffortEstimate {
  roles: Array<{
    role: string;
    hours: number;
  }>;
  total_hours: number;
  estimated_duration_weeks: number;
  complexity_assessment: string;
  notes?: string;
}

/**
 * Cost Estimate structure from CostAnalystAgent
 */
export interface CostEstimate {
  estimated_cost: number;
  currency: string;
  rate_card_used?: string;
  rate_card_id?: string;
  breakdown_by_role: Array<{
    role: string;
    hours: number;
    hourly_rate: number;
    total_cost: number;
    currency: string;
    rate_source?: string;
  }>;
  calculation_method?: string;
  warnings?: string[];
  notes?: string;
}

/**
 * Value Projection Scenario from SalesValueAnalystAgent
 */
export interface ValueProjectionScenario {
  case: string; // e.g., "Low", "Base", "High"
  value: number;
  description?: string;
}

/**
 * Value Projection structure from SalesValueAnalystAgent
 */
export interface ValueProjection {
  scenarios: ValueProjectionScenario[];
  currency: string;
  template_used?: string;
  methodology?: string;
  assumptions?: string[];
  notes?: string;
}

/**
 * Financial Summary structure from FinancialModelAgent
 */
export interface FinancialSummary {
  total_estimated_cost: number;
  currency: string;
  value_scenarios: { [key: string]: number }; // e.g., { "Low": 75000, "Base": 175000, "High": 350000 }
  financial_metrics: {
    // Primary metrics for summary display
    primary_net_value: number;
    primary_roi_percentage: number | string;
    simple_payback_period_years: number | string;
    payback_period_note?: string;
    // Per-scenario metrics (dynamic keys)
    [key: string]: number | string | undefined;
  };
  cost_breakdown_source?: string; // e.g., "Default Development Rates V1"
  value_methodology?: string; // e.g., "AI-assisted healthcare value projection"
  notes?: string;
  generated_timestamp?: string; // ISO 8601 timestamp
}

/**
 * Represents the full details of a business case.
 */
export interface BusinessCaseDetails extends BusinessCaseSummary {
  problem_statement: string;
  relevant_links: Array<{ name: string; url: string }>;
  history: AgentUpdate[]; // Re-using AgentUpdate for history items
  prd_draft?: {
    // Assuming prd_draft structure from OrchestratorAgent
    title: string;
    content_markdown: string;
    version: string;
  } | null;
  system_design_v1_draft?: {
    // System design structure from ArchitectAgent
    content_markdown: string;
    generated_by: string;
    version: string;
    generated_at?: string;
    last_edited_by?: string;
    last_edited_at?: string;
  } | null;
  effort_estimate_v1?: EffortEstimate | null; // New: Effort estimate from PlannerAgent
  cost_estimate_v1?: CostEstimate | null; // New: Cost estimate from CostAnalystAgent
  value_projection_v1?: ValueProjection | null; // New: Value projection from SalesValueAnalystAgent
  financial_summary_v1?: FinancialSummary | null; // New: Financial summary from FinancialModelAgent
}

/**
 * Represents the payload for updating a PRD.
 */
export interface UpdatePrdPayload {
  caseId: string;
  content_markdown: string;
  // version?: string; // Optional: if client wants to suggest/send a version
}

/**
 * Represents the response from updating a PRD.
 */
export interface UpdatePrdResponse {
  message: string;
  updated_prd_draft: {
    // This should match the structure returned by the backend
    title: string;
    content_markdown: string;
    version: string;
  };
}

/**
 * Represents the payload for updating a business case status.
 */
export interface UpdateStatusPayload {
  caseId: string;
  status: string;
  comment?: string;
}

/**
 * Represents the response from updating a business case status.
 */
export interface UpdateStatusResponse {
  message: string;
  new_status: string;
  case_id: string;
}

/**
 * Defines the contract for agent communication services.
 */
export interface AgentService {
  /**
   * Initiates a new business case with the agent system.
   * @param payload - The initial details for the business case.
   * @returns A promise that resolves with details of the initiated case.
   */
  initiateCase(payload: InitiateCasePayload): Promise<InitiateCaseResponse>;

  /**
   * Sends feedback or further input to an agent for a specific business case.
   * @param payload - The feedback details.
   * @returns A promise that resolves when the feedback is successfully submitted.
   */
  provideFeedback(payload: ProvideFeedbackPayload): Promise<void>; // Or a more detailed response

  /**
   * Subscribes to real-time updates from the agent system for a specific business case.
   * @param caseId - The ID of the business case to listen for updates on.
   * @param onUpdateCallback - A callback function that will be invoked with each new AgentUpdate.
   * @returns A function to unsubscribe from updates.
   */
  onAgentUpdate(
    caseId: string,
    onUpdateCallback: (update: AgentUpdate) => void
  ): () => void;

  /**
   * Retrieves a list of business case summaries for the authenticated user.
   * @returns A promise that resolves with an array of business case summaries.
   */
  listCases(): Promise<BusinessCaseSummary[]>;

  /**
   * Retrieves the full details for a specific business case.
   * @param caseId - The ID of the business case to retrieve.
   * @returns A promise that resolves with the full details of the business case.
   */
  getCaseDetails(caseId: string): Promise<BusinessCaseDetails>;

  /**
   * Updates the PRD draft for a specific business case.
   * @param payload - The case ID and the new PRD content.
   * @returns A promise that resolves with a confirmation message and the updated PRD draft.
   */
  updatePrd(payload: UpdatePrdPayload): Promise<UpdatePrdResponse>;

  /**
   * Updates the status of a specific business case.
   * @param payload - The case ID, new status, and optional comment.
   * @returns A promise that resolves with a confirmation message and the new status.
   */
  updateStatus(payload: UpdateStatusPayload): Promise<UpdateStatusResponse>;

  /**
   * Submits the PRD for review, updating the case status to PRD_REVIEW.
   * @param caseId - The ID of the business case to submit for review.
   * @returns A promise that resolves with a confirmation message and the new status.
   */
  submitPrdForReview(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }>;

  /**
   * Approves the PRD for a business case.
   * @param caseId - The ID of the business case to approve.
   * @returns A promise that resolves with a confirmation message and the new status.
   */
  approvePrd(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }>;

  /**
   * Rejects the PRD for a business case with an optional reason.
   * @param caseId - The ID of the business case to reject.
   * @param reason - Optional rejection reason.
   * @returns A promise that resolves with a confirmation message and the new status.
   */
  rejectPrd(
    caseId: string,
    reason?: string
  ): Promise<{ message: string; new_status: string; case_id: string }>;

  /**
   * Updates the System Design draft for a specific business case.
   * @param caseId - The ID of the business case to update.
   * @param content - The new system design content in markdown.
   * @returns A promise that resolves with a confirmation message and the updated system design.
   */
  updateSystemDesign(
    caseId: string,
    content: string
  ): Promise<{ message: string; updated_system_design: unknown }>;

  /**
   * Submits the System Design for review, updating the case status to SYSTEM_DESIGN_PENDING_REVIEW.
   * @param caseId - The ID of the business case to submit for review.
   * @returns A promise that resolves with a confirmation message and the new status.
   */
  submitSystemDesignForReview(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }>;

  /**
   * Approves the System Design for a business case.
   * @param caseId - The ID of the business case to approve.
   * @returns A promise that resolves with a confirmation message and the new status.
   */
  approveSystemDesign(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }>;

  /**
   * Rejects the System Design for a business case with an optional reason.
   * @param caseId - The ID of the business case to reject.
   * @param reason - Optional rejection reason.
   * @returns A promise that resolves with a confirmation message and the new status.
   */
  rejectSystemDesign(
    caseId: string,
    reason?: string
  ): Promise<{ message: string; new_status: string; case_id: string }>;

  /**
   * Updates the Effort Estimate for a specific business case.
   * @param caseId - The ID of the business case to update.
   * @param data - The effort estimate data to update.
   * @returns A promise that resolves with a confirmation message and the updated effort estimate.
   */
  updateEffortEstimate(
    caseId: string,
    data: EffortEstimate
  ): Promise<{ message: string; updated_effort_estimate: EffortEstimate }>;

  /**
   * Submits the Effort Estimate for review, updating the case status to EFFORT_PENDING_REVIEW.
   * @param caseId - The ID of the business case to submit for review.
   * @returns A promise that resolves with a confirmation message and the new status.
   */
  submitEffortEstimateForReview(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }>;

  /**
   * Updates the Cost Estimate for a specific business case.
   * @param caseId - The ID of the business case to update.
   * @param data - The cost estimate data to update.
   * @returns A promise that resolves with a confirmation message and the updated cost estimate.
   */
  updateCostEstimate(
    caseId: string,
    data: CostEstimate
  ): Promise<{ message: string; updated_cost_estimate: CostEstimate }>;

  /**
   * Submits the Cost Estimate for review, updating the case status to COSTING_PENDING_REVIEW.
   * @param caseId - The ID of the business case to submit for review.
   * @returns A promise that resolves with a confirmation message and the new status.
   */
  submitCostEstimateForReview(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }>;

  /**
   * Updates the Value Projection for a specific business case.
   * @param caseId - The ID of the business case to update.
   * @param data - The value projection data to update.
   * @returns A promise that resolves with a confirmation message and the updated value projection.
   */
  updateValueProjection(
    caseId: string,
    data: ValueProjection
  ): Promise<{ message: string; updated_value_projection: ValueProjection }>;

  /**
   * Submits the Value Projection for review, updating the case status to VALUE_PENDING_REVIEW.
   * @param caseId - The ID of the business case to submit for review.
   * @returns A promise that resolves with a confirmation message and the new status.
   */
  submitValueProjectionForReview(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }>;

  /**
   * Approves the Effort Estimate for a business case.
   * @param caseId - The ID of the business case to approve.
   * @returns A promise that resolves with a confirmation message and the new status.
   */
  approveEffortEstimate(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }>;

  /**
   * Rejects the Effort Estimate for a business case with an optional reason.
   * @param caseId - The ID of the business case to reject.
   * @param reason - Optional rejection reason.
   * @returns A promise that resolves with a confirmation message and the new status.
   */
  rejectEffortEstimate(
    caseId: string,
    reason?: string
  ): Promise<{ message: string; new_status: string; case_id: string }>;

  /**
   * Approves the Cost Estimate for a business case.
   * @param caseId - The ID of the business case to approve.
   * @returns A promise that resolves with a confirmation message and the new status.
   */
  approveCostEstimate(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }>;

  /**
   * Rejects the Cost Estimate for a business case with an optional reason.
   * @param caseId - The ID of the business case to reject.
   * @param reason - Optional rejection reason.
   * @returns A promise that resolves with a confirmation message and the new status.
   */
  rejectCostEstimate(
    caseId: string,
    reason?: string
  ): Promise<{ message: string; new_status: string; case_id: string }>;

  /**
   * Approves the Value Projection for a business case.
   * @param caseId - The ID of the business case to approve.
   * @returns A promise that resolves with a confirmation message and the new status.
   */
  approveValueProjection(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }>;

  /**
   * Rejects the Value Projection for a business case with an optional reason.
   * @param caseId - The ID of the business case to reject.
   * @param reason - Optional rejection reason.
   * @returns A promise that resolves with a confirmation message and the new status.
   */
  rejectValueProjection(
    caseId: string,
    reason?: string
  ): Promise<{ message: string; new_status: string; case_id: string }>;

  // ============================
  // FINAL BUSINESS CASE APPROVAL METHODS
  // ============================

  /**
   * Submits the business case for final approval.
   * @param caseId - The ID of the business case to submit for final approval.
   * @returns A promise that resolves with a confirmation message and the new status.
   */
  submitCaseForFinalApproval(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }>;

  /**
   * Approves the final business case.
   * @param caseId - The ID of the business case to approve.
   * @returns A promise that resolves with a confirmation message and the new status.
   */
  approveFinalCase(
    caseId: string
  ): Promise<{ message: string; new_status: string; case_id: string }>;

  /**
   * Rejects the final business case with an optional reason.
   * @param caseId - The ID of the business case to reject.
   * @param reason - Optional rejection reason.
   * @returns A promise that resolves with a confirmation message and the new status.
   */
  rejectFinalCase(
    caseId: string,
    reason?: string
  ): Promise<{ message: string; new_status: string; case_id: string }>;

  /**
   * Exports the business case as a PDF document.
   * @param caseId - The ID of the business case to export.
   * @returns A promise that resolves with a Blob containing the PDF data.
   */
  exportCaseToPdf(caseId: string): Promise<Blob>;

  // Potential future methods:
  // getCaseHistory(caseId: string): Promise<AgentUpdate[]>;
  // getCaseStatus(caseId: string): Promise<string>; // More detailed status object
  // listCases(userId: string): Promise<Array<{caseId: string, title: string, status: string}>>;
}
