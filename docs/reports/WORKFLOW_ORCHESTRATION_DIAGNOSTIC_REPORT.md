# Workflow Orchestration Diagnostic Report
## DrFirst Agentic Business Case Generator

**Report Date:** December 19, 2024  
**Issue:** Workflow Stalling After PRD Approval  
**Analyst:** AI Backend Development Expert  
**Status:** 🚨 Critical - Workflow Broken

---

## 🔍 Executive Summary

The "DrFirst Agentic Business Case Generator" workflow **stalls after PRD approval** and fails to progress through the System Design approval stage to Effort Estimation. While the system successfully generates system designs using the ArchitectAgent, there is **no orchestration mechanism** to automatically trigger the next workflow stage (Effort Estimation) after System Design approval.

**Root Cause:** Missing System Design approval orchestration logic and API endpoints, despite having a complete implementation pattern for later workflow stages.

**Impact:** Users cannot progress business cases beyond the System Design stage, breaking the entire multi-stage workflow.

---

## 🚨 Critical Issues Identified

### 1. Missing System Design Approval Handler
**File:** `backend/app/agents/orchestrator_agent.py`  
**Issue:** No `handle_system_design_approval()` method exists  
**Line References:** Methods exist for `handle_prd_approval()` (line 843) and `handle_cost_completion()` (line 1231)  

**Impact:** System design approval cannot trigger effort estimation
```python
# MISSING METHOD - Should exist alongside other handlers
async def handle_system_design_approval(self, case_id: str) -> Dict[str, Any]:
    """Handle System Design approval by triggering Effort Estimation generation."""
    pass
```

### 2. Missing System Design API Endpoints
**File:** `backend/app/api/v1/cases/__init__.py`  
**Lines:** 25-27  
**Issue:** System design routes are commented as "TODO"  

**Evidence:**
```python
# Note: Additional routers can be added here as they are created:
# - system_design_routes  # ← THIS IS MISSING
# - financial_routes  
```

**Impact:** Frontend cannot call system design approval endpoints, resulting in broken UI functionality.

### 3. Overly Aggressive PRD Approval Logic
**File:** `backend/app/agents/orchestrator_agent.py`  
**Lines:** 946-1040  
**Issue:** `handle_prd_approval()` attempts both system design AND effort estimation in one call  

**Evidence:**
```python
# Lines 946-975: System design generation (CORRECT)
system_design_response = await self.architect_agent.generate_system_design(...)

# Lines 948-1006: Automatic effort estimation (INCORRECT - bypasses HITL)
effort_response = await self.planner_agent.generate_effort_estimate(...)
```

**Impact:** Bypasses intended Human-in-the-Loop (HITL) review workflow shown in UI screenshots.

### 4. Workflow Pattern Inconsistency
**Comparison Analysis:**

**✅ Working Pattern (Cost → Value):**
```python
# File: backend/app/api/v1/cases/financial_estimates_routes.py (lines 95-110)
@router.post("/cases/{case_id}/cost-estimate/approve")
async def approve_cost_estimate():
    # ... approval logic ...
    value_result = await orchestrator.handle_cost_completion(case_id)  # ✅ Exists
```

**❌ Broken Pattern (System Design → Effort):**
```python
# File: MISSING - Should be backend/app/api/v1/cases/system_design_routes.py
@router.post("/cases/{case_id}/system-design/approve")
async def approve_system_design():
    # ... approval logic ...
    effort_result = await orchestrator.handle_system_design_approval(case_id)  # ❌ Missing
```

### 5. Status Transition Gap
**File:** `backend/app/agents/orchestrator_agent.py`  
**Lines:** 912-946  
**Issue:** Workflow dead-ends at `SYSTEM_DESIGN_DRAFTED` status  

**Current Behavior:**
```
PRD_APPROVED → SYSTEM_DESIGN_DRAFTING → SYSTEM_DESIGN_DRAFTED → ⚠️ STALLS HERE
```

**Expected Behavior:**
```
PRD_APPROVED → SYSTEM_DESIGN_DRAFTING → SYSTEM_DESIGN_DRAFTED → 
SYSTEM_DESIGN_PENDING_REVIEW → SYSTEM_DESIGN_APPROVED → 
PLANNING_IN_PROGRESS → PLANNING_COMPLETE
```

