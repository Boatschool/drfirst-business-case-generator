"""
Agent-related API routes for the DrFirst Business Case Generator
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any

# Import the OrchestratorAgent
from app.agents.orchestrator_agent import OrchestratorAgent

router = APIRouter()

# Initialize the OrchestratorAgent instance (can be improved with dependency injection later)
orchestrator = OrchestratorAgent()

@router.get("/", summary="List all available agents")
async def list_agents():
    """Get a list of all available agents"""
    return {
        "agents": [
            {"id": "orchestrator", "name": "Orchestrator Agent", "status": "available"},
            {"id": "product_manager", "name": "Product Manager Agent", "status": "available"},
            {"id": "architect", "name": "Architect Agent", "status": "available"}
        ]
    }

@router.post("/generate", summary="Generate business case")
async def generate_business_case(request_data: dict):
    """Generate a business case using the agent system"""
    # TODO: Implement business case generation logic
    return {"message": "Business case generation started", "job_id": "placeholder"}

@router.get("/status/{job_id}", summary="Get generation status")
async def get_generation_status(job_id: str):
    """Get the status of a business case generation job"""
    # TODO: Implement status checking logic
    return {"job_id": job_id, "status": "in_progress", "progress": 50}

@router.post("/invoke", summary="Invoke an agent action")
async def invoke_agent_action(request_data: Dict[str, Any]):
    """
    Invoke a specific action on an agent, typically the Orchestrator.
    Expects a JSON body with 'request_type' and 'payload'.
    Example for echo: {"request_type": "echo", "payload": {"input_text": "Hello World"}}
    """
    request_type = request_data.get("request_type")
    payload = request_data.get("payload")

    if not request_type:
        raise HTTPException(status_code=400, detail="'request_type' field is required.")
    if payload is None: # payload can be an empty dict, but not None
        raise HTTPException(status_code=400, detail="'payload' field is required.")

    try:
        # Delegate to the OrchestratorAgent's handle_request method
        response = await orchestrator.handle_request(request_type, payload)
        
        if response.get("status") == "error":
            # You might want to map agent errors to specific HTTP status codes
            raise HTTPException(status_code=400, detail=response.get("message", "Agent processing error"))
        
        return response
    except HTTPException as http_exc:
        raise http_exc # Re-raise HTTPException so FastAPI handles it
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 