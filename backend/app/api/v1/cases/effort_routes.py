"""
API routes for effort estimate approval workflow.
"""

import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException

from app.auth.firebase_auth import get_current_active_user
from app.core.dependencies import get_firestore_service
from app.services.firestore_service import FirestoreService
from .models import EffortEstimateUpdateRequest, EffortEstimateRejectRequest

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter()


@router.put(
    "/cases/{case_id}/effort-estimate",
    status_code=200,
    summary="Update effort estimate for a specific business case",
)
async def update_effort_estimate(
    case_id: str,
    effort_update_request: EffortEstimateUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """
    Updates the effort estimate for a business case.
    Ensures the authenticated user is the owner/initiator of the case and case is in allowed status.
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")

    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    try:
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
                detail="You do not have permission to update this effort estimate.",
            )

        # Status check: ensure case is in allowed status for effort estimate editing
        current_status_str = str(business_case.status)
        if hasattr(business_case.status, "value"):
            current_status_str = business_case.status.value

        allowed_statuses = [
            BusinessCaseStatus.EFFORT_PENDING_REVIEW.value,
            BusinessCaseStatus.PLANNING_COMPLETE.value
        ]
        
        if current_status_str not in allowed_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot update effort estimate from current status: {current_status_str}. Must be in EFFORT_PENDING_REVIEW or PLANNING_COMPLETE status.",
            )

        # Prepare the updated effort estimate
        updated_effort_estimate = {
            "roles": effort_update_request.roles,
            "total_hours": effort_update_request.total_hours,
            "estimated_duration_weeks": effort_update_request.estimated_duration_weeks,
            "complexity_assessment": effort_update_request.complexity_assessment,
            "notes": effort_update_request.notes,
            "updated_by": user_email,
            "updated_timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "v1"
        }

        # If there's an existing effort estimate, preserve metadata
        current_effort = business_case.effort_estimate_v1 or {}
        if current_effort.get("generated_by"):
            updated_effort_estimate["generated_by"] = current_effort["generated_by"]
        if current_effort.get("generated_timestamp"):
            updated_effort_estimate["original_generated_timestamp"] = current_effort["generated_timestamp"]

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "EFFORT_ESTIMATE_UPDATE",
            "content": f"Effort estimate manually updated by {user_email}",
        }

        # Prepare update data
        current_history = business_case.history or []
        current_history.append(history_entry)
        
        update_data = {
            "effort_estimate_v1": updated_effort_estimate,
            "updated_at": datetime.now(timezone.utc),
            "history": current_history,
        }

        # Use FirestoreService to update the business case
        success = await firestore_service.update_business_case(case_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to update effort estimate"
            )

        return {
            "message": "Effort estimate updated successfully",
            "case_id": case_id,
            "updated_effort_estimate": updated_effort_estimate,
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error updating effort estimate for case {case_id}, user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update effort estimate: {str(e)}")


@router.post(
    "/cases/{case_id}/effort-estimate/generate",
    status_code=200,
    summary="Generate effort estimate for a specific business case",
)
async def generate_effort_estimate(
    case_id: str,
    current_user: dict = Depends(get_current_active_user),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """
    Triggers AI-powered effort estimate generation for a business case.
    Ensures the authenticated user is the owner/initiator of the case and system design is approved.
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")

    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    try:
        from app.agents.orchestrator_agent import BusinessCaseStatus, OrchestratorAgent

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
                detail="You do not have permission to generate effort estimates for this case.",
            )

        # Status check: ensure system design is approved
        current_status_str = str(business_case.status)
        if hasattr(business_case.status, "value"):
            current_status_str = business_case.status.value

        allowed_statuses = [
            BusinessCaseStatus.SYSTEM_DESIGN_APPROVED.value,
            BusinessCaseStatus.PLANNING_IN_PROGRESS.value
        ]
        
        if current_status_str not in allowed_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot generate effort estimate from current status: {current_status_str}. System design must be approved first.",
            )

        # Check if effort estimate already exists
        if business_case.effort_estimate_v1:
            raise HTTPException(
                status_code=409,
                detail="Effort estimate already exists for this case. Use the update endpoint to modify it.",
            )

        # Trigger effort estimation using orchestrator
        orchestrator = OrchestratorAgent()
        
        logger.info(f"Triggering effort estimate generation for case {case_id} by user {user_email}")
        result = await orchestrator.handle_system_design_approval(case_id)

        if result.get("status") == "success":
            logger.info(f"Effort estimate generation completed successfully for case {case_id}")
            return {
                "message": "Effort estimate generation triggered successfully",
                "new_status": result.get("new_status", BusinessCaseStatus.EFFORT_PENDING_REVIEW.value),
                "case_id": case_id,
            }
        else:
            error_msg = result.get("message", "Failed to generate effort estimate")
            logger.warning(f"Effort estimate generation failed for case {case_id}: {error_msg}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate effort estimate: {error_msg}",
            )

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error generating effort estimate for case {case_id}, user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate effort estimate: {str(e)}")


