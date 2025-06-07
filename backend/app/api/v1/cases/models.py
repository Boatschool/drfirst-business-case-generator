"""
Pydantic models for business case API routes.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import re


# Response models
class BusinessCaseSummary(BaseModel):
    case_id: str
    user_id: str
    title: str
    status: str  # Ideally, this would use the BusinessCaseStatus Enum
    created_at: datetime
    updated_at: datetime


class BusinessCaseDetailsModel(BaseModel):
    case_id: str
    user_id: str
    title: str
    problem_statement: str
    relevant_links: List[Dict[str, str]] = Field(default_factory=list)
    status: str  # Ideally, this would use an Enum shared with the agent
    history: List[Dict[str, Any]] = Field(default_factory=list)
    prd_draft: Optional[Dict[str, Any]] = None
    system_design_v1_draft: Optional[Dict[str, Any]] = None
    effort_estimate_v1: Optional[Dict[str, Any]] = None  # Effort estimate from PlannerAgent
    cost_estimate_v1: Optional[Dict[str, Any]] = None  # Cost estimate from CostAnalystAgent
    value_projection_v1: Optional[Dict[str, Any]] = None  # Value projection from SalesValueAnalystAgent
    financial_summary_v1: Optional[Dict[str, Any]] = None  # Financial summary from FinancialModelAgent
    created_at: datetime
    updated_at: datetime


# Update request models
class PrdUpdateRequest(BaseModel):
    content_markdown: str = Field(
        ..., 
        min_length=10, 
        max_length=50000,
        description="PRD content in markdown format"
    )

    @field_validator('content_markdown')
    def validate_content_markdown(cls, v):
        """Validate PRD markdown content"""
        content = v.strip()
        if not content:
            raise ValueError('PRD content cannot be empty or just whitespace')
        
        # Check for minimum meaningful content (at least 3 words)
        words = content.split()
        if len(words) < 3:
            raise ValueError('PRD content must contain at least 3 words')
        
        # Basic markdown validation - ensure it's not just formatting
        content_without_markdown = re.sub(r'[#*`\-_\[\]()]+', '', content).strip()
        if len(content_without_markdown) < 10:
            raise ValueError('PRD content must contain substantial text beyond markdown formatting')
        
        return content


class StatusUpdateRequest(BaseModel):
    status: str = Field(
        ...,
        min_length=1,
        max_length=50,
        pattern=r'^[A-Z_]+$',
        description="Status in uppercase with underscores (e.g., PRD_REVIEW)"
    )
    comment: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional comment about the status update"
    )

    @field_validator('comment')
    def validate_comment(cls, v):
        """Validate comment if provided"""
        if v is not None:
            comment = v.strip()
            if comment and len(comment) < 3:
                raise ValueError('Comment must be at least 3 characters if provided')
            return comment if comment else None
        return v


class SystemDesignUpdateRequest(BaseModel):
    content_markdown: str = Field(
        ..., 
        min_length=10, 
        max_length=100000,
        description="System design content in markdown format"
    )

    @field_validator('content_markdown')
    def validate_content_markdown(cls, v):
        """Validate system design markdown content"""
        content = v.strip()
        if not content:
            raise ValueError('System design content cannot be empty or just whitespace')
        
        # Check for minimum meaningful content
        words = content.split()
        if len(words) < 5:
            raise ValueError('System design content must contain at least 5 words')
        
        # Basic validation for technical content
        content_without_markdown = re.sub(r'[#*`\-_\[\]()]+', '', content).strip()
        if len(content_without_markdown) < 20:
            raise ValueError('System design must contain substantial technical content')
        
        return content


class EffortEstimateUpdateRequest(BaseModel):
    roles: List[Dict[str, Any]] = Field(
        ...,
        min_items=1,
        max_items=20,
        description="List of roles with effort estimates"
    )
    total_hours: int = Field(
        ...,
        gt=0,
        le=100000,
        description="Total estimated hours (1-100,000)"
    )
    estimated_duration_weeks: int = Field(
        ...,
        gt=0,
        le=260,  # 5 years max
        description="Estimated duration in weeks (1-260)"
    )
    complexity_assessment: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Complexity assessment description"
    )
    notes: Optional[str] = Field(
        None,
        max_length=2000,
        description="Additional notes about the effort estimate"
    )

    @field_validator('roles')
    def validate_role_structure(cls, roles):
        """Validate each role in the roles list"""
        validated_roles = []
        for role in roles:
            if not isinstance(role, dict):
                raise ValueError('Each role must be a dictionary')
            
            required_fields = ['role_name', 'hours']
            for field in required_fields:
                if field not in role:
                    raise ValueError(f'Each role must have a {field} field')
            
            # Validate role_name
            if not isinstance(role['role_name'], str) or not role['role_name'].strip():
                raise ValueError('role_name must be a non-empty string')
            
            # Validate hours
            try:
                hours = float(role['hours'])
                if hours <= 0 or hours > 10000:
                    raise ValueError('Role hours must be between 0 and 10,000')
            except (ValueError, TypeError):
                raise ValueError('Role hours must be a valid positive number')
            
            validated_roles.append(role)
        return validated_roles

    @field_validator('complexity_assessment')
    def validate_complexity_assessment(cls, v):
        """Validate complexity assessment content"""
        assessment = v.strip()
        if not assessment:
            raise ValueError('Complexity assessment cannot be empty')
        
        words = assessment.split()
        if len(words) < 3:
            raise ValueError('Complexity assessment must contain at least 3 words')
        
        return assessment


class CostEstimateUpdateRequest(BaseModel):
    estimated_cost: float = Field(
        ...,
        gt=0,
        le=100000000,  # 100 million max
        description="Estimated cost in currency units"
    )
    currency: str = Field(
        ...,
        min_length=3,
        max_length=3,
        pattern=r'^[A-Z]{3}$',
        description="3-letter currency code (e.g., USD, EUR)"
    )
    rate_card_used: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Rate card identifier used for calculation"
    )
    breakdown_by_role: List[Dict[str, Any]] = Field(
        ...,
        min_items=1,
        max_items=20,
        description="Cost breakdown by role"
    )
    calculation_method: Optional[str] = Field(
        None,
        max_length=500,
        description="Method used for cost calculation"
    )
    notes: Optional[str] = Field(
        None,
        max_length=2000,
        description="Additional notes about the cost estimate"
    )

    @field_validator('breakdown_by_role')
    def validate_role_breakdown(cls, roles):
        """Validate each role breakdown item"""
        validated_roles = []
        for role in roles:
            if not isinstance(role, dict):
                raise ValueError('Each role breakdown must be a dictionary')
            
            required_fields = ['role_name', 'cost']
            for field in required_fields:
                if field not in role:
                    raise ValueError(f'Each role breakdown must have a {field} field')
            
            # Validate role_name
            if not isinstance(role['role_name'], str) or not role['role_name'].strip():
                raise ValueError('role_name must be a non-empty string')
            
            # Validate cost
            try:
                cost = float(role['cost'])
                if cost < 0 or cost > 10000000:  # 10 million per role max
                    raise ValueError('Role cost must be between 0 and 10,000,000')
            except (ValueError, TypeError):
                raise ValueError('Role cost must be a valid number')
            
            validated_roles.append(role)
        return validated_roles


class ValueProjectionUpdateRequest(BaseModel):
    scenarios: List[Dict[str, Any]] = Field(
        ...,
        min_items=1,
        max_items=10,
        description="List of value projection scenarios"
    )
    currency: str = Field(
        ...,
        min_length=3,
        max_length=3,
        pattern=r'^[A-Z]{3}$',
        description="3-letter currency code (e.g., USD, EUR)"
    )
    template_used: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Template used for value projection"
    )
    methodology: Optional[str] = Field(
        None,
        max_length=1000,
        description="Methodology used for value calculation"
    )
    assumptions: Optional[List[str]] = Field(
        None,
        max_items=20,
        description="List of assumptions used"
    )
    notes: Optional[str] = Field(
        None,
        max_length=2000,
        description="Additional notes about the value projection"
    )

    @field_validator('scenarios')
    def validate_scenario(cls, scenarios):
        """Validate each scenario in the scenarios list"""
        validated_scenarios = []
        for scenario in scenarios:
            if not isinstance(scenario, dict):
                raise ValueError('Each scenario must be a dictionary')
            
            required_fields = ['name', 'value']
            for field in required_fields:
                if field not in scenario:
                    raise ValueError(f'Each scenario must have a {field} field')
            
            # Validate scenario name
            if not isinstance(scenario['name'], str) or not scenario['name'].strip():
                raise ValueError('Scenario name must be a non-empty string')
            
            # Validate value
            try:
                value = float(scenario['value'])
                if value < 0 or value > 1000000000:  # 1 billion max
                    raise ValueError('Scenario value must be between 0 and 1,000,000,000')
            except (ValueError, TypeError):
                raise ValueError('Scenario value must be a valid number')
            
            validated_scenarios.append(scenario)
        return validated_scenarios

    @field_validator('assumptions')
    def validate_assumptions(cls, v):
        """Validate assumptions list"""
        if v is not None:
            for assumption in v:
                if not isinstance(assumption, str) or not assumption.strip():
                    raise ValueError('Each assumption must be a non-empty string')
                if len(assumption.strip()) < 5:
                    raise ValueError('Each assumption must be at least 5 characters')
            return [assumption.strip() for assumption in v]
        return v


# Reject request models
class PrdRejectRequest(BaseModel):
    reason: Optional[str] = Field(
        None,
        min_length=5,
        max_length=1000,
        description="Reason for rejecting the PRD"
    )

    @field_validator('reason')
    def validate_reason(cls, v):
        """Validate rejection reason"""
        if v is not None:
            reason = v.strip()
            if reason and len(reason.split()) < 2:
                raise ValueError('Rejection reason must contain at least 2 words')
            return reason if reason else None
        return v


class SystemDesignRejectRequest(BaseModel):
    reason: Optional[str] = Field(
        None,
        min_length=5,
        max_length=1000,
        description="Reason for rejecting the system design"
    )

    @field_validator('reason')
    def validate_reason(cls, v):
        """Validate rejection reason"""
        if v is not None:
            reason = v.strip()
            if reason and len(reason.split()) < 2:
                raise ValueError('Rejection reason must contain at least 2 words')
            return reason if reason else None
        return v


class EffortEstimateRejectRequest(BaseModel):
    reason: Optional[str] = Field(
        None,
        min_length=5,
        max_length=1000,
        description="Reason for rejecting the effort estimate"
    )

    @field_validator('reason')
    def validate_reason(cls, v):
        """Validate rejection reason"""
        if v is not None:
            reason = v.strip()
            if reason and len(reason.split()) < 2:
                raise ValueError('Rejection reason must contain at least 2 words')
            return reason if reason else None
        return v


class CostEstimateRejectRequest(BaseModel):
    reason: Optional[str] = Field(
        None,
        min_length=5,
        max_length=1000,
        description="Reason for rejecting the cost estimate"
    )

    @field_validator('reason')
    def validate_reason(cls, v):
        """Validate rejection reason"""
        if v is not None:
            reason = v.strip()
            if reason and len(reason.split()) < 2:
                raise ValueError('Rejection reason must contain at least 2 words')
            return reason if reason else None
        return v


class ValueProjectionRejectRequest(BaseModel):
    reason: Optional[str] = Field(
        None,
        min_length=5,
        max_length=1000,
        description="Reason for rejecting the value projection"
    )

    @field_validator('reason')
    def validate_reason(cls, v):
        """Validate rejection reason"""
        if v is not None:
            reason = v.strip()
            if reason and len(reason.split()) < 2:
                raise ValueError('Rejection reason must contain at least 2 words')
            return reason if reason else None
        return v


class FinalRejectRequest(BaseModel):
    reason: Optional[str] = Field(
        None,
        min_length=10,
        max_length=2000,
        description="Detailed reason for final rejection"
    )

    @field_validator('reason')
    def validate_reason(cls, v):
        """Validate final rejection reason - should be more detailed"""
        if v is not None:
            reason = v.strip()
            if reason:
                words = reason.split()
                if len(words) < 5:
                    raise ValueError('Final rejection reason must contain at least 5 words for proper documentation')
            return reason if reason else None
        return v 