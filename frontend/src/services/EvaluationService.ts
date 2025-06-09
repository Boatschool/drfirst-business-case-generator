/* eslint-disable @typescript-eslint/no-explicit-any */
/**
 * Evaluation Service for DrFirst Business Case Generator
 * Handles human evaluation operations
 */

export interface MetricScoreComment {
  score: number;
  comment: string;
}

export interface EvaluationTask {
  eval_id: string;
  golden_dataset_inputId: string;
  case_id?: string;
  trace_id?: string;
  agent_name: string;
  input_payload_summary: string;
  agent_output_to_evaluate: string;
  expected_characteristics?: any;
  applicable_metrics: string[];
}

export interface HumanEvaluationSubmission {
  eval_id: string;
  golden_dataset_inputId: string;
  case_id?: string;
  trace_id?: string;
  agent_name: string;
  metric_scores_and_comments: Record<string, MetricScoreComment>;
  overall_quality_score: number;
  overall_comments: string;
}

export interface EvaluationResponse {
  success: boolean;
  submission_id: string;
  message: string;
}

export interface EvaluationResult {
  submission_id: string;
  eval_id: string;
  golden_dataset_inputId: string;
  case_id?: string;
  trace_id?: string;
  agent_name: string;
  evaluator_id: string;
  evaluator_email: string;
  evaluation_date: string;
  metric_scores_and_comments: Record<string, MetricScoreComment>;
  overall_quality_score: number;
  overall_comments: string;
  created_at: string;
  updated_at: string;
}

// Dashboard-related interfaces
export interface DashboardSummaryData {
  total_runs: number;
  total_examples_processed: number;
  latest_run_success_rate?: number;
  latest_run_validation_pass_rate?: number;
  latest_run_timestamp?: string;
  overall_avg_success_rate: number;
  overall_avg_validation_pass_rate: number;
}

export interface EvaluationRunSummary {
  eval_run_id: string;
  run_timestamp_start: string;
  run_timestamp_end: string;
  total_examples_processed: number;
  successful_agent_runs: number;
  failed_agent_runs: number;
  overall_validation_passed_count: number;
  dataset_file_used: string;
  success_rate_percentage: number;
  validation_pass_rate_percentage: number;
  total_evaluation_time_seconds: number;
}

export interface PaginatedRunListData {
  runs: EvaluationRunSummary[];
  total_count: number;
  current_page: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface FailedValidationEntry {
  golden_dataset_inputId: string;
  agent_name: string;
  agent_run_status: string;
  validation_results: Record<string, any>;
  agent_error_message: string;
  execution_time_ms: number;
  processed_at: string;
}

export interface RunDetailsData {
  run_summary: EvaluationRunSummary;
  agent_specific_statistics: Record<string, any>;
  failed_validations: FailedValidationEntry[];
  failed_validations_count: number;
}

export interface RunListParams {
  page: number;
  limit: number;
  sortBy: string;
  order: 'asc' | 'desc';
}

// Human Evaluation Dashboard Interfaces
export interface HumanEvalSummaryData {
  total_evaluations: number;
  unique_evaluators: number;
  average_overall_score: number;
  score_distribution: Record<string, number>; // {"1": count, "2": count, ...}
  evaluations_by_agent: Record<string, number>;
  latest_evaluation_date?: string;
}

export interface HumanEvaluationResult {
  submission_id: string;
  eval_id: string;
  golden_dataset_inputId: string;
  case_id?: string;
  trace_id?: string;
  agent_name: string;
  evaluator_id: string;
  evaluator_email: string;
  evaluation_date: string;
  overall_quality_score: number;
  overall_comments: string;
  metric_scores_and_comments: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface PaginatedHumanEvalData {
  evaluations: HumanEvaluationResult[];
  total_count: number;
  current_page: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface HumanEvalResultDetail {
  submission_id: string;
  eval_id: string;
  golden_dataset_inputId: string;
  case_id?: string;
  trace_id?: string;
  agent_name: string;
  evaluator_id: string;
  evaluator_email: string;
  evaluation_date: string;
  overall_quality_score: number;
  overall_comments: string;
  metric_scores_and_comments: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface HumanEvalListParams {
  page: number;
  limit: number;
  sortBy: string;
  order: 'asc' | 'desc';
  agent_name?: string;
  evaluator_id?: string;
  golden_dataset_inputId?: string;
}

/**
 * EvaluationService interface defines the contract for evaluation operations
 */
export interface EvaluationService {
  /**
   * Get available evaluation tasks
   * @returns Promise<EvaluationTask[]> List of evaluation tasks
   */
  getEvaluationTasks(): Promise<EvaluationTask[]>;

  /**
   * Submit a human evaluation
   * @param evaluation Evaluation data to submit
   * @returns Promise<EvaluationResponse> Submission response
   */
  submitEvaluation(evaluation: HumanEvaluationSubmission): Promise<EvaluationResponse>;

  /**
   * Get evaluation results with optional filtering
   * @param agentName Optional agent name filter
   * @param evaluatorId Optional evaluator ID filter
   * @param limit Optional limit (default 50)
   * @returns Promise<EvaluationResult[]> List of evaluation results
   */
  getEvaluationResults(
    agentName?: string,
    evaluatorId?: string,
    limit?: number
  ): Promise<EvaluationResult[]>;

  /**
   * Get available metrics for a specific agent
   * @param agentName Name of the agent
   * @returns Promise<string[]> List of metric names
   */
  getAgentMetrics(agentName: string): Promise<string[]>;

  /**
   * Get dashboard summary metrics
   * @returns Promise<DashboardSummaryData> Dashboard summary data
   */
  getDashboardSummary(): Promise<DashboardSummaryData>;

  /**
   * Get paginated list of evaluation runs
   * @param params Pagination and sorting parameters
   * @returns Promise<PaginatedRunListData> Paginated run list
   */
  listEvaluationRuns(params: RunListParams): Promise<PaginatedRunListData>;

  /**
   * Get detailed information about a specific evaluation run
   * @param evalRunId Evaluation run ID
   * @returns Promise<RunDetailsData> Run details with failed validations
   */
  getEvaluationRunDetails(evalRunId: string): Promise<RunDetailsData>;

  /**
   * Get human evaluation summary metrics
   * @returns Promise<HumanEvalSummaryData> Human evaluation summary data
   */
  getHumanEvalDashboardSummary(): Promise<HumanEvalSummaryData>;

  /**
   * Get paginated list of human evaluation results
   * @param params Pagination, sorting, and filtering parameters
   * @returns Promise<PaginatedHumanEvalData> Paginated human evaluation data
   */
  listHumanEvaluationResults(params: HumanEvalListParams): Promise<PaginatedHumanEvalData>;

  /**
   * Get detailed view of a specific human evaluation
   * @param submissionId Human evaluation submission ID
   * @returns Promise<HumanEvalResultDetail> Detailed human evaluation result
   */
  getHumanEvaluationResultDetails(submissionId: string): Promise<HumanEvalResultDetail>;
}

/**
 * Default implementation of EvaluationService using Firebase auth
 */
export class DefaultEvaluationService implements EvaluationService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = import.meta.env.DEV 
      ? 'http://localhost:8000' 
      : window.location.origin;
  }

  private async getAuthHeaders(): Promise<HeadersInit> {
    // Get Firebase auth token
    const auth = (await import('firebase/auth')).getAuth();
    const user = auth.currentUser;
    
    if (!user) {
      throw new Error('User not authenticated');
    }

    const token = await user.getIdToken();
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    };
  }

