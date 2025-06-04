"""
Pydantic models for Firestore database interactions
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class UserRole(str, Enum):
    """User roles in the system"""
    ADMIN = "ADMIN"
    USER = "USER"
    VIEWER = "VIEWER"

class JobStatus(str, Enum):
    """Job status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class User(BaseModel):
    """User model for Firestore"""
    uid: str = Field(..., description="Firebase UID")
    email: str = Field(..., description="User email address")
    display_name: Optional[str] = Field(None, description="User display name")
    systemRole: UserRole = Field(UserRole.USER, description="User system role")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    is_active: bool = True

class BusinessCaseRequest(BaseModel):
    """Business case generation request model"""
    title: str = Field(..., description="Business case title")
    description: str = Field(..., description="Business case description")
    requester_uid: str = Field(..., description="UID of the user requesting the business case")
    requirements: Dict[str, Any] = Field(default_factory=dict, description="Business requirements")
    priority: str = Field("medium", description="Priority level")
    deadline: Optional[datetime] = Field(None, description="Target completion date")

class BusinessCase(BaseModel):
    """Generated business case model"""
    id: Optional[str] = Field(None, description="Document ID")
    request_data: BusinessCaseRequest = Field(..., description="Original request data")
    generated_content: Dict[str, Any] = Field(default_factory=dict, description="Generated business case content")
    status: JobStatus = Field(JobStatus.PENDING, description="Generation status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    generated_by_agents: List[str] = Field(default_factory=list, description="List of agents that contributed")

class Job(BaseModel):
    """Job tracking model"""
    id: Optional[str] = Field(None, description="Job ID")
    job_type: str = Field(..., description="Type of job")
    status: JobStatus = Field(JobStatus.PENDING, description="Job status")
    user_uid: str = Field(..., description="UID of the user who created the job")
    business_case_id: Optional[str] = Field(None, description="Associated business case ID")
    progress: int = Field(0, description="Progress percentage (0-100)")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional job metadata") 