@router.post(
    "/cases/{case_id}/effort-estimate/submit",
    status_code=200,
    summary="Submit effort estimate for review",
)
async def submit_effort_estimate_for_review(
    case_id: str,
    current_user: dict = Depends(get_current_active_user),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """
    Submits the effort estimate for review, updating the case status to EFFORT_PENDING_REVIEW.
    Ensures the authenticated user is the owner/initiator of the case and case has a completed effort estimate.
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")

    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    try:
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
                detail="You do not have permission to submit this effort estimate for review.",
            )

        # Status check: ensure case is in allowed status for submission
        current_status_str = str(business_case.status)
        if hasattr(business_case.status, "value"):
            current_status_str = business_case.status.value

        allowed_statuses = [
            BusinessCaseStatus.PLANNING_COMPLETE.value,
            BusinessCaseStatus.EFFORT_REJECTED.value
        ]
        
        if current_status_str not in allowed_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot submit effort estimate from current status: {current_status_str}. Must be in PLANNING_COMPLETE or EFFORT_REJECTED status.",
            )

        # Check if effort estimate exists
        if not business_case.effort_estimate_v1:
            raise HTTPException(
                status_code=400,
                detail="Cannot submit effort estimate for review: no effort estimate found. Generate an effort estimate first.",
            )

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "EFFORT_ESTIMATE_SUBMISSION",
            "content": f"Effort estimate submitted for review by {user_email}",
        }

        # Prepare update data
        current_history = business_case.history or []
        current_history.append(history_entry)
        
        update_data = {
            "status": BusinessCaseStatus.EFFORT_PENDING_REVIEW.value,
            "updated_at": datetime.now(timezone.utc),
            "history": current_history,
        }

        # Use FirestoreService to update the business case
        success = await firestore_service.update_business_case(case_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to submit effort estimate for review"
            )

        return {
            "message": "Effort estimate submitted for review successfully",
            "new_status": BusinessCaseStatus.EFFORT_PENDING_REVIEW.value,
            "case_id": case_id,
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error submitting effort estimate for review for case {case_id}, user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit effort estimate for review: {str(e)}")


@router.post(
    "/cases/{case_id}/effort-estimate/approve",
    status_code=200,
    summary="Approve effort estimate for a specific business case",
)
async def approve_effort_estimate(
    case_id: str, 
    current_user: dict = Depends(get_current_active_user),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """
    Approves the effort estimate for a business case, updating the case status to EFFORT_APPROVED.
    Ensures the authenticated user is the owner/initiator of the case and case is in EFFORT_PENDING_REVIEW status.
    After approval, triggers cost analysis via orchestrator.
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")

    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    try:
        from app.agents.orchestrator_agent import BusinessCaseStatus

        # Use FirestoreService to get the business case
        business_case = await firestore_service.get_business_case(case_id)
        
        if not business_case:
            raise HTTPException(
                status_code=404, detail=f"Business case {case_id} not found."
            )

        # Use centralized approval permission logic with admin override
        from app.utils.approval_permissions import check_approval_permissions
        await check_approval_permissions(current_user, business_case.user_id, "EffortEstimate")

        # Status check: ensure case is in EFFORT_PENDING_REVIEW status
        current_status_str = str(business_case.status)
        if hasattr(business_case.status, "value"):
            current_status_str = business_case.status.value

        if current_status_str != BusinessCaseStatus.EFFORT_PENDING_REVIEW.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot approve effort estimate from current status: {current_status_str}. Effort estimate must be in EFFORT_PENDING_REVIEW status.",
            )

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "EFFORT_ESTIMATE_APPROVAL",
            "content": f"Effort estimate approved by {user_email}",
        }

        # Prepare update data
        current_history = business_case.history or []
        current_history.append(history_entry)
        
        update_data = {
            "status": BusinessCaseStatus.EFFORT_APPROVED.value,
            "updated_at": datetime.now(timezone.utc),
            "history": current_history,
        }

        # Use FirestoreService to update the business case
        success = await firestore_service.update_business_case(case_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to approve effort estimate"
            )

        # After successful effort estimate approval, initiate cost analysis
        try:
            from app.agents.orchestrator_agent import OrchestratorAgent

            orchestrator = OrchestratorAgent()

            logger.info(f"Triggering cost analysis for approved effort estimate in case {case_id}")
            cost_result = await orchestrator.handle_effort_approval(case_id)

            if cost_result.get("status") == "success":
                logger.info(f"Cost analysis initiated successfully for case {case_id}")
                return {
                    "message": "Effort estimate approved successfully and cost analysis initiated",
                    "new_status": cost_result.get("new_status", BusinessCaseStatus.EFFORT_APPROVED.value),
                    "case_id": case_id,
                    "cost_analysis_initiated": True,
                }
            else:
                logger.info(f"Cost analysis failed for case {case_id}: {cost_result.get('message')}")
                return {
                    "message": "Effort estimate approved successfully but cost analysis encountered an issue",
                    "new_status": BusinessCaseStatus.EFFORT_APPROVED.value,
                    "case_id": case_id,
                    "cost_analysis_initiated": False,
                    "cost_analysis_error": cost_result.get("message"),
                }
        except Exception as cost_error:
            logger.info(f"Error initiating cost analysis for case {case_id}: {str(cost_error)}")
            return {
                "message": "Effort estimate approved successfully but cost analysis could not be initiated",
                "new_status": BusinessCaseStatus.EFFORT_APPROVED.value,
                "case_id": case_id,
                "cost_analysis_initiated": False,
                "cost_analysis_error": str(cost_error),
            }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error approving effort estimate for case {case_id}, user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to approve effort estimate: {str(e)}")


