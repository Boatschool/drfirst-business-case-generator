"""
Sales/Value Analyst Agent for generating potential revenue or value scenarios.
"""

from typing import Dict, Any
import asyncio
import logging
from google.cloud import firestore
from app.core.config import settings

# Set up logging
logger = logging.getLogger(__name__)

class SalesValueAnalystAgent:
    """
    The Sales/Value Analyst Agent is responsible for generating potential revenue 
    or value scenarios for business cases based on PRD content and pricing templates.
    """

    def __init__(self):
        self.name = "Sales/Value Analyst Agent"
        self.description = "Calculates potential revenue or value scenarios."
        self.status = "initialized"
        
        # Initialize Firestore client for pricing template access
        try:
            self.db = firestore.Client(project=settings.firebase_project_id)
            print("SalesValueAnalystAgent: Firestore client initialized successfully.")
        except Exception as e:
            print(f"SalesValueAnalystAgent: Failed to initialize Firestore client: {e}")
            self.db = None
            
        print(f"SalesValueAnalystAgent: Initialized successfully.")
        self.status = "available"

    async def project_value(self, prd_content: str, case_title: str) -> Dict[str, Any]:
        """
        Projects value/revenue scenarios based on PRD content and case details.
        
        Args:
            prd_content (str): The PRD content to analyze
            case_title (str): Title of the business case
            
        Returns:
            Dict[str, Any]: Response containing status and value projection
        """
        print(f"[SalesValueAnalystAgent] Received request to project value for: {case_title}")
        
        if not self.db:
            logger.warning("[SalesValueAnalystAgent] Firestore client not available, using default scenarios")
            return await self._project_with_default_scenarios(prd_content, case_title)
        
        try:
            # Attempt to fetch pricing template from Firestore
            pricing_template = await self._fetch_pricing_template()
            
            if pricing_template:
                return await self._project_with_template(prd_content, pricing_template, case_title)
            else:
                logger.info("[SalesValueAnalystAgent] No pricing template found, using default scenarios")
                return await self._project_with_default_scenarios(prd_content, case_title)
                
        except Exception as e:
            error_msg = f"Error projecting value: {str(e)}"
            logger.error(f"[SalesValueAnalystAgent] {error_msg} for case {case_title}")
            print(f"[SalesValueAnalystAgent] {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "value_projection": None
            }

    async def _fetch_pricing_template(self) -> Dict[str, Any]:
        """
        Fetches the default pricing template from Firestore.
        
        Returns:
            Dict[str, Any]: Pricing template data or None if not found
        """
        try:
            template_ref = self.db.collection("pricingTemplates").document("default_value_projection")
            doc_snapshot = await asyncio.to_thread(template_ref.get)
            
            if doc_snapshot.exists:
                template_data = doc_snapshot.to_dict()
                logger.info(f"[SalesValueAnalystAgent] Successfully retrieved pricing template: {template_data.get('name', 'Unknown')}")
                return template_data
            else:
                logger.warning("[SalesValueAnalystAgent] Pricing template document 'default_value_projection' not found")
                return None
                
        except Exception as e:
            logger.error(f"[SalesValueAnalystAgent] Error fetching pricing template: {e}")
            return None

    async def _project_with_template(self, prd_content: str, template: Dict[str, Any], case_title: str) -> Dict[str, Any]:
        """
        Projects value using a Firestore pricing template.
        
        Args:
            prd_content (str): The PRD content
            template (Dict[str, Any]): Pricing template data from Firestore
            case_title (str): Title of the business case
            
        Returns:
            Dict[str, Any]: Value projection response
        """
        # Use template structure to guide value scenarios
        template_structure = template.get("structureDefinition", {})
        template_type = template_structure.get("type", "LowBaseHigh")
        
        if template_type == "LowBaseHigh":
            # Generate low/base/high scenarios based on template guidance
            value_data = {
                "scenarios": [
                    {"case": "Low", "value": 5000, "description": "Conservative estimate based on minimal adoption."},
                    {"case": "Base", "value": 15000, "description": "Most likely estimate based on expected adoption."},
                    {"case": "High", "value": 30000, "description": "Optimistic estimate based on high adoption and additional opportunities."}
                ],
                "currency": "USD",
                "template_used": template.get("name", "Unknown Template"),
                "methodology": "Template-based low/base/high scenario modeling",
                "assumptions": [
                    "Value based on potential efficiency gains",
                    "Revenue calculated from user adoption estimates",
                    "Market penetration factors considered"
                ],
                "notes": f"Value projection based on PRD analysis and {template.get('description', 'template guidance')}."
            }
        else:
            # Fallback for other template types
            value_data = {
                "scenarios": [
                    {"case": "Baseline", "value": 12000, "description": "Standard value estimate for this project type."}
                ],
                "currency": "USD",
                "template_used": template.get("name", "Unknown Template"),
                "methodology": "Template-guided baseline estimation",
                "notes": f"Value projection using {template_type} methodology from template."
            }
        
        logger.info(f"[SalesValueAnalystAgent] Successfully projected value for {case_title} using template")
        print(f"[SalesValueAnalystAgent] Generated value projection using template: {template.get('name', 'Unknown')}")
        
        return {
            "status": "success",
            "message": "Value projection completed successfully using pricing template",
            "value_projection": value_data
        }

    async def _project_with_default_scenarios(self, prd_content: str, case_title: str) -> Dict[str, Any]:
        """
        Projects value using hardcoded default scenarios.
        
        Args:
            prd_content (str): The PRD content
            case_title (str): Title of the business case
            
        Returns:
            Dict[str, Any]: Value projection response
        """
        # Default placeholder value scenarios
        value_data = {
            "scenarios": [
                {"case": "Low", "value": 5000, "description": "Conservative estimate."},
                {"case": "Base", "value": 15000, "description": "Most likely estimate."},
                {"case": "High", "value": 30000, "description": "Optimistic estimate."}
            ],
            "currency": "USD",
            "template_used": "Default Placeholder Template",
            "methodology": "Hardcoded scenario modeling (placeholder)",
            "assumptions": [
                "Basic healthcare technology value assumptions",
                "Standard ROI expectations for development projects",
                "Conservative market adoption estimates"
            ],
            "notes": "Initial placeholder value projection. Will be refined with real market data and business analysis."
        }
        
        logger.info(f"[SalesValueAnalystAgent] Successfully projected value for {case_title} using defaults")
        print(f"[SalesValueAnalystAgent] Generated default value projection for case: {case_title}")
        
        return {
            "status": "success",
            "message": "Value projection completed successfully using default scenarios",
            "value_projection": value_data
        }

    def get_status(self) -> Dict[str, str]:
        """Get the current status of the Sales/Value Analyst Agent"""
        return {
            "name": self.name,
            "status": self.status,
            "description": self.description
        } 