---

## 📊 Status Enum Analysis

### ✅ Complete Status Coverage
The `BusinessCaseStatus` enum (lines 45-82) contains all necessary statuses:

```python
class BusinessCaseStatus(Enum):
    # System Design statuses - ALL PRESENT ✅
    SYSTEM_DESIGN_DRAFTING = "SYSTEM_DESIGN_DRAFTING"
    SYSTEM_DESIGN_DRAFTED = "SYSTEM_DESIGN_DRAFTED"  
    SYSTEM_DESIGN_PENDING_REVIEW = "SYSTEM_DESIGN_PENDING_REVIEW"
    SYSTEM_DESIGN_APPROVED = "SYSTEM_DESIGN_APPROVED"
    SYSTEM_DESIGN_REJECTED = "SYSTEM_DESIGN_REJECTED"
    
    # Planning statuses - ALL PRESENT ✅
    PLANNING_IN_PROGRESS = "PLANNING_IN_PROGRESS"
    PLANNING_COMPLETE = "PLANNING_COMPLETE"
    EFFORT_PENDING_REVIEW = "EFFORT_PENDING_REVIEW"
    EFFORT_APPROVED = "EFFORT_APPROVED"
    EFFORT_REJECTED = "EFFORT_REJECTED"
```

### ❌ Missing Orchestration Logic
While all statuses exist, the orchestration logic to transition between them is incomplete.

---

## 🔄 Architectural Analysis

### Agent Integration Status
**✅ ArchitectAgent Integration:** Complete  
- Method: `generate_system_design()` (working)
- Called from: `handle_prd_approval()`
- Status: Fully operational

**✅ PlannerAgent Integration:** Complete  
- Method: `generate_effort_estimate()` (working)  
- Called from: `handle_prd_approval()` (incorrect location)
- Status: Operational but misplaced

**❌ System Design → Effort Orchestration:** Missing  
- Missing: `handle_system_design_approval()`
- Missing: System design API endpoints
- Status: Not implemented

### Data Flow Analysis
**✅ Firestore Integration:** Complete  
- Business case updates: Working
- History logging: Working  
- Status management: Working

**✅ Frontend Integration:** Partial  
- System design display: Working
- System design editing: Working
- System design approval: **Broken (missing backend)**

---

## 🛠️ Detailed Fix Recommendations

### 1. Create System Design Orchestrator Handler
**File:** `backend/app/agents/orchestrator_agent.py`  
**Location:** After line 1081 (end of `handle_prd_approval`)