  async getEvaluationTasks(): Promise<EvaluationTask[]> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/api/v1/evaluations/tasks`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: Failed to fetch evaluation tasks`);
    }

    return response.json();
  }

  async submitEvaluation(evaluation: HumanEvaluationSubmission): Promise<EvaluationResponse> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/api/v1/evaluations/submit`, {
      method: 'POST',
      headers,
      body: JSON.stringify(evaluation),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: Failed to submit evaluation`);
    }

    return response.json();
  }

  async getEvaluationResults(
    agentName?: string,
    evaluatorId?: string,
    limit = 50
  ): Promise<EvaluationResult[]> {
    const headers = await this.getAuthHeaders();
    
    const params = new URLSearchParams();
    if (agentName) params.append('agent_name', agentName);
    if (evaluatorId) params.append('evaluator_id', evaluatorId);
    params.append('limit', limit.toString());
    
    const response = await fetch(`${this.baseUrl}/api/v1/evaluations/results?${params}`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: Failed to fetch evaluation results`);
    }

    return response.json();
  }

  async getAgentMetrics(agentName: string): Promise<string[]> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/api/v1/evaluations/metrics/${encodeURIComponent(agentName)}`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: Failed to fetch agent metrics`);
    }

    return response.json();
  }

  async getDashboardSummary(): Promise<DashboardSummaryData> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/api/v1/evaluations/dashboard/summary`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: Failed to fetch dashboard summary`);
    }

    return response.json();
  }

  async listEvaluationRuns(params: RunListParams): Promise<PaginatedRunListData> {
    const headers = await this.getAuthHeaders();
    
    const queryParams = new URLSearchParams({
      page: params.page.toString(),
      limit: params.limit.toString(),
      sort_by: params.sortBy,
      order: params.order,
    });
    
    const response = await fetch(`${this.baseUrl}/api/v1/evaluations/dashboard/runs?${queryParams}`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: Failed to fetch evaluation runs`);
    }

    return response.json();
  }

  async getEvaluationRunDetails(evalRunId: string): Promise<RunDetailsData> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/api/v1/evaluations/dashboard/runs/${encodeURIComponent(evalRunId)}/details`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: Failed to fetch evaluation run details`);
    }

    return response.json();
  }

  async getHumanEvalDashboardSummary(): Promise<HumanEvalSummaryData> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/api/v1/evaluations/dashboard/human/summary`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: Failed to fetch human evaluation summary`);
    }

    return response.json();
  }

  async listHumanEvaluationResults(params: HumanEvalListParams): Promise<PaginatedHumanEvalData> {
    const headers = await this.getAuthHeaders();
    
    // Build query parameters
    const searchParams = new URLSearchParams({
      page: params.page.toString(),
      limit: params.limit.toString(),
      sort_by: params.sortBy,
      order: params.order,
    });

    if (params.agent_name) {
      searchParams.append('agent_name', params.agent_name);
    }
    if (params.evaluator_id) {
      searchParams.append('evaluator_id', params.evaluator_id);
    }
    if (params.golden_dataset_inputId) {
      searchParams.append('golden_dataset_inputId', params.golden_dataset_inputId);
    }

    const response = await fetch(
      `${this.baseUrl}/api/v1/evaluations/dashboard/human/results?${searchParams.toString()}`,
      { method: 'GET', headers }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: Failed to fetch human evaluation results`);
    }

    return response.json();
  }

  async getHumanEvaluationResultDetails(submissionId: string): Promise<HumanEvalResultDetail> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(
      `${this.baseUrl}/api/v1/evaluations/dashboard/human/results/${encodeURIComponent(submissionId)}`,
      { method: 'GET', headers }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: Failed to fetch human evaluation result details`);
    }

    return response.json();
  }
}

// Export a singleton instance
export const evaluationService = new DefaultEvaluationService(); 