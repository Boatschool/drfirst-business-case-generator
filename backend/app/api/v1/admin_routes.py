"""
Admin API routes for the DrFirst Business Case Generator
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from typing import List, Dict, Any, Optional
import asyncio
import uuid
from datetime import datetime, timezone
from google.cloud import firestore
from app.auth.firebase_auth import require_admin_role
from app.core.config import settings
from pydantic import BaseModel, Field

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

# Pydantic models for request bodies
class RoleRate(BaseModel):
    """Role with hourly rate"""
    roleName: str = Field(..., description="Name of the role")
    hourlyRate: float = Field(..., gt=0, description="Hourly rate for the role")

class CreateRateCardRequest(BaseModel):
    """Request model for creating a new rate card"""
    name: str = Field(..., min_length=1, max_length=100, description="Name of the rate card")
    description: str = Field(..., min_length=1, max_length=500, description="Description of the rate card")
    isActive: bool = Field(True, description="Whether the rate card is active")
    defaultOverallRate: float = Field(..., gt=0, description="Default overall hourly rate")
    roles: List[RoleRate] = Field(default=[], description="List of roles with specific rates")

class UpdateRateCardRequest(BaseModel):
    """Request model for updating an existing rate card"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Name of the rate card")
    description: Optional[str] = Field(None, min_length=1, max_length=500, description="Description of the rate card")
    isActive: Optional[bool] = Field(None, description="Whether the rate card is active")
    defaultOverallRate: Optional[float] = Field(None, gt=0, description="Default overall hourly rate")
    roles: Optional[List[RoleRate]] = Field(None, description="List of roles with specific rates")

# Pydantic models for Pricing Template operations
class CreatePricingTemplateRequest(BaseModel):
    """Request model for creating a new pricing template"""
    name: str = Field(..., min_length=1, max_length=100, description="Name of the pricing template")
    description: str = Field(..., min_length=1, max_length=500, description="Description of the pricing template")
    version: str = Field(..., min_length=1, max_length=20, description="Version of the pricing template")
    structureDefinition: Dict[str, Any] = Field(..., description="Structure definition (JSON object)")

