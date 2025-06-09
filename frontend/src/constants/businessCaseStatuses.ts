/**
 * All possible business case status values from the backend BusinessCaseStatus enum.
 * This should be kept in sync with backend/app/agents/orchestrator_agent.py
 */
export const ALL_BUSINESS_CASE_STATUSES = [
  // Initial stages
  'INTAKE',
  'PRD_DRAFTING',
  'PRD_REVIEW',
  'PRD_APPROVED',
  'PRD_REJECTED',
  
  // System Design stages
  'SYSTEM_DESIGN_DRAFTING',
  'SYSTEM_DESIGN_DRAFTED',
  'SYSTEM_DESIGN_PENDING_REVIEW',
  'SYSTEM_DESIGN_APPROVED',
  'SYSTEM_DESIGN_REJECTED',
  
  // Planning stages
  'PLANNING_IN_PROGRESS',
  'PLANNING_COMPLETE',
  
  // Effort estimation stages
  'EFFORT_PENDING_REVIEW',
  'EFFORT_APPROVED',
  'EFFORT_REJECTED',
  
  // Cost estimation stages
  'COSTING_IN_PROGRESS',
  'COSTING_COMPLETE',
  'COSTING_PENDING_REVIEW',
  'COSTING_APPROVED',
  'COSTING_REJECTED',
  
  // Value analysis stages
  'VALUE_ANALYSIS_IN_PROGRESS',
  'VALUE_ANALYSIS_COMPLETE',
  'VALUE_PENDING_REVIEW',
  'VALUE_APPROVED',
  'VALUE_REJECTED',
  
  // Financial model stages
  'FINANCIAL_MODEL_IN_PROGRESS',
  'FINANCIAL_MODEL_COMPLETE',
  'FINANCIAL_MODEL_PENDING_REVIEW',
  'FINANCIAL_MODEL_APPROVED',
  'FINANCIAL_MODEL_REJECTED',
  'FINANCIAL_ANALYSIS',
  
  // Final approval stages
  'FINAL_REVIEW',
  'PENDING_FINAL_APPROVAL',
  'APPROVED',
  'REJECTED',
] as const;

/**
 * Type for business case status values
 */
export type BusinessCaseStatus = typeof ALL_BUSINESS_CASE_STATUSES[number]; 