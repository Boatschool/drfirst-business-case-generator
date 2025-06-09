"""
Pydantic models for Agent Tool Inputs and Outputs
Provides type safety and validation for all agent method calls
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


# ===== COMMON ENUMS AND TYPES =====

class AgentStatus(str, Enum):
    """Status values for agent operations"""
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    TIMEOUT = "timeout"


class ComplexityLevel(str, Enum):
    """Complexity assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class OperationStatus(str, Enum):
    """Status for long-running operations"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ===== BASE RESPONSE MODEL =====

class BaseAgentResponse(BaseModel):
    """Base response model for all agent operations"""
    status: AgentStatus = Field(..., description="Operation status")
    message: str = Field(..., description="Human-readable status message")
    operation_id: Optional[str] = Field(None, description="Unique operation identifier")
    duration_ms: Optional[int] = Field(None, description="Operation duration in milliseconds")
    agent_version: str = Field(default="1.0.0", description="Agent version")
    generated_at: datetime = Field(default_factory=datetime.now, description="Response generation timestamp")


# ===== PRODUCT MANAGER AGENT MODELS =====

class DraftPrdInput(BaseModel):
    """Input model for PRD draft generation"""
    problem_statement: str = Field(..., min_length=10, max_length=5000, description="Problem statement for the business case")
    case_title: str = Field(..., min_length=3, max_length=200, description="Title of the business case")
    relevant_links: List[Dict[str, str]] = Field(
        default_factory=list, 
        description="Relevant documentation links with 'name' and 'url' keys"
    )
    
    @field_validator('relevant_links')
    def validate_links(cls, v):
        for link in v:
            if not isinstance(link, dict) or 'name' not in link or 'url' not in link:
                raise ValueError("Each link must be a dict with 'name' and 'url' keys")
        return v


class PrdDraft(BaseModel):
    """PRD draft content model"""
    title: str = Field(..., description="PRD title")
    content_markdown: str = Field(..., description="PRD content in markdown format")
    version: str = Field(default="1.0.0", description="PRD version")
    generated_with: str = Field(..., description="Generation method/model")
    sections: List[str] = Field(..., description="List of PRD sections")
    word_count: Optional[int] = Field(None, description="Approximate word count")


class DraftPrdOutput(BaseAgentResponse):
    """Output model for PRD draft generation"""
    prd_draft: Optional[PrdDraft] = Field(None, description="Generated PRD draft content")
    new_status: Optional[str] = Field(None, description="Updated case status")


# ===== ARCHITECT AGENT MODELS =====

class GenerateSystemDesignInput(BaseModel):
    """Input model for system design generation"""
    prd_content: str = Field(..., min_length=100, description="Approved PRD content in markdown")
    case_title: str = Field(..., min_length=3, max_length=200, description="Business case title")
    case_id: Optional[str] = Field(None, description="Unique case identifier")
    
    @field_validator('prd_content')
    def validate_prd_content(cls, v):
        if len(v.strip()) < 100:
            raise ValueError("PRD content must be at least 100 characters")
        return v


class PrdAnalysis(BaseModel):
    """PRD analysis results"""
    key_features: List[str] = Field(..., description="Identified key features")
    user_roles: List[str] = Field(..., description="Identified user roles")
    data_entities: List[str] = Field(..., description="Identified data entities")
    external_integrations: List[str] = Field(..., description="External integrations needed")
    functional_requirements: List[str] = Field(..., description="Functional requirements")
    non_functional_requirements: List[str] = Field(..., description="Non-functional requirements")
    complexity_indicators: Dict[str, Any] = Field(..., description="Complexity assessment")
    api_needs: List[str] = Field(..., description="API requirements")
    data_storage_needs: List[str] = Field(..., description="Data storage requirements")


class SystemDesignDraft(BaseModel):
    """System design draft content model"""
    content_markdown: str = Field(..., description="System design content in markdown")
    generated_by: str = Field(..., description="Generation agent and method")
    version: str = Field(..., description="System design version")
    generated_at: str = Field(..., description="Generation timestamp")
    prd_analysis: PrdAnalysis = Field(..., description="PRD analysis results")
    generation_metadata: Dict[str, Any] = Field(..., description="Generation metadata")


class GenerateSystemDesignOutput(BaseAgentResponse):
    """Output model for system design generation"""
    system_design_draft: Optional[SystemDesignDraft] = Field(None, description="Generated system design")
    new_status: Optional[str] = Field(None, description="Updated case status")


# ===== PLANNER AGENT MODELS =====

class EstimateEffortInput(BaseModel):
    """Input model for effort estimation"""
    system_design_content: str = Field(..., min_length=100, description="System design content")
    case_title: str = Field(..., description="Business case title")
    complexity_override: Optional[ComplexityLevel] = Field(None, description="Manual complexity override")


class EffortEstimate(BaseModel):
    """Effort estimation results"""
    total_hours: int = Field(..., ge=0, description="Total estimated hours")
    breakdown_by_phase: Dict[str, int] = Field(..., description="Hours breakdown by development phase")
    breakdown_by_role: Dict[str, int] = Field(..., description="Hours breakdown by team role")
    confidence_level: str = Field(..., description="Estimation confidence level")
    assumptions: List[str] = Field(..., description="Key assumptions made")
    risks: List[str] = Field(..., description="Identified risks")


class EstimateEffortOutput(BaseAgentResponse):
    """Output model for effort estimation"""
    effort_estimate: Optional[EffortEstimate] = Field(None, description="Generated effort estimate")
    complexity_assessment: Optional[ComplexityLevel] = Field(None, description="Assessed complexity level")


# ===== COST ANALYST AGENT MODELS =====

class EstimateCostInput(BaseModel):
    """Input model for cost estimation"""
    effort_estimate: Dict[str, Any] = Field(..., description="Effort estimation data")
    case_title: str = Field(..., description="Business case title")
    include_infrastructure: bool = Field(default=True, description="Include infrastructure costs")


class CostEstimate(BaseModel):
    """Cost estimation results"""
    total_cost: float = Field(..., ge=0, description="Total estimated cost")
    development_cost: float = Field(..., ge=0, description="Development cost")
    infrastructure_cost: float = Field(..., ge=0, description="Infrastructure cost")
    operational_cost: float = Field(..., ge=0, description="Ongoing operational cost")
    cost_breakdown: Dict[str, float] = Field(..., description="Detailed cost breakdown")
    assumptions: List[str] = Field(..., description="Cost assumptions")


class EstimateCostOutput(BaseAgentResponse):
    """Output model for cost estimation"""
    cost_estimate: Optional[CostEstimate] = Field(None, description="Generated cost estimate")


# ===== SALES VALUE ANALYST AGENT MODELS =====

class EstimateValueInput(BaseModel):
    """Input model for value estimation"""
    prd_content: str = Field(..., description="PRD content")
    case_title: str = Field(..., description="Business case title")
    target_market_size: Optional[str] = Field(None, description="Target market size hint")


class ValueProjection(BaseModel):
    """Value projection results"""
    revenue_projection: Dict[str, float] = Field(..., description="Revenue projections by year")
    cost_savings: Dict[str, float] = Field(..., description="Cost savings by category")
    roi_percentage: float = Field(..., description="Return on investment percentage")
    payback_period_months: int = Field(..., ge=0, description="Payback period in months")
    assumptions: List[str] = Field(..., description="Value assumptions")
    risk_factors: List[str] = Field(..., description="Risk factors affecting value")


class EstimateValueOutput(BaseAgentResponse):
    """Output model for value estimation"""
    value_projection: Optional[ValueProjection] = Field(None, description="Generated value projection")


# ===== FINANCIAL MODEL AGENT MODELS =====

class GenerateFinancialModelInput(BaseModel):
    """Input model for financial model generation"""
    cost_estimate: Dict[str, Any] = Field(..., description="Cost estimation data")
    value_projection: Dict[str, Any] = Field(..., description="Value projection data")
    case_title: str = Field(..., description="Business case title")
    time_horizon_years: int = Field(default=3, ge=1, le=10, description="Financial model time horizon")


class FinancialSummary(BaseModel):
    """Financial model summary"""
    net_present_value: float = Field(..., description="Net Present Value")
    internal_rate_of_return: float = Field(..., description="Internal Rate of Return")
    payback_period: float = Field(..., description="Payback period in years")
    risk_adjusted_roi: float = Field(..., description="Risk-adjusted ROI")
    cash_flow_projection: Dict[str, float] = Field(..., description="Cash flow by year")
    sensitivity_analysis: Dict[str, Any] = Field(..., description="Sensitivity analysis results")


class GenerateFinancialModelOutput(BaseAgentResponse):
    """Output model for financial model generation"""
    financial_summary: Optional[FinancialSummary] = Field(None, description="Generated financial summary")


# ===== ENHANCED OPERATION TRACKING =====

class AgentOperation(BaseModel):
    """Model for tracking long-running agent operations"""
    operation_id: str = Field(..., description="Unique operation identifier")
    agent_name: str = Field(..., description="Name of the agent performing the operation")
    operation_type: str = Field(..., description="Type of operation being performed")
    status: OperationStatus = Field(..., description="Current operation status")
    progress_percentage: int = Field(default=0, ge=0, le=100, description="Progress percentage")
    current_step: str = Field(..., description="Description of current step")
    estimated_completion_ms: Optional[int] = Field(None, description="Estimated completion time")
    started_at: datetime = Field(default_factory=datetime.now, description="Operation start time")
    completed_at: Optional[datetime] = Field(None, description="Operation completion time")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    result_data: Optional[Dict[str, Any]] = Field(None, description="Operation result data")


class OperationProgress(BaseModel):
    """Progress update for operations"""
    operation_id: str = Field(..., description="Operation identifier")
    status: OperationStatus = Field(..., description="Current status")
    progress_percentage: int = Field(..., ge=0, le=100, description="Progress percentage")
    current_step: str = Field(..., description="Current step description")
    estimated_completion_ms: Optional[int] = Field(None, description="Estimated completion time")
    error: Optional[str] = Field(None, description="Error message if applicable")


# ===== ENHANCED ERROR MODELS =====

class AgentError(BaseModel):
    """Enhanced error information"""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    field: Optional[str] = Field(None, description="Field that caused the error")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class EnhancedAgentResponse(BaseModel):
    """Enhanced response model with detailed error information"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Human-readable message")
    data: Optional[Any] = Field(None, description="Response data")
    errors: List[AgentError] = Field(default_factory=list, description="List of errors if any")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    operation_id: Optional[str] = Field(None, description="Operation identifier")
    duration_ms: Optional[int] = Field(None, description="Operation duration")
    agent_version: str = Field(default="1.0.0", description="Agent version") 