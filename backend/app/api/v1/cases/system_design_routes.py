"""
API routes for system design HITL workflow (edit, submit, approve, reject).
"""

import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException

from app.auth.firebase_auth import get_current_active_user
from app.core.dependencies import get_firestore_service
from app.services.firestore_service import FirestoreService
from app.core.constants import HTTPStatus, ErrorMessages, SuccessMessages, MessageTypes, MessageSources
from app.agents.orchestrator_agent import BusinessCaseStatus
from .models import SystemDesignUpdateRequest, SystemDesignRejectRequest

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter()


@router.put(
    "/cases/{case_id}/system-design",
    status_code=200,
    summary="Update system design content for a specific business case",
)
async def update_system_design(
    case_id: str,
    system_design_request: SystemDesignUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    firestore_service: FirestoreService = Depends(get_firestore_service),
):
    """
    Updates the system design content for a business case.
    Ensures the authenticated user is the owner or has DEVELOPER role.
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")

    if not user_id:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=ErrorMessages.USER_ID_NOT_FOUND)

    try:
        # Use FirestoreService to get the business case
        business_case = await firestore_service.get_business_case(case_id)
        
        if not business_case:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, 
                detail=f"Business case {case_id} not found."
            )

        # Authorization check: owner or DEVELOPER role
        user_role = current_user.get("custom_claims", {}).get("role")
        is_owner = business_case.user_id == user_id
        is_developer = user_role == "DEVELOPER"
        
        if not (is_owner or is_developer):
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="You do not have permission to edit this system design.",
            )

        # Status check
        current_status = str(business_case.status)
        if hasattr(business_case.status, "value"):
            current_status = business_case.status.value

        allowed_statuses = [
            BusinessCaseStatus.SYSTEM_DESIGN_DRAFTED.value,
            BusinessCaseStatus.SYSTEM_DESIGN_PENDING_REVIEW.value,
            BusinessCaseStatus.SYSTEM_DESIGN_REJECTED.value,
        ]

        if current_status not in allowed_statuses:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f"Cannot edit system design from current status: {current_status}",
            )

        # Update system design content
        current_system_design = business_case.system_design_v1_draft or {}
        current_system_design["content_markdown"] = system_design_request.content_markdown
        current_system_design["last_edited_by"] = user_email
        current_system_design["last_edited_at"] = datetime.now(timezone.utc).isoformat()

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": MessageSources.USER,
            "messageType": MessageTypes.SYSTEM_DESIGN_UPDATE,
            "content": f"System design updated by {user_email}",
        }

        # Prepare update data
        current_history = business_case.history or []
        current_history.append(history_entry)
        
        update_data = {
            "system_design_v1_draft": current_system_design,
            "updated_at": datetime.now(timezone.utc),
            "history": current_history,
        }

        # Use FirestoreService to update the business case
        success = await firestore_service.update_business_case(case_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, 
                detail="Failed to update system design"
            )

        return {
            "message": "System design updated successfully",
            "case_id": case_id,
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error updating system design for case {case_id}, user {user_id}: {e}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, 
            detail=f"Failed to update system design: {str(e)}"
        )


@router.post(
    "/cases/{case_id}/system-design/submit",
    status_code=200,
    summary="Submit system design for review",
)
async def submit_system_design_for_review(
    case_id: str,
    current_user: dict = Depends(get_current_active_user),
    firestore_service: FirestoreService = Depends(get_firestore_service),
):
    """
    Submits the system design for review, updating the case status to SYSTEM_DESIGN_PENDING_REVIEW.
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")

    if not user_id:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=ErrorMessages.USER_ID_NOT_FOUND)

    try:
        # Use FirestoreService to get the business case
        business_case = await firestore_service.get_business_case(case_id)
        
        if not business_case:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, 
                detail=f"Business case {case_id} not found."
            )

        # Authorization check: only owner can submit
        if business_case.user_id != user_id:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="You do not have permission to submit this system design for review.",
            )

        # Status check
        current_status = str(business_case.status)
        if hasattr(business_case.status, "value"):
            current_status = business_case.status.value

        allowed_statuses = [
            BusinessCaseStatus.SYSTEM_DESIGN_DRAFTED.value,
            BusinessCaseStatus.SYSTEM_DESIGN_REJECTED.value,
        ]

        if current_status not in allowed_statuses:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f"Cannot submit system design from current status: {current_status}",
            )

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": MessageSources.USER,
            "messageType": MessageTypes.STATUS_UPDATE,
            "content": f"System design submitted for review by {user_email}",
        }

        # Prepare update data
        current_history = business_case.history or []
        current_history.append(history_entry)
        
        update_data = {
            "status": BusinessCaseStatus.SYSTEM_DESIGN_PENDING_REVIEW.value,
            "updated_at": datetime.now(timezone.utc),
            "history": current_history,
        }

        # Use FirestoreService to update the business case
        success = await firestore_service.update_business_case(case_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, 
                detail="Failed to submit system design for review"
            )

        return {
            "message": "System design submitted for review successfully",
            "new_status": BusinessCaseStatus.SYSTEM_DESIGN_PENDING_REVIEW.value,
            "case_id": case_id,
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error submitting system design for case {case_id}, user {user_id}: {e}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, 
            detail=f"Failed to submit system design for review: {str(e)}"
        )


