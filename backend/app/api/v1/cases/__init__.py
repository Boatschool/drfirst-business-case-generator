"""
Combined router for all business case related API endpoints.
"""

from fastapi import APIRouter

from .list_retrieve_routes import router as list_retrieve_router
from .status_routes import router as status_router
from .prd_routes import router as prd_router
from .export_routes import router as export_router
from .final_approval_routes import router as final_approval_router
from .financial_estimates_routes import router as financial_estimates_router
from .system_design_routes import router as system_design_router

# Create main cases router
cases_router = APIRouter()

# Include all sub-routers
cases_router.include_router(list_retrieve_router, tags=["Business Cases - List/Retrieve"])
cases_router.include_router(status_router, tags=["Business Cases - Status"])
cases_router.include_router(prd_router, tags=["Business Cases - PRD"])
cases_router.include_router(system_design_router, tags=["Business Cases - System Design"])
cases_router.include_router(financial_estimates_router, tags=["Business Cases - Financial Estimates"])
cases_router.include_router(final_approval_router, tags=["Business Cases - Final Approval"])
cases_router.include_router(export_router, tags=["Business Cases - Export"])

# Note: Additional routers can be added here as they are created:
# - financial_routes (additional financial-specific routes beyond estimates) 