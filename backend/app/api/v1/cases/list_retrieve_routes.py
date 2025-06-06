"""
API routes for listing and retrieving business cases.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, Request
from datetime import datetime
from slowapi import Limiter
from slowapi.util import get_remote_address

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
    Retrieves a list of business cases initiated by the authenticated user.
    Supports pagination, filtering, and sorting.
    """
    user_id = current_user.get("uid")
    if not user_id:
        raise AuthenticationError("User ID not found in token")

    # Create contextual logger for this request
    request_logger = log_api_request(logger, "list_cases", user_id, "/cases", "GET")
    
    try:
        request_logger.info(
            "Listing business cases for user", 
            extra={
                'limit': limit,
                'offset': offset,
                'status_filter': status_filter,
                'sort_by': sort_by,
                'sort_order': sort_order
            }
        )
        
        # Use FirestoreService instead of direct database calls
        business_cases = await firestore_service.list_business_cases_for_user(user_id)
        
        # Apply filters
        if status_filter:
            business_cases = [case for case in business_cases if str(case.status).upper() == status_filter.upper()]
        
        if created_after:
            try:
                filter_date = datetime.fromisoformat(created_after.replace('Z', '+00:00'))
                business_cases = [case for case in business_cases if case.created_at >= filter_date]
            except ValueError:
                raise ValueError("created_after must be in ISO format (e.g., '2023-01-01T00:00:00Z')")
        
        # Convert to BusinessCaseSummary models
        summaries: List[BusinessCaseSummary] = []
        for case in business_cases:
            # Convert status Enum to string if it's an Enum object, otherwise assume it's already a string
            status_value = case.status
            if hasattr(status_value, "value"):  # Check if it's an Enum instance
                status_str = status_value.value
            else:
                status_str = str(status_value)  # Fallback to string conversion

            summaries.append(
                BusinessCaseSummary(
                    case_id=case.case_id,
                    user_id=case.user_id,
                    title=case.title or "N/A",
                    status=status_str,
                    created_at=case.created_at,
                    updated_at=case.updated_at,
                )
            )
        
        # Apply sorting
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
        
        request_logger.info(
            "Successfully listed business cases", 
            extra={
                'total_count': total_count,
                'returned_count': len(paginated_summaries),
                'offset': offset,
                'limit': limit
            }
        )
        
        return paginated_summaries
    except ValueError as ve:
        raise AuthenticationError(str(ve))
    except DatabaseError:
        # Re-raise database errors as they're already properly formatted
        raise
    except Exception as e:
        log_error_with_context(
            request_logger,
            "Failed to list business cases for user",
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
    user_id = current_user.get("uid")
    if not user_id:
        raise AuthenticationError("User ID not found in token")

    # Create contextual logger for this request
    request_logger = log_business_case_operation(logger, case_id, user_id, "get_details")

    try:
        request_logger.info(
            "Retrieving business case details",
            extra={
                'include_history': include_history,
                'include_drafts': include_drafts
            }
        )
        
        # Use FirestoreService to get the business case
        business_case = await firestore_service.get_business_case(case_id)
        
        if not business_case:
            request_logger.warning("Business case not found")
            raise BusinessCaseNotFoundError(case_id)

        # Authorization logic: Check if user has permission to view this case
        case_owner_id = business_case.user_id
        
        # Convert enum status to string if needed
        case_status_str = str(business_case.status)
        if hasattr(business_case.status, "value"):
            case_status_str = business_case.status.value

        # Define "shareable" statuses that any authenticated user can view
        shareable_statuses = [
            "APPROVED",  # Final approved cases
            "PENDING_FINAL_APPROVAL",  # Cases pending final approval
            # Add other statuses as needed for sharing
        ]

        # Allow access if:
        # 1. User is the case owner/initiator, OR
        # 2. Case is in a shareable status (for authenticated DrFirst users)
        if case_owner_id != user_id and case_status_str not in shareable_statuses:
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

        # Convert status to string for response
        status_value = business_case.status
        if hasattr(status_value, "value"):  # Check if it's an Enum instance
            status_str = status_value.value
        else:
            status_str = str(status_value)  # Fallback to string conversion

        request_logger.info(
            "Successfully retrieved business case details",
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
        else:
            response_data["history"] = []

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
        else:
            response_data.update({
                "prd_draft": None,
                "system_design_v1_draft": None,
                "effort_estimate_v1": None,
                "cost_estimate_v1": None,
                "value_projection_v1": None,
                "financial_summary_v1": None,
            })

        return BusinessCaseDetailsModel(**response_data)
        
    except (AuthenticationError, AuthorizationError, BusinessCaseNotFoundError, DatabaseError):
        # Re-raise custom exceptions as they're already properly formatted
        raise
    except Exception as e:
        log_error_with_context(
            request_logger,
            "Failed to retrieve business case details",
            e,
            {"case_id": case_id, "user_id": user_id}
        )
        raise DatabaseError(
            operation="get business case details",
            detail=str(e),
            context={"case_id": case_id, "user_id": user_id}
        ) 