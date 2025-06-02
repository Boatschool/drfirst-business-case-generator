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

  // Potential future methods:
  // getCaseHistory(caseId: string): Promise<AgentUpdate[]>;
  // getCaseStatus(caseId: string): Promise<string>; // More detailed status object
  // listCases(userId: string): Promise<Array<{caseId: string, title: string, status: string}>>;
} 