```python
async def handle_system_design_approval(self, case_id: str) -> Dict[str, Any]:
    """
    Handle System Design approval by triggering Effort Estimation generation.
    
    Args:
        case_id (str): The business case ID
        
    Returns:
        Dict[str, Any]: Result of the effort estimation generation trigger
    """
    try:
        orchestrator_logger = log_agent_operation(
            self.logger, "OrchestratorAgent", case_id, "handle_system_design_approval"
        )
        orchestrator_logger.info(f"Handling system design approval for case {case_id}")
        
        # Get the business case
        case_doc_ref = self.db.collection("businessCases").document(case_id)
        doc_snapshot = await asyncio.to_thread(case_doc_ref.get)
        
        if not doc_snapshot.exists:
            return {
                "status": "error",
                "message": f"Business case {case_id} not found",
            }
        
        case_data = doc_snapshot.to_dict()
        
        # Verify system design is approved
        if case_data.get("status") != BusinessCaseStatus.SYSTEM_DESIGN_APPROVED.value:
            return {
                "status": "error",
                "message": f"Case status is {case_data.get('status')}, expected SYSTEM_DESIGN_APPROVED",
            }
        
        # Check if system design exists
        system_design = case_data.get("system_design_v1_draft")
        if not system_design:
            return {
                "status": "error",
                "message": "System design draft not found",
            }
        
        # Trigger Effort Estimation generation
        orchestrator_logger.info(f"Triggering effort estimation for case {case_id}")
        
        # Update status to PLANNING_IN_PROGRESS
        current_time = datetime.now(timezone.utc)
        update_data = {
            "status": BusinessCaseStatus.PLANNING_IN_PROGRESS.value,
            "updated_at": current_time,
            "history": get_array_union([
                {
                    "timestamp": current_time.isoformat(),
                    "source": "ORCHESTRATOR_AGENT", 
                    "type": "STATUS_UPDATE",
                    "content": f"Status updated to {BusinessCaseStatus.PLANNING_IN_PROGRESS.value}. PlannerAgent initiated for effort estimation.",
                }
            ]),
        }
        await asyncio.to_thread(case_doc_ref.update, update_data)
        
        # Generate effort estimation using PlannerAgent
        effort_response = await self.planner_agent.generate_effort_estimate(
            system_design_content=system_design,
            case_title=case_data.get("title", "Unknown"),
            problem_statement=case_data.get("problem_statement", ""),
        )
        
        updated_at_time = datetime.now(timezone.utc)
        
        if effort_response.get("status") == "success" and effort_response.get("effort_estimate"):
            # Effort estimation successful
            effort_estimate = effort_response["effort_estimate"]
            effort_estimate["generated_by"] = "PlannerAgent"
            effort_estimate["version"] = "v1"
            effort_estimate["generated_timestamp"] = updated_at_time.isoformat()
            
            # Update case with effort estimate and change status to PLANNING_COMPLETE
            update_data = {
                "effort_estimate_v1": effort_estimate,
                "status": BusinessCaseStatus.PLANNING_COMPLETE.value,
                "updated_at": updated_at_time,
                "history": get_array_union([
                    {
                        "timestamp": updated_at_time.isoformat(),
                        "source": "PLANNER_AGENT",
                        "type": "EFFORT_ESTIMATE",
                        "content": f"Effort estimate generated for {case_data.get('title', 'Unknown')}",
                    },
                    {
                        "timestamp": updated_at_time.isoformat(),
                        "source": "ORCHESTRATOR_AGENT",
                        "type": "STATUS_UPDATE",
                        "content": f"Status updated to {BusinessCaseStatus.PLANNING_COMPLETE.value}. Effort estimation completed.",
                    }
                ]),
            }
            
            await asyncio.to_thread(case_doc_ref.update, update_data)
            orchestrator_logger.info(f"Effort estimation completed successfully for case {case_id}")
            
            return {
                "status": "success",
                "message": "Effort estimation generated successfully",
                "case_id": case_id,
                "new_status": BusinessCaseStatus.PLANNING_COMPLETE.value,
            }
        else:
            # Effort estimation failed
            error_message = effort_response.get("message", "Failed to generate effort estimate")
            orchestrator_logger.warning(f"Effort estimation failed for case {case_id}: {error_message}")
            
            # Revert to SYSTEM_DESIGN_APPROVED state
            revert_update_data = {
                "status": BusinessCaseStatus.SYSTEM_DESIGN_APPROVED.value,
                "updated_at": updated_at_time,
                "history": get_array_union([
                    {
                        "timestamp": updated_at_time.isoformat(),
                        "source": "ORCHESTRATOR_AGENT",
                        "type": "ERROR",
                        "content": f"Effort estimation failed: {error_message}. Status reverted to SYSTEM_DESIGN_APPROVED.",
                    }
                ]),
            }
            
            await asyncio.to_thread(case_doc_ref.update, revert_update_data)
            
            return {
                "status": "error",
                "message": f"Effort estimation failed: {error_message}",
                "case_id": case_id,
            }
            
    except Exception as e:
        orchestrator_logger = log_agent_operation(
            self.logger, "OrchestratorAgent", case_id, "handle_system_design_approval"
        )
        log_error_with_context(
            orchestrator_logger, 
            f"Error handling system design approval for case {case_id}", 
            e,
            {'case_id': case_id}
        )
        return {
            "status": "error",
            "message": f"Error handling system design approval: {str(e)}",
        }
```

### 2. Create System Design API Routes
**File:** `backend/app/api/v1/cases/system_design_routes.py` (new file)

