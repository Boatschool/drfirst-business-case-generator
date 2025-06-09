"""
Admin API routes for the DrFirst Business Case Generator
"""

import logging
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from fastapi.security import HTTPBearer
from typing import List, Dict, Any, Optional
import asyncio
import uuid
from datetime import datetime, timezone
from google.cloud import firestore
from app.auth.firebase_auth import require_admin_role
from app.core.config import settings
from pydantic import BaseModel, Field
from app.models.firestore_models import UserRole
from app.services.user_service import user_service

logger = logging.getLogger(__name__)

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

    name: str = Field(
        ..., min_length=1, max_length=100, description="Name of the rate card"
    )
    description: str = Field(
        ..., min_length=1, max_length=500, description="Description of the rate card"
    )
    isActive: bool = Field(True, description="Whether the rate card is active")
    defaultOverallRate: float = Field(
        ..., gt=0, description="Default overall hourly rate"
    )
    roles: List[RoleRate] = Field(
        default=[], description="List of roles with specific rates"
    )


class UpdateRateCardRequest(BaseModel):
    """Request model for updating an existing rate card"""

    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Name of the rate card"
    )
    description: Optional[str] = Field(
        None, min_length=1, max_length=500, description="Description of the rate card"
    )
    isActive: Optional[bool] = Field(
        None, description="Whether the rate card is active"
    )
    defaultOverallRate: Optional[float] = Field(
        None, gt=0, description="Default overall hourly rate"
    )
    roles: Optional[List[RoleRate]] = Field(
        None, description="List of roles with specific rates"
    )


# Pydantic models for Pricing Template operations
class CreatePricingTemplateRequest(BaseModel):
    """Request model for creating a new pricing template"""

    name: str = Field(
        ..., min_length=1, max_length=100, description="Name of the pricing template"
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Description of the pricing template",
    )
    version: str = Field(
        ..., min_length=1, max_length=20, description="Version of the pricing template"
    )
    structureDefinition: Dict[str, Any] = Field(
        ..., description="Structure definition (JSON object)"
    )


class UpdatePricingTemplateRequest(BaseModel):
    """Request model for updating an existing pricing template"""

    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Name of the pricing template"
    )
    description: Optional[str] = Field(
        None,
        min_length=1,
        max_length=500,
        description="Description of the pricing template",
    )
    version: Optional[str] = Field(
        None, min_length=1, max_length=20, description="Version of the pricing template"
    )
    structureDefinition: Optional[Dict[str, Any]] = Field(
        None, description="Structure definition (JSON object)"
    )


# Add User Pydantic model near the top with other models
class User(BaseModel):
    """User model for API responses"""

    uid: str
    email: str
    display_name: Optional[str] = None
    systemRole: Optional[str] = None
    is_active: Optional[bool] = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_login: Optional[str] = None


# Global Configuration Models
class FinalApproverRoleConfig(BaseModel):
    """Final approver role configuration model"""

    finalApproverRoleName: str
    updatedAt: Optional[str] = None
    description: Optional[str] = None


class UpdateFinalApproverRoleRequest(BaseModel):
    """Request model for updating final approver role"""

    finalApproverRoleName: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="System role name to use for final approvals",
    )


class UpdateUserRoleRequest(BaseModel):
    """Request model for updating a user's system role"""
    
    newSystemRole: str = Field(
        ...,
        description="New system role for the user",
        pattern="^[A-Z_]+$"
    )

class StageApproverRolesConfig(BaseModel):
    """Stage-specific approver roles configuration model"""
    
    stageApproverRoles: Dict[str, str] = Field(
        ...,
        description="Mapping of workflow stages to their designated approver roles"
    )
    updatedAt: Optional[str] = None
    updatedBy: Optional[str] = None
    description: Optional[str] = None

class UpdateStageApproverRolesRequest(BaseModel):
    """Request model for updating stage-specific approver roles"""
    
    stageApproverRoles: Dict[str, str] = Field(
        ...,
        description="New stage-to-role mappings"
    )


# Lazy initialization of Firestore client
_db_instance = None
_db_initialized = False

