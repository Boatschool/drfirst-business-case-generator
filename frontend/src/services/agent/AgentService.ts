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
  messageType: 'TEXT' | 'PROMPT' | 'PRD_DRAFT' | 'SYSTEM_DESIGN_DRAFT' | 'STATUS_UPDATE' | 'ERROR'; // Type of update
  content: any; // Flexible content based on messageType (e.g., string for TEXT, object for DRAFT)
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
 * Represents the full details of a business case.
 */
export interface BusinessCaseDetails extends BusinessCaseSummary {
  problem_statement: string;
  relevant_links: Array<{ name: string; url: string }>;
  history: AgentUpdate[]; // Re-using AgentUpdate for history items
  prd_draft?: { // Assuming prd_draft structure from OrchestratorAgent
    title: string;
    content_markdown: string;
    version: string;
  } | null;
  // Add other fields as they are defined, e.g., system_design_draft, financial_model
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
  updated_prd_draft: { // This should match the structure returned by the backend
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
  onAgentUpdate(caseId: string, onUpdateCallback: (update: AgentUpdate) => void): () => void;

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
  submitPrdForReview(caseId: string): Promise<{ message: string; new_status: string; case_id: string }>;

  /**
   * Approves the PRD for a business case.
   * @param caseId - The ID of the business case to approve.
   * @returns A promise that resolves with a confirmation message and the new status.
   */
  approvePrd(caseId: string): Promise<{ message: string; new_status: string; case_id: string }>;

  /**
   * Rejects the PRD for a business case with an optional reason.
   * @param caseId - The ID of the business case to reject.
   * @param reason - Optional rejection reason.
   * @returns A promise that resolves with a confirmation message and the new status.
   */
  rejectPrd(caseId: string, reason?: string): Promise<{ message: string; new_status: string; case_id: string }>;

  // Potential future methods:
  // getCaseHistory(caseId: string): Promise<AgentUpdate[]>;
  // getCaseStatus(caseId: string): Promise<string>; // More detailed status object
  // listCases(userId: string): Promise<Array<{caseId: string, title: string, status: string}>>;
} 