// Workflow types and stage definitions for the business case workflow stepper

export interface WorkflowStage {
  id: string;
  label: string;
  description: string;
  statuses: string[];
  routePath?: string;
  icon?: string;
}

export interface WorkflowStageState {
  activeStage: WorkflowStage | null;
  completedStages: WorkflowStage[];
  availableStages: WorkflowStage[];
  allStages: WorkflowStage[];
}

// Define the main workflow stages based on BusinessCaseStatus enum
export const WORKFLOW_STAGES: WorkflowStage[] = [
  {
    id: 'intake',
    label: 'Intake & PRD Creation',
    description: 'Initial case intake and PRD drafting',
    statuses: ['INTAKE', 'PRD_DRAFTING'],
    routePath: '/prd',
  },
  {
    id: 'prd_review',
    label: 'PRD Review & Approval',
    description: 'PRD review and approval process',
    statuses: ['PRD_REVIEW', 'PRD_APPROVED', 'PRD_REJECTED'],
    routePath: '/prd-review',
  },
  {
    id: 'system_design',
    label: 'System Design',
    description: 'System design creation and drafting',
    statuses: [
      'SYSTEM_DESIGN_DRAFTING',
      'SYSTEM_DESIGN_DRAFTED',
      'SYSTEM_DESIGN_PENDING_REVIEW',
      'SYSTEM_DESIGN_APPROVED',
      'SYSTEM_DESIGN_REJECTED'
    ],
    routePath: '/design',
  },
  {
    id: 'effort_estimation',
    label: 'Effort Estimation',
    description: 'Project planning and effort estimation',
    statuses: [
      'PLANNING_IN_PROGRESS',
      'PLANNING_COMPLETE',
      'EFFORT_PENDING_REVIEW',
      'EFFORT_APPROVED',
      'EFFORT_REJECTED'
    ],
    routePath: '/effort-estimation',
  },
  {
    id: 'cost_analysis',
    label: 'Cost Analysis',
    description: 'Cost estimation and analysis',
    statuses: [
      'COSTING_IN_PROGRESS',
      'COSTING_COMPLETE',
      'COSTING_PENDING_REVIEW',
      'COSTING_APPROVED',
      'COSTING_REJECTED'
    ],
    routePath: '/cost-analysis',
  },
  {
    id: 'value_analysis',
    label: 'Value Analysis',
    description: 'Value projection and analysis',
    statuses: [
      'VALUE_ANALYSIS_IN_PROGRESS',
      'VALUE_ANALYSIS_COMPLETE',
      'VALUE_PENDING_REVIEW',
      'VALUE_APPROVED',
      'VALUE_REJECTED'
    ],
    routePath: '/value-analysis',
  },
  {
    id: 'financial_model',
    label: 'Financial Model',
    description: 'Financial modeling and analysis',
    statuses: [
      'FINANCIAL_MODEL_IN_PROGRESS',
      'FINANCIAL_MODEL_COMPLETE',
      'FINANCIAL_ANALYSIS'
    ],
    routePath: '/financial-model',
  },
  {
    id: 'final_review',
    label: 'Final Review & Approval',
    description: 'Final review and approval process',
    statuses: [
      'FINAL_REVIEW',
      'PENDING_FINAL_APPROVAL',
      'APPROVED',
      'REJECTED'
    ],
    routePath: '/summary',
  },
];

// Utility function to get workflow stage state based on current status
export const getWorkflowStageState = (currentStatus: string): WorkflowStageState => {
  const currentStage = WORKFLOW_STAGES.find(stage => 
    stage.statuses.includes(currentStatus)
  );

  if (!currentStage) {
    return {
      activeStage: null,
      completedStages: [],
      availableStages: [],
      allStages: WORKFLOW_STAGES,
    };
  }

  const currentStageIndex = WORKFLOW_STAGES.findIndex(stage => stage.id === currentStage.id);
  const completedStages = WORKFLOW_STAGES.slice(0, currentStageIndex);
  const availableStages = WORKFLOW_STAGES.slice(0, currentStageIndex + 1);

  return {
    activeStage: currentStage,
    completedStages,
    availableStages,
    allStages: WORKFLOW_STAGES,
  };
};

// Utility function to check if a stage is accessible for navigation
export const isStageAccessible = (stage: WorkflowStage, currentStatus: string): boolean => {
  const { activeStage, completedStages } = getWorkflowStageState(currentStatus);
  
  // Can access completed stages and the current active stage
  return completedStages.includes(stage) || 
         (activeStage?.id === stage.id) || false;
}; 