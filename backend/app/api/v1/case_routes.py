"""
API routes for managing business cases.
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import asyncio

from app.auth.firebase_auth import get_current_active_user
from google.cloud import firestore
from app.core.config import settings

# Assuming BusinessCaseStatus is defined in orchestrator_agent or a shared models location
# If it's in orchestrator_agent, the import might be: from app.agents.orchestrator_agent import BusinessCaseStatus
# For now, let's define a simple status enum here if not easily importable or use string.
# from app.models.firestore_models import BusinessCase # This model is too detailed for a list summary

router = APIRouter()

# Pydantic model for the response of listing cases (summary)
class BusinessCaseSummary(BaseModel):
    case_id: str
    user_id: str
    title: str
    status: str # Ideally, this would use the BusinessCaseStatus Enum
    created_at: datetime
    updated_at: datetime
    # prd_draft_available: bool # Example of an additional summary field

# Pydantic model for the full details of a business case
class BusinessCaseDetailsModel(BaseModel):
    case_id: str
    user_id: str
    title: str
    problem_statement: str
    relevant_links: List[Dict[str, str]] = Field(default_factory=list)
    status: str # Ideally, this would use an Enum shared with the agent
    history: List[Dict[str, Any]] = Field(default_factory=list)
    prd_draft: Optional[Dict[str, Any]] = None
    system_design_v1_draft: Optional[Dict[str, Any]] = None
    effort_estimate_v1: Optional[Dict[str, Any]] = None     # New: Effort estimate from PlannerAgent
    cost_estimate_v1: Optional[Dict[str, Any]] = None       # New: Cost estimate from CostAnalystAgent
    value_projection_v1: Optional[Dict[str, Any]] = None    # New: Value projection from SalesValueAnalystAgent
    financial_summary_v1: Optional[Dict[str, Any]] = None   # New: Financial summary from FinancialModelAgent
    created_at: datetime
    updated_at: datetime

class PrdUpdateRequest(BaseModel):
    content_markdown: str
    # version: Optional[str] = None # Could add versioning later

class StatusUpdateRequest(BaseModel):
    status: str
    comment: Optional[str] = None

@router.get("/cases", response_model=List[BusinessCaseSummary], summary="List business cases for the authenticated user")
async def list_user_cases(
    current_user: dict = Depends(get_current_active_user)
):
    """
    Retrieves a list of business cases initiated by the authenticated user.
    Filters cases by the `user_id` from the Firebase token.
    """
    user_id = current_user.get("uid")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    try:
        db = firestore.Client(project=settings.firebase_project_id)
        cases_query = db.collection("businessCases").where("user_id", "==", user_id)
        docs_snapshot = await asyncio.to_thread(cases_query.stream)
        
        # Convert to list and sort by updated_at in Python (since we removed Firestore ordering)
        docs_list = list(docs_snapshot)
        docs_list.sort(key=lambda doc: doc.to_dict().get("updated_at", datetime.min), reverse=True)
        
        summaries: List[BusinessCaseSummary] = []
        for doc in docs_list:
            data = doc.to_dict()
            if data: # Ensure data exists
                # Convert status Enum to string if it's an Enum object, otherwise assume it's already a string
                status_value = data.get("status")
                if hasattr(status_value, 'value'): # Check if it's an Enum instance
                    status_str = status_value.value
                else:
                    status_str = str(status_value) # Fallback to string conversion
                
                summaries.append(
                    BusinessCaseSummary(
                        case_id=data.get("case_id", doc.id),
                        user_id=data.get("user_id"),
                        title=data.get("title", "N/A"),
                        status=status_str,
                        created_at=data.get("created_at"),
                        updated_at=data.get("updated_at")
                    )
                )
        return summaries
    except Exception as e:
        print(f"Error listing cases for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve business cases: {str(e)}")

@router.get("/cases/{case_id}", response_model=BusinessCaseDetailsModel, summary="Get details for a specific business case")
async def get_case_details(
    case_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Retrieves the full details for a specific business case.
    Ensures the authenticated user is the owner of the case or has appropriate access (future enhancement).
    """
    user_id = current_user.get("uid")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    try:
        db = firestore.Client(project=settings.firebase_project_id)
        case_doc_ref = db.collection("businessCases").document(case_id)
        # Use asyncio.to_thread for the blocking Firestore call
        doc = await asyncio.to_thread(case_doc_ref.get)

        if not doc.exists:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} not found.")
        
        data = doc.to_dict()
        if not data: # Should not happen if doc.exists is true, but good practice
             raise HTTPException(status_code=404, detail=f"Business case {case_id} data is empty.")

        # Basic authorization: check if the current user is the owner of the case
        if data.get("user_id") != user_id:
            # More granular permissions could be implemented here in the future
            # For example, allow admins or collaborators to view.
            raise HTTPException(status_code=403, detail="You do not have permission to view this business case.")

        status_value = data.get("status")
        if hasattr(status_value, 'value'): # Check if it's an Enum instance
            status_str = status_value.value
        else:
            status_str = str(status_value) # Fallback to string conversion

        return BusinessCaseDetailsModel(
            case_id=data.get("case_id", doc.id),
            user_id=data.get("user_id"),
            title=data.get("title", "N/A"),
            problem_statement=data.get("problem_statement", ""),
            relevant_links=data.get("relevant_links", []),
            status=status_str,
            history=data.get("history", []),
            prd_draft=data.get("prd_draft"),
            system_design_v1_draft=data.get("system_design_v1_draft"),
            effort_estimate_v1=data.get("effort_estimate_v1"),
            cost_estimate_v1=data.get("cost_estimate_v1"),
            value_projection_v1=data.get("value_projection_v1"),
            financial_summary_v1=data.get("financial_summary_v1"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
    except HTTPException as http_exc: # Re-raise known HTTP exceptions
        raise http_exc
    except Exception as e:
        print(f"Error retrieving case {case_id} for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve business case details: {str(e)}")

@router.put("/cases/{case_id}/prd", status_code=200, summary="Update PRD for a specific business case")
async def update_prd_draft(
    case_id: str,
    prd_update_request: PrdUpdateRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Updates the PRD draft for a specific business case.
    Ensures the authenticated user is the owner of the case.
    """
    user_id = current_user.get("uid")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    try:
        db = firestore.Client(project=settings.firebase_project_id)
        case_doc_ref = db.collection("businessCases").document(case_id)

        doc_snapshot = await asyncio.to_thread(case_doc_ref.get)
        if not doc_snapshot.exists:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} not found.")

        case_data = doc_snapshot.to_dict()
        if not case_data:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} data is empty.")

        if case_data.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="You do not have permission to edit this business case.")

        # Construct the PRD draft object to be stored
        # This assumes a similar structure to how ProductManagerAgent might store it initially
        existing_prd_draft = case_data.get("prd_draft") or {}
        updated_prd_draft = {
            "title": case_data.get("title", "PRD") + " - Draft", # Or derive title differently
            "content_markdown": prd_update_request.content_markdown,
            "version": existing_prd_draft.get("version", "1.0.0") # Basic versioning, could be incremented
            # Potentially add last_edited_by, last_edited_at fields here
        }

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "PRD_UPDATE",
            "content": f"User updated the PRD draft. New version: {updated_prd_draft.get('version')}"
        }

        update_data = {
            "prd_draft": updated_prd_draft,
            "updated_at": datetime.now(timezone.utc),
            "history": firestore.ArrayUnion([history_entry])
        }

        await asyncio.to_thread(case_doc_ref.update, update_data)
        
        # Return the updated PRD draft or a success message
        # For consistency with GET, could return the whole updated case, or just the PRD part
        return {"message": "PRD draft updated successfully", "updated_prd_draft": updated_prd_draft}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error updating PRD for case {case_id}, user {user_id}: {e}")
        print(f"Full traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to update PRD draft: {str(e)}")

@router.post("/cases/{case_id}/submit-prd", status_code=200, summary="Submit PRD for review")
async def submit_prd_for_review(
    case_id: str,
    current_user: dict = Depends(get_current_active_user)
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
        
        db = firestore.Client(project=settings.firebase_project_id)
        case_doc_ref = db.collection("businessCases").document(case_id)

        doc_snapshot = await asyncio.to_thread(case_doc_ref.get)
        if not doc_snapshot.exists:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} not found.")

        case_data = doc_snapshot.to_dict()
        if not case_data:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} data is empty.")

        # Authorization check: verify user is the owner/initiator
        if case_data.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="You do not have permission to submit this business case.")

        # Status check: ensure case is in appropriate state for PRD submission
        current_status = case_data.get("status")
        if hasattr(current_status, 'value'):
            current_status_str = current_status.value
        else:
            current_status_str = str(current_status)

        # Allow submission from INTAKE (if PRD content exists), PRD_DRAFTING, or PRD_REVIEW (resubmission)
        valid_submission_statuses = [BusinessCaseStatus.INTAKE.value, BusinessCaseStatus.PRD_DRAFTING.value, BusinessCaseStatus.PRD_REVIEW.value]
        if current_status_str not in valid_submission_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot submit PRD for review from current status: {current_status_str}. Must be in INTAKE, PRD_DRAFTING, or PRD_REVIEW state."
            )

        # Verify PRD draft exists and has content
        prd_draft = case_data.get("prd_draft")
        if not prd_draft or not prd_draft.get("content_markdown"):
            raise HTTPException(status_code=400, detail="Cannot submit PRD for review: PRD draft is empty or missing.")

        # Get user email for history entry
        user_email = current_user.get("email", f"User {user_id}")

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "STATUS_UPDATE",
            "content": f"PRD submitted for review by {user_email}"
        }

        # Update case status and add history entry
        update_data = {
            "status": BusinessCaseStatus.PRD_REVIEW.value,
            "updated_at": datetime.now(timezone.utc),
            "history": firestore.ArrayUnion([history_entry])
        }

        await asyncio.to_thread(case_doc_ref.update, update_data)
        
        return {
            "message": "PRD submitted for review successfully",
            "new_status": BusinessCaseStatus.PRD_REVIEW.value,
            "case_id": case_id
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error submitting PRD for review for case {case_id}, user {user_id}: {e}")
        print(f"Full traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to submit PRD for review: {str(e)}")

class PrdRejectRequest(BaseModel):
    reason: Optional[str] = None

# Pydantic models for System Design workflow
class SystemDesignUpdateRequest(BaseModel):
    content_markdown: str

class SystemDesignRejectRequest(BaseModel):
    reason: Optional[str] = None

class EffortEstimateUpdateRequest(BaseModel):
    roles: List[Dict[str, Any]]
    total_hours: int
    estimated_duration_weeks: int
    complexity_assessment: str
    notes: Optional[str] = None

class CostEstimateUpdateRequest(BaseModel):
    estimated_cost: float
    currency: str
    rate_card_used: Optional[str] = None
    breakdown_by_role: List[Dict[str, Any]]
    calculation_method: Optional[str] = None
    notes: Optional[str] = None

class ValueProjectionUpdateRequest(BaseModel):
    scenarios: List[Dict[str, Any]]
    currency: str
    template_used: Optional[str] = None
    methodology: Optional[str] = None
    assumptions: Optional[List[str]] = None
    notes: Optional[str] = None

class EffortEstimateRejectRequest(BaseModel):
    reason: Optional[str] = None

class CostEstimateRejectRequest(BaseModel):
    reason: Optional[str] = None

class ValueProjectionRejectRequest(BaseModel):
    reason: Optional[str] = None

@router.post("/cases/{case_id}/prd/approve", status_code=200, summary="Approve PRD for a specific business case")
async def approve_prd(
    case_id: str,
    current_user: dict = Depends(get_current_active_user)
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
        
        db = firestore.Client(project=settings.firebase_project_id)
        case_doc_ref = db.collection("businessCases").document(case_id)

        doc_snapshot = await asyncio.to_thread(case_doc_ref.get)
        if not doc_snapshot.exists:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} not found.")

        case_data = doc_snapshot.to_dict()
        if not case_data:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} data is empty.")

        # Authorization check: verify user is the owner/initiator (V1 - self-approval)
        if case_data.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="You do not have permission to approve this PRD.")

        # Status check: ensure case is in PRD_REVIEW status
        current_status = case_data.get("status")
        if hasattr(current_status, 'value'):
            current_status_str = current_status.value
        else:
            current_status_str = str(current_status)

        if current_status_str != BusinessCaseStatus.PRD_REVIEW.value:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot approve PRD from current status: {current_status_str}. PRD must be in review status."
            )

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "PRD_APPROVAL",
            "content": f"PRD approved by {user_email}"
        }

        # Update case status to PRD_APPROVED and add history entry
        update_data = {
            "status": BusinessCaseStatus.PRD_APPROVED.value,
            "updated_at": datetime.now(timezone.utc),
            "history": firestore.ArrayUnion([history_entry])
        }

        await asyncio.to_thread(case_doc_ref.update, update_data)
        
        # After successful PRD approval, initiate system design generation
        try:
            from app.agents.orchestrator_agent import OrchestratorAgent
            orchestrator = OrchestratorAgent()
            
            print(f"Triggering system design generation for approved PRD in case {case_id}")
            design_result = await orchestrator.handle_prd_approval(case_id)
            
            if design_result.get("status") == "success":
                print(f"System design generation initiated successfully for case {case_id}")
                return {
                    "message": "PRD approved successfully and system design generation initiated",
                    "new_status": design_result.get("new_status", BusinessCaseStatus.PRD_APPROVED.value),
                    "case_id": case_id,
                    "system_design_initiated": True
                }
            else:
                print(f"System design generation failed for case {case_id}: {design_result.get('message')}")
                return {
                    "message": "PRD approved successfully but system design generation encountered an issue",
                    "new_status": BusinessCaseStatus.PRD_APPROVED.value,
                    "case_id": case_id,
                    "system_design_initiated": False,
                    "system_design_error": design_result.get('message')
                }
        except Exception as design_error:
            print(f"Error initiating system design for case {case_id}: {str(design_error)}")
            return {
                "message": "PRD approved successfully but system design generation could not be initiated",
                "new_status": BusinessCaseStatus.PRD_APPROVED.value,
                "case_id": case_id,
                "system_design_initiated": False,
                "system_design_error": str(design_error)
            }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error approving PRD for case {case_id}, user {user_id}: {e}")
        print(f"Full traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to approve PRD: {str(e)}")

@router.post("/cases/{case_id}/prd/reject", status_code=200, summary="Reject PRD for a specific business case")
async def reject_prd(
    case_id: str,
    reject_request: PrdRejectRequest = PrdRejectRequest(),
    current_user: dict = Depends(get_current_active_user)
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
        
        db = firestore.Client(project=settings.firebase_project_id)
        case_doc_ref = db.collection("businessCases").document(case_id)

        doc_snapshot = await asyncio.to_thread(case_doc_ref.get)
        if not doc_snapshot.exists:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} not found.")

        case_data = doc_snapshot.to_dict()
        if not case_data:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} data is empty.")

        # Authorization check: verify user is the owner/initiator (V1 - self-approval)
        if case_data.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="You do not have permission to reject this PRD.")

        # Status check: ensure case is in PRD_REVIEW status
        current_status = case_data.get("status")
        if hasattr(current_status, 'value'):
            current_status_str = current_status.value
        else:
            current_status_str = str(current_status)

        if current_status_str != BusinessCaseStatus.PRD_REVIEW.value:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot reject PRD from current status: {current_status_str}. PRD must be in review status."
            )

        # Prepare history entry with optional reason
        rejection_content = f"PRD rejected by {user_email}"
        if reject_request.reason:
            rejection_content += f". Reason: {reject_request.reason}"

        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "PRD_REJECTION",
            "content": rejection_content
        }

        # Update case status to PRD_REJECTED and add history entry
        update_data = {
            "status": BusinessCaseStatus.PRD_REJECTED.value,
            "updated_at": datetime.now(timezone.utc),
            "history": firestore.ArrayUnion([history_entry])
        }

        await asyncio.to_thread(case_doc_ref.update, update_data)
        
        return {
            "message": "PRD rejected successfully",
            "new_status": BusinessCaseStatus.PRD_REJECTED.value,
            "case_id": case_id
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error rejecting PRD for case {case_id}, user {user_id}: {e}")
        print(f"Full traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to reject PRD: {str(e)}")

@router.put("/cases/{case_id}/status", status_code=200, summary="Update status for a specific business case")
async def update_case_status(
    case_id: str,
    status_update_request: StatusUpdateRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Updates the status of a specific business case.
    Used for workflow transitions like submitting PRD for review, approval, etc.
    Ensures the authenticated user has permission to change the status.
    """
    user_id = current_user.get("uid")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    # Define valid status transitions
    VALID_STATUSES = [
        "INTAKE_COMPLETE",
        "PRD_DRAFTED", 
        "PRD_PENDING_APPROVAL",
        "PRD_APPROVED",
        "PRD_REJECTED",
        "SYSTEM_DESIGN_DRAFTED",
        "SYSTEM_DESIGN_PENDING_APPROVAL",
        "SYSTEM_DESIGN_APPROVED",
        "PLANNING_COMPLETE",
        "COSTING_COMPLETE",
        "REVENUE_COMPLETE",
        "PENDING_FINAL_APPROVAL",
        "APPROVED",
        "REJECTED_FINAL"
    ]

    if status_update_request.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status_update_request.status}")

    try:
        db = firestore.Client(project=settings.firebase_project_id)
        case_doc_ref = db.collection("businessCases").document(case_id)

        doc_snapshot = await asyncio.to_thread(case_doc_ref.get)
        if not doc_snapshot.exists:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} not found.")

        case_data = doc_snapshot.to_dict()
        if not case_data:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} data is empty.")

        # Basic authorization: check if the current user is the owner of the case
        # TODO: Implement more granular permissions for different status updates
        if case_data.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="You do not have permission to update this business case status.")

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "STATUS_UPDATE",
            "content": f"Status changed to {status_update_request.status}"
        }
        
        if status_update_request.comment:
            history_entry["content"] += f". Comment: {status_update_request.comment}"

        update_data = {
            "status": status_update_request.status,
            "updated_at": datetime.now(timezone.utc),
            "history": firestore.ArrayUnion([history_entry])
        }

        await asyncio.to_thread(case_doc_ref.update, update_data)
        
        return {
            "message": f"Status updated to {status_update_request.status} successfully",
            "new_status": status_update_request.status,
            "case_id": case_id
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error updating status for case {case_id}, user {user_id}: {e}")
        print(f"Full traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to update case status: {str(e)}")

# System Design HITL Endpoints

@router.put("/cases/{case_id}/system-design", status_code=200, summary="Update System Design for a specific business case")
async def update_system_design_draft(
    case_id: str,
    system_design_update_request: SystemDesignUpdateRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Updates the System Design draft for a specific business case.
    Ensures the authenticated user is the owner/initiator of the case or has DEVELOPER role.
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")
    system_role = current_user.get("systemRole")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    try:
        # Import BusinessCaseStatus from orchestrator_agent
        from app.agents.orchestrator_agent import BusinessCaseStatus
        
        db = firestore.Client(project=settings.firebase_project_id)
        case_doc_ref = db.collection("businessCases").document(case_id)

        doc_snapshot = await asyncio.to_thread(case_doc_ref.get)
        if not doc_snapshot.exists:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} not found.")

        case_data = doc_snapshot.to_dict()
        if not case_data:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} data is empty.")

        # Authorization check: owner OR DEVELOPER role
        is_owner = case_data.get("user_id") == user_id
        is_developer = system_role == "DEVELOPER"
        
        if not (is_owner or is_developer):
            raise HTTPException(status_code=403, detail="You do not have permission to edit this system design.")

        # Status check: allow editing if SYSTEM_DESIGN_DRAFTED or SYSTEM_DESIGN_PENDING_REVIEW
        current_status = case_data.get("status")
        if hasattr(current_status, 'value'):
            current_status_str = current_status.value
        else:
            current_status_str = str(current_status)

        allowed_statuses = [
            BusinessCaseStatus.SYSTEM_DESIGN_DRAFTED.value,
            BusinessCaseStatus.SYSTEM_DESIGN_PENDING_REVIEW.value
        ]
        
        if current_status_str not in allowed_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot edit system design from current status: {current_status_str}"
            )

        # Update system design content
        existing_system_design = case_data.get("system_design_v1_draft") or {}
        updated_system_design = {
            "content_markdown": system_design_update_request.content_markdown,
            "generated_by": existing_system_design.get("generated_by", "ArchitectAgent"),
            "version": existing_system_design.get("version", "1.0.0"),
            "generated_at": existing_system_design.get("generated_at"),
            "last_edited_by": user_email,
            "last_edited_at": datetime.now(timezone.utc).isoformat()
        }

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "SYSTEM_DESIGN_UPDATE",
            "content": f"System Design updated by {user_email}"
        }

        update_data = {
            "system_design_v1_draft": updated_system_design,
            "updated_at": datetime.now(timezone.utc),
            "history": firestore.ArrayUnion([history_entry])
        }

        await asyncio.to_thread(case_doc_ref.update, update_data)

        return {
            "message": "System Design updated successfully",
            "updated_system_design": updated_system_design
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error updating system design for case {case_id}, user {user_id}: {e}")
        print(f"Full traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to update system design: {str(e)}")

@router.post("/cases/{case_id}/system-design/submit", status_code=200, summary="Submit System Design for review")
async def submit_system_design_for_review(
    case_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Submits the System Design for review, updating the case status to SYSTEM_DESIGN_PENDING_REVIEW.
    Ensures the authenticated user is the owner/initiator of the case or has DEVELOPER role.
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")
    system_role = current_user.get("systemRole")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    try:
        # Import BusinessCaseStatus from orchestrator_agent
        from app.agents.orchestrator_agent import BusinessCaseStatus
        
        db = firestore.Client(project=settings.firebase_project_id)
        case_doc_ref = db.collection("businessCases").document(case_id)

        doc_snapshot = await asyncio.to_thread(case_doc_ref.get)
        if not doc_snapshot.exists:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} not found.")

        case_data = doc_snapshot.to_dict()
        if not case_data:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} data is empty.")

        # Authorization check: owner OR DEVELOPER role
        is_owner = case_data.get("user_id") == user_id
        is_developer = system_role == "DEVELOPER"
        
        if not (is_owner or is_developer):
            raise HTTPException(status_code=403, detail="You do not have permission to submit this system design.")

        # Status check: can only submit from SYSTEM_DESIGN_DRAFTED
        current_status = case_data.get("status")
        if hasattr(current_status, 'value'):
            current_status_str = current_status.value
        else:
            current_status_str = str(current_status)

        if current_status_str != BusinessCaseStatus.SYSTEM_DESIGN_DRAFTED.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot submit system design from current status: {current_status_str}"
            )

        # Ensure system design exists
        if not case_data.get("system_design_v1_draft"):
            raise HTTPException(status_code=400, detail="No system design draft found to submit.")

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "SYSTEM_DESIGN_SUBMISSION",
            "content": f"System Design submitted for review by {user_email}"
        }

        # Update case status and add history entry
        update_data = {
            "status": BusinessCaseStatus.SYSTEM_DESIGN_PENDING_REVIEW.value,
            "updated_at": datetime.now(timezone.utc),
            "history": firestore.ArrayUnion([history_entry])
        }

        await asyncio.to_thread(case_doc_ref.update, update_data)

        return {
            "message": "System Design submitted for review successfully",
            "new_status": BusinessCaseStatus.SYSTEM_DESIGN_PENDING_REVIEW.value,
            "case_id": case_id
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error submitting system design for case {case_id}, user {user_id}: {e}")
        print(f"Full traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to submit system design: {str(e)}")

@router.post("/cases/{case_id}/system-design/approve", status_code=200, summary="Approve System Design for a specific business case")
async def approve_system_design(
    case_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Approves the System Design for a business case, updating the case status to SYSTEM_DESIGN_APPROVED.
    Requires DEVELOPER role and case must be in SYSTEM_DESIGN_PENDING_REVIEW status.
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")
    system_role = current_user.get("systemRole")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    # Authorization check: Must have DEVELOPER role
    if system_role != "DEVELOPER":
        raise HTTPException(status_code=403, detail="Only users with DEVELOPER role can approve system designs.")

    try:
        # Import BusinessCaseStatus from orchestrator_agent
        from app.agents.orchestrator_agent import BusinessCaseStatus
        
        db = firestore.Client(project=settings.firebase_project_id)
        case_doc_ref = db.collection("businessCases").document(case_id)

        doc_snapshot = await asyncio.to_thread(case_doc_ref.get)
        if not doc_snapshot.exists:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} not found.")

        case_data = doc_snapshot.to_dict()
        if not case_data:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} data is empty.")

        # Status check: ensure case is in SYSTEM_DESIGN_PENDING_REVIEW status
        current_status = case_data.get("status")
        if hasattr(current_status, 'value'):
            current_status_str = current_status.value
        else:
            current_status_str = str(current_status)

        if current_status_str != BusinessCaseStatus.SYSTEM_DESIGN_PENDING_REVIEW.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot approve system design from current status: {current_status_str}. System Design must be pending review."
            )

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "SYSTEM_DESIGN_APPROVAL",
            "content": f"System Design approved by {user_email} (DEVELOPER)"
        }

        # Update case status to SYSTEM_DESIGN_APPROVED and add history entry
        update_data = {
            "status": BusinessCaseStatus.SYSTEM_DESIGN_APPROVED.value,
            "updated_at": datetime.now(timezone.utc),
            "history": firestore.ArrayUnion([history_entry])
        }

        await asyncio.to_thread(case_doc_ref.update, update_data)

        return {
            "message": "System Design approved successfully",
            "new_status": BusinessCaseStatus.SYSTEM_DESIGN_APPROVED.value,
            "case_id": case_id
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error approving system design for case {case_id}, user {user_id}: {e}")
        print(f"Full traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to approve system design: {str(e)}")

@router.post("/cases/{case_id}/system-design/reject", status_code=200, summary="Reject System Design for a specific business case")
async def reject_system_design(
    case_id: str,
    reject_request: SystemDesignRejectRequest = SystemDesignRejectRequest(),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Rejects the System Design for a business case, updating the case status to SYSTEM_DESIGN_REJECTED.
    Requires DEVELOPER role and case must be in SYSTEM_DESIGN_PENDING_REVIEW status.
    Optionally accepts a rejection reason.
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")
    system_role = current_user.get("systemRole")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    # Authorization check: Must have DEVELOPER role
    if system_role != "DEVELOPER":
        raise HTTPException(status_code=403, detail="Only users with DEVELOPER role can reject system designs.")

    try:
        # Import BusinessCaseStatus from orchestrator_agent
        from app.agents.orchestrator_agent import BusinessCaseStatus
        
        db = firestore.Client(project=settings.firebase_project_id)
        case_doc_ref = db.collection("businessCases").document(case_id)

        doc_snapshot = await asyncio.to_thread(case_doc_ref.get)
        if not doc_snapshot.exists:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} not found.")

        case_data = doc_snapshot.to_dict()
        if not case_data:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} data is empty.")

        # Status check: ensure case is in SYSTEM_DESIGN_PENDING_REVIEW status
        current_status = case_data.get("status")
        if hasattr(current_status, 'value'):
            current_status_str = current_status.value
        else:
            current_status_str = str(current_status)

        if current_status_str != BusinessCaseStatus.SYSTEM_DESIGN_PENDING_REVIEW.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot reject system design from current status: {current_status_str}. System Design must be pending review."
            )

        # Prepare history entry with optional reason
        rejection_content = f"System Design rejected by {user_email} (DEVELOPER)"
        if reject_request.reason:
            rejection_content += f". Reason: {reject_request.reason}"

        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "SYSTEM_DESIGN_REJECTION",
            "content": rejection_content
        }

        # Update case status to SYSTEM_DESIGN_REJECTED and add history entry
        update_data = {
            "status": BusinessCaseStatus.SYSTEM_DESIGN_REJECTED.value,
            "updated_at": datetime.now(timezone.utc),
            "history": firestore.ArrayUnion([history_entry])
        }

        await asyncio.to_thread(case_doc_ref.update, update_data)

        return {
            "message": "System Design rejected successfully",
            "new_status": BusinessCaseStatus.SYSTEM_DESIGN_REJECTED.value,
            "case_id": case_id
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error rejecting system design for case {case_id}, user {user_id}: {e}")
        print(f"Full traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to reject system design: {str(e)}")

@router.put("/cases/{case_id}/effort-estimate", status_code=200, summary="Update Effort Estimate for a specific business case")
async def update_effort_estimate(
    case_id: str,
    effort_update_request: EffortEstimateUpdateRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Updates the Effort Estimate for a specific business case.
    Ensures the authenticated user is the owner of the case.
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    try:
        from app.agents.orchestrator_agent import BusinessCaseStatus
        
        db = firestore.Client(project=settings.firebase_project_id)
        case_doc_ref = db.collection("businessCases").document(case_id)

        doc_snapshot = await asyncio.to_thread(case_doc_ref.get)
        if not doc_snapshot.exists:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} not found.")

        case_data = doc_snapshot.to_dict()
        if not case_data:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} data is empty.")

        if case_data.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="You do not have permission to edit this business case.")

        # Check status allows editing
        current_status = case_data.get("status")
        if hasattr(current_status, 'value'):
            current_status_str = current_status.value
        else:
            current_status_str = str(current_status)

        allowed_statuses = [
            BusinessCaseStatus.PLANNING_COMPLETE.value,
            BusinessCaseStatus.EFFORT_PENDING_REVIEW.value,
            BusinessCaseStatus.EFFORT_REJECTED.value
        ]

        if current_status_str not in allowed_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot edit effort estimate from current status: {current_status_str}"
            )

        # Construct the effort estimate object
        updated_effort_estimate = {
            "roles": effort_update_request.roles,
            "total_hours": effort_update_request.total_hours,
            "estimated_duration_weeks": effort_update_request.estimated_duration_weeks,
            "complexity_assessment": effort_update_request.complexity_assessment,
            "notes": effort_update_request.notes
        }

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "EFFORT_ESTIMATE_UPDATE",
            "content": f"Effort Estimate updated by {user_email}"
        }

        # Update effort estimate and add history entry
        update_data = {
            "effort_estimate_v1": updated_effort_estimate,
            "updated_at": datetime.now(timezone.utc),
            "history": firestore.ArrayUnion([history_entry])
        }

        await asyncio.to_thread(case_doc_ref.update, update_data)

        return {
            "message": "Effort Estimate updated successfully",
            "updated_effort_estimate": updated_effort_estimate
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error updating effort estimate for case {case_id}, user {user_id}: {e}")
        print(f"Full traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to update effort estimate: {str(e)}")

@router.post("/cases/{case_id}/effort-estimate/submit", status_code=200, summary="Submit Effort Estimate for review")
async def submit_effort_estimate_for_review(
    case_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Submits the Effort Estimate for review, updating the case status to EFFORT_PENDING_REVIEW.
    Ensures the authenticated user is the owner of the case.
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    try:
        from app.agents.orchestrator_agent import BusinessCaseStatus
        
        db = firestore.Client(project=settings.firebase_project_id)
        case_doc_ref = db.collection("businessCases").document(case_id)

        doc_snapshot = await asyncio.to_thread(case_doc_ref.get)
        if not doc_snapshot.exists:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} not found.")

        case_data = doc_snapshot.to_dict()
        if not case_data:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} data is empty.")

        if case_data.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="You do not have permission to submit this business case.")

        # Check if effort estimate exists
        if not case_data.get("effort_estimate_v1"):
            raise HTTPException(status_code=400, detail="No effort estimate found to submit.")

        # Check status allows submission
        current_status = case_data.get("status")
        if hasattr(current_status, 'value'):
            current_status_str = current_status.value
        else:
            current_status_str = str(current_status)

        allowed_statuses = [BusinessCaseStatus.PLANNING_COMPLETE.value, BusinessCaseStatus.EFFORT_REJECTED.value]

        if current_status_str not in allowed_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot submit effort estimate from current status: {current_status_str}"
            )

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "EFFORT_ESTIMATE_SUBMISSION",
            "content": f"Effort Estimate submitted for review by {user_email}"
        }

        # Update case status and add history entry
        update_data = {
            "status": BusinessCaseStatus.EFFORT_PENDING_REVIEW.value,
            "updated_at": datetime.now(timezone.utc),
            "history": firestore.ArrayUnion([history_entry])
        }

        await asyncio.to_thread(case_doc_ref.update, update_data)

        return {
            "message": "Effort Estimate submitted for review successfully",
            "new_status": BusinessCaseStatus.EFFORT_PENDING_REVIEW.value,
            "case_id": case_id
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error submitting effort estimate for case {case_id}, user {user_id}: {e}")
        print(f"Full traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to submit effort estimate: {str(e)}")

@router.put("/cases/{case_id}/cost-estimate", status_code=200, summary="Update Cost Estimate for a specific business case")
async def update_cost_estimate(
    case_id: str,
    cost_update_request: CostEstimateUpdateRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Updates the Cost Estimate for a specific business case.
    Ensures the authenticated user is the owner of the case.
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    try:
        from app.agents.orchestrator_agent import BusinessCaseStatus
        
        db = firestore.Client(project=settings.firebase_project_id)
        case_doc_ref = db.collection("businessCases").document(case_id)

        doc_snapshot = await asyncio.to_thread(case_doc_ref.get)
        if not doc_snapshot.exists:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} not found.")

        case_data = doc_snapshot.to_dict()
        if not case_data:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} data is empty.")

        if case_data.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="You do not have permission to edit this business case.")

        # Check status allows editing
        current_status = case_data.get("status")
        if hasattr(current_status, 'value'):
            current_status_str = current_status.value
        else:
            current_status_str = str(current_status)

        allowed_statuses = [
            BusinessCaseStatus.COSTING_COMPLETE.value,
            BusinessCaseStatus.COSTING_PENDING_REVIEW.value,
            BusinessCaseStatus.COSTING_REJECTED.value
        ]

        if current_status_str not in allowed_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot edit cost estimate from current status: {current_status_str}"
            )

        # Construct the cost estimate object
        updated_cost_estimate = {
            "estimated_cost": cost_update_request.estimated_cost,
            "currency": cost_update_request.currency,
            "rate_card_used": cost_update_request.rate_card_used,
            "breakdown_by_role": cost_update_request.breakdown_by_role,
            "calculation_method": cost_update_request.calculation_method,
            "notes": cost_update_request.notes
        }

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "COST_ESTIMATE_UPDATE",
            "content": f"Cost Estimate updated by {user_email}"
        }

        # Update cost estimate and add history entry
        update_data = {
            "cost_estimate_v1": updated_cost_estimate,
            "updated_at": datetime.now(timezone.utc),
            "history": firestore.ArrayUnion([history_entry])
        }

        await asyncio.to_thread(case_doc_ref.update, update_data)

        return {
            "message": "Cost Estimate updated successfully",
            "updated_cost_estimate": updated_cost_estimate
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error updating cost estimate for case {case_id}, user {user_id}: {e}")
        print(f"Full traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to update cost estimate: {str(e)}")

@router.post("/cases/{case_id}/cost-estimate/submit", status_code=200, summary="Submit Cost Estimate for review")
async def submit_cost_estimate_for_review(
    case_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Submits the Cost Estimate for review, updating the case status to COSTING_PENDING_REVIEW.
    Ensures the authenticated user is the owner of the case.
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    try:
        from app.agents.orchestrator_agent import BusinessCaseStatus
        
        db = firestore.Client(project=settings.firebase_project_id)
        case_doc_ref = db.collection("businessCases").document(case_id)

        doc_snapshot = await asyncio.to_thread(case_doc_ref.get)
        if not doc_snapshot.exists:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} not found.")

        case_data = doc_snapshot.to_dict()
        if not case_data:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} data is empty.")

        if case_data.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="You do not have permission to submit this business case.")

        # Check if cost estimate exists
        if not case_data.get("cost_estimate_v1"):
            raise HTTPException(status_code=400, detail="No cost estimate found to submit.")

        # Check status allows submission
        current_status = case_data.get("status")
        if hasattr(current_status, 'value'):
            current_status_str = current_status.value
        else:
            current_status_str = str(current_status)

        allowed_statuses = [BusinessCaseStatus.COSTING_COMPLETE.value, BusinessCaseStatus.COSTING_REJECTED.value]

        if current_status_str not in allowed_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot submit cost estimate from current status: {current_status_str}"
            )

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "COST_ESTIMATE_SUBMISSION",
            "content": f"Cost Estimate submitted for review by {user_email}"
        }

        # Update case status and add history entry
        update_data = {
            "status": BusinessCaseStatus.COSTING_PENDING_REVIEW.value,
            "updated_at": datetime.now(timezone.utc),
            "history": firestore.ArrayUnion([history_entry])
        }

        await asyncio.to_thread(case_doc_ref.update, update_data)

        return {
            "message": "Cost Estimate submitted for review successfully",
            "new_status": BusinessCaseStatus.COSTING_PENDING_REVIEW.value,
            "case_id": case_id
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error submitting cost estimate for case {case_id}, user {user_id}: {e}")
        print(f"Full traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to submit cost estimate: {str(e)}")

@router.put("/cases/{case_id}/value-projection", status_code=200, summary="Update Value Projection for a specific business case")
async def update_value_projection(
    case_id: str,
    value_update_request: ValueProjectionUpdateRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Updates the Value Projection for a specific business case.
    Ensures the authenticated user is the owner of the case.
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    try:
        from app.agents.orchestrator_agent import BusinessCaseStatus
        
        db = firestore.Client(project=settings.firebase_project_id)
        case_doc_ref = db.collection("businessCases").document(case_id)

        doc_snapshot = await asyncio.to_thread(case_doc_ref.get)
        if not doc_snapshot.exists:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} not found.")

        case_data = doc_snapshot.to_dict()
        if not case_data:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} data is empty.")

        if case_data.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="You do not have permission to edit this business case.")

        # Check status allows editing
        current_status = case_data.get("status")
        if hasattr(current_status, 'value'):
            current_status_str = current_status.value
        else:
            current_status_str = str(current_status)

        allowed_statuses = [
            BusinessCaseStatus.VALUE_ANALYSIS_COMPLETE.value,
            BusinessCaseStatus.VALUE_PENDING_REVIEW.value,
            BusinessCaseStatus.VALUE_REJECTED.value
        ]

        if current_status_str not in allowed_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot edit value projection from current status: {current_status_str}"
            )

        # Construct the value projection object
        updated_value_projection = {
            "scenarios": value_update_request.scenarios,
            "currency": value_update_request.currency,
            "template_used": value_update_request.template_used,
            "methodology": value_update_request.methodology,
            "assumptions": value_update_request.assumptions,
            "notes": value_update_request.notes
        }

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "VALUE_PROJECTION_UPDATE",
            "content": f"Value Projection updated by {user_email}"
        }

        # Update value projection and add history entry
        update_data = {
            "value_projection_v1": updated_value_projection,
            "updated_at": datetime.now(timezone.utc),
            "history": firestore.ArrayUnion([history_entry])
        }

        await asyncio.to_thread(case_doc_ref.update, update_data)

        return {
            "message": "Value Projection updated successfully",
            "updated_value_projection": updated_value_projection
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error updating value projection for case {case_id}, user {user_id}: {e}")
        print(f"Full traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to update value projection: {str(e)}")

@router.post("/cases/{case_id}/value-projection/submit", status_code=200, summary="Submit Value Projection for review")
async def submit_value_projection_for_review(
    case_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Submits the Value Projection for review, updating the case status to VALUE_PENDING_REVIEW.
    Ensures the authenticated user is the owner of the case.
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    try:
        from app.agents.orchestrator_agent import BusinessCaseStatus
        
        db = firestore.Client(project=settings.firebase_project_id)
        case_doc_ref = db.collection("businessCases").document(case_id)

        doc_snapshot = await asyncio.to_thread(case_doc_ref.get)
        if not doc_snapshot.exists:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} not found.")

        case_data = doc_snapshot.to_dict()
        if not case_data:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} data is empty.")

        if case_data.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="You do not have permission to submit this business case.")

        # Check if value projection exists
        if not case_data.get("value_projection_v1"):
            raise HTTPException(status_code=400, detail="No value projection found to submit.")

        # Check status allows submission
        current_status = case_data.get("status")
        if hasattr(current_status, 'value'):
            current_status_str = current_status.value
        else:
            current_status_str = str(current_status)

        allowed_statuses = [BusinessCaseStatus.VALUE_ANALYSIS_COMPLETE.value, BusinessCaseStatus.VALUE_REJECTED.value]

        if current_status_str not in allowed_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot submit value projection from current status: {current_status_str}"
            )

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "VALUE_PROJECTION_SUBMISSION",
            "content": f"Value Projection submitted for review by {user_email}"
        }

        # Update case status and add history entry
        update_data = {
            "status": BusinessCaseStatus.VALUE_PENDING_REVIEW.value,
            "updated_at": datetime.now(timezone.utc),
            "history": firestore.ArrayUnion([history_entry])
        }

        await asyncio.to_thread(case_doc_ref.update, update_data)

        return {
            "message": "Value Projection submitted for review successfully",
            "new_status": BusinessCaseStatus.VALUE_PENDING_REVIEW.value,
            "case_id": case_id
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error submitting value projection for case {case_id}, user {user_id}: {e}")
        print(f"Full traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to submit value projection: {str(e)}")

# Financial Estimate Approval/Rejection Endpoints

@router.post("/cases/{case_id}/effort-estimate/approve", status_code=200, summary="Approve Effort Estimate for a specific business case")
async def approve_effort_estimate(
    case_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Approves the Effort Estimate for a specific business case.
    Only the case initiator can approve effort estimates.
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    try:
        from app.agents.orchestrator_agent import BusinessCaseStatus
        
        db = firestore.Client(project=settings.firebase_project_id)
        case_doc_ref = db.collection("businessCases").document(case_id)

        doc_snapshot = await asyncio.to_thread(case_doc_ref.get)
        if not doc_snapshot.exists:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} not found.")

        case_data = doc_snapshot.to_dict()
        if not case_data:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} data is empty.")

        # Authorization check: only case initiator can approve effort estimates
        if case_data.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="You do not have permission to approve this effort estimate.")

        # Status check: must be in EFFORT_PENDING_REVIEW
        current_status = case_data.get("status")
        if hasattr(current_status, 'value'):
            current_status_str = current_status.value
        else:
            current_status_str = str(current_status)

        if current_status_str != BusinessCaseStatus.EFFORT_PENDING_REVIEW.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot approve effort estimate from current status: {current_status_str}"
            )

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "EFFORT_ESTIMATE_APPROVAL",
            "content": f"Effort Estimate approved by {user_email}"
        }

        # Update case status and add history entry
        update_data = {
            "status": BusinessCaseStatus.EFFORT_APPROVED.value,
            "updated_at": datetime.now(timezone.utc),
            "history": firestore.ArrayUnion([history_entry])
        }

        await asyncio.to_thread(case_doc_ref.update, update_data)

        return {
            "message": "Effort Estimate approved successfully",
            "new_status": BusinessCaseStatus.EFFORT_APPROVED.value,
            "case_id": case_id
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error approving effort estimate for case {case_id}, user {user_id}: {e}")
        print(f"Full traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to approve effort estimate: {str(e)}")

@router.post("/cases/{case_id}/effort-estimate/reject", status_code=200, summary="Reject Effort Estimate for a specific business case")
async def reject_effort_estimate(
    case_id: str,
    reject_request: EffortEstimateRejectRequest = EffortEstimateRejectRequest(),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Rejects the Effort Estimate for a specific business case.
    Only the case initiator can reject effort estimates.
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    try:
        from app.agents.orchestrator_agent import BusinessCaseStatus
        
        db = firestore.Client(project=settings.firebase_project_id)
        case_doc_ref = db.collection("businessCases").document(case_id)

        doc_snapshot = await asyncio.to_thread(case_doc_ref.get)
        if not doc_snapshot.exists:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} not found.")

        case_data = doc_snapshot.to_dict()
        if not case_data:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} data is empty.")

        # Authorization check: only case initiator can reject effort estimates
        if case_data.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="You do not have permission to reject this effort estimate.")

        # Status check: must be in EFFORT_PENDING_REVIEW
        current_status = case_data.get("status")
        if hasattr(current_status, 'value'):
            current_status_str = current_status.value
        else:
            current_status_str = str(current_status)

        if current_status_str != BusinessCaseStatus.EFFORT_PENDING_REVIEW.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot reject effort estimate from current status: {current_status_str}"
            )

        # Prepare history entry with optional reason
        rejection_message = f"Effort Estimate rejected by {user_email}"
        if reject_request.reason:
            rejection_message += f". Reason: {reject_request.reason}"

        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "EFFORT_ESTIMATE_REJECTION",
            "content": rejection_message
        }

        # Update case status and add history entry (revert to PLANNING_COMPLETE for re-edit)
        update_data = {
            "status": BusinessCaseStatus.PLANNING_COMPLETE.value,
            "updated_at": datetime.now(timezone.utc),
            "history": firestore.ArrayUnion([history_entry])
        }

        await asyncio.to_thread(case_doc_ref.update, update_data)

        return {
            "message": "Effort Estimate rejected successfully",
            "new_status": BusinessCaseStatus.PLANNING_COMPLETE.value,
            "case_id": case_id
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error rejecting effort estimate for case {case_id}, user {user_id}: {e}")
        print(f"Full traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to reject effort estimate: {str(e)}")

@router.post("/cases/{case_id}/cost-estimate/approve", status_code=200, summary="Approve Cost Estimate for a specific business case")
async def approve_cost_estimate(
    case_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Approves the Cost Estimate for a specific business case.
    Only the case initiator can approve cost estimates.
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    try:
        from app.agents.orchestrator_agent import BusinessCaseStatus
        
        db = firestore.Client(project=settings.firebase_project_id)
        case_doc_ref = db.collection("businessCases").document(case_id)

        doc_snapshot = await asyncio.to_thread(case_doc_ref.get)
        if not doc_snapshot.exists:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} not found.")

        case_data = doc_snapshot.to_dict()
        if not case_data:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} data is empty.")

        # Authorization check: only case initiator can approve cost estimates
        if case_data.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="You do not have permission to approve this cost estimate.")

        # Status check: must be in COSTING_PENDING_REVIEW
        current_status = case_data.get("status")
        if hasattr(current_status, 'value'):
            current_status_str = current_status.value
        else:
            current_status_str = str(current_status)

        if current_status_str != BusinessCaseStatus.COSTING_PENDING_REVIEW.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot approve cost estimate from current status: {current_status_str}"
            )

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "COST_ESTIMATE_APPROVAL",
            "content": f"Cost Estimate approved by {user_email}"
        }

        # Update case status and add history entry
        update_data = {
            "status": BusinessCaseStatus.COSTING_APPROVED.value,
            "updated_at": datetime.now(timezone.utc),
            "history": firestore.ArrayUnion([history_entry])
        }

        await asyncio.to_thread(case_doc_ref.update, update_data)

        # Check if we should trigger financial model generation
        try:
            from app.agents.orchestrator_agent import OrchestratorAgent
            orchestrator = OrchestratorAgent()
            financial_model_result = await orchestrator.check_and_trigger_financial_model(case_id)
            print(f"Financial model check result: {financial_model_result}")
        except Exception as e:
            print(f"Error checking financial model trigger after cost approval: {e}")
            # Don't fail the approval if financial model check fails

        return {
            "message": "Cost Estimate approved successfully",
            "new_status": BusinessCaseStatus.COSTING_APPROVED.value,
            "case_id": case_id
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error approving cost estimate for case {case_id}, user {user_id}: {e}")
        print(f"Full traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to approve cost estimate: {str(e)}")

@router.post("/cases/{case_id}/cost-estimate/reject", status_code=200, summary="Reject Cost Estimate for a specific business case")
async def reject_cost_estimate(
    case_id: str,
    reject_request: CostEstimateRejectRequest = CostEstimateRejectRequest(),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Rejects the Cost Estimate for a specific business case.
    Only the case initiator can reject cost estimates.
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    try:
        from app.agents.orchestrator_agent import BusinessCaseStatus
        
        db = firestore.Client(project=settings.firebase_project_id)
        case_doc_ref = db.collection("businessCases").document(case_id)

        doc_snapshot = await asyncio.to_thread(case_doc_ref.get)
        if not doc_snapshot.exists:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} not found.")

        case_data = doc_snapshot.to_dict()
        if not case_data:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} data is empty.")

        # Authorization check: only case initiator can reject cost estimates
        if case_data.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="You do not have permission to reject this cost estimate.")

        # Status check: must be in COSTING_PENDING_REVIEW
        current_status = case_data.get("status")
        if hasattr(current_status, 'value'):
            current_status_str = current_status.value
        else:
            current_status_str = str(current_status)

        if current_status_str != BusinessCaseStatus.COSTING_PENDING_REVIEW.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot reject cost estimate from current status: {current_status_str}"
            )

        # Prepare history entry with optional reason
        rejection_message = f"Cost Estimate rejected by {user_email}"
        if reject_request.reason:
            rejection_message += f". Reason: {reject_request.reason}"

        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "COST_ESTIMATE_REJECTION",
            "content": rejection_message
        }

        # Update case status and add history entry (revert to COSTING_COMPLETE for re-edit)
        update_data = {
            "status": BusinessCaseStatus.COSTING_COMPLETE.value,
            "updated_at": datetime.now(timezone.utc),
            "history": firestore.ArrayUnion([history_entry])
        }

        await asyncio.to_thread(case_doc_ref.update, update_data)

        return {
            "message": "Cost Estimate rejected successfully",
            "new_status": BusinessCaseStatus.COSTING_COMPLETE.value,
            "case_id": case_id
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error rejecting cost estimate for case {case_id}, user {user_id}: {e}")
        print(f"Full traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to reject cost estimate: {str(e)}")

@router.post("/cases/{case_id}/value-projection/approve", status_code=200, summary="Approve Value Projection for a specific business case")
async def approve_value_projection(
    case_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Approves the Value Projection for a specific business case.
    Option A (V1): Only the case initiator can approve value projections.
    Option B (Future): Users with SALES_MANAGER_APPROVER role can approve.
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    try:
        from app.agents.orchestrator_agent import BusinessCaseStatus
        
        db = firestore.Client(project=settings.firebase_project_id)
        case_doc_ref = db.collection("businessCases").document(case_id)

        doc_snapshot = await asyncio.to_thread(case_doc_ref.get)
        if not doc_snapshot.exists:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} not found.")

        case_data = doc_snapshot.to_dict()
        if not case_data:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} data is empty.")

        # Authorization check for Value Projection approval
        system_role = current_user.get("system_role") or current_user.get("systemRole")
        
        # Option A (V1 Simplest): Current user is the case initiator
        # Option B (Preferred): Check for SALES_MANAGER_APPROVER role
        is_case_initiator = case_data.get("user_id") == user_id
        is_sales_manager_approver = system_role == "SALES_MANAGER_APPROVER"
        
        if not (is_case_initiator or is_sales_manager_approver):
            raise HTTPException(
                status_code=403, 
                detail="You do not have permission to approve this value projection. Must be case initiator or have SALES_MANAGER_APPROVER role."
            )

        # Status check: must be in VALUE_PENDING_REVIEW
        current_status = case_data.get("status")
        if hasattr(current_status, 'value'):
            current_status_str = current_status.value
        else:
            current_status_str = str(current_status)

        if current_status_str != BusinessCaseStatus.VALUE_PENDING_REVIEW.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot approve value projection from current status: {current_status_str}"
            )

        # Prepare history entry
        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "VALUE_PROJECTION_APPROVAL",
            "content": f"Value Projection approved by {user_email}"
        }

        # Update case status and add history entry
        update_data = {
            "status": BusinessCaseStatus.VALUE_APPROVED.value,
            "updated_at": datetime.now(timezone.utc),
            "history": firestore.ArrayUnion([history_entry])
        }

        await asyncio.to_thread(case_doc_ref.update, update_data)

        # Check if we should trigger financial model generation
        try:
            from app.agents.orchestrator_agent import OrchestratorAgent
            orchestrator = OrchestratorAgent()
            financial_model_result = await orchestrator.check_and_trigger_financial_model(case_id)
            print(f"Financial model check result: {financial_model_result}")
        except Exception as e:
            print(f"Error checking financial model trigger after value approval: {e}")
            # Don't fail the approval if financial model check fails

        return {
            "message": "Value Projection approved successfully",
            "new_status": BusinessCaseStatus.VALUE_APPROVED.value,
            "case_id": case_id
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error approving value projection for case {case_id}, user {user_id}: {e}")
        print(f"Full traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to approve value projection: {str(e)}")

@router.post("/cases/{case_id}/value-projection/reject", status_code=200, summary="Reject Value Projection for a specific business case")
async def reject_value_projection(
    case_id: str,
    reject_request: ValueProjectionRejectRequest = ValueProjectionRejectRequest(),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Rejects the Value Projection for a specific business case.
    Option A (V1): Only the case initiator can reject value projections.
    Option B (Future): Users with SALES_MANAGER_APPROVER role can reject.
    """
    user_id = current_user.get("uid")
    user_email = current_user.get("email", f"User {user_id}")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    try:
        from app.agents.orchestrator_agent import BusinessCaseStatus
        
        db = firestore.Client(project=settings.firebase_project_id)
        case_doc_ref = db.collection("businessCases").document(case_id)

        doc_snapshot = await asyncio.to_thread(case_doc_ref.get)
        if not doc_snapshot.exists:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} not found.")

        case_data = doc_snapshot.to_dict()
        if not case_data:
            raise HTTPException(status_code=404, detail=f"Business case {case_id} data is empty.")

        # Authorization check for Value Projection rejection
        system_role = current_user.get("system_role") or current_user.get("systemRole")
        
        # Option A (V1 Simplest): Current user is the case initiator
        # Option B (Preferred): Check for SALES_MANAGER_APPROVER role
        is_case_initiator = case_data.get("user_id") == user_id
        is_sales_manager_approver = system_role == "SALES_MANAGER_APPROVER"
        
        if not (is_case_initiator or is_sales_manager_approver):
            raise HTTPException(
                status_code=403, 
                detail="You do not have permission to reject this value projection. Must be case initiator or have SALES_MANAGER_APPROVER role."
            )

        # Status check: must be in VALUE_PENDING_REVIEW
        current_status = case_data.get("status")
        if hasattr(current_status, 'value'):
            current_status_str = current_status.value
        else:
            current_status_str = str(current_status)

        if current_status_str != BusinessCaseStatus.VALUE_PENDING_REVIEW.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot reject value projection from current status: {current_status_str}"
            )

        # Prepare history entry with optional reason
        rejection_message = f"Value Projection rejected by {user_email}"
        if reject_request.reason:
            rejection_message += f". Reason: {reject_request.reason}"

        history_entry = {
            "timestamp": datetime.now(timezone.utc),
            "source": "USER",
            "messageType": "VALUE_PROJECTION_REJECTION",
            "content": rejection_message
        }

        # Update case status and add history entry (revert to VALUE_ANALYSIS_COMPLETE for re-edit)
        update_data = {
            "status": BusinessCaseStatus.VALUE_ANALYSIS_COMPLETE.value,
            "updated_at": datetime.now(timezone.utc),
            "history": firestore.ArrayUnion([history_entry])
        }

        await asyncio.to_thread(case_doc_ref.update, update_data)

        return {
            "message": "Value Projection rejected successfully",
            "new_status": BusinessCaseStatus.VALUE_ANALYSIS_COMPLETE.value,
            "case_id": case_id
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error rejecting value projection for case {case_id}, user {user_id}: {e}")
        print(f"Full traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to reject value projection: {str(e)}") 