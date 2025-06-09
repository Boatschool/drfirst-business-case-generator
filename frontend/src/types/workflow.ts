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
    statuses: ['PRD_REVIEW', 'PRD_REJECTED'],
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
      'FINANCIAL_MODEL_PENDING_REVIEW',
      'FINANCIAL_MODEL_APPROVED',
      'FINANCIAL_MODEL_REJECTED',
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

// Define statuses that indicate a stage is complete and should trigger progression to the next stage
const COMPLETION_STATUSES = [
  'PRD_APPROVED',
  'SYSTEM_DESIGN_APPROVED', 
  'EFFORT_APPROVED',
  'COSTING_APPROVED',
  'VALUE_APPROVED',
  'FINANCIAL_MODEL_COMPLETE',
  'FINANCIAL_MODEL_APPROVED'
];

// Define statuses that indicate a stage is "submitted" and should show as completed from user's perspective
const SUBMITTED_STATUSES = [
  'PRD_REVIEW',
  'SYSTEM_DESIGN_PENDING_REVIEW',
  'EFFORT_PENDING_REVIEW',
  'COSTING_PENDING_REVIEW',
  'VALUE_PENDING_REVIEW',
  'FINANCIAL_MODEL_PENDING_REVIEW'
];

// Utility function to get workflow stage state based on current status
export const getWorkflowStageState = (currentStatus: string): WorkflowStageState => {
  // Handle completion statuses that should progress to the next stage
  if (COMPLETION_STATUSES.includes(currentStatus)) {
    // Find which stage this completion status belongs to
    const completedStageIndex = WORKFLOW_STAGES.findIndex(stage => {
      // Check if this status logically belongs to this stage (by naming convention)
      if (currentStatus === 'PRD_APPROVED') return stage.id === 'prd_review';
      if (currentStatus === 'SYSTEM_DESIGN_APPROVED') return stage.id === 'system_design';
      if (currentStatus === 'EFFORT_APPROVED') return stage.id === 'effort_estimation';
      if (currentStatus === 'COSTING_APPROVED') return stage.id === 'cost_analysis';
      if (currentStatus === 'VALUE_APPROVED') return stage.id === 'value_analysis';
      if (currentStatus === 'FINANCIAL_MODEL_COMPLETE') return stage.id === 'financial_model';
      if (currentStatus === 'FINANCIAL_MODEL_APPROVED') return stage.id === 'financial_model';
      return false;
    });

    if (completedStageIndex !== -1) {
      const completedStages = WORKFLOW_STAGES.slice(0, completedStageIndex + 1);
      const nextStageIndex = completedStageIndex + 1;
      const activeStage = nextStageIndex < WORKFLOW_STAGES.length ? WORKFLOW_STAGES[nextStageIndex] : null;
      const availableStages = activeStage ? WORKFLOW_STAGES.slice(0, nextStageIndex + 1) : completedStages;

      return {
        activeStage,
        completedStages,
        availableStages,
        allStages: WORKFLOW_STAGES,
      };
    }
  }

  // Handle submitted statuses that should show the stage as completed
  if (SUBMITTED_STATUSES.includes(currentStatus)) {
    // Find which stage this submitted status belongs to
    const submittedStageIndex = WORKFLOW_STAGES.findIndex(stage => {
      // Check if this status logically belongs to this stage (by naming convention)
      if (currentStatus === 'PRD_REVIEW') return stage.id === 'intake'; // PRD creation is complete when in review
      if (currentStatus === 'SYSTEM_DESIGN_PENDING_REVIEW') return stage.id === 'system_design';
      if (currentStatus === 'EFFORT_PENDING_REVIEW') return stage.id === 'effort_estimation';
      if (currentStatus === 'COSTING_PENDING_REVIEW') return stage.id === 'cost_analysis';
      if (currentStatus === 'VALUE_PENDING_REVIEW') return stage.id === 'value_analysis';
      if (currentStatus === 'FINANCIAL_MODEL_PENDING_REVIEW') return stage.id === 'financial_model';
      return false;
    });

    if (submittedStageIndex !== -1) {
      // For submitted statuses, show the submitted stage as completed but stay on the review stage
      const completedStages = WORKFLOW_STAGES.slice(0, submittedStageIndex + 1);
      let activeStage = null;
      let availableStages = completedStages;

      // Determine the active stage for submitted statuses
      if (currentStatus === 'PRD_REVIEW') {
        activeStage = WORKFLOW_STAGES.find(stage => stage.id === 'prd_review') || null;
        if (activeStage) availableStages = [...completedStages, activeStage];
      } else if (currentStatus === 'SYSTEM_DESIGN_PENDING_REVIEW') {
        // For system design pending review, the system design stage is complete and we're in review
        activeStage = WORKFLOW_STAGES.find(stage => stage.id === 'system_design') || null;
      } else {
        // For other pending review statuses, find the corresponding review stage
        const reviewStageIndex = submittedStageIndex + 1;
        if (reviewStageIndex < WORKFLOW_STAGES.length) {
          activeStage = WORKFLOW_STAGES[reviewStageIndex];
          availableStages = WORKFLOW_STAGES.slice(0, reviewStageIndex + 1);
        }
      }

      return {
        activeStage,
        completedStages,
        availableStages,
        allStages: WORKFLOW_STAGES,
      };
    }
  }

  // Regular status matching for non-completion statuses
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