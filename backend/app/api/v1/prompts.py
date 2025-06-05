"""
API endpoints for managing agent prompts.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from ...auth.firebase_auth import get_current_user
from ...services.prompt_service import PromptService
from ...models.agent_prompt import (
    AgentPrompt,
    AgentPromptCreate,
    AgentPromptUpdate,
    AgentPromptVersionCreate,
)
from google.cloud import firestore

router = APIRouter()


def get_prompt_service() -> PromptService:
    """Get PromptService instance."""
    db = firestore.Client()
    return PromptService(db)


@router.get("/", response_model=List[AgentPrompt])
async def list_prompts(
    agent_name: str = None,
    current_user: dict = Depends(get_current_user),
    prompt_service: PromptService = Depends(get_prompt_service),
):
    """List all agent prompts, optionally filtered by agent name."""
    try:
        prompts = await prompt_service.list_prompts(agent_name=agent_name)
        return prompts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list prompts: {str(e)}",
        )


@router.get("/{prompt_id}", response_model=AgentPrompt)
async def get_prompt(
    prompt_id: str,
    current_user: dict = Depends(get_current_user),
    prompt_service: PromptService = Depends(get_prompt_service),
):
    """Get a specific agent prompt by ID."""
    try:
        prompt = await prompt_service.get_prompt_by_id(prompt_id)
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found"
            )
        return prompt
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get prompt: {str(e)}",
        )


@router.post("/", response_model=dict)
async def create_prompt(
    prompt_data: AgentPromptCreate,
    current_user: dict = Depends(get_current_user),
    prompt_service: PromptService = Depends(get_prompt_service),
):
    """Create a new agent prompt."""
    try:
        prompt_id = await prompt_service.create_prompt(prompt_data, current_user["uid"])
        return {"prompt_id": prompt_id, "message": "Prompt created successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create prompt: {str(e)}",
        )


@router.put("/{prompt_id}", response_model=dict)
async def update_prompt(
    prompt_id: str,
    update_data: AgentPromptUpdate,
    current_user: dict = Depends(get_current_user),
    prompt_service: PromptService = Depends(get_prompt_service),
):
    """Update an existing agent prompt."""
    try:
        success = await prompt_service.update_prompt(
            prompt_id, update_data, current_user["uid"]
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found"
            )
        return {"message": "Prompt updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update prompt: {str(e)}",
        )


@router.post("/{prompt_id}/versions", response_model=dict)
async def add_prompt_version(
    prompt_id: str,
    version_data: AgentPromptVersionCreate,
    current_user: dict = Depends(get_current_user),
    prompt_service: PromptService = Depends(get_prompt_service),
):
    """Add a new version to an existing prompt."""
    try:
        success = await prompt_service.add_prompt_version(
            prompt_id, version_data, current_user["uid"]
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found"
            )
        return {"message": "Prompt version added successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add prompt version: {str(e)}",
        )


@router.get("/{agent_name}/{agent_function}/active", response_model=dict)
async def get_active_prompt_template(
    agent_name: str,
    agent_function: str,
    current_user: dict = Depends(get_current_user),
    prompt_service: PromptService = Depends(get_prompt_service),
):
    """Get the active prompt template for an agent function."""
    try:
        template = await prompt_service.get_active_prompt_template(
            agent_name, agent_function
        )
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No active prompt found for {agent_name}.{agent_function}",
            )
        return {
            "agent_name": agent_name,
            "agent_function": agent_function,
            "template": template,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get active prompt template: {str(e)}",
        )


@router.post("/render", response_model=dict)
async def render_prompt_template(
    agent_name: str,
    agent_function: str,
    variables: dict,
    current_user: dict = Depends(get_current_user),
    prompt_service: PromptService = Depends(get_prompt_service),
):
    """Render a prompt template with provided variables."""
    try:
        rendered = await prompt_service.render_prompt(
            agent_name, agent_function, variables
        )
        if not rendered:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No active prompt found for {agent_name}.{agent_function} or missing variables",
            )
        return {
            "agent_name": agent_name,
            "agent_function": agent_function,
            "rendered_prompt": rendered,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to render prompt: {str(e)}",
        )
