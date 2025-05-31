"""
Agent-related API routes for the DrFirst Business Case Generator
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List

router = APIRouter()

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