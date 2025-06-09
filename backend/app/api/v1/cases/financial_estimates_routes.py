"""
API routes for financial estimates approval workflow (cost and value analysis).
"""

import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException

from app.auth.firebase_auth import get_current_active_user
from app.core.dependencies import get_firestore_service
from app.services.firestore_service import FirestoreService
from .models import CostEstimateRejectRequest, ValueProjectionRejectRequest, ValueProjectionUpdateRequest

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

        # Use centralized approval permission logic with admin override
        from app.utils.approval_permissions import check_approval_permissions
        await check_approval_permissions(current_user, business_case.user_id, "CostEstimate")

        # Status check: ensure case is in COSTING_PENDING_REVIEW status
        current_status_str = str(business_case.status)
        if hasattr(business_case.status, "value"):
            current_status_str = business_case.status.value

        if current_status_str != BusinessCaseStatus.COSTING_PENDING_REVIEW.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot approve cost estimate from current status: {current_status_str}. Cost estimate must be in COSTING_PENDING_REVIEW status.",
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
            value_result = await orchestrator.handle_cost_approval(case_id)

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

        # Use centralized rejection permission logic with admin override
        from app.utils.approval_permissions import check_approval_permissions
        await check_approval_permissions(current_user, business_case.user_id, "CostEstimate")

        # Status check: ensure case is in COSTING_PENDING_REVIEW status
        current_status_str = str(business_case.status)
        if hasattr(business_case.status, "value"):
            current_status_str = business_case.status.value

        if current_status_str != BusinessCaseStatus.COSTING_PENDING_REVIEW.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot reject cost estimate from current status: {current_status_str}. Cost estimate must be in COSTING_PENDING_REVIEW status.",
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

        # Use centralized approval permission logic with admin override
        from app.utils.approval_permissions import check_approval_permissions
        await check_approval_permissions(current_user, business_case.user_id, "ValueProjection")

        # Status check: ensure case is in VALUE_PENDING_REVIEW status
        current_status_str = str(business_case.status)
        if hasattr(business_case.status, "value"):
            current_status_str = business_case.status.value

        if current_status_str != BusinessCaseStatus.VALUE_PENDING_REVIEW.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot approve value projection from current status: {current_status_str}. Value projection must be in VALUE_PENDING_REVIEW status.",
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

        # After successful value projection approval, trigger financial model generation if cost is also approved
        try:
            from app.agents.orchestrator_agent import OrchestratorAgent

            orchestrator = OrchestratorAgent()

            logger.info(f"Triggering value approval handler for case {case_id}")
            financial_result = await orchestrator.handle_value_approval(case_id)

            if financial_result.get("status") == "success":
                final_status = financial_result.get("new_status", BusinessCaseStatus.VALUE_APPROVED.value)
                logger.info(f"Value approval handling completed for case {case_id} with status {final_status}")
                return {
                    "message": "Value projection approved successfully",
                    "new_status": final_status,
                    "case_id": case_id,
                    "orchestrator_message": financial_result.get("message"),
                }
            else:
                logger.info(f"Value approval handling failed for case {case_id}: {financial_result.get('message')}")
                return {
                    "message": "Value projection approved successfully but orchestrator handling encountered an issue",
                    "new_status": BusinessCaseStatus.VALUE_APPROVED.value,
                    "case_id": case_id,
                    "orchestrator_error": financial_result.get("message"),
                }
        except Exception as orchestrator_error:
            logger.info(f"Error in orchestrator value approval handling for case {case_id}: {str(orchestrator_error)}")
            return {
                "message": "Value projection approved successfully but orchestrator handling could not be performed",
                "new_status": BusinessCaseStatus.VALUE_APPROVED.value,
                "case_id": case_id,
                "orchestrator_error": str(orchestrator_error),
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

        # Use centralized rejection permission logic with admin override
        from app.utils.approval_permissions import check_approval_permissions
        await check_approval_permissions(current_user, business_case.user_id, "ValueProjection")

        # Status check: ensure case is in VALUE_PENDING_REVIEW status
        current_status_str = str(business_case.status)
        if hasattr(business_case.status, "value"):
            current_status_str = business_case.status.value

        if current_status_str != BusinessCaseStatus.VALUE_PENDING_REVIEW.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot reject value projection from current status: {current_status_str}. Value projection must be in VALUE_PENDING_REVIEW status.",
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


@router.put(
    "/cases/{case_id}/value-projection",
    status_code=200,
    summary="Update value projection for a specific business case",
)
async def update_value_projection(
    case_id: str,
    update_request: ValueProjectionUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """
    Updates the value projection for a business case.
    Ensures the authenticated user is the owner/initiator or has appropriate permissions
    and case is in VALUE_PENDING_REVIEW status.
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
        await check_approval_permissions(current_user, business_case.user_id, "ValueProjection")

        # Status check: ensure case is in VALUE_PENDING_REVIEW status
        current_status_str = str(business_case.status)
        if hasattr(business_case.status, "value"):
            current_status_str = business_case.status.value

        if current_status_str != BusinessCaseStatus.VALUE_PENDING_REVIEW.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot update value projection from current status: {current_status_str}. Value projection must be in VALUE_PENDING_REVIEW status.",
            )

        # Prepare updated value projection data
        updated_value_projection = {
            "scenarios": update_request.scenarios,
            "currency": update_request.currency,
        }
        
        # Add optional fields if provided
        if update_request.template_used:
            updated_value_projection["template_used"] = update_request.template_used
        if update_request.methodology:
            updated_value_projection["methodology"] = update_request.methodology
        if update_request.assumptions:
            updated_value_projection["assumptions"] = update_request.assumptions
        if update_request.notes:
            updated_value_projection["notes"] = update_request.notes
            
        # Keep existing metadata
        existing_value_projection = business_case.value_projection_v1 or {}
        updated_value_projection.update({
            "generated_by": existing_value_projection.get("generated_by", "SalesValueAnalystAgent"),
            "version": "v1",
            "generated_timestamp": existing_value_projection.get("generated_timestamp"),
            "last_edited_by": user_email,
            "last_edited_at": datetime.now(timezone.utc).isoformat(),
        })

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "VALUE_PROJECTION_UPDATE",
            "content": f"Value projection updated by {user_email}",
        }

        # Prepare update data
        current_history = business_case.history or []
        current_history.append(history_entry)
        
        update_data = {
            "value_projection_v1": updated_value_projection,
            "updated_at": datetime.now(timezone.utc),
            "history": current_history,
        }

        # Use FirestoreService to update the business case
        success = await firestore_service.update_business_case(case_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to update value projection"
            )

        return {
            "message": "Value projection updated successfully",
            "case_id": case_id,
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error updating value projection for case {case_id}, user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update value projection: {str(e)}")


@router.post(
    "/cases/{case_id}/financial-model/submit-review",
    status_code=200,
    summary="Submit financial model for review",
)
async def submit_financial_model_for_review(
    case_id: str, 
    current_user: dict = Depends(get_current_active_user),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """
    Submits the financial model for review by updating status to FINANCIAL_MODEL_PENDING_REVIEW.
    Only the case initiator can submit for review.
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

        # Authorization check: verify user is the owner/initiator
        if business_case.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to submit this financial model for review.",
            )

        # Status check: ensure case is in FINANCIAL_MODEL_COMPLETE status
        current_status_str = str(business_case.status)
        if hasattr(business_case.status, "value"):
            current_status_str = business_case.status.value

        allowed_statuses = [
            BusinessCaseStatus.FINANCIAL_MODEL_COMPLETE.value,
            BusinessCaseStatus.FINANCIAL_MODEL_REJECTED.value
        ]
        if current_status_str not in allowed_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot submit financial model for review from current status: {current_status_str}. Must be in FINANCIAL_MODEL_COMPLETE or FINANCIAL_MODEL_REJECTED status.",
            )

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "FINANCIAL_MODEL_SUBMIT_FOR_REVIEW",
            "content": f"Financial model submitted for review by {user_email}",
        }

        # Prepare update data
        current_history = business_case.history or []
        current_history.append(history_entry)
        
        update_data = {
            "status": BusinessCaseStatus.FINANCIAL_MODEL_PENDING_REVIEW.value,
            "updated_at": datetime.now(timezone.utc),
            "history": current_history,
        }

        # Use FirestoreService to update the business case
        success = await firestore_service.update_business_case(case_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to submit financial model for review"
            )

        return {
            "message": "Financial model submitted for review successfully",
            "new_status": BusinessCaseStatus.FINANCIAL_MODEL_PENDING_REVIEW.value,
            "case_id": case_id,
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error submitting financial model for review for case {case_id}, user {user_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to submit financial model for review: {str(e)}"
        )


@router.post(
    "/cases/{case_id}/financial-model/approve",
    status_code=200,
    summary="Approve financial model for a specific business case",
)
async def approve_financial_model(
    case_id: str, 
    current_user: dict = Depends(get_current_active_user),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """
    Approves the financial model for a business case, updating the case status to FINANCIAL_MODEL_APPROVED.
    Ensures the authenticated user has permission to approve financial models.
    Case must be in FINANCIAL_MODEL_PENDING_REVIEW status.
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
        await check_approval_permissions(current_user, business_case.user_id, "FinancialModel")

        # Status check: ensure case is in FINANCIAL_MODEL_PENDING_REVIEW status
        current_status_str = str(business_case.status)
        if hasattr(business_case.status, "value"):
            current_status_str = business_case.status.value

        if current_status_str != BusinessCaseStatus.FINANCIAL_MODEL_PENDING_REVIEW.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot approve financial model from current status: {current_status_str}. Financial model must be in FINANCIAL_MODEL_PENDING_REVIEW status.",
            )

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "FINANCIAL_MODEL_APPROVAL",
            "content": f"Financial model approved by {user_email}",
        }

        # Prepare update data
        current_history = business_case.history or []
        current_history.append(history_entry)
        
        update_data = {
            "status": BusinessCaseStatus.FINANCIAL_MODEL_APPROVED.value,
            "updated_at": datetime.now(timezone.utc),
            "history": current_history,
        }

        # Use FirestoreService to update the business case
        success = await firestore_service.update_business_case(case_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to approve financial model"
            )

        return {
            "message": "Financial model approved successfully",
            "new_status": BusinessCaseStatus.FINANCIAL_MODEL_APPROVED.value,
            "case_id": case_id,
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error approving financial model for case {case_id}, user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to approve financial model: {str(e)}")


@router.post(
    "/cases/{case_id}/financial-model/reject",
    status_code=200,
    summary="Reject financial model for a specific business case",
)
async def reject_financial_model(
    case_id: str,
    reject_request: dict = {},
    current_user: dict = Depends(get_current_active_user),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """
    Rejects the financial model for a business case, updating the case status to FINANCIAL_MODEL_REJECTED.
    Ensures the authenticated user has permission to approve financial models.
    Case must be in FINANCIAL_MODEL_PENDING_REVIEW status.
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
        await check_approval_permissions(current_user, business_case.user_id, "FinancialModel")

        # Status check: ensure case is in FINANCIAL_MODEL_PENDING_REVIEW status
        current_status_str = str(business_case.status)
        if hasattr(business_case.status, "value"):
            current_status_str = business_case.status.value

        if current_status_str != BusinessCaseStatus.FINANCIAL_MODEL_PENDING_REVIEW.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot reject financial model from current status: {current_status_str}. Financial model must be in FINANCIAL_MODEL_PENDING_REVIEW status.",
            )

        # Prepare history entry with optional reason
        rejection_message = f"Financial model rejected by {user_email}"
        reason = reject_request.get("reason", "").strip()
        if reason:
            rejection_message += f" - Reason: {reason}"

        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "FINANCIAL_MODEL_REJECTION",
            "content": rejection_message,
        }

        # Prepare update data
        current_history = business_case.history or []
        current_history.append(history_entry)
        
        update_data = {
            "status": BusinessCaseStatus.FINANCIAL_MODEL_REJECTED.value,
            "updated_at": datetime.now(timezone.utc),
            "history": current_history,
        }

        # Use FirestoreService to update the business case
        success = await firestore_service.update_business_case(case_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to reject financial model"
            )

        return {
            "message": "Financial model rejected successfully",
            "new_status": BusinessCaseStatus.FINANCIAL_MODEL_REJECTED.value,
            "case_id": case_id,
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error rejecting financial model for case {case_id}, user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reject financial model: {str(e)}") 