class UpdatePricingTemplateRequest(BaseModel):
    """Request model for updating an existing pricing template"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Name of the pricing template")
    description: Optional[str] = Field(None, min_length=1, max_length=500, description="Description of the pricing template")
    version: Optional[str] = Field(None, min_length=1, max_length=20, description="Version of the pricing template")
    structureDefinition: Optional[Dict[str, Any]] = Field(None, description="Structure definition (JSON object)")

# Initialize Firestore client
db = None
try:
    db = firestore.Client(project=settings.firebase_project_id)
    print("Admin routes: Firestore client initialized successfully.")
except Exception as e:
    print(f"Admin routes: Failed to initialize Firestore client: {e}")

# Rate Cards CRUD Operations

@router.get("/rate-cards", response_model=List[Dict[str, Any]], summary="List all rate cards")
async def list_rate_cards(current_user: dict = Depends(require_admin_role)):
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

@router.post("/rate-cards", response_model=Dict[str, Any], summary="Create a new rate card")
async def create_rate_card(
    rate_card_data: CreateRateCardRequest,
    current_user: dict = Depends(require_admin_role)
):
    """Create a new rate card (admin only)"""
    if not db:
        raise HTTPException(
            status_code=500,
            detail="Database connection not available"
        )
    
    try:
        # Generate unique ID for the new rate card
        card_id = str(uuid.uuid4())
        current_time = datetime.now(timezone.utc).isoformat()
        
        # Convert RoleRate objects to dictionaries
        roles_data = [role.model_dump() for role in rate_card_data.roles]
        
        # Prepare the rate card document
        rate_card_doc = {
            "name": rate_card_data.name,
            "description": rate_card_data.description,
            "isActive": rate_card_data.isActive,
            "defaultOverallRate": rate_card_data.defaultOverallRate,
            "roles": roles_data,
            "created_at": current_time,
            "updated_at": current_time,
            "created_by": current_user.get('email', 'unknown'),
            "updated_by": current_user.get('email', 'unknown')
        }
        
        # Save to Firestore
        rate_cards_ref = db.collection("rateCards")
        await asyncio.to_thread(rate_cards_ref.document(card_id).set, rate_card_doc)
        
        # Return the created rate card with ID
        rate_card_doc['id'] = card_id
        
        print(f"[AdminAPI] Created new rate card '{rate_card_data.name}' with ID {card_id} by user: {current_user.get('email', 'unknown')}")
        return rate_card_doc
        
    except Exception as e:
        print(f"[AdminAPI] Error creating rate card: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create rate card: {str(e)}"
        )

@router.put("/rate-cards/{card_id}", response_model=Dict[str, Any], summary="Update an existing rate card")
async def update_rate_card(
    card_id: str,
    rate_card_data: UpdateRateCardRequest,
    current_user: dict = Depends(require_admin_role)
):
    """Update an existing rate card (admin only)"""
    if not db:
        raise HTTPException(
            status_code=500,
            detail="Database connection not available"
        )
    
    try:
        # Check if rate card exists
        rate_cards_ref = db.collection("rateCards")
        doc_ref = rate_cards_ref.document(card_id)
        doc = await asyncio.to_thread(doc_ref.get)
        
        if not doc.exists:
            raise HTTPException(
                status_code=404,
                detail=f"Rate card with ID {card_id} not found"
            )
        
        # Prepare update data (only include non-None fields)
        update_data = {}
        if rate_card_data.name is not None:
            update_data["name"] = rate_card_data.name
        if rate_card_data.description is not None:
            update_data["description"] = rate_card_data.description
        if rate_card_data.isActive is not None:
            update_data["isActive"] = rate_card_data.isActive
        if rate_card_data.defaultOverallRate is not None:
            update_data["defaultOverallRate"] = rate_card_data.defaultOverallRate
        if rate_card_data.roles is not None:
            update_data["roles"] = [role.model_dump() for role in rate_card_data.roles]
        
        # Always update timestamp and user
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        update_data["updated_by"] = current_user.get('email', 'unknown')
        
        # Update the document
        await asyncio.to_thread(doc_ref.update, update_data)
        
        # Fetch and return the updated document
        updated_doc = await asyncio.to_thread(doc_ref.get)
        updated_data = updated_doc.to_dict()
        updated_data['id'] = card_id
        
        print(f"[AdminAPI] Updated rate card {card_id} by user: {current_user.get('email', 'unknown')}")
        return updated_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[AdminAPI] Error updating rate card: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update rate card: {str(e)}"
        )

@router.delete("/rate-cards/{card_id}", response_model=Dict[str, str], summary="Delete a rate card")
async def delete_rate_card(
    card_id: str,
    current_user: dict = Depends(require_admin_role)
):
    """Delete a rate card (admin only)"""
    if not db:
        raise HTTPException(
            status_code=500,
            detail="Database connection not available"
        )
    
    try:
        # Check if rate card exists
        rate_cards_ref = db.collection("rateCards")
        doc_ref = rate_cards_ref.document(card_id)
        doc = await asyncio.to_thread(doc_ref.get)
        
        if not doc.exists:
            raise HTTPException(
                status_code=404,
                detail=f"Rate card with ID {card_id} not found"
            )
        
        # Get rate card name for logging
        rate_card_data = doc.to_dict()
        rate_card_name = rate_card_data.get('name', 'Unknown')
        
        # Delete the document
        await asyncio.to_thread(doc_ref.delete)
        
        print(f"[AdminAPI] Deleted rate card '{rate_card_name}' (ID: {card_id}) by user: {current_user.get('email', 'unknown')}")
        return {
            "message": f"Rate card '{rate_card_name}' deleted successfully",
            "deleted_id": card_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[AdminAPI] Error deleting rate card: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete rate card: {str(e)}"
        )

@router.get("/pricing-templates", response_model=List[Dict[str, Any]], summary="List all pricing templates")
async def list_pricing_templates(current_user: dict = Depends(require_admin_role)):
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

@router.post("/pricing-templates", response_model=Dict[str, Any], summary="Create a new pricing template")
async def create_pricing_template(
    template_data: CreatePricingTemplateRequest,
    current_user: dict = Depends(require_admin_role)
):
    """Create a new pricing template (admin only)"""
    if not db:
        raise HTTPException(
            status_code=500,
            detail="Database connection not available"
        )
    
    try:
        # Generate unique ID for the new pricing template
        template_id = str(uuid.uuid4())
        current_time = datetime.now(timezone.utc).isoformat()
        
        # Prepare the pricing template document
        template_doc = {
            "name": template_data.name,
            "description": template_data.description,
            "version": template_data.version,
            "structureDefinition": template_data.structureDefinition,
            "created_at": current_time,
            "updated_at": current_time,
            "created_by": current_user.get('email', 'unknown'),
            "updated_by": current_user.get('email', 'unknown')
        }
        
        # Save to Firestore
        templates_ref = db.collection("pricingTemplates")
        await asyncio.to_thread(templates_ref.document(template_id).set, template_doc)
        
        # Return the created template with ID
        template_doc['id'] = template_id
        
        print(f"[AdminAPI] Created new pricing template '{template_data.name}' with ID {template_id} by user: {current_user.get('email', 'unknown')}")
        return template_doc
        
    except Exception as e:
        print(f"[AdminAPI] Error creating pricing template: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create pricing template: {str(e)}"
        )

@router.put("/pricing-templates/{template_id}", response_model=Dict[str, Any], summary="Update an existing pricing template")
async def update_pricing_template(
    template_id: str,
    template_data: UpdatePricingTemplateRequest,
    current_user: dict = Depends(require_admin_role)
):
    """Update an existing pricing template (admin only)"""
    if not db:
        raise HTTPException(
            status_code=500,
            detail="Database connection not available"
        )
    
    try:
        # Check if pricing template exists
        templates_ref = db.collection("pricingTemplates")
        doc_ref = templates_ref.document(template_id)
        doc = await asyncio.to_thread(doc_ref.get)
        
        if not doc.exists:
            raise HTTPException(
                status_code=404,
                detail=f"Pricing template with ID {template_id} not found"
            )
        
        # Prepare update data (only include non-None fields)
        update_data = {}
        if template_data.name is not None:
            update_data["name"] = template_data.name
        if template_data.description is not None:
            update_data["description"] = template_data.description
        if template_data.version is not None:
            update_data["version"] = template_data.version
        if template_data.structureDefinition is not None:
            update_data["structureDefinition"] = template_data.structureDefinition
        
        # Always update timestamp and user
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        update_data["updated_by"] = current_user.get('email', 'unknown')
        
        # Update the document
        await asyncio.to_thread(doc_ref.update, update_data)
        
        # Fetch and return the updated document
        updated_doc = await asyncio.to_thread(doc_ref.get)
        updated_data = updated_doc.to_dict()
        updated_data['id'] = template_id
        
        print(f"[AdminAPI] Updated pricing template {template_id} by user: {current_user.get('email', 'unknown')}")
        return updated_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[AdminAPI] Error updating pricing template: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update pricing template: {str(e)}"
        )

@router.delete("/pricing-templates/{template_id}", response_model=Dict[str, str], summary="Delete a pricing template")
async def delete_pricing_template(
    template_id: str,
    current_user: dict = Depends(require_admin_role)
):
    """Delete a pricing template (admin only)"""
    if not db:
        raise HTTPException(
            status_code=500,
            detail="Database connection not available"
        )
    
    try:
        # Check if pricing template exists
        templates_ref = db.collection("pricingTemplates")
        doc_ref = templates_ref.document(template_id)
        doc = await asyncio.to_thread(doc_ref.get)
        
        if not doc.exists:
            raise HTTPException(
                status_code=404,
                detail=f"Pricing template with ID {template_id} not found"
            )
        
        # Get template name for logging
        template_data = doc.to_dict()
        template_name = template_data.get('name', 'Unknown')
        
        # Delete the document
        await asyncio.to_thread(doc_ref.delete)
        
        print(f"[AdminAPI] Deleted pricing template '{template_name}' (ID: {template_id}) by user: {current_user.get('email', 'unknown')}")
        return {
            "message": f"Pricing template '{template_name}' deleted successfully",
            "deleted_id": template_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[AdminAPI] Error deleting pricing template: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete pricing template: {str(e)}"
        )

# Legacy endpoints (kept for backwards compatibility)
@router.get("/users", summary="List all users")
async def list_users(current_user: dict = Depends(require_admin_role)):
    """Get a list of all users (admin only)"""
    # TODO: Implement admin user listing
    return {"message": "Admin users endpoint - implementation pending"}

@router.get("/analytics", summary="Get system analytics")
async def get_analytics(current_user: dict = Depends(require_admin_role)):
    """Get system usage analytics (admin only)"""
    # TODO: Implement analytics retrieval
    return {"message": "Admin analytics endpoint - implementation pending"}

@router.post("/agent/deploy", summary="Deploy agent updates")
async def deploy_agent_updates(current_user: dict = Depends(require_admin_role)):
    """Deploy updates to the agent system (admin only)"""
    # TODO: Implement agent deployment logic
    return {"message": "Agent deployment endpoint - implementation pending"} 