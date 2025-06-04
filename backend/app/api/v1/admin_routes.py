"""
Admin API routes for the DrFirst Business Case Generator
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from typing import List, Dict, Any
import asyncio
from google.cloud import firestore
from app.auth.firebase_auth import get_current_active_user
from app.core.config import settings
from pydantic import BaseModel

router = APIRouter()
security = HTTPBearer()

# Pydantic models for response structures
class RateCard(BaseModel):
    """Rate card model for API responses"""
    id: str
    name: str
    description: str
    isActive: bool
    defaultOverallRate: float
    roles: List[Dict[str, Any]]
    created_at: str
    updated_at: str

class PricingTemplate(BaseModel):
    """Pricing template model for API responses"""
    id: str
    name: str
    description: str
    version: str
    structureDefinition: Dict[str, Any]
    created_at: str
    updated_at: str

# Initialize Firestore client
db = None
try:
    db = firestore.Client(project=settings.firebase_project_id)
    print("Admin routes: Firestore client initialized successfully.")
except Exception as e:
    print(f"Admin routes: Failed to initialize Firestore client: {e}")

@router.get("/rate-cards", response_model=List[Dict[str, Any]], summary="List all rate cards")
async def list_rate_cards(current_user: dict = Depends(get_current_active_user)):
    """Get a list of all rate cards (admin only)"""
    if not db:
        raise HTTPException(
            status_code=500,
            detail="Database connection not available"
        )
    
    try:
        # Fetch all documents from rateCards collection
        rate_cards_ref = db.collection("rateCards")
        docs = await asyncio.to_thread(lambda: list(rate_cards_ref.stream()))
        
        rate_cards = []
        for doc in docs:
            rate_card_data = doc.to_dict()
            rate_card_data['id'] = doc.id  # Add document ID
            rate_cards.append(rate_card_data)
        
        print(f"[AdminAPI] Retrieved {len(rate_cards)} rate cards for user: {current_user.get('email', 'unknown')}")
        return rate_cards
        
    except Exception as e:
        print(f"[AdminAPI] Error fetching rate cards: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch rate cards: {str(e)}"
        )

@router.get("/pricing-templates", response_model=List[Dict[str, Any]], summary="List all pricing templates")
async def list_pricing_templates(current_user: dict = Depends(get_current_active_user)):
    """Get a list of all pricing templates (admin only)"""
    if not db:
        raise HTTPException(
            status_code=500,
            detail="Database connection not available"
        )
    
    try:
        # Fetch all documents from pricingTemplates collection
        templates_ref = db.collection("pricingTemplates")
        docs = await asyncio.to_thread(lambda: list(templates_ref.stream()))
        
        pricing_templates = []
        for doc in docs:
            template_data = doc.to_dict()
            template_data['id'] = doc.id  # Add document ID
            pricing_templates.append(template_data)
        
        print(f"[AdminAPI] Retrieved {len(pricing_templates)} pricing templates for user: {current_user.get('email', 'unknown')}")
        return pricing_templates
        
    except Exception as e:
        print(f"[AdminAPI] Error fetching pricing templates: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch pricing templates: {str(e)}"
        )

# Legacy endpoints (kept for backwards compatibility)
@router.get("/users", summary="List all users")
async def list_users(current_user: dict = Depends(get_current_active_user)):
    """Get a list of all users (admin only)"""
    # TODO: Implement admin user listing
    return {"message": "Admin users endpoint - implementation pending"}

@router.get("/analytics", summary="Get system analytics")
async def get_analytics(current_user: dict = Depends(get_current_active_user)):
    """Get system usage analytics (admin only)"""
    # TODO: Implement analytics retrieval
    return {"message": "Admin analytics endpoint - implementation pending"}

@router.post("/agent/deploy", summary="Deploy agent updates")
async def deploy_agent_updates(current_user: dict = Depends(get_current_active_user)):
    """Deploy updates to the agent system (admin only)"""
    # TODO: Implement agent deployment logic
    return {"message": "Agent deployment endpoint - implementation pending"} 