def get_admin_db():
    """Get Firestore client with lazy initialization"""
    global _db_instance, _db_initialized
    if not _db_initialized:
        try:
            _db_instance = firestore.Client(project=settings.firebase_project_id)
            _db_initialized = True
            logger.info("Admin routes: Firestore client initialized successfully.")
        except Exception as e:
            logger.info(f"Admin routes: Failed to initialize Firestore client: {e}")
            _db_instance = None
    return _db_instance

# Rate Cards CRUD Operations


@router.get(
    "/rate-cards", response_model=List[Dict[str, Any]], summary="List all rate cards"
)
async def list_rate_cards(
    current_user: dict = Depends(require_admin_role),
    limit: int = Query(
        50,
        ge=1,
        le=200,
        description="Maximum number of rate cards to return (1-200)"
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Number of rate cards to skip for pagination"
    ),
    active_only: bool = Query(
        False,
        description="Filter to show only active rate cards"
    )
):
    """Get a list of all rate cards (admin only)"""
    db = get_admin_db()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection not available")

    try:
        # Fetch all documents from rateCards collection
        rate_cards_ref = db.collection("rateCards")
        docs = await asyncio.to_thread(lambda: list(rate_cards_ref.stream()))

        rate_cards = []
        for doc in docs:
            rate_card_data = doc.to_dict()
            rate_card_data["id"] = doc.id  # Add document ID
            rate_cards.append(rate_card_data)

        logger.info(
            f"[AdminAPI] Retrieved {len(rate_cards)} rate cards for user: {current_user.get('email', 'unknown')}"
        )
        return rate_cards

    except Exception as e:
        logger.info(f"[AdminAPI] Error fetching rate cards: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch rate cards: {str(e)}"
        )


@router.post(
    "/rate-cards", response_model=Dict[str, Any], summary="Create a new rate card"
)
async def create_rate_card(
    rate_card_data: CreateRateCardRequest,
    current_user: dict = Depends(require_admin_role),
):
    """Create a new rate card (admin only)"""
    db = get_admin_db()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection not available")

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
            "created_by": current_user.get("email", "unknown"),
            "updated_by": current_user.get("email", "unknown"),
        }

        # Save to Firestore
        rate_cards_ref = db.collection("rateCards")
        await asyncio.to_thread(rate_cards_ref.document(card_id).set, rate_card_doc)

        # Return the created rate card with ID
        rate_card_doc["id"] = card_id

        logger.info(
            f"[AdminAPI] Created new rate card '{rate_card_data.name}' with ID {card_id} by user: {current_user.get('email', 'unknown')}"
        )
        return rate_card_doc

    except Exception as e:
        logger.info(f"[AdminAPI] Error creating rate card: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create rate card: {str(e)}"
        )