@router.post(
    "/cases/{case_id}/system-design/approve",
    status_code=200,
    summary="Approve system design for a specific business case",
)
async def approve_system_design(
    case_id: str, 
    current_user: dict = Depends(get_current_active_user),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """
    Approves the system design for a business case, updating the case status to SYSTEM_DESIGN_APPROVED.
    Ensures the authenticated user has DEVELOPER role and case is in SYSTEM_DESIGN_PENDING_REVIEW status.
    After approval, triggers effort estimation via orchestrator.
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")

    # Enhanced Logging: System Design Approval Attempts
    logger.info(f"System design approval initiated for case {case_id} by user {user_email}")

    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    # Get business case first to check ownership and permissions
    business_case = await firestore_service.get_business_case(case_id)
    
    if not business_case:
        raise HTTPException(
            status_code=404, detail=f"Business case {case_id} not found."
        )

    # Use centralized approval permission logic with admin override
    from app.utils.approval_permissions import check_approval_permissions
    await check_approval_permissions(current_user, business_case.user_id, "SystemDesign")

    try:
        # Use FirestoreService to get the business case
        business_case = await firestore_service.get_business_case(case_id)
        
        if not business_case:
            raise HTTPException(
                status_code=404, detail=f"Business case {case_id} not found."
            )

        # Status check: ensure case is in SYSTEM_DESIGN_PENDING_REVIEW status
        current_status_str = str(business_case.status)
        if hasattr(business_case.status, "value"):
            current_status_str = business_case.status.value

        # Enhanced Logging: Status Transition Validation
        logger.info(f"Status check for case {case_id}: current is {current_status_str}, expecting {BusinessCaseStatus.SYSTEM_DESIGN_PENDING_REVIEW.value}")

        if current_status_str != BusinessCaseStatus.SYSTEM_DESIGN_PENDING_REVIEW.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot approve system design from current status: {current_status_str}. System design must be in PENDING_REVIEW status.",
            )

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "SYSTEM_DESIGN_APPROVAL",
            "content": f"System design approved by {user_email}",
        }

        # Prepare update data
        current_history = business_case.history or []
        current_history.append(history_entry)
        
        update_data = {
            "status": BusinessCaseStatus.SYSTEM_DESIGN_APPROVED.value,
            "updated_at": datetime.now(timezone.utc),
            "history": current_history,
        }

        # Use FirestoreService to update the business case
        success = await firestore_service.update_business_case(case_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to approve system design"
            )

        # Enhanced Logging: Status Transition 
        logger.info(f"Status transition: {current_status_str} -> {BusinessCaseStatus.SYSTEM_DESIGN_APPROVED.value} for case {case_id}")

        # After successful system design approval, initiate effort estimation
        try:
            from app.agents.orchestrator_agent import OrchestratorAgent

            orchestrator = OrchestratorAgent()

            # Enhanced Logging: Orchestrator Method Calls
            logger.info(f"Triggering effort estimation for approved system design in case {case_id}")
            logger.info(f"Calling orchestrator.handle_system_design_approval() for case {case_id}")
            effort_result = await orchestrator.handle_system_design_approval(case_id)

            if effort_result.get("status") == "success":
                logger.info(f"Effort estimation initiated successfully for case {case_id}")
                return {
                    "message": "System design approved successfully and effort estimation initiated",
                    "new_status": effort_result.get("new_status", BusinessCaseStatus.SYSTEM_DESIGN_APPROVED.value),
                    "case_id": case_id,
                    "effort_estimation_initiated": True,
                }
            else:
                logger.info(f"Effort estimation failed for case {case_id}: {effort_result.get('message')}")
                return {
                    "message": "System design approved successfully but effort estimation encountered an issue",
                    "new_status": BusinessCaseStatus.SYSTEM_DESIGN_APPROVED.value,
                    "case_id": case_id,
                    "effort_estimation_initiated": False,
                    "effort_estimation_error": effort_result.get("message"),
                }
        except Exception as effort_error:
            logger.info(f"Error initiating effort estimation for case {case_id}: {str(effort_error)}")
            return {
                "message": "System design approved successfully but effort estimation could not be initiated",
                "new_status": BusinessCaseStatus.SYSTEM_DESIGN_APPROVED.value,
                "case_id": case_id,
                "effort_estimation_initiated": False,
                "effort_estimation_error": str(effort_error),
            }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error approving system design for case {case_id}, user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to approve system design: {str(e)}")


@router.post(
    "/cases/{case_id}/system-design/reject",
    status_code=200,
    summary="Reject system design for a specific business case",
)
async def reject_system_design(
    case_id: str,
    reject_request: SystemDesignRejectRequest = SystemDesignRejectRequest(),
    current_user: dict = Depends(get_current_active_user),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """
    Rejects the system design for a business case, updating the case status to SYSTEM_DESIGN_REJECTED.
    Ensures the authenticated user has DEVELOPER role and case is in SYSTEM_DESIGN_PENDING_REVIEW status.
    Optionally accepts a rejection reason.
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")

    # Enhanced Logging: System Design Rejection Attempts
    logger.info(f"System design rejection initiated for case {case_id} by user {user_email}")

    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    # Get business case first to check permissions
    business_case = await firestore_service.get_business_case(case_id)
    
    if not business_case:
        raise HTTPException(
            status_code=404, detail=f"Business case {case_id} not found."
        )

    # Use centralized rejection permission logic
    from app.utils.approval_permissions import check_rejection_permissions
    check_rejection_permissions(current_user, business_case.user_id, "system design")

    try:
        # Status check: ensure case is in SYSTEM_DESIGN_PENDING_REVIEW status
        current_status_str = str(business_case.status)
        if hasattr(business_case.status, "value"):
            current_status_str = business_case.status.value

        # Enhanced Logging: Status Transition Validation
        logger.info(f"Status check for case {case_id}: current is {current_status_str}, expecting {BusinessCaseStatus.SYSTEM_DESIGN_PENDING_REVIEW.value}")

        if current_status_str != BusinessCaseStatus.SYSTEM_DESIGN_PENDING_REVIEW.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot reject system design from current status: {current_status_str}. System design must be in PENDING_REVIEW status.",
            )

        # Prepare history entry with optional reason
        rejection_content = f"System design rejected by {user_email}"
        if reject_request.reason:
            rejection_content += f". Reason: {reject_request.reason}"

        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "SYSTEM_DESIGN_REJECTION",
            "content": rejection_content,
        }

        # Prepare update data
        current_history = business_case.history or []
        current_history.append(history_entry)
        
        update_data = {
            "status": BusinessCaseStatus.SYSTEM_DESIGN_REJECTED.value,
            "updated_at": datetime.now(timezone.utc),
            "history": current_history,
        }

        # Use FirestoreService to update the business case
        success = await firestore_service.update_business_case(case_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to reject system design"
            )

        # Enhanced Logging: Status Transition 
        logger.info(f"Status transition: {current_status_str} -> {BusinessCaseStatus.SYSTEM_DESIGN_REJECTED.value} for case {case_id}")

        return {
            "message": "System design rejected successfully",
            "new_status": BusinessCaseStatus.SYSTEM_DESIGN_REJECTED.value,
            "case_id": case_id,
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error rejecting system design for case {case_id}, user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reject system design: {str(e)}") 