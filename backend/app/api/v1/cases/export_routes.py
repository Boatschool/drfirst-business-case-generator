"""
API routes for business case export functionality.
"""

import logging
import io
import re
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.auth.firebase_auth import get_current_active_user
from app.core.dependencies import get_firestore_service
from app.services.firestore_service import FirestoreService
from app.core.constants import HTTPStatus, ErrorMessages
from app.models.firestore_models import UserRole

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/cases/{case_id}/export-pdf", summary="Export business case as PDF")
async def export_case_to_pdf(
    case_id: str, 
    current_user: dict = Depends(get_current_active_user),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """
    Exports a business case as a PDF document.
    User must have access to view the case (currently owner only).
    Returns the PDF as a downloadable file.
    """
    user_id = current_user.get("uid")
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

        # Basic authorization: check if the current user is the owner of the case
        # In the future, this could be expanded to allow other roles (e.g., ADMIN, FINAL_APPROVER)
        if business_case.user_id != user_id:
            # Check if user has admin role for broader access
            user_role = current_user.get("systemRole")
            if user_role not in [UserRole.ADMIN.value, UserRole.FINAL_APPROVER.value]:
                raise HTTPException(
                    status_code=HTTPStatus.FORBIDDEN,
                    detail=ErrorMessages.INSUFFICIENT_PERMISSIONS,
                )

        # Convert business case to dict for PDF generation
        case_data = {
            "case_id": business_case.case_id,
            "user_id": business_case.user_id,
            "title": business_case.title,
            "problem_statement": business_case.problem_statement,
            "relevant_links": business_case.relevant_links,
            "status": business_case.status,
            "history": business_case.history,
            "prd_draft": business_case.prd_draft,
            "system_design_v1_draft": business_case.system_design_v1_draft,
            "effort_estimate_v1": business_case.effort_estimate_v1,
            "cost_estimate_v1": business_case.cost_estimate_v1,
            "value_projection_v1": business_case.value_projection_v1,
            "financial_summary_v1": business_case.financial_summary_v1,
            "created_at": business_case.created_at,
            "updated_at": business_case.updated_at,
        }

        # Generate PDF
        from app.utils.pdf_generator import generate_business_case_pdf
        pdf_bytes = await generate_business_case_pdf(case_data)

        # Generate filename
        title = business_case.title or "Business Case"
        # Clean title for filename (remove special characters)
        clean_title = re.sub(r'[<>:"/\\|?*]', "_", title)
        filename = f"business_case_{case_id}_{clean_title}.pdf"

        # Return PDF as streaming response
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "application/pdf",
            },
        )

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error exporting PDF for case {case_id} by user {user_id}: {e}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, 
            detail=f"Failed to export PDF: {str(e)}"
        ) 