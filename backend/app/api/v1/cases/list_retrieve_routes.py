"""
API routes for listing and retrieving business cases.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, Request
from datetime import datetime
from slowapi import Limiter
from slowapi.util import get_remote_address
import traceback

from app.auth.firebase_auth import get_current_active_user
from app.core.dependencies import get_firestore_service
from app.core.exceptions import (
    AuthenticationError, AuthorizationError, BusinessCaseNotFoundError,
    DatabaseError
)
from app.core.logging_config import log_api_request, log_business_case_operation, log_error_with_context
from app.services.firestore_service import FirestoreService
from app.middleware.rate_limiter import limiter
from .models import BusinessCaseSummary, BusinessCaseDetailsModel

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/cases",
    response_model=List[BusinessCaseSummary],
    summary="List business cases for the authenticated user",
)
@limiter.limit("50/minute")
async def list_user_cases(
    request: Request,
    current_user: dict = Depends(get_current_active_user),
    firestore_service: FirestoreService = Depends(get_firestore_service),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Maximum number of cases to return (1-100)"
    ),
    offset: int = Query(
        0,
        ge=0,
        le=10000,
        description="Number of cases to skip for pagination"
    ),
    status_filter: Optional[str] = Query(
        None,
        min_length=1,
        max_length=50,
        pattern=r'^[A-Z_]+$',
        description="Filter by status (e.g., PENDING, APPROVED)"
    ),
    created_after: Optional[str] = Query(
        None,
        description="Filter cases created after this date (ISO format)"
    ),
    sort_by: str = Query(
        "updated_at",
        pattern=r'^(created_at|updated_at|title|status)$',
        description="Sort field: created_at, updated_at, title, or status"
    ),
    sort_order: str = Query(
        "desc",
        pattern=r'^(asc|desc)$',
        description="Sort order: asc or desc"
    )
):
    """
    Lists business cases for the authenticated user with optional filtering, sorting, and pagination.
    """
    logger.info("🗂️ [CASES-LIST] Starting business case list request")
    
    user_id = current_user.get("uid")
    if not user_id:
        logger.error("🗂️ [CASES-LIST] ❌ No user ID found in token")
        raise AuthenticationError("User ID not found in token")

    logger.info(f"🗂️ [CASES-LIST] ✅ EXTRACTED USER ID FROM TOKEN: {user_id}")
    logger.info(f"🗂️ [CASES-LIST] 🔍 Current user object: {current_user}")
    logger.info(f"🗂️ [CASES-LIST] User: {user_id}, Filters: status={status_filter}, limit={limit}, offset={offset}")

    # Create contextual logger for this request
    request_logger = log_business_case_operation(logger, "list", user_id, "list_cases")

    try:
        request_logger.info(
            "🗂️ [CASES-LIST] Retrieving business cases for user",
            extra={
                'limit': limit,
                'offset': offset,
                'status_filter': status_filter,
                'sort_by': sort_by,
                'sort_order': sort_order
            }
        )
        
        logger.info("🗂️ [CASES-LIST] 📞 Calling firestore_service.list_business_cases_for_user")
        
        # Get all cases for the user first (filtering by status if provided)
        logger.info(f"🗂️ [CASES-LIST] 🔍 QUERYING FIRESTORE FOR USER ID: {user_id}")
        business_cases = await firestore_service.list_business_cases_for_user(
            user_id, status_filter=status_filter
        )
        
        logger.info(f"🗂️ [CASES-LIST] ✅ Retrieved {len(business_cases)} cases from Firestore for user {user_id}")
        if len(business_cases) == 0:
            logger.warning(f"🗂️ [CASES-LIST] ⚠️ NO CASES FOUND for user ID: {user_id}")
            logger.warning(f"🗂️ [CASES-LIST] 🔍 This might indicate a user ID mismatch!")
        
        # Convert to summary format
        summaries = []
        for i, case in enumerate(business_cases):
            try:
                logger.debug(f"🗂️ [CASES-LIST] 🔄 Processing case {i+1}/{len(business_cases)}: {case.case_id}")
                
                # Convert enum status to string
                status_value = case.status
                if hasattr(status_value, "value"):
                    status_str = status_value.value
                else:
                    status_str = str(status_value)
                
                summary = BusinessCaseSummary(
                    case_id=case.case_id,
                    user_id=case.user_id,
                    title=case.title or "N/A",
                    status=status_str,
                    created_at=case.created_at,
                    updated_at=case.updated_at,
                )
                summaries.append(summary)
                logger.debug(f"🗂️ [CASES-LIST] ✅ Successfully processed case: {case.case_id}")
                
            except Exception as case_error:
                logger.error(f"🗂️ [CASES-LIST] ❌ Error processing case {case.case_id}: {case_error}")
                logger.error(f"🗂️ [CASES-LIST] 🔍 Case data: {case}")
                logger.error(f"🗂️ [CASES-LIST] 📊 Full traceback: {traceback.format_exc()}")
                # Continue processing other cases instead of failing completely
                continue
        
        logger.info(f"🗂️ [CASES-LIST] ✅ Successfully converted {len(summaries)} cases to summaries")
        
        # HARDENING: Alert if no cases were converted but cases were found
        if len(business_cases) > 0 and len(summaries) == 0:
            logger.critical(f"🗂️ [CASES-LIST] 🚨 CRITICAL: Found {len(business_cases)} cases but converted 0 summaries - possible data conversion issue!")
            logger.critical(f"🗂️ [CASES-LIST] 🔍 This indicates a serious bug in the API response generation")
        
        # HARDENING: Log successful conversion ratio
        conversion_ratio = len(summaries) / len(business_cases) if len(business_cases) > 0 else 1.0
        if conversion_ratio < 1.0:
            logger.warning(f"🗂️ [CASES-LIST] ⚠️ Conversion ratio: {conversion_ratio:.2%} ({len(summaries)}/{len(business_cases)})")
        else:
            logger.info(f"🗂️ [CASES-LIST] ✅ Perfect conversion ratio: 100% ({len(summaries)}/{len(business_cases)})")
        
        # Apply date filtering if provided
        if created_after:
            try:
                filter_date = datetime.fromisoformat(created_after.replace("Z", "+00:00"))
                summaries = [s for s in summaries if s.created_at and s.created_at >= filter_date]
                logger.info(f"🗂️ [CASES-LIST] 📅 Date filter applied, {len(summaries)} cases remain")
            except ValueError as ve:
                logger.error(f"🗂️ [CASES-LIST] ❌ Invalid date format: {created_after}")
                raise AuthenticationError(f"Invalid date format: {str(ve)}")
        
        # Apply sorting
        logger.info(f"🗂️ [CASES-LIST] 🔤 Applying sort: {sort_by} {sort_order}")
        reverse_sort = sort_order == "desc"
        if sort_by == "created_at":
            summaries.sort(key=lambda x: x.created_at or datetime.min, reverse=reverse_sort)
        elif sort_by == "updated_at":
            summaries.sort(key=lambda x: x.updated_at or datetime.min, reverse=reverse_sort)
        elif sort_by == "title":
            summaries.sort(key=lambda x: x.title.lower(), reverse=reverse_sort)
        elif sort_by == "status":
            summaries.sort(key=lambda x: x.status, reverse=reverse_sort)
        
        # Apply pagination
        total_count = len(summaries)
        paginated_summaries = summaries[offset:offset + limit]
        
        logger.info(f"🗂️ [CASES-LIST] ✅ Successfully completed list request: {len(paginated_summaries)}/{total_count} cases returned")
        
        request_logger.info(
            "🗂️ [CASES-LIST] Successfully listed business cases", 
            extra={
                'total_count': total_count,
                'returned_count': len(paginated_summaries),
                'offset': offset,
                'limit': limit
            }
        )
        
        return paginated_summaries
        
    except ValueError as ve:
        logger.error(f"🗂️ [CASES-LIST] ❌ Value error: {ve}")
        raise AuthenticationError(str(ve))
    except DatabaseError as de:
        logger.error(f"🗂️ [CASES-LIST] ❌ Database error: {de}")
        # Re-raise database errors as they're already properly formatted
        raise
    except Exception as e:
        logger.error(f"🗂️ [CASES-LIST] ❌ Unexpected error: {e}")
        logger.error(f"🗂️ [CASES-LIST] 📊 Full traceback: {traceback.format_exc()}")
        log_error_with_context(
            request_logger,
            "🗂️ [CASES-LIST] Failed to list business cases for user",
            e,
            {"user_id": user_id}
        )
        raise DatabaseError(
            operation="list business cases",
            detail=str(e),
            context={"user_id": user_id}
        )


@router.get(
    "/cases/{case_id}",
    response_model=BusinessCaseDetailsModel,
    summary="Get details for a specific business case",
)
@limiter.limit("30/minute")
async def get_case_details(
    request: Request,
    case_id: str = Path(
        ...,
        min_length=1,
        max_length=128,
        description="Business case ID"
    ), 
    current_user: dict = Depends(get_current_active_user),
    firestore_service: FirestoreService = Depends(get_firestore_service),
    include_history: bool = Query(
        True,
        description="Whether to include case history in response"
    ),
    include_drafts: bool = Query(
        True,
        description="Whether to include draft content in response"
    )
):
    """
    Retrieves the full details for a specific business case.
    Ensures the authenticated user is the owner of the case or has appropriate access.
    """
    logger.info(f"📋 [CASE-DETAILS] Starting case details request for case: {case_id}")
    
    user_id = current_user.get("uid")
    if not user_id:
        logger.error(f"📋 [CASE-DETAILS] ❌ No user ID found in token for case: {case_id}")
        raise AuthenticationError("User ID not found in token")

    logger.info(f"📋 [CASE-DETAILS] User: {user_id}, Case: {case_id}, Include history: {include_history}, Include drafts: {include_drafts}")

    # Create contextual logger for this request
    request_logger = log_business_case_operation(logger, case_id, user_id, "get_details")

    try:
        request_logger.info(
            f"📋 [CASE-DETAILS] Retrieving business case details for {case_id}",
            extra={
                'include_history': include_history,
                'include_drafts': include_drafts
            }
        )
        
        logger.info(f"📋 [CASE-DETAILS] 📞 Calling firestore_service.get_business_case({case_id})")
        
        # Use FirestoreService to get the business case
        business_case = await firestore_service.get_business_case(case_id)
        
        if not business_case:
            logger.warning(f"📋 [CASE-DETAILS] ❌ Business case not found: {case_id}")
            request_logger.warning("Business case not found")
            raise BusinessCaseNotFoundError(case_id)

        logger.info(f"📋 [CASE-DETAILS] ✅ Retrieved business case from Firestore: {case_id}")
        logger.debug(f"📋 [CASE-DETAILS] 🔍 Case data: user_id={business_case.user_id}, status={business_case.status}, title={business_case.title}")

        # Authorization logic: Check if user has permission to view this case
        case_owner_id = business_case.user_id
        
        logger.info(f"📋 [CASE-DETAILS] 🔐 Authorization check: case_owner={case_owner_id}, requesting_user={user_id}")
        
        # Convert enum status to string if needed
        case_status_str = str(business_case.status)
        if hasattr(business_case.status, "value"):
            case_status_str = business_case.status.value

        logger.info(f"📋 [CASE-DETAILS] 📊 Case status: {case_status_str}")

        # Define "shareable" statuses that any authenticated user can view
        shareable_statuses = [
            "APPROVED",  # Final approved cases
            "PENDING_FINAL_APPROVAL",  # Cases pending final approval
            # Add other statuses as needed for sharing
        ]

        # Check if user can approve for the current stage
        user_role = current_user.get("systemRole") or current_user.get("custom_claims", {}).get("systemRole", "")
        can_approve_stage = False
        
        # Stage-specific approval permissions (matching Firestore rules)
        if case_status_str == "PRD_REVIEW" and user_role == "PRODUCT_OWNER":
            can_approve_stage = True
        elif case_status_str in ["SYSTEM_DESIGN_PENDING_REVIEW", "SYSTEM_DESIGN_DRAFTED"] and user_role in ["DEVELOPER", "TECHNICAL_ARCHITECT"]:
            can_approve_stage = True
        elif case_status_str == "EFFORT_PENDING_REVIEW" and user_role in ["DEVELOPER", "TECHNICAL_ARCHITECT"]:
            can_approve_stage = True
        elif case_status_str == "COSTING_PENDING_REVIEW" and user_role == "FINANCE_APPROVER":
            can_approve_stage = True
        elif case_status_str == "VALUE_PENDING_REVIEW" and user_role == "SALES_MANAGER":
            can_approve_stage = True
        elif case_status_str == "PENDING_FINAL_APPROVAL" and user_role == "FINAL_APPROVER":
            can_approve_stage = True

        # Allow access if:
        # 1. User is the case owner/initiator, OR
        # 2. Case is in a shareable status (for authenticated DrFirst users), OR
        # 3. User has approval permissions for the current stage, OR
        # 4. User is an admin
        is_owner = case_owner_id == user_id
        is_shareable = case_status_str in shareable_statuses
        is_admin = user_role == "ADMIN"
        
        logger.info(f"📋 [CASE-DETAILS] 🔐 Authorization: is_owner={is_owner}, is_shareable={is_shareable}, can_approve_stage={can_approve_stage}, is_admin={is_admin}, user_role={user_role}")
        
        if not (is_owner or is_shareable or can_approve_stage or is_admin):
            logger.warning(f"📋 [CASE-DETAILS] ❌ User unauthorized to view business case: {case_id}")
            request_logger.warning(
                "User unauthorized to view business case",
                extra={
                    'case_owner_id': case_owner_id,
                    'case_status': case_status_str,
                    'is_shareable': False
                }
            )
            raise AuthorizationError(
                detail="You do not have permission to view this business case",
                context={"case_id": case_id, "case_status": case_status_str}
            )

        logger.info(f"📋 [CASE-DETAILS] ✅ Authorization passed for case: {case_id}")

        # Convert status to string for response
        status_value = business_case.status
        if hasattr(status_value, "value"):  # Check if it's an Enum instance
            status_str = status_value.value
        else:
            status_str = str(status_value)  # Fallback to string conversion

        logger.info(f"📋 [CASE-DETAILS] 🔄 Building response data for case: {case_id}")

        request_logger.info(
            f"📋 [CASE-DETAILS] Successfully retrieved business case details for {case_id}",
            extra={
                'case_status': status_str,
                'is_owner': case_owner_id == user_id
            }
        )

        # Build response based on query parameters
        response_data = {
            "case_id": business_case.case_id,
            "user_id": business_case.user_id,
            "title": business_case.title or "N/A",
            "problem_statement": business_case.problem_statement or "",
            "relevant_links": business_case.relevant_links or [],
            "status": status_str,
            "created_at": business_case.created_at,
            "updated_at": business_case.updated_at,
        }

        # Conditionally include history
        if include_history:
            response_data["history"] = business_case.history or []
            logger.debug(f"📋 [CASE-DETAILS] ✅ Included history: {len(business_case.history or [])} entries")
        else:
            response_data["history"] = []
            logger.debug(f"📋 [CASE-DETAILS] ⏭️ Skipped history inclusion")

        # Conditionally include drafts
        if include_drafts:
            response_data.update({
                "prd_draft": business_case.prd_draft,
                "system_design_v1_draft": business_case.system_design_v1_draft,
                "effort_estimate_v1": business_case.effort_estimate_v1,
                "cost_estimate_v1": business_case.cost_estimate_v1,
                "value_projection_v1": business_case.value_projection_v1,
                "financial_summary_v1": business_case.financial_summary_v1,
            })
            logger.debug(f"📋 [CASE-DETAILS] ✅ Included draft content for case: {case_id}")
        else:
            response_data.update({
                "prd_draft": None,
                "system_design_v1_draft": None,
                "effort_estimate_v1": None,
                "cost_estimate_v1": None,
                "value_projection_v1": None,
                "financial_summary_v1": None,
            })
            logger.debug(f"📋 [CASE-DETAILS] ⏭️ Skipped draft content inclusion")

        logger.info(f"📋 [CASE-DETAILS] 🏗️ Creating BusinessCaseDetailsModel for case: {case_id}")
        
        try:
            result = BusinessCaseDetailsModel(**response_data)
            logger.info(f"📋 [CASE-DETAILS] ✅ Successfully created response model for case: {case_id}")
            return result
        except Exception as model_error:
            logger.error(f"📋 [CASE-DETAILS] ❌ Error creating response model for case {case_id}: {model_error}")
            logger.error(f"📋 [CASE-DETAILS] 🔍 Response data keys: {list(response_data.keys())}")
            logger.error(f"📋 [CASE-DETAILS] 📊 Full traceback: {traceback.format_exc()}")
            raise
        
    except (AuthenticationError, AuthorizationError, BusinessCaseNotFoundError, DatabaseError):
        # Re-raise custom exceptions as they're already properly formatted
        logger.info(f"📋 [CASE-DETAILS] ⚠️ Known exception for case {case_id}, re-raising")
        raise
    except Exception as e:
        logger.error(f"📋 [CASE-DETAILS] ❌ Unexpected error for case {case_id}: {e}")
        logger.error(f"📋 [CASE-DETAILS] 📊 Full traceback: {traceback.format_exc()}")
        log_error_with_context(
            request_logger,
            f"📋 [CASE-DETAILS] Failed to retrieve business case details for {case_id}",
            e,
            {"case_id": case_id, "user_id": user_id}
        )
        raise DatabaseError(
            operation="get business case details",
            detail=str(e),
            context={"case_id": case_id, "user_id": user_id}
        ) 