@router.put(
    "/rate-cards/{card_id}",
    response_model=Dict[str, Any],
    summary="Update an existing rate card",
)
async def update_rate_card(
    card_id: str = Path(
        ...,
        min_length=1,
        max_length=128,
        description="Rate card ID"
    ),
    rate_card_data: UpdateRateCardRequest = ...,
    current_user: dict = Depends(require_admin_role),
):
    """Update an existing rate card (admin only)"""
    db = get_admin_db()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection not available")

    try:
        # Check if rate card exists
        rate_cards_ref = db.collection("rateCards")
        doc_ref = rate_cards_ref.document(card_id)
        doc = await asyncio.to_thread(doc_ref.get)

        if not doc.exists:
            raise HTTPException(
                status_code=404, detail=f"Rate card with ID {card_id} not found"
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
        update_data["updated_by"] = current_user.get("email", "unknown")

        # Update the document
        await asyncio.to_thread(doc_ref.update, update_data)

        # Fetch and return the updated document
        updated_doc = await asyncio.to_thread(doc_ref.get)
        updated_data = updated_doc.to_dict()
        updated_data["id"] = card_id

        logger.info(
            f"[AdminAPI] Updated rate card {card_id} by user: {current_user.get('email', 'unknown')}"
        )
        return updated_data

    except HTTPException:
        raise
    except Exception as e:
        logger.info(f"[AdminAPI] Error updating rate card: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to update rate card: {str(e)}"
        )


@router.delete(
    "/rate-cards/{card_id}", response_model=Dict[str, str], summary="Delete a rate card"
)
async def delete_rate_card(
    card_id: str = Path(
        ...,
        min_length=1,
        max_length=128,
        description="Rate card ID"
    ), 
    current_user: dict = Depends(require_admin_role)
):
    """Delete a rate card (admin only)"""
    db = get_admin_db()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection not available")

    try:
        # Check if rate card exists
        rate_cards_ref = db.collection("rateCards")
        doc_ref = rate_cards_ref.document(card_id)
        doc = await asyncio.to_thread(doc_ref.get)

        if not doc.exists:
            raise HTTPException(
                status_code=404, detail=f"Rate card with ID {card_id} not found"
            )

        # Get rate card name for logging
        rate_card_data = doc.to_dict()
        rate_card_name = rate_card_data.get("name", "Unknown")

        # Delete the document
        await asyncio.to_thread(doc_ref.delete)

        logger.info(
            f"[AdminAPI] Deleted rate card '{rate_card_name}' (ID: {card_id}) by user: {current_user.get('email', 'unknown')}"
        )
        return {
            "message": f"Rate card '{rate_card_name}' deleted successfully",
            "deleted_id": card_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.info(f"[AdminAPI] Error deleting rate card: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to delete rate card: {str(e)}"
        )


@router.get(
    "/pricing-templates",
    response_model=List[Dict[str, Any]],
    summary="List all pricing templates",
)
async def list_pricing_templates(current_user: dict = Depends(require_admin_role)):
    """Get a list of all pricing templates (admin only)"""
    db = get_admin_db()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection not available")

    try:
        # Fetch all documents from pricingTemplates collection
        templates_ref = db.collection("pricingTemplates")
        docs = await asyncio.to_thread(lambda: list(templates_ref.stream()))

        pricing_templates = []
        for doc in docs:
            template_data = doc.to_dict()
            template_data["id"] = doc.id  # Add document ID
            pricing_templates.append(template_data)

        logger.info(
            f"[AdminAPI] Retrieved {len(pricing_templates)} pricing templates for user: {current_user.get('email', 'unknown')}"
        )
        return pricing_templates

    except Exception as e:
        logger.info(f"[AdminAPI] Error fetching pricing templates: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch pricing templates: {str(e)}"
        )


@router.post(
    "/pricing-templates",
    response_model=Dict[str, Any],
    summary="Create a new pricing template",
)
async def create_pricing_template(
    template_data: CreatePricingTemplateRequest,
    current_user: dict = Depends(require_admin_role),
):
    """Create a new pricing template (admin only)"""
    db = get_admin_db()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection not available")

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
            "created_by": current_user.get("email", "unknown"),
            "updated_by": current_user.get("email", "unknown"),
        }

        # Save to Firestore
        templates_ref = db.collection("pricingTemplates")
        await asyncio.to_thread(templates_ref.document(template_id).set, template_doc)

        # Return the created template with ID
        template_doc["id"] = template_id

        logger.info(
            f"[AdminAPI] Created new pricing template '{template_data.name}' with ID {template_id} by user: {current_user.get('email', 'unknown')}"
        )
        return template_doc

    except Exception as e:
        logger.info(f"[AdminAPI] Error creating pricing template: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create pricing template: {str(e)}"
        )


@router.put(
    "/pricing-templates/{template_id}",
    response_model=Dict[str, Any],
    summary="Update an existing pricing template",
)
async def update_pricing_template(
    template_id: str,
    template_data: UpdatePricingTemplateRequest,
    current_user: dict = Depends(require_admin_role),
):
    """Update an existing pricing template (admin only)"""
    db = get_admin_db()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection not available")

    try:
        # Check if pricing template exists
        templates_ref = db.collection("pricingTemplates")
        doc_ref = templates_ref.document(template_id)
        doc = await asyncio.to_thread(doc_ref.get)

        if not doc.exists:
            raise HTTPException(
                status_code=404,
                detail=f"Pricing template with ID {template_id} not found",
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
        update_data["updated_by"] = current_user.get("email", "unknown")

        # Update the document
        await asyncio.to_thread(doc_ref.update, update_data)

        # Fetch and return the updated document
        updated_doc = await asyncio.to_thread(doc_ref.get)
        updated_data = updated_doc.to_dict()
        updated_data["id"] = template_id

        logger.info(
            f"[AdminAPI] Updated pricing template {template_id} by user: {current_user.get('email', 'unknown')}"
        )
        return updated_data

    except HTTPException:
        raise
    except Exception as e:
        logger.info(f"[AdminAPI] Error updating pricing template: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to update pricing template: {str(e)}"
        )


@router.delete(
    "/pricing-templates/{template_id}",
    response_model=Dict[str, str],
    summary="Delete a pricing template",
)
async def delete_pricing_template(
    template_id: str, current_user: dict = Depends(require_admin_role)
):
    """Delete a pricing template (admin only)"""
    db = get_admin_db()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection not available")

    try:
        # Check if pricing template exists
        templates_ref = db.collection("pricingTemplates")
        doc_ref = templates_ref.document(template_id)
        doc = await asyncio.to_thread(doc_ref.get)

        if not doc.exists:
            raise HTTPException(
                status_code=404,
                detail=f"Pricing template with ID {template_id} not found",
            )

        # Get template name for logging
        template_data = doc.to_dict()
        template_name = template_data.get("name", "Unknown")

        # Delete the document
        await asyncio.to_thread(doc_ref.delete)

        logger.info(
            f"[AdminAPI] Deleted pricing template '{template_name}' (ID: {template_id}) by user: {current_user.get('email', 'unknown')}"
        )
        return {
            "message": f"Pricing template '{template_name}' deleted successfully",
            "deleted_id": template_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.info(f"[AdminAPI] Error deleting pricing template: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to delete pricing template: {str(e)}"
        )


# Replace the placeholder users endpoint with complete implementation
def _convert_datetime_to_string(dt_value) -> Optional[str]:
    """Convert Firestore datetime to ISO string, handling various input types"""
    if dt_value is None:
        return None
    if isinstance(dt_value, str):
        return dt_value
    if hasattr(dt_value, 'isoformat'):
        return dt_value.isoformat()
    return str(dt_value)


@router.get("/users", response_model=List[User], summary="List all users")
async def list_users(current_user: dict = Depends(require_admin_role)):
    """Get a list of all users with their system roles (admin only)"""
    db = get_admin_db()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection not available")

    try:
        # Fetch all documents from users collection
        users_ref = db.collection("users")
        docs = await asyncio.to_thread(lambda: list(users_ref.stream()))

        users = []
        skipped_users = 0
        
        for doc in docs:
            try:
                user_data = doc.to_dict()
                # Add document ID as uid if not present
                if "uid" not in user_data:
                    user_data["uid"] = doc.id

                # Clean and validate data before creating User object
                uid = str(user_data.get("uid", doc.id))
                email = str(user_data.get("email", "N/A"))
                display_name = user_data.get("display_name")
                if display_name is not None:
                    display_name = str(display_name)
                
                systemRole = user_data.get("systemRole")
                if systemRole is not None:
                    systemRole = str(systemRole)
                
                is_active = user_data.get("is_active")
                if is_active is None:
                    is_active = True
                else:
                    is_active = bool(is_active)

                # Create User object with safe field access and datetime conversion
                user = User(
                    uid=uid,
                    email=email,
                    display_name=display_name,
                    systemRole=systemRole,
                    is_active=is_active,
                    created_at=_convert_datetime_to_string(user_data.get("created_at")),
                    updated_at=_convert_datetime_to_string(user_data.get("updated_at")),
                    last_login=_convert_datetime_to_string(user_data.get("last_login")),
                )
                users.append(user)
                
            except Exception as user_error:
                logger.warning(f"[AdminAPI] Skipping invalid user {doc.id}: {user_error}")
                skipped_users += 1
                continue

        logger.info(
            f"[AdminAPI] Retrieved {len(users)} users for admin: {current_user.get('email', 'unknown')}"
        )
        if skipped_users > 0:
            logger.warning(f"[AdminAPI] Skipped {skipped_users} users due to validation errors")
            
        return users

    except Exception as e:
        logger.error(f"[AdminAPI] Error fetching users: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")


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


# Global Configuration Endpoints


@router.get(
    "/config/final-approver-role",
    response_model=FinalApproverRoleConfig,
    summary="Get global final approver role setting",
)
async def get_final_approver_role(current_user: dict = Depends(require_admin_role)):
    """Get the currently configured global final approver role (admin only)"""
    db = get_admin_db()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection not available")

    try:
        # Fetch configuration from Firestore
        config_ref = db.collection("systemConfiguration").document("approvalSettings")
        doc = await asyncio.to_thread(config_ref.get)

        if not doc.exists:
            # Return default configuration if not found
            logger.info(
                "[AdminAPI] No final approver configuration found, returning default"
            )
            return FinalApproverRoleConfig(
                finalApproverRoleName="FINAL_APPROVER",
                description="Default final approver role (configuration not yet initialized)",
            )

        config_data = doc.to_dict()
        final_approver_role = config_data.get("finalApproverRoleName", "FINAL_APPROVER")

        # Convert datetime to string if it exists
        updated_at = config_data.get("updatedAt")
        if updated_at and hasattr(updated_at, "isoformat"):
            updated_at = updated_at.isoformat()
        elif updated_at and not isinstance(updated_at, str):
            updated_at = str(updated_at)

        logger.info(
            f"[AdminAPI] Retrieved final approver role configuration: {final_approver_role} for admin: {current_user.get('email', 'unknown')}"
        )

        return FinalApproverRoleConfig(
            finalApproverRoleName=final_approver_role,
            updatedAt=updated_at,
            description=config_data.get("description"),
        )

    except Exception as e:
        logger.info(f"[AdminAPI] Error fetching final approver role configuration: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch final approver role configuration: {str(e)}",
        )


@router.put(
    "/config/final-approver-role",
    response_model=FinalApproverRoleConfig,
    summary="Update global final approver role setting",
)
async def update_final_approver_role(
    config_update: UpdateFinalApproverRoleRequest,
    current_user: dict = Depends(require_admin_role),
):
    """Update the global final approver role configuration (admin only)"""
    db = get_admin_db()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection not available")

    try:
        new_role = config_update.finalApproverRoleName.strip()

        # Validate role name (basic validation - could be enhanced)
        valid_roles = [
            "ADMIN",
            "DEVELOPER",
            "SALES_MANAGER_APPROVER",
            "FINAL_APPROVER",
            "CASE_INITIATOR",
        ]
        if new_role not in valid_roles:
            logger.info(f"[AdminAPI] Invalid role name provided: {new_role}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid role name. Must be one of: {', '.join(valid_roles)}",
            )

        # Prepare update data
        current_time = datetime.now(timezone.utc).isoformat()
        update_data = {
            "finalApproverRoleName": new_role,
            "updatedAt": current_time,
            "updatedBy": current_user.get("email", "unknown"),
            "description": "Global configuration for which systemRole acts as the final approver for business cases",
        }

        # Update or create configuration document
        config_ref = db.collection("systemConfiguration").document("approvalSettings")
        await asyncio.to_thread(config_ref.set, update_data, merge=True)

        # Clear cache to ensure immediate effect
        from app.utils.config_helpers import clear_final_approver_role_cache

        clear_final_approver_role_cache()

        logger.info(
            f"[AdminAPI] Updated final approver role to '{new_role}' by admin: {current_user.get('email', 'unknown')}"
        )

        return FinalApproverRoleConfig(
            finalApproverRoleName=new_role,
            updatedAt=current_time,
            description=update_data["description"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.info(f"[AdminAPI] Error updating final approver role configuration: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update final approver role configuration: {str(e)}",
        )


# User Role Management Endpoints

@router.put(
    "/users/{target_user_uid}/role",
    response_model=Dict[str, Any],
    summary="Update a user's system role",
)
async def update_user_system_role(
    target_user_uid: str = Path(
        ...,
        description="UID of the user whose role should be updated"
    ),
    role_update: UpdateUserRoleRequest = ...,
    current_user: dict = Depends(require_admin_role),
):
    """Update a user's system role in Firestore and sync to Firebase custom claims (admin only)"""
    admin_email = current_user.get("email", "unknown")
    
    try:
        new_role_str = role_update.newSystemRole.strip()
        
        # Validate role name against UserRole enum
        try:
            new_role = UserRole(new_role_str)
        except ValueError:
            valid_roles = [role.value for role in UserRole]
            raise HTTPException(
                status_code=400,
                detail=f"Invalid role name '{new_role_str}'. Must be one of: {', '.join(valid_roles)}"
            )
        
        # Update user role using UserService
        success = await user_service.update_user_role(target_user_uid, new_role)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update role for user {target_user_uid}"
            )
        
        logger.info(
            f"[AdminAPI] Updated user {target_user_uid} role to '{new_role_str}' by admin: {admin_email}"
        )
        
        return {
            "message": f"User role updated successfully to {new_role_str}",
            "target_user_uid": target_user_uid,
            "new_role": new_role_str,
            "updated_by": admin_email,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[AdminAPI] Error updating user role for {target_user_uid}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update user role: {str(e)}"
        )

# Stage-Specific Approver Configuration Endpoints

@router.get(
    "/config/stage-approver-roles",
    response_model=StageApproverRolesConfig,
    summary="Get stage-specific approver role settings",
)
async def get_stage_approver_roles(current_user: dict = Depends(require_admin_role)):
    """Get the currently configured stage-specific approver roles (admin only)"""
    db = get_admin_db()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection not available")

    try:
        # Fetch configuration from Firestore
        config_ref = db.collection("systemConfiguration").document("approvalSettings")
        doc = await asyncio.to_thread(config_ref.get)

        if not doc.exists:
            # Return default configuration if not found
            default_stage_roles = {
                "PRD": "PRODUCT_OWNER",
                "SystemDesign": "DEVELOPER", 
                "EffortEstimate": "DEVELOPER",
                "CostEstimate": "FINANCE_APPROVER",
                "ValueProjection": "SALES_MANAGER"
            }
            
            logger.info(
                "[AdminAPI] No stage approver configuration found, returning defaults"
            )
            return StageApproverRolesConfig(
                stageApproverRoles=default_stage_roles,
                description="Default stage approver roles (configuration not yet initialized)",
            )

        config_data = doc.to_dict()
        stage_approver_roles = config_data.get("stageApproverRoles", {})

        # Convert datetime to string if it exists
        updated_at = config_data.get("updatedAt")
        if updated_at and hasattr(updated_at, "isoformat"):
            updated_at = updated_at.isoformat()
        elif updated_at and not isinstance(updated_at, str):
            updated_at = str(updated_at)

        logger.info(
            f"[AdminAPI] Retrieved stage approver roles configuration for admin: {current_user.get('email', 'unknown')}"
        )

        return StageApproverRolesConfig(
            stageApproverRoles=stage_approver_roles,
            updatedAt=updated_at,
            updatedBy=config_data.get("updatedBy"),
            description=config_data.get("description"),
        )

    except Exception as e:
        logger.error(f"[AdminAPI] Error fetching stage approver roles configuration: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch stage approver roles configuration: {str(e)}",
        )

@router.put(
    "/config/stage-approver-roles",
    response_model=StageApproverRolesConfig,
    summary="Update stage-specific approver role settings",
)
async def update_stage_approver_roles(
    config_update: UpdateStageApproverRolesRequest,
    current_user: dict = Depends(require_admin_role),
):
    """Update the stage-specific approver roles configuration (admin only)"""
    db = get_admin_db()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection not available")

    try:
        new_stage_roles = config_update.stageApproverRoles
        
        # Validate all role names against UserRole enum
        valid_roles = [role.value for role in UserRole]
        for stage, role_name in new_stage_roles.items():
            if role_name not in valid_roles:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid role name '{role_name}' for stage '{stage}'. Must be one of: {', '.join(valid_roles)}"
                )

        # Prepare update data
        current_time = datetime.now(timezone.utc).isoformat()
        update_data = {
            "stageApproverRoles": new_stage_roles,
            "updatedAt": current_time,
            "updatedBy": current_user.get("email", "unknown"),
            "description": "Configuration for which systemRole can approve each specific workflow stage",
        }

        # Update or create configuration document
        config_ref = db.collection("systemConfiguration").document("approvalSettings")
        await asyncio.to_thread(config_ref.set, update_data, merge=True)

        # Clear cache to ensure immediate effect
        from app.utils.approval_permissions import clear_stage_approver_roles_cache
        clear_stage_approver_roles_cache()

        logger.info(
            f"[AdminAPI] Updated stage approver roles by admin: {current_user.get('email', 'unknown')}"
        )

        return StageApproverRolesConfig(
            stageApproverRoles=new_stage_roles,
            updatedAt=current_time,
            updatedBy=current_user.get("email", "unknown"),
            description=update_data["description"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[AdminAPI] Error updating stage approver roles configuration: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update stage approver roles configuration: {str(e)}",
        )
