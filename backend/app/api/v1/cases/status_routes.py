"""
API routes for business case status management.
"""

import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException

from app.auth.firebase_auth import get_current_active_user
from app.core.dependencies import get_firestore_service
from app.services.firestore_service import FirestoreService
from app.core.constants import HTTPStatus, ErrorMessages, SuccessMessages, MessageTypes, MessageSources
from app.agents.orchestrator_agent import BusinessCaseStatus
from .models import StatusUpdateRequest

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter()


@router.put(
    "/cases/{case_id}/status",
    status_code=200,
    summary="Update status for a specific business case",
)
async def update_case_status(
    case_id: str,
    status_update_request: StatusUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    firestore_service: FirestoreService = Depends(get_firestore_service),
):
    """
    Updates the status of a specific business case.
    Used for workflow transitions like submitting PRD for review, approval, etc.
    Ensures the authenticated user has permission to change the status.
    """
    user_id = current_user.get("uid")
    if not user_id:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=ErrorMessages.USER_ID_NOT_FOUND)

    # Define valid status transitions using the BusinessCaseStatus enum
    VALID_STATUSES = [
        BusinessCaseStatus.INTAKE.value,
        BusinessCaseStatus.PRD_DRAFTING.value,
        BusinessCaseStatus.PRD_REVIEW.value,
        BusinessCaseStatus.PRD_APPROVED.value,
        BusinessCaseStatus.PRD_REJECTED.value,
        BusinessCaseStatus.SYSTEM_DESIGN_DRAFTING.value,
        BusinessCaseStatus.SYSTEM_DESIGN_DRAFTED.value,
        BusinessCaseStatus.SYSTEM_DESIGN_PENDING_REVIEW.value,
        BusinessCaseStatus.SYSTEM_DESIGN_APPROVED.value,
        BusinessCaseStatus.SYSTEM_DESIGN_REJECTED.value,
        BusinessCaseStatus.PLANNING_IN_PROGRESS.value,
        BusinessCaseStatus.PLANNING_COMPLETE.value,
        BusinessCaseStatus.EFFORT_PENDING_REVIEW.value,
        BusinessCaseStatus.EFFORT_APPROVED.value,
        BusinessCaseStatus.EFFORT_REJECTED.value,
        BusinessCaseStatus.COSTING_IN_PROGRESS.value,
        BusinessCaseStatus.COSTING_COMPLETE.value,
        BusinessCaseStatus.COSTING_PENDING_REVIEW.value,
        BusinessCaseStatus.COSTING_APPROVED.value,
        BusinessCaseStatus.COSTING_REJECTED.value,
        BusinessCaseStatus.VALUE_ANALYSIS_IN_PROGRESS.value,
        BusinessCaseStatus.VALUE_ANALYSIS_COMPLETE.value,
        BusinessCaseStatus.VALUE_PENDING_REVIEW.value,
        BusinessCaseStatus.VALUE_APPROVED.value,
        BusinessCaseStatus.VALUE_REJECTED.value,
        BusinessCaseStatus.FINANCIAL_MODEL_IN_PROGRESS.value,
        BusinessCaseStatus.FINANCIAL_MODEL_COMPLETE.value,
        BusinessCaseStatus.FINANCIAL_ANALYSIS.value,
        BusinessCaseStatus.FINAL_REVIEW.value,
        BusinessCaseStatus.PENDING_FINAL_APPROVAL.value,
        BusinessCaseStatus.APPROVED.value,
        BusinessCaseStatus.REJECTED.value,
    ]

    if status_update_request.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, 
            detail=f"Invalid status: {status_update_request.status}"
        )

    try:
        # Use FirestoreService to get the business case
        business_case = await firestore_service.get_business_case(case_id)
        
        if not business_case:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, 
                detail=f"Business case {case_id} not found."
            )

        # Basic authorization: check if the current user is the owner of the case
        # TODO: Implement more granular permissions for different status updates
        if business_case.user_id != user_id:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail=ErrorMessages.INSUFFICIENT_PERMISSIONS,
            )

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": MessageSources.USER,
            "messageType": MessageTypes.STATUS_UPDATE,
            "content": f"Status changed to {status_update_request.status}",
        }

        if status_update_request.comment:
            history_entry["content"] += f". Comment: {status_update_request.comment}"

        # Prepare update data
        update_data = {
            "status": status_update_request.status,
            "updated_at": datetime.now(timezone.utc),
        }
        
        # Add history entry to existing history
        current_history = business_case.history or []
        current_history.append(history_entry)
        update_data["history"] = current_history

        # Use FirestoreService to update the business case
        success = await firestore_service.update_business_case(case_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, 
                detail="Failed to update business case status"
            )

        return {
            "message": f"Status updated to {status_update_request.status} successfully",
            "new_status": status_update_request.status,
            "case_id": case_id,
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error updating status for case {case_id}, user {user_id}: {e}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, 
            detail=f"Failed to update case status: {str(e)}"
        ) 