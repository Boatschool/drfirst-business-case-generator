"""
API routes for financial estimates approval workflow (cost and value analysis).
"""

import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException

from app.auth.firebase_auth import get_current_active_user
from app.core.dependencies import get_firestore_service
from app.services.firestore_service import FirestoreService
from .models import CostEstimateRejectRequest, ValueProjectionRejectRequest

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/cases/{case_id}/cost-estimate/approve",
    status_code=200,
    summary="Approve cost estimate for a specific business case",
)
async def approve_cost_estimate(
    case_id: str, 
    current_user: dict = Depends(get_current_active_user),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """
    Approves the cost estimate for a business case, updating the case status to COSTING_APPROVED.
    Ensures the authenticated user is the owner/initiator of the case and case is in COSTING_COMPLETE status.
    After approval, triggers value analysis via orchestrator.
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

        # Authorization check: verify user is the owner/initiator (V1 - self-approval)
        if business_case.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to approve this cost estimate.",
            )

        # Status check: ensure case is in COSTING_COMPLETE status
        current_status_str = str(business_case.status)
        if hasattr(business_case.status, "value"):
            current_status_str = business_case.status.value

        if current_status_str != BusinessCaseStatus.COSTING_COMPLETE.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot approve cost estimate from current status: {current_status_str}. Cost estimate must be in COSTING_COMPLETE status.",
            )

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "COST_ESTIMATE_APPROVAL",
            "content": f"Cost estimate approved by {user_email}",
        }

        # Prepare update data
        current_history = business_case.history or []
        current_history.append(history_entry)
        
        update_data = {
            "status": BusinessCaseStatus.COSTING_APPROVED.value,
            "updated_at": datetime.now(timezone.utc),
            "history": current_history,
        }

        # Use FirestoreService to update the business case
        success = await firestore_service.update_business_case(case_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to approve cost estimate"
            )

        # After successful cost estimate approval, initiate value analysis generation
        try:
            from app.agents.orchestrator_agent import OrchestratorAgent

            orchestrator = OrchestratorAgent()

            logger.info(f"Triggering value analysis generation for approved cost estimate in case {case_id}")
            value_result = await orchestrator.handle_cost_completion(case_id)

            if value_result.get("status") == "success":
                logger.info(f"Value analysis generation initiated successfully for case {case_id}")
                return {
                    "message": "Cost estimate approved successfully and value analysis generation initiated",
                    "new_status": value_result.get("new_status", BusinessCaseStatus.COSTING_APPROVED.value),
                    "case_id": case_id,
                    "value_analysis_initiated": True,
                }
            else:
                logger.info(f"Value analysis generation failed for case {case_id}: {value_result.get('message')}")
                return {
                    "message": "Cost estimate approved successfully but value analysis generation encountered an issue",
                    "new_status": BusinessCaseStatus.COSTING_APPROVED.value,
                    "case_id": case_id,
                    "value_analysis_initiated": False,
                    "value_analysis_error": value_result.get("message"),
                }
        except Exception as value_error:
            logger.info(f"Error initiating value analysis for case {case_id}: {str(value_error)}")
            return {
                "message": "Cost estimate approved successfully but value analysis generation could not be initiated",
                "new_status": BusinessCaseStatus.COSTING_APPROVED.value,
                "case_id": case_id,
                "value_analysis_initiated": False,
                "value_analysis_error": str(value_error),
            }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error approving cost estimate for case {case_id}, user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to approve cost estimate: {str(e)}")


@router.post(
    "/cases/{case_id}/cost-estimate/reject",
    status_code=200,
    summary="Reject cost estimate for a specific business case",
)
async def reject_cost_estimate(
    case_id: str,
    reject_request: CostEstimateRejectRequest = CostEstimateRejectRequest(),
    current_user: dict = Depends(get_current_active_user),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """
    Rejects the cost estimate for a business case, updating the case status to COSTING_REJECTED.
    Ensures the authenticated user is the owner/initiator of the case and case is in COSTING_COMPLETE status.
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

        # Authorization check: verify user is the owner/initiator (V1 - self-approval)
        if business_case.user_id != user_id:
            raise HTTPException(
                status_code=403, detail="You do not have permission to reject this cost estimate."
            )

        # Status check: ensure case is in COSTING_COMPLETE status
        current_status_str = str(business_case.status)
        if hasattr(business_case.status, "value"):
            current_status_str = business_case.status.value

        if current_status_str != BusinessCaseStatus.COSTING_COMPLETE.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot reject cost estimate from current status: {current_status_str}. Cost estimate must be in COSTING_COMPLETE status.",
            )

        # Prepare history entry with optional reason
        rejection_content = f"Cost estimate rejected by {user_email}"
        if reject_request.reason:
            rejection_content += f". Reason: {reject_request.reason}"

        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "COST_ESTIMATE_REJECTION",
            "content": rejection_content,
        }

        # Prepare update data
        current_history = business_case.history or []
        current_history.append(history_entry)
        
        update_data = {
            "status": BusinessCaseStatus.COSTING_REJECTED.value,
            "updated_at": datetime.now(timezone.utc),
            "history": current_history,
        }

        # Use FirestoreService to update the business case
        success = await firestore_service.update_business_case(case_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to reject cost estimate"
            )

        return {
            "message": "Cost estimate rejected successfully",
            "new_status": BusinessCaseStatus.COSTING_REJECTED.value,
            "case_id": case_id,
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error rejecting cost estimate for case {case_id}, user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reject cost estimate: {str(e)}")


@router.post(
    "/cases/{case_id}/value-projection/approve",
    status_code=200,
    summary="Approve value projection for a specific business case",
)
async def approve_value_projection(
    case_id: str, 
    current_user: dict = Depends(get_current_active_user),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """
    Approves the value projection for a business case, updating the case status to VALUE_APPROVED.
    Ensures the authenticated user is the owner/initiator of the case and case is in VALUE_ANALYSIS_COMPLETE status.
    After approval, triggers financial model generation if cost estimate is also approved.
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

        # Authorization check: verify user is the owner/initiator (V1 - self-approval)
        if business_case.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to approve this value projection.",
            )

        # Status check: ensure case is in VALUE_ANALYSIS_COMPLETE status
        current_status_str = str(business_case.status)
        if hasattr(business_case.status, "value"):
            current_status_str = business_case.status.value

        if current_status_str != BusinessCaseStatus.VALUE_ANALYSIS_COMPLETE.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot approve value projection from current status: {current_status_str}. Value projection must be in VALUE_ANALYSIS_COMPLETE status.",
            )

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "VALUE_PROJECTION_APPROVAL",
            "content": f"Value projection approved by {user_email}",
        }

        # Prepare update data
        current_history = business_case.history or []
        current_history.append(history_entry)
        
        update_data = {
            "status": BusinessCaseStatus.VALUE_APPROVED.value,
            "updated_at": datetime.now(timezone.utc),
            "history": current_history,
        }

        # Use FirestoreService to update the business case
        success = await firestore_service.update_business_case(case_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to approve value projection"
            )

        # After successful value projection approval, check if we can trigger financial model generation
        try:
            from app.agents.orchestrator_agent import OrchestratorAgent

            orchestrator = OrchestratorAgent()

            logger.info(f"Checking if financial model generation can be triggered for case {case_id}")
            financial_result = await orchestrator.check_and_trigger_financial_model(case_id)

            if financial_result.get("status") == "success":
                logger.info(f"Financial model check completed for case {case_id}")
                return {
                    "message": "Value projection approved successfully",
                    "new_status": BusinessCaseStatus.VALUE_APPROVED.value,
                    "case_id": case_id,
                    "financial_model_check": financial_result.get("message"),
                }
            else:
                logger.info(f"Financial model check failed for case {case_id}: {financial_result.get('message')}")
                return {
                    "message": "Value projection approved successfully",
                    "new_status": BusinessCaseStatus.VALUE_APPROVED.value,
                    "case_id": case_id,
                    "financial_model_error": financial_result.get("message"),
                }
        except Exception as financial_error:
            logger.info(f"Error checking financial model for case {case_id}: {str(financial_error)}")
            return {
                "message": "Value projection approved successfully but financial model check could not be performed",
                "new_status": BusinessCaseStatus.VALUE_APPROVED.value,
                "case_id": case_id,
                "financial_model_error": str(financial_error),
            }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error approving value projection for case {case_id}, user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to approve value projection: {str(e)}")


@router.post(
    "/cases/{case_id}/value-projection/reject",
    status_code=200,
    summary="Reject value projection for a specific business case",
)
async def reject_value_projection(
    case_id: str,
    reject_request: ValueProjectionRejectRequest = ValueProjectionRejectRequest(),
    current_user: dict = Depends(get_current_active_user),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """
    Rejects the value projection for a business case, updating the case status to VALUE_REJECTED.
    Ensures the authenticated user is the owner/initiator of the case and case is in VALUE_ANALYSIS_COMPLETE status.
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

        # Authorization check: verify user is the owner/initiator (V1 - self-approval)
        if business_case.user_id != user_id:
            raise HTTPException(
                status_code=403, detail="You do not have permission to reject this value projection."
            )

        # Status check: ensure case is in VALUE_ANALYSIS_COMPLETE status
        current_status_str = str(business_case.status)
        if hasattr(business_case.status, "value"):
            current_status_str = business_case.status.value

        if current_status_str != BusinessCaseStatus.VALUE_ANALYSIS_COMPLETE.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot reject value projection from current status: {current_status_str}. Value projection must be in VALUE_ANALYSIS_COMPLETE status.",
            )

        # Prepare history entry with optional reason
        rejection_content = f"Value projection rejected by {user_email}"
        if reject_request.reason:
            rejection_content += f". Reason: {reject_request.reason}"

        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "VALUE_PROJECTION_REJECTION",
            "content": rejection_content,
        }

        # Prepare update data
        current_history = business_case.history or []
        current_history.append(history_entry)
        
        update_data = {
            "status": BusinessCaseStatus.VALUE_REJECTED.value,
            "updated_at": datetime.now(timezone.utc),
            "history": current_history,
        }

        # Use FirestoreService to update the business case
        success = await firestore_service.update_business_case(case_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to reject value projection"
            )

        return {
            "message": "Value projection rejected successfully",
            "new_status": BusinessCaseStatus.VALUE_REJECTED.value,
            "case_id": case_id,
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error rejecting value projection for case {case_id}, user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reject value projection: {str(e)}") 