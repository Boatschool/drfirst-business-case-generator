"""
Approval permissions utility module

Centralizes permission logic for all approval workflows to ensure consistency
across PRD, System Design, Effort Estimation, and other approval stages.
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from fastapi import HTTPException
from google.cloud import firestore
from app.core.config import settings

logger = logging.getLogger(__name__)

# Cache for stage approver roles configuration
_stage_approver_roles_cache = None
_cache_expiry = None

def _get_firestore_client():
    """Get Firestore client instance"""
    try:
        return firestore.Client(project=settings.firebase_project_id)
    except Exception as e:
        logger.error(f"Failed to initialize Firestore client: {e}")
        return None

async def get_stage_approver_roles() -> Dict[str, str]:
    """
    Get the configured stage approver roles from Firestore with caching
    
    Returns:
        Dictionary mapping stage names to approver role names
    """
    global _stage_approver_roles_cache, _cache_expiry
    
    # Simple 5-minute cache
    import time
    current_time = time.time()
    
    if _stage_approver_roles_cache and _cache_expiry and current_time < _cache_expiry:
        return _stage_approver_roles_cache
    
    try:
        db = _get_firestore_client()
        if not db:
            # Fallback to defaults if Firestore unavailable
            return {
                "PRD": "PRODUCT_OWNER",
                "SystemDesign": "DEVELOPER", 
                "EffortEstimate": "DEVELOPER",
                "CostEstimate": "FINANCE_APPROVER",
                "ValueProjection": "SALES_MANAGER",
                "FinancialModel": "FINANCE_APPROVER",
                "FinalApproval": "FINAL_APPROVER"
            }
        
        config_ref = db.collection("systemConfiguration").document("approvalSettings")
        doc = await asyncio.to_thread(config_ref.get)
        
        if doc.exists:
            config_data = doc.to_dict()
            stage_roles = config_data.get("stageApproverRoles", {})
            
            # Cache for 5 minutes
            _stage_approver_roles_cache = stage_roles
            _cache_expiry = current_time + 300
            
            return stage_roles
        else:
            # Return defaults if configuration doesn't exist
            defaults = {
                "PRD": "PRODUCT_OWNER",
                "SystemDesign": "DEVELOPER", 
                "EffortEstimate": "DEVELOPER",
                "CostEstimate": "FINANCE_APPROVER",
                "ValueProjection": "SALES_MANAGER",
                "FinancialModel": "FINANCE_APPROVER",
                "FinalApproval": "FINAL_APPROVER"
            }
            _stage_approver_roles_cache = defaults
            _cache_expiry = current_time + 300
            return defaults
            
    except Exception as e:
        logger.error(f"Error fetching stage approver roles: {e}")
        # Return fallback defaults
        return {
            "PRD": "PRODUCT_OWNER",
            "SystemDesign": "DEVELOPER", 
            "EffortEstimate": "DEVELOPER",
            "CostEstimate": "FINANCE_APPROVER",
            "ValueProjection": "SALES_MANAGER",
            "FinancialModel": "FINANCE_APPROVER",
            "FinalApproval": "FINAL_APPROVER"
        }

def clear_stage_approver_roles_cache():
    """Clear the stage approver roles cache to force refresh"""
    global _stage_approver_roles_cache, _cache_expiry
    _stage_approver_roles_cache = None
    _cache_expiry = None

async def check_approval_permissions(
    current_user: Dict[str, Any], 
    business_case_user_id: str, 
    stage_name: str = "item",
    allow_self_approval: bool = True
) -> None:
    """
    Check if the current user has permission to approve the specified stage.
    
    Args:
        current_user: The authenticated user information
        business_case_user_id: The user ID of the business case owner
        stage_name: Name of the stage being approved (for configuration lookup)
        allow_self_approval: Whether case owners can approve their own cases
        
    Raises:
        HTTPException: If user doesn't have approval permissions
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")
    
    # Get user's system role from custom claims or token
    user_role = current_user.get("systemRole") or current_user.get("custom_claims", {}).get("systemRole", "")
    
    # **ADMIN OVERRIDE**: Admin can always approve any stage
    if user_role == "ADMIN":
        logger.info(f"🔑 [APPROVAL] ADMIN override: {user_email} approved for {stage_name} stage")
        return
    
    # Check if user is case owner (self-approval)
    if allow_self_approval and user_id == business_case_user_id:
        logger.info(f"👤 [APPROVAL] Case owner approval: {user_email} approved for {stage_name} stage")
        return
    
    # Get configured approver role for this stage
    stage_approver_roles = await get_stage_approver_roles()
    configured_approver_role = stage_approver_roles.get(stage_name)
    
    if not configured_approver_role:
        logger.warning(f"⚠️ [APPROVAL] No configured approver role found for stage '{stage_name}', falling back to ADMIN-only approval")
        raise HTTPException(
            status_code=403, 
            detail=f"Access denied. No approver role configured for {stage_name} stage. Only ADMIN users can approve."
        )
    
    # Check if user has the configured role for this stage
    if user_role == configured_approver_role:
        logger.info(f"✅ [APPROVAL] Role-based approval: {user_email} ({user_role}) approved for {stage_name} stage")
        return
    
    # Permission denied
    logger.warning(
        f"🚫 [APPROVAL] Access denied for {user_email} - stage: {stage_name}, "
        f"user_role: {user_role}, required_role: {configured_approver_role}"
    )
    raise HTTPException(
        status_code=403, 
        detail=f"Access denied. You need the '{configured_approver_role}' role to approve {stage_name}. Current role: '{user_role}'"
    )

