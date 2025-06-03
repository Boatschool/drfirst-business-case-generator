"""
Agent Prompt model for configurable agent prompts.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class AgentPromptVersion(BaseModel):
    """A specific version of an agent prompt."""
    version: str = Field(..., description="Version identifier (e.g., '1.0.0', '2.1.3')")
    prompt_template: str = Field(..., description="The actual prompt template with placeholders")
    description: str = Field(..., description="Description of this prompt version")
    created_at: datetime = Field(default_factory=datetime.now, description="When this version was created")
    created_by: str = Field(..., description="User ID who created this version")
    is_active: bool = Field(default=False, description="Whether this version is currently active")
    performance_notes: Optional[str] = Field(None, description="Notes about this version's performance")

class AgentPrompt(BaseModel):
    """
    Configurable prompt template for AI agents.
    Stored in Firestore for easy updates without code deployment.
    """
    prompt_id: str = Field(..., description="Unique identifier for this prompt")
    agent_name: str = Field(..., description="Name of the agent this prompt belongs to")
    agent_function: str = Field(..., description="Specific function/task this prompt handles")
    
    # Prompt template with placeholders
    current_version: str = Field(..., description="Currently active version identifier")
    versions: List[AgentPromptVersion] = Field(default_factory=list, description="All versions of this prompt")
    
    # Metadata
    title: str = Field(..., description="Human-readable title for this prompt")
    description: str = Field(..., description="Description of what this prompt does")
    category: str = Field(default="general", description="Category (e.g., 'prd_generation', 'system_design')")
    
    # Configuration
    placeholders: List[str] = Field(default_factory=list, description="List of placeholder variables in the template")
    ai_model_config: Dict[str, Any] = Field(default_factory=dict, description="Model-specific configuration (temperature, tokens, etc.)")
    
    # Management
    is_enabled: bool = Field(default=True, description="Whether this prompt is enabled")
    created_at: datetime = Field(default_factory=datetime.now, description="When this prompt was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="When this prompt was last updated")
    created_by: str = Field(..., description="User ID who created this prompt")
    last_updated_by: str = Field(..., description="User ID who last updated this prompt")
    
    # Usage tracking
    usage_count: int = Field(default=0, description="How many times this prompt has been used")
    last_used_at: Optional[datetime] = Field(None, description="When this prompt was last used")

class AgentPromptCreate(BaseModel):
    """Model for creating a new agent prompt."""
    agent_name: str
    agent_function: str
    title: str
    description: str
    prompt_template: str
    category: str = "general"
    placeholders: List[str] = []
    ai_model_config: Dict[str, Any] = {}
    version_description: str = "Initial version"

class AgentPromptUpdate(BaseModel):
    """Model for updating an existing agent prompt."""
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_enabled: Optional[bool] = None
    ai_model_config: Optional[Dict[str, Any]] = None

class AgentPromptVersionCreate(BaseModel):
    """Model for creating a new version of an existing prompt."""
    prompt_template: str
    description: str
    placeholders: List[str] = []
    ai_model_config: Dict[str, Any] = {}
    make_active: bool = False 