```python
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

    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    # Role check: only DEVELOPER can approve
    user_role = current_user.get("custom_claims", {}).get("role")
    if user_role != "DEVELOPER":
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to approve system designs. DEVELOPER role required.",
        )

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

        # After successful system design approval, initiate effort estimation
        try:
            from app.agents.orchestrator_agent import OrchestratorAgent

            orchestrator = OrchestratorAgent()

            logger.info(f"Triggering effort estimation for approved system design in case {case_id}")
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

    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")

    # Role check: only DEVELOPER can reject
    user_role = current_user.get("custom_claims", {}).get("role")
    if user_role != "DEVELOPER":
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to reject system designs. DEVELOPER role required.",
        )

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
```

### 3. Fix PRD Approval Logic
**File:** `backend/app/agents/orchestrator_agent.py`  
**Lines:** 946-1040

**REMOVE** the automatic effort estimation logic from `handle_prd_approval()`:

```python
# REMOVE LINES 946-1040 (effort estimation logic)
# KEEP ONLY: System design generation and status update to SYSTEM_DESIGN_DRAFTED
```

### 4. Register System Design Routes
**File:** `backend/app/api/v1/cases/__init__.py`

```python
from .system_design_routes import router as system_design_router

cases_router.include_router(system_design_router, tags=["Business Cases - System Design"])
```

### 5. Add Required Models
**File:** `backend/app/api/v1/cases/models.py`

```python
class SystemDesignUpdateRequest(BaseModel):
    content_markdown: str = Field(..., description="Updated system design content in markdown format")

class SystemDesignRejectRequest(BaseModel):
    reason: Optional[str] = Field(None, description="Optional reason for rejecting the system design")
```

---

## 🔍 Enhanced Logging Recommendations

### Critical Logging Points
Add logging to these key workflow transition points:

1. **System Design Approval Attempts:**
```python
logger.info(f"System design approval initiated for case {case_id} by user {user_email}")
```

2. **Orchestrator Method Calls:**
```python
orchestrator_logger.info(f"handle_system_design_approval triggered for case {case_id}")
```

3. **Agent Invocation Results:**
```python
orchestrator_logger.info(f"PlannerAgent response for case {case_id}: {effort_response.get('status')}")
```

4. **Status Transition Validation:**
```python
orchestrator_logger.info(f"Status transition: {old_status} → {new_status} for case {case_id}")
```

---

## 🚀 Implementation Priority

| Priority | Task | Estimated Effort | Impact |
|----------|------|------------------|---------|
| **CRITICAL** | Create `handle_system_design_approval()` method | 2 hours | Fixes core workflow |
| **CRITICAL** | Create system design API endpoints | 3 hours | Enables frontend integration |
| **HIGH** | Fix PRD approval logic | 1 hour | Prevents workflow bypass |
| **HIGH** | Register system design routes | 15 minutes | Completes API integration |
| **MEDIUM** | Add Pydantic models | 30 minutes | Enables proper validation |
| **LOW** | Enhanced logging | 1 hour | Improves debugging |

**Total Estimated Effort:** 6.75 hours

---

## ✅ Testing Strategy

### 1. Unit Tests
- Test `handle_system_design_approval()` method
- Test system design API endpoints
- Test status transitions

### 2. Integration Tests
- Test complete workflow: PRD → System Design → Effort Estimation
- Test HITL approval/rejection workflows
- Test role-based authorization

### 3. End-to-End Tests
- Test full business case workflow
- Test UI interaction with new endpoints
- Test error handling and rollback scenarios

---

## 📋 Acceptance Criteria

- [x] **Root Cause Identified**: Missing system design approval orchestration
- [x] **Actionable Recommendations**: Specific code changes provided  
- [x] **Pattern Analysis**: Confirmed later stages work correctly
- [x] **Status Enum Review**: All necessary statuses exist
- [x] **Workflow Support**: Architecture supports full multi-stage workflow

---

## 🎯 Success Metrics

After implementation, the workflow should support:

1. **Complete HITL Workflow:** PRD → System Design → Effort → Cost → Value → Financial → Approval
2. **Proper Status Transitions:** Each stage has distinct draft/review/approved states
3. **Role-Based Authorization:** Different roles can perform appropriate actions
4. **Automatic Progression:** Each approval triggers the next workflow stage
5. **Error Handling:** Failed agent calls don't break the workflow

---

**Report Status:** ✅ Complete  
**Next Steps:** Implement fixes in priority order  
**Expected Resolution Time:** 1-2 development days 