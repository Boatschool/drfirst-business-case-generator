// Business Case related types
import { Priority, JobStatus } from './index';

export interface BusinessCaseRequest {
  title: string;
  description: string;
  requester_uid: string;
  requirements: Record<string, any>;
  priority: Priority;
  deadline?: Date;
}

export interface BusinessCase {
  id?: string;
  request_data: BusinessCaseRequest;
  generated_content: Record<string, any>;
  status: JobStatus;
  created_at: Date;
  updated_at: Date;
  completed_at?: Date;
  generated_by_agents: string[];
}

export interface BusinessCaseSection {
  id: string;
  title: string;
  content: string;
  order: number;
  agent_generated: boolean;
  last_updated: Date;
}

export interface MarketAnalysis {
  market_size: string;
  target_audience: string;
  competitive_landscape: string;
  growth_projections: string;
}

export interface ROICalculation {
  projected_revenue: number;
  implementation_cost: number;
  roi_percentage: number;
  payback_period: string;
  npv: number;
}

export interface TechnicalRequirements {
  recommended_architecture: string;
  technology_stack: string[];
  scalability_considerations: string;
  estimated_duration: string;
  team_size_recommendation: number;
  complexity_assessment: string;
} 