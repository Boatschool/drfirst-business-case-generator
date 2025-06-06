"""
API routes for final business case approval workflow.
"""

import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException

from app.auth.firebase_auth import get_current_active_user
from app.utils.config_helpers import require_dynamic_final_approver_role
from app.core.dependencies import get_firestore_service
from app.services.firestore_service import FirestoreService
from .models import FinalRejectRequest

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/cases/{case_id}/submit-final",
    status_code=200,
    summary="Submit business case for final approval",
)
async def submit_case_for_final_approval(
    case_id: str, 
    current_user: dict = Depends(get_current_active_user),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """
    Submits the business case for final approval by updating status to PENDING_FINAL_APPROVAL.
    Only the case initiator can submit for final approval.
    Case must be in FINANCIAL_MODEL_COMPLETE status.
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

        # Authorization check: only case initiator can submit for final approval
        if business_case.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Only the case initiator can submit for final approval.",
            )

        # Status check: must be in FINANCIAL_MODEL_COMPLETE
        current_status_str = str(business_case.status)
        if hasattr(business_case.status, "value"):
            current_status_str = business_case.status.value

        if current_status_str != BusinessCaseStatus.FINANCIAL_MODEL_COMPLETE.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot submit for final approval from current status: {current_status_str}. Must be in FINANCIAL_MODEL_COMPLETE status.",
            )

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "FINAL_SUBMISSION",
            "content": f"Case submitted for final approval by {user_email}",
        }

        # Prepare update data
        current_history = business_case.history or []
        current_history.append(history_entry)
        
        update_data = {
            "status": BusinessCaseStatus.PENDING_FINAL_APPROVAL.value,
            "updated_at": datetime.now(timezone.utc),
            "history": current_history,
        }

        # Use FirestoreService to update the business case
        success = await firestore_service.update_business_case(case_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to submit for final approval"
            )

        return {
            "message": "Business case submitted for final approval successfully",
            "new_status": BusinessCaseStatus.PENDING_FINAL_APPROVAL.value,
            "case_id": case_id,
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error submitting case {case_id} for final approval by user {user_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to submit for final approval: {str(e)}"
        )


@router.post(
    "/cases/{case_id}/approve-final",
    status_code=200,
    summary="Approve final business case",
)
async def approve_final_case(
    case_id: str,
    current_user: dict = Depends(lambda: require_dynamic_final_approver_role()()),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """
    Approves the entire business case by updating status to APPROVED.
    Only users with FINAL_APPROVER role can approve.
    Case must be in PENDING_FINAL_APPROVAL status.
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

        # Status check: must be in PENDING_FINAL_APPROVAL
        current_status_str = str(business_case.status)
        if hasattr(business_case.status, "value"):
            current_status_str = business_case.status.value

        if current_status_str != BusinessCaseStatus.PENDING_FINAL_APPROVAL.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot approve from current status: {current_status_str}. Must be in PENDING_FINAL_APPROVAL status.",
            )

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "FINAL_APPROVAL",
            "content": f"Business Case approved by {user_email}",
        }

        # Prepare update data
        current_history = business_case.history or []
        current_history.append(history_entry)
        
        update_data = {
            "status": BusinessCaseStatus.APPROVED.value,
            "updated_at": datetime.now(timezone.utc),
            "history": current_history,
        }

        # Use FirestoreService to update the business case
        success = await firestore_service.update_business_case(case_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to approve business case"
            )

        return {
            "message": "Business Case approved successfully",
            "new_status": BusinessCaseStatus.APPROVED.value,
            "case_id": case_id,
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error approving final case {case_id} by user {user_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to approve business case: {str(e)}"
        )


@router.post(
    "/cases/{case_id}/reject-final",
    status_code=200,
    summary="Reject final business case",
)
async def reject_final_case(
    case_id: str,
    reject_request: FinalRejectRequest = FinalRejectRequest(),
    current_user: dict = Depends(lambda: require_dynamic_final_approver_role()()),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """
    Rejects the entire business case by updating status to REJECTED.
    Only users with FINAL_APPROVER role can reject.
    Case must be in PENDING_FINAL_APPROVAL status.
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

        # Status check: must be in PENDING_FINAL_APPROVAL
        current_status_str = str(business_case.status)
        if hasattr(business_case.status, "value"):
            current_status_str = business_case.status.value

        if current_status_str != BusinessCaseStatus.PENDING_FINAL_APPROVAL.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot reject from current status: {current_status_str}. Must be in PENDING_FINAL_APPROVAL status.",
            )

        # Prepare history entry with optional reason
        rejection_message = f"Business Case rejected by {user_email}"
        if reject_request.reason:
            rejection_message += f". Reason: {reject_request.reason}"

        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "FINAL_REJECTION",
            "content": rejection_message,
        }

        # Prepare update data
        current_history = business_case.history or []
        current_history.append(history_entry)
        
        update_data = {
            "status": BusinessCaseStatus.REJECTED.value,
            "updated_at": datetime.now(timezone.utc),
            "history": current_history,
        }

        # Use FirestoreService to update the business case
        success = await firestore_service.update_business_case(case_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to reject business case"
            )

        return {
            "message": "Business Case rejected successfully",
            "new_status": BusinessCaseStatus.REJECTED.value,
            "case_id": case_id,
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error rejecting final case {case_id} by user {user_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to reject business case: {str(e)}"
        ) 