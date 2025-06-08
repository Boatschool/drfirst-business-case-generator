"""
Pydantic models for Firestore database interactions
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator, HttpUrl
from enum import Enum
import re


class UserRole(str, Enum):
    """User roles in the system"""

    ADMIN = "ADMIN"
    USER = "USER"
    VIEWER = "VIEWER"
    DEVELOPER = "DEVELOPER"
    SALES_REP = "SALES_REP"
    SALES_MANAGER = "SALES_MANAGER"
    FINANCE_APPROVER = "FINANCE_APPROVER"
    LEGAL_APPROVER = "LEGAL_APPROVER"
    TECHNICAL_ARCHITECT = "TECHNICAL_ARCHITECT"
    PRODUCT_OWNER = "PRODUCT_OWNER"
    BUSINESS_ANALYST = "BUSINESS_ANALYST"
    FINAL_APPROVER = "FINAL_APPROVER"


class JobStatus(str, Enum):
    """Job status enumeration"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class User(BaseModel):
    """User model for Firestore"""

    uid: str = Field(
        ..., 
        min_length=1, 
        max_length=128,
        pattern=r'^[a-zA-Z0-9_-]+$',
        description="Firebase UID - alphanumeric, underscore, dash only"
    )
    email: EmailStr = Field(..., description="User email address")
    display_name: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=100,
        description="User display name"
    )
    systemRole: UserRole = Field(UserRole.USER, description="User system role")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None
    is_active: bool = True

    @field_validator('email')
    def validate_drfirst_email(cls, v):
        """Ensure email is from DrFirst domain"""
        if not str(v).endswith('@drfirst.com'):
            raise ValueError('Email must be from DrFirst domain (@drfirst.com)')
        return v

    @field_validator('display_name')
    def validate_display_name(cls, v):
        """Validate display name doesn't contain special characters"""
        if v is not None and not re.match(r'^[a-zA-Z0-9\s\-\.]+$', v):
            raise ValueError('Display name can only contain letters, numbers, spaces, hyphens, and periods')
        return v

    @model_validator(mode='after')
    def updated_at_not_before_created_at(self):
        """Ensure updated_at is not before created_at"""
        if self.updated_at < self.created_at:
            raise ValueError('updated_at cannot be before created_at')
        return self


class RelevantLink(BaseModel):
    """Model for validating relevant links"""
    
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="Link name/title"
    )
    url: HttpUrl = Field(..., description="Valid URL")

    @field_validator('name')
    def validate_name_not_empty(cls, v):
        """Ensure name is not just whitespace"""
        if not v.strip():
            raise ValueError('Link name cannot be empty or just whitespace')
        return v.strip()


class BusinessCaseRequest(BaseModel):
    """Business case generation request model"""

    title: str = Field(
        ..., 
        min_length=3, 
        max_length=200,
        description="Business case title"
    )
    description: str = Field(
        ..., 
        min_length=10, 
        max_length=5000,
        description="Business case description"
    )
    requester_uid: str = Field(
        ..., 
        min_length=1, 
        max_length=128,
        pattern=r'^[a-zA-Z0-9_-]+$',
        description="UID of the user requesting the business case"
    )
    requirements: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Business requirements"
    )
    priority: str = Field(
        "medium", 
        pattern=r'^(low|medium|high|critical)$',
        description="Priority level: low, medium, high, or critical"
    )
    deadline: Optional[datetime] = Field(None, description="Target completion date")
    relevant_links: Optional[List[RelevantLink]] = Field(
        None, 
        max_length=10,
        description="List of relevant links (max 10)"
    )

    @field_validator('title')
    def validate_title(cls, v):
        """Validate title is not just whitespace and doesn't contain special chars"""
        title = v.strip()
        if not title:
            raise ValueError('Title cannot be empty or just whitespace')
        if not re.match(r'^[a-zA-Z0-9\s\-\.\(\)\_\:]+$', title):
            raise ValueError('Title contains invalid characters')
        return title

    @field_validator('description')
    def validate_description(cls, v):
        """Validate description is meaningful"""
        desc = v.strip()
        if not desc:
            raise ValueError('Description cannot be empty or just whitespace')
        # Check for minimum word count
        words = desc.split()
        if len(words) < 3:
            raise ValueError('Description must contain at least 3 words')
        return desc

    @field_validator('deadline')
    def validate_deadline(cls, v):
        """Ensure deadline is in the future"""
        if v is not None and v <= datetime.now(timezone.utc):
            raise ValueError('Deadline must be in the future')
        return v

    @field_validator('requirements')
    def validate_requirements(cls, v):
        """Validate requirements dictionary"""
        if not isinstance(v, dict):
            raise ValueError('Requirements must be a dictionary')
        # Limit the size of requirements to prevent abuse
        if len(str(v)) > 10000:  # 10KB limit
            raise ValueError('Requirements data is too large (max 10KB)')
        return v