@router.post(
    "/cases/{case_id}/effort-estimate/reject",
    status_code=200,
    summary="Reject effort estimate for a specific business case",
)
async def reject_effort_estimate(
    case_id: str,
    reject_request: EffortEstimateRejectRequest = EffortEstimateRejectRequest(),
    current_user: dict = Depends(get_current_active_user),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """
    Rejects the effort estimate for a business case, updating the case status to EFFORT_REJECTED.
    Ensures the authenticated user is the owner/initiator of the case and case is in EFFORT_PENDING_REVIEW status.
    Optionally accepts a rejection reason.
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")

    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    try:
        from app.agents.orchestrator_agent import BusinessCaseStatus

        # Use FirestoreService to get the business case
        business_case = await firestore_service.get_business_case(case_id)
        
        if not business_case:
            raise HTTPException(
                status_code=404, detail=f"Business case {case_id} not found."
            )

        # Use centralized rejection permission logic with admin override
        from app.utils.approval_permissions import check_approval_permissions
        await check_approval_permissions(current_user, business_case.user_id, "EffortEstimate")

        # Status check: ensure case is in EFFORT_PENDING_REVIEW status
        current_status_str = str(business_case.status)
        if hasattr(business_case.status, "value"):
            current_status_str = business_case.status.value

        if current_status_str != BusinessCaseStatus.EFFORT_PENDING_REVIEW.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot reject effort estimate from current status: {current_status_str}. Effort estimate must be in EFFORT_PENDING_REVIEW status.",
            )

        # Prepare history entry with optional reason
        rejection_content = f"Effort estimate rejected by {user_email}"
        if reject_request.reason:
            rejection_content += f". Reason: {reject_request.reason}"

        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "EFFORT_ESTIMATE_REJECTION",
            "content": rejection_content,
        }

        # Prepare update data
        current_history = business_case.history or []
        current_history.append(history_entry)
        
        update_data = {
            "status": BusinessCaseStatus.EFFORT_REJECTED.value,
            "updated_at": datetime.now(timezone.utc),
            "history": current_history,
        }

        # Use FirestoreService to update the business case
        success = await firestore_service.update_business_case(case_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to reject effort estimate"
            )

        return {
            "message": "Effort estimate rejected successfully",
            "new_status": BusinessCaseStatus.EFFORT_REJECTED.value,
            "case_id": case_id,
            "rejection_reason": reject_request.reason,
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error rejecting effort estimate for case {case_id}, user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reject effort estimate: {str(e)}") 