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
    # Add other fields as necessary, e.g., system_design_draft, financial_model
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