class BusinessCase(BaseModel):
    """Generated business case model"""

    id: Optional[str] = Field(None, description="Document ID")
    request_data: BusinessCaseRequest = Field(..., description="Original request data")
    generated_content: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Generated business case content"
    )
    status: JobStatus = Field(JobStatus.PENDING, description="Generation status")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    generated_by_agents: List[str] = Field(
        default_factory=list, 
        max_length=20,
        description="List of agents that contributed (max 20)"
    )

    @field_validator('generated_content')
    def validate_generated_content(cls, v):
        """Validate generated content size"""
        if len(str(v)) > 100000:  # 100KB limit
            raise ValueError('Generated content is too large (max 100KB)')
        return v

    @model_validator(mode='after')
    def validate_timestamps_and_status(self):
        """Validate timestamp relationships and status consistency"""
        # Ensure updated_at is not before created_at
        if self.updated_at < self.created_at:
            raise ValueError('updated_at cannot be before created_at')
        
        # Validate completed_at logic
        if self.completed_at is not None:
            # completed_at should not be before created_at
            if self.completed_at < self.created_at:
                raise ValueError('completed_at cannot be before created_at')
            # If completed_at is set, status should be completed or failed
            if self.status not in [JobStatus.COMPLETED, JobStatus.FAILED]:
                raise ValueError('completed_at can only be set when status is completed or failed')
        return self

    @field_validator('generated_by_agents')
    def validate_agent_names(cls, v):
        """Validate agent names are properly formatted"""
        for agent_name in v:
            if not isinstance(agent_name, str) or not agent_name.strip():
                raise ValueError('Agent names must be non-empty strings')
            if not re.match(r'^[a-zA-Z0-9_-]+$', agent_name.strip()):
                raise ValueError('Agent names can only contain letters, numbers, underscores, and hyphens')
        return [name.strip() for name in v]


class Job(BaseModel):
    """Job tracking model"""

    id: Optional[str] = Field(None, description="Job ID")
    job_type: str = Field(
        ..., 
        min_length=1, 
        max_length=50,
        pattern=r'^[a-zA-Z0-9_-]+$',
        description="Type of job"
    )
    status: JobStatus = Field(JobStatus.PENDING, description="Job status")
    user_uid: str = Field(
        ..., 
        min_length=1, 
        max_length=128,
        pattern=r'^[a-zA-Z0-9_-]+$',
        description="UID of the user who created the job"
    )
    business_case_id: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=128,
        description="Associated business case ID"
    )
    progress: int = Field(
        0, 
        ge=0, 
        le=100, 
        description="Progress percentage (0-100)"
    )
    error_message: Optional[str] = Field(
        None, 
        max_length=1000,
        description="Error message if failed"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Additional job metadata"
    )

    @field_validator('metadata')
    def validate_metadata_size(cls, v):
        """Limit metadata size to prevent abuse"""
        if len(str(v)) > 5000:  # 5KB limit
            raise ValueError('Job metadata is too large (max 5KB)')
        return v

    @model_validator(mode='after')
    def validate_job_timestamps_and_status(self):
        """Validate job timestamp relationships and status consistency"""
        # Ensure updated_at is not before created_at
        if self.updated_at < self.created_at:
            raise ValueError('updated_at cannot be before created_at')
        
        # Validate started_at timing
        if self.started_at is not None:
            if self.started_at < self.created_at:
                raise ValueError('started_at cannot be before created_at')
            # If started_at is set, status should not be pending
            if self.status == JobStatus.PENDING:
                raise ValueError('started_at cannot be set when status is pending')
        
        # Validate completed_at timing and status consistency
        if self.completed_at is not None:
            if self.completed_at < self.created_at:
                raise ValueError('completed_at cannot be before created_at')
            if self.started_at and self.completed_at < self.started_at:
                raise ValueError('completed_at cannot be before started_at')
            # If completed_at is set, status should be completed, failed, or cancelled
            if self.status not in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                raise ValueError('completed_at can only be set when status is completed, failed, or cancelled')
            # If status is completed, progress should be 100
            if self.status == JobStatus.COMPLETED and self.progress != 100:
                raise ValueError('Progress must be 100 when status is completed')
        
        return self
