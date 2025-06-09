"""
API routes for PRD (Product Requirements Document) management.
"""

import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Path

from app.auth.firebase_auth import get_current_active_user
from app.core.dependencies import get_firestore_service
from app.services.firestore_service import FirestoreService
from .models import PrdUpdateRequest, PrdRejectRequest

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter()


@router.put(
    "/cases/{case_id}/prd",
    status_code=200,
    summary="Update PRD for a specific business case",
)
async def update_prd_draft(
    case_id: str = Path(
        ...,
        min_length=1,
        max_length=128,
        description="Business case ID"
    ),
    prd_update_request: PrdUpdateRequest = ...,
    current_user: dict = Depends(get_current_active_user),
    firestore_service: FirestoreService = Depends(get_firestore_service),
):
    """
    Updates the PRD draft for a specific business case.
    Ensures the authenticated user is the owner of the case.
    """
    user_id = current_user.get("uid")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    try:
        # Use FirestoreService to get the business case
        business_case = await firestore_service.get_business_case(case_id)
        
        if not business_case:
            raise HTTPException(
                status_code=404, detail=f"Business case {case_id} not found."
            )

        if business_case.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to edit this business case.",
            )

        # Construct the PRD draft object to be stored
        existing_prd_draft = business_case.prd_draft or {}
        updated_prd_draft = {
            "title": (business_case.title or "PRD") + " - Draft",
            "content_markdown": prd_update_request.content_markdown,
            "version": existing_prd_draft.get("version", "1.0.0"),
        }

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "PRD_UPDATE",
            "content": f"User updated the PRD draft. New version: {updated_prd_draft.get('version')}",
        }

        # Prepare update data
        current_history = business_case.history or []
        current_history.append(history_entry)
        
        update_data = {
            "prd_draft": updated_prd_draft,
            "updated_at": datetime.now(timezone.utc),
            "history": current_history,
        }

        # Use FirestoreService to update the business case
        success = await firestore_service.update_business_case(case_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to update PRD draft"
            )

        return {
            "message": "PRD draft updated successfully",
            "updated_prd_draft": updated_prd_draft,
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error updating PRD for case {case_id}, user {user_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to update PRD draft: {str(e)}"
        )


@router.post(
    "/cases/{case_id}/submit-prd", status_code=200, summary="Submit PRD for review"
)
async def submit_prd_for_review(
    case_id: str = Path(
        ...,
        min_length=1,
        max_length=128,
        description="Business case ID"
    ), 
    current_user: dict = Depends(get_current_active_user),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """
    Submits the PRD for review, updating the case status to PRD_REVIEW.
    Ensures the authenticated user is the owner of the case and case is in appropriate state.
    """
    user_id = current_user.get("uid")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    try:
        # Import BusinessCaseStatus from orchestrator_agent
        from app.agents.orchestrator_agent import BusinessCaseStatus

        # Use FirestoreService to get the business case
        business_case = await firestore_service.get_business_case(case_id)
        
        if not business_case:
            raise HTTPException(
                status_code=404, detail=f"Business case {case_id} not found."
            )

        # Authorization check: verify user is the owner/initiator
        if business_case.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to submit this business case.",
            )

        # Status check: ensure case is in appropriate state for PRD submission
        current_status_str = str(business_case.status)
        if hasattr(business_case.status, "value"):
            current_status_str = business_case.status.value

        # Allow submission from INTAKE (if PRD content exists), PRD_DRAFTING, or PRD_REVIEW (resubmission)
        valid_submission_statuses = [
            BusinessCaseStatus.INTAKE.value,
            BusinessCaseStatus.PRD_DRAFTING.value,
            BusinessCaseStatus.PRD_REVIEW.value,
        ]
        if current_status_str not in valid_submission_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot submit PRD for review from current status: {current_status_str}. Must be in INTAKE, PRD_DRAFTING, or PRD_REVIEW state.",
            )

        # Verify PRD draft exists and has content
        prd_draft = business_case.prd_draft
        if not prd_draft or not prd_draft.get("content_markdown"):
            raise HTTPException(
                status_code=400,
                detail="Cannot submit PRD for review: PRD draft is empty or missing.",
            )

        # Get user email for history entry
        user_email = current_user.get("email", f"User {user_id}")

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "STATUS_UPDATE",
            "content": f"PRD submitted for review by {user_email}",
        }

        # Prepare update data
        current_history = business_case.history or []
        current_history.append(history_entry)
        
        update_data = {
            "status": BusinessCaseStatus.PRD_REVIEW.value,
            "updated_at": datetime.now(timezone.utc),
            "history": current_history,
        }

        # Use FirestoreService to update the business case
        success = await firestore_service.update_business_case(case_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to submit PRD for review"
            )

        return {
            "message": "PRD submitted for review successfully",
            "new_status": BusinessCaseStatus.PRD_REVIEW.value,
            "case_id": case_id,
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error submitting PRD for review for case {case_id}, user {user_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to submit PRD for review: {str(e)}"
        )


@router.post(
    "/cases/{case_id}/prd/approve",
    status_code=200,
    summary="Approve PRD for a specific business case",
)
async def approve_prd(
    case_id: str, 
    current_user: dict = Depends(get_current_active_user),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """
    Approves the PRD for a business case, updating the case status to PRD_APPROVED.
    Ensures the authenticated user is the owner/initiator of the case and case is in PRD_REVIEW status.
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")

    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    try:
        # Import BusinessCaseStatus from orchestrator_agent
        from app.agents.orchestrator_agent import BusinessCaseStatus

        # Use FirestoreService to get the business case
        business_case = await firestore_service.get_business_case(case_id)
        
        if not business_case:
            raise HTTPException(
                status_code=404, detail=f"Business case {case_id} not found."
            )

        # Use centralized approval permission logic with admin override
        from app.utils.approval_permissions import check_approval_permissions
        await check_approval_permissions(current_user, business_case.user_id, "PRD")

        # Status check: ensure case is in PRD_REVIEW status
        current_status_str = str(business_case.status)
        if hasattr(business_case.status, "value"):
            current_status_str = business_case.status.value

        if current_status_str != BusinessCaseStatus.PRD_REVIEW.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot approve PRD from current status: {current_status_str}. PRD must be in review status.",
            )

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "PRD_APPROVAL",
            "content": f"PRD approved by {user_email}",
        }

        # Prepare update data
        current_history = business_case.history or []
        current_history.append(history_entry)
        
        update_data = {
            "status": BusinessCaseStatus.PRD_APPROVED.value,
            "updated_at": datetime.now(timezone.utc),
            "history": current_history,
        }

        # Use FirestoreService to update the business case
        success = await firestore_service.update_business_case(case_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to approve PRD"
            )

        # After successful PRD approval, initiate system design generation
        try:
            from app.agents.orchestrator_agent import OrchestratorAgent

            orchestrator = OrchestratorAgent()

            logger.info(f"Triggering system design generation for approved PRD in case {case_id}")
            design_result = await orchestrator.handle_prd_approval(case_id)

            if design_result.get("status") == "success":
                logger.info(f"System design generation initiated successfully for case {case_id}")
                return {
                    "message": "PRD approved successfully and system design generation initiated",
                    "new_status": design_result.get("new_status", BusinessCaseStatus.PRD_APPROVED.value),
                    "case_id": case_id,
                    "system_design_initiated": True,
                }
            else:
                logger.info(f"System design generation failed for case {case_id}: {design_result.get('message')}")
                return {
                    "message": "PRD approved successfully but system design generation encountered an issue",
                    "new_status": BusinessCaseStatus.PRD_APPROVED.value,
                    "case_id": case_id,
                    "system_design_initiated": False,
                    "system_design_error": design_result.get("message"),
                }
        except Exception as design_error:
            logger.info(f"Error initiating system design for case {case_id}: {str(design_error)}")
            return {
                "message": "PRD approved successfully but system design generation could not be initiated",
                "new_status": BusinessCaseStatus.PRD_APPROVED.value,
                "case_id": case_id,
                "system_design_initiated": False,
                "system_design_error": str(design_error),
            }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error approving PRD for case {case_id}, user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to approve PRD: {str(e)}")


@router.post(
    "/cases/{case_id}/prd/reject",
    status_code=200,
    summary="Reject PRD for a specific business case",
)
async def reject_prd(
    case_id: str,
    reject_request: PrdRejectRequest = PrdRejectRequest(),
    current_user: dict = Depends(get_current_active_user),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """
    Rejects the PRD for a business case, updating the case status to PRD_REJECTED.
    Ensures the authenticated user is the owner/initiator of the case and case is in PRD_REVIEW status.
    Optionally accepts a rejection reason.
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")

    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    try:
        # Import BusinessCaseStatus from orchestrator_agent
        from app.agents.orchestrator_agent import BusinessCaseStatus

        # Use FirestoreService to get the business case
        business_case = await firestore_service.get_business_case(case_id)
        
        if not business_case:
            raise HTTPException(
                status_code=404, detail=f"Business case {case_id} not found."
            )

        # Use centralized rejection permission logic with admin override
        from app.utils.approval_permissions import check_approval_permissions
        await check_approval_permissions(current_user, business_case.user_id, "PRD")

        # Status check: ensure case is in PRD_REVIEW status
        current_status_str = str(business_case.status)
        if hasattr(business_case.status, "value"):
            current_status_str = business_case.status.value

        if current_status_str != BusinessCaseStatus.PRD_REVIEW.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot reject PRD from current status: {current_status_str}. PRD must be in review status.",
            )

        # Prepare history entry with optional reason
        rejection_content = f"PRD rejected by {user_email}"
        if reject_request.reason:
            rejection_content += f". Reason: {reject_request.reason}"

        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "PRD_REJECTION",
            "content": rejection_content,
        }

        # Prepare update data
        current_history = business_case.history or []
        current_history.append(history_entry)
        
        update_data = {
            "status": BusinessCaseStatus.PRD_REJECTED.value,
            "updated_at": datetime.now(timezone.utc),
            "history": current_history,
        }

        # Use FirestoreService to update the business case
        success = await firestore_service.update_business_case(case_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to reject PRD"
            )

        return {
            "message": "PRD rejected successfully",
            "new_status": BusinessCaseStatus.PRD_REJECTED.value,
            "case_id": case_id,
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error rejecting PRD for case {case_id}, user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reject PRD: {str(e)}")


@router.post(
    "/cases/{case_id}/trigger-system-design",
    status_code=200,
    summary="Manually trigger system design generation for a PRD_APPROVED case",
)
async def trigger_system_design_generation(
    case_id: str,
    current_user: dict = Depends(get_current_active_user),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """
    Manually triggers system design generation for a business case that is PRD_APPROVED 
    but missing system design (e.g., due to previous workflow failures).
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")

    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    try:
        # Import BusinessCaseStatus from orchestrator_agent
        from app.agents.orchestrator_agent import BusinessCaseStatus

        # Use FirestoreService to get the business case
        business_case = await firestore_service.get_business_case(case_id)
        
        if not business_case:
            raise HTTPException(
                status_code=404, detail=f"Business case {case_id} not found."
            )

        # Authorization check: verify user is the owner/initiator
        if business_case.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to trigger system design for this case.",
            )

        # Status check: ensure case is PRD_APPROVED
        current_status_str = str(business_case.status)
        if hasattr(business_case.status, "value"):
            current_status_str = business_case.status.value

        if current_status_str != BusinessCaseStatus.PRD_APPROVED.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot trigger system design from current status: {current_status_str}. Case must be PRD_APPROVED.",
            )

        # Check if system design already exists
        if hasattr(business_case, 'system_design_v1_draft') and business_case.system_design_v1_draft:
            return {
                "message": "System design already exists for this case",
                "case_id": case_id,
                "system_design_exists": True,
            }

        # Trigger system design generation
        try:
            from app.agents.orchestrator_agent import OrchestratorAgent

            orchestrator = OrchestratorAgent()

            logger.info(f"Manually triggering system design generation for case {case_id} by {user_email}")
            design_result = await orchestrator.handle_prd_approval(case_id)

            if design_result.get("status") == "success":
                logger.info(f"System design generation completed successfully for case {case_id}")
                return {
                    "message": "System design generation initiated successfully",
                    "new_status": design_result.get("new_status", BusinessCaseStatus.PRD_APPROVED.value),
                    "case_id": case_id,
                    "system_design_initiated": True,
                }
            else:
                logger.warning(f"System design generation failed for case {case_id}: {design_result.get('message')}")
                return {
                    "message": "System design generation encountered an issue",
                    "case_id": case_id,
                    "system_design_initiated": False,
                    "error": design_result.get("message"),
                }
        except Exception as design_error:
            logger.error(f"Error triggering system design for case {case_id}: {str(design_error)}")
            return {
                "message": "Failed to initiate system design generation",
                "case_id": case_id,
                "system_design_initiated": False,
                "error": str(design_error),
            }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error triggering system design for case {case_id}, user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger system design generation: {str(e)}")