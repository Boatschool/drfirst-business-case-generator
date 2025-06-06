"""
Agent-related API routes for the DrFirst Business Case Generator
"""

import logging
from fastapi import APIRouter, HTTPException, Depends, Path, Query, Request
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator

from app.middleware.rate_limiter import limiter

logger = logging.getLogger(__name__)

# Import the OrchestratorAgent
from app.agents.orchestrator_agent import OrchestratorAgent

# Import the authentication dependency
from app.auth.firebase_auth import get_current_active_user

router = APIRouter()

# Initialize the OrchestratorAgent instance (can be improved with dependency injection later)
orchestrator = OrchestratorAgent()


# Pydantic models for request validation
class BusinessCaseGenerationRequest(BaseModel):
    """Request model for generating a business case"""
    
    title: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Title for the business case"
    )
    requirements: Dict[str, Any] = Field(
        ...,
        description="Business requirements and specifications"
    )
    priority: Optional[str] = Field(
        "medium",
        pattern=r'^(low|medium|high|critical)$',
        description="Priority level: low, medium, high, or critical"
    )
    deadline: Optional[str] = Field(
        None,
        description="Target deadline in ISO format (optional)"
    )

    @validator('title')
    def validate_title(cls, v):
        """Validate title content"""
        title = v.strip()
        if not title:
            raise ValueError('Title cannot be empty or just whitespace')
        return title

    @validator('requirements')
    def validate_requirements(cls, v):
        """Validate requirements structure and content"""
        if not isinstance(v, dict):
            raise ValueError('Requirements must be a dictionary')
        
        if not v:
            raise ValueError('Requirements cannot be empty')
        
        # Limit size to prevent abuse
        if len(str(v)) > 50000:  # 50KB limit
            raise ValueError('Requirements data is too large (max 50KB)')
        
        # Check for required fields
        required_fields = ['description']
        missing_fields = [field for field in required_fields if field not in v or not str(v[field]).strip()]
        if missing_fields:
            raise ValueError(f'Requirements must include: {", ".join(missing_fields)}')
        
        return v


class AgentActionRequest(BaseModel):
    """Request model for invoking agent actions"""
    
    request_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        pattern=r'^[a-zA-Z0-9_]+$',
        description="Type of request/action to perform"
    )
    payload: Dict[str, Any] = Field(
        ...,
        description="Payload data for the action"
    )

    @validator('payload')
    def validate_payload(cls, v):
        """Validate payload structure"""
        if not isinstance(v, dict):
            raise ValueError('Payload must be a dictionary')
        
        # Limit payload size
        if len(str(v)) > 10000:  # 10KB limit
            raise ValueError('Payload data is too large (max 10KB)')
        
        return v


# Response models
class AgentListResponse(BaseModel):
    """Response model for listing agents"""
    agents: List[Dict[str, str]] = Field(..., description="List of available agents")


class GenerationResponse(BaseModel):
    """Response model for business case generation"""
    message: str = Field(..., description="Response message")
    job_id: Optional[str] = Field(None, description="Job tracking ID")
    status: str = Field(..., description="Operation status")


class JobStatusResponse(BaseModel):
    """Response model for job status"""
    job_id: str = Field(..., description="Job tracking ID")
    status: str = Field(..., description="Current job status")
    progress: int = Field(..., ge=0, le=100, description="Progress percentage")
    business_case_id: Optional[str] = Field(None, description="Associated business case ID")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: Optional[str] = Field(None, description="Job creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")


@router.get(
    "/", 
    response_model=AgentListResponse,
    summary="List all available agents"
)
@limiter.limit("30/minute")
async def list_agents(request: Request):
    """Get a list of all available agents"""
    return AgentListResponse(
        agents=[
            {"id": "orchestrator", "name": "Orchestrator Agent", "status": "available"},
            {
                "id": "product_manager",
                "name": "Product Manager Agent",
                "status": "available",
            },
            {"id": "architect", "name": "Architect Agent", "status": "available"},
        ]
    )


@router.post(
    "/generate", 
    response_model=GenerationResponse,
    summary="Generate business case"
)
@limiter.limit("5/minute")  # Strict limit for resource-intensive operations
async def generate_business_case(
    request: Request,
    request_data: BusinessCaseGenerationRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Generate a business case using the agent system"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found in token.")
        
        # Use the orchestrator to handle business case generation with job tracking
        response = await orchestrator.handle_request(
            "generate_business_case", 
            {
                "requirements": request_data.requirements, 
                "title": request_data.title,
                "priority": request_data.priority,
                "deadline": request_data.deadline
            }, 
            user_id
        )
        
        if response.get("status") == "error":
            raise HTTPException(
                status_code=400,
                detail=response.get("message", "Business case generation failed"),
            )
        
        return GenerationResponse(
            message=response.get("message", "Business case generation started"),
            job_id=response.get("job_id"),
            status="success"
        )
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error in generate_business_case: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/status/{job_id}", 
    response_model=JobStatusResponse,
    summary="Get generation status"
)
@limiter.limit("20/minute")
async def get_generation_status(
    request: Request,
    job_id: str = Path(
        ...,
        min_length=1,
        max_length=128,
        description="Job tracking ID"
    ),
    current_user: dict = Depends(get_current_active_user)
):
    """Get the status of a business case generation job"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found in token.")
        
        # Use the orchestrator to get job status
        response = await orchestrator.handle_request(
            "get_job_status", 
            {"job_id": job_id}, 
            user_id
        )
        
        if response.get("status") == "error":
            raise HTTPException(
                status_code=404 if "not found" in response.get("message", "").lower() else 400,
                detail=response.get("message", "Failed to retrieve job status"),
            )
        
        job_result = response.get("result", {})
        return JobStatusResponse(
            job_id=job_id,
            status=job_result.get("status", "unknown"),
            progress=job_result.get("progress", 0),
            business_case_id=job_result.get("business_case_id"),
            error_message=job_result.get("error_message"),
            created_at=job_result.get("created_at"),
            updated_at=job_result.get("updated_at")
        )
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error in get_generation_status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/invoke", 
    summary="Invoke an agent action"
)
async def invoke_agent_action(
    request_data: AgentActionRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Invoke a specific action on an agent, typically the Orchestrator.
    Requires Firebase ID Token authentication.
    Example for echo: {"request_type": "echo", "payload": {"input_text": "Hello World"}}
    """
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found in token.")

        logger.info(f"Action '{request_data.request_type}' invoked by user: {current_user.get('email')}")

        # Delegate to the OrchestratorAgent's handle_request method, passing user_id
        response = await orchestrator.handle_request(
            request_data.request_type, 
            request_data.payload, 
            user_id
        )

        if response.get("status") == "error":
            # Map agent errors to specific HTTP status codes
            raise HTTPException(
                status_code=400,
                detail=response.get("message", "Agent processing error"),
            )

        return response
        
    except HTTPException as http_exc:
        raise http_exc  # Re-raise HTTPException so FastAPI handles it
    except Exception as e:
        logger.error(f"Error in invoke_agent_action: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