# Legacy function for backward compatibility
def check_approval_permissions_legacy(
    current_user: Dict[str, Any], 
    business_case_user_id: str, 
    stage_name: str = "item"
) -> None:
    """
    Legacy approval permission check (synchronous version)
    
    Args:
        current_user: The authenticated user information
        business_case_user_id: The user ID of the business case owner
        stage_name: Name of the stage being approved (for error messages)
        
    Raises:
        HTTPException: If user doesn't have approval permissions
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")
    
    # Get user's system role from custom claims
    user_role = current_user.get("custom_claims", {}).get("role") or current_user.get("systemRole", "")
    
    # Define roles that can approve any stage (legacy logic)
    approver_roles = {"ADMIN", "FINAL_APPROVER", "DEVELOPER"}  # Add more as needed
    
    # Check permissions:
    # 1. User is the business case owner (self-approval)
    # 2. User has an approver role
    has_permission = (
        user_id == business_case_user_id or  # Case owner
        user_role in approver_roles  # Designated approver role
    )
    
    if not has_permission:
        logger.warning(
            f"🚫 [APPROVAL] Access denied for {user_email} - requires case ownership or approver role for {stage_name}"
        )
        raise HTTPException(
            status_code=403,
            detail=f"You do not have permission to approve this {stage_name}. Required: case ownership or one of {approver_roles}",
        )
    
    logger.info(f"✅ [APPROVAL] Permission granted for {user_email} to approve {stage_name}")

def check_rejection_permissions(
    current_user: Dict[str, Any], 
    business_case_user_id: str, 
    stage_name: str = "item"
) -> None:
    """
    Check if the current user has permission to reject the specified stage.
    Currently uses the same logic as approval permissions.
    
    Args:
        current_user: The authenticated user information
        business_case_user_id: The user ID of the business case owner
        stage_name: Name of the stage being rejected (for error messages)
        
    Raises:
        HTTPException: If user doesn't have rejection permissions
    """
    # For now, rejection permissions are the same as approval permissions
    check_approval_permissions(current_user, business_case_user_id, stage_name)

async def check_final_approval_permissions(
    current_user: Dict[str, Any], 
    business_case_user_id: str,
    allow_self_approval: bool = False
) -> None:
    """
    Check if the current user has permission to approve/reject final business case.
    Uses the finalApproverRoleName configuration from Firestore.
    
    Args:
        current_user: The authenticated user information
        business_case_user_id: The user ID of the business case owner
        allow_self_approval: Whether case owners can approve their own final cases (usually False)
        
    Raises:
        HTTPException: If user doesn't have final approval permissions
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")
    
    # Get user's system role from custom claims or token
    user_role = current_user.get("systemRole") or current_user.get("custom_claims", {}).get("systemRole", "")
    
    # **ADMIN OVERRIDE**: Admin can always approve final cases
    if user_role == "ADMIN":
        logger.info(f"🔑 [FINAL_APPROVAL] ADMIN override: {user_email} approved for final approval")
        return
    
    # Check if user is case owner (self-approval - usually disabled for final approval)
    if allow_self_approval and user_id == business_case_user_id:
        logger.info(f"👤 [FINAL_APPROVAL] Case owner approval: {user_email} approved for final approval")
        return
    
    # Get configured final approver role from Firestore
    try:
        db = _get_firestore_client()
        if not db:
            raise HTTPException(
                status_code=500, 
                detail="Database connection not available for authorization check"
            )
        
        config_ref = db.collection("systemConfiguration").document("approvalSettings")
        doc = await asyncio.to_thread(config_ref.get)
        
        if doc.exists:
            config_data = doc.to_dict()
            configured_final_approver_role = config_data.get("finalApproverRoleName", "FINAL_APPROVER")
        else:
            # Default to FINAL_APPROVER if no configuration exists
            configured_final_approver_role = "FINAL_APPROVER"
            logger.info(f"⚠️ [FINAL_APPROVAL] No final approver configuration found, using default: FINAL_APPROVER")
            
    except Exception as e:
        logger.error(f"❌ [FINAL_APPROVAL] Error fetching final approver configuration: {e}")
        # Fallback to default
        configured_final_approver_role = "FINAL_APPROVER"
    
    # Check if user has the configured final approver role
    if user_role == configured_final_approver_role:
        logger.info(f"✅ [FINAL_APPROVAL] Role-based final approval: {user_email} ({user_role}) approved for final approval")
        return
    
    # Permission denied
    logger.warning(
        f"🚫 [FINAL_APPROVAL] Access denied for {user_email} - "
        f"user_role: {user_role}, required_role: {configured_final_approver_role}"
    )
    raise HTTPException(
        status_code=403, 
        detail=f"Access denied. You need the '{configured_final_approver_role}' role for final approval. Current role: '{user_role}'"
    ) 