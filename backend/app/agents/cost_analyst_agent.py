"""
Cost Analyst Agent for applying rate cards to generate cost estimates.
"""

from typing import Dict, Any
import asyncio
import logging
from google.cloud import firestore
from app.core.config import settings

# Set up logging
logger = logging.getLogger(__name__)

class CostAnalystAgent:
    """
    The Cost Analyst Agent is responsible for applying rate cards to effort estimates
    to generate financial cost projections for business cases.
    """

    def __init__(self):
        self.name = "Cost Analyst Agent"
        self.description = "Applies rate card to generate cost estimates."
        self.status = "initialized"
        
        # Initialize Firestore client for rate card access
        try:
            self.db = firestore.Client(project=settings.firebase_project_id)
            print("CostAnalystAgent: Firestore client initialized successfully.")
        except Exception as e:
            print(f"CostAnalystAgent: Failed to initialize Firestore client: {e}")
            self.db = None
            
        print(f"CostAnalystAgent: Initialized successfully.")
        self.status = "available"

    async def calculate_cost(self, effort_breakdown: Dict[str, Any], case_title: str) -> Dict[str, Any]:
        """
        Calculates cost estimates based on effort breakdown and rate cards.
        
        Args:
            effort_breakdown (Dict[str, Any]): The effort breakdown from PlannerAgent
            case_title (str): Title of the business case
            
        Returns:
            Dict[str, Any]: Response containing status and cost estimate
        """
        print(f"[CostAnalystAgent] Received request to calculate cost for: {case_title}")
        
        if not self.db:
            logger.warning("[CostAnalystAgent] Firestore client not available, using default rates")
            return await self._calculate_with_default_rates(effort_breakdown, case_title)
        
        try:
            # Attempt to fetch rate card from Firestore
            rate_card = await self._fetch_rate_card()
            
            if rate_card:
                return await self._calculate_with_rate_card(effort_breakdown, rate_card, case_title)
            else:
                logger.info("[CostAnalystAgent] No rate card found, using default rates")
                return await self._calculate_with_default_rates(effort_breakdown, case_title)
                
        except Exception as e:
            error_msg = f"Error calculating cost: {str(e)}"
            logger.error(f"[CostAnalystAgent] {error_msg} for case {case_title}")
            print(f"[CostAnalystAgent] {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "cost_estimate": None
            }

    async def _fetch_rate_card(self) -> Dict[str, Any]:
        """
        Fetches the default rate card from Firestore.
        
        Returns:
            Dict[str, Any]: Rate card data or None if not found
        """
        try:
            rate_card_ref = self.db.collection("rateCards").document("default_dev_rates")
            doc_snapshot = await asyncio.to_thread(rate_card_ref.get)
            
            if doc_snapshot.exists:
                rate_card_data = doc_snapshot.to_dict()
                logger.info(f"[CostAnalystAgent] Successfully retrieved rate card: {rate_card_data.get('name', 'Unknown')}")
                return rate_card_data
            else:
                logger.warning("[CostAnalystAgent] Rate card document 'default_dev_rates' not found")
                return None
                
        except Exception as e:
            logger.error(f"[CostAnalystAgent] Error fetching rate card: {e}")
            return None

    async def _calculate_with_rate_card(self, effort_breakdown: Dict[str, Any], rate_card: Dict[str, Any], case_title: str) -> Dict[str, Any]:
        """
        Calculates cost using a Firestore rate card.
        
        Args:
            effort_breakdown (Dict[str, Any]): The effort breakdown
            rate_card (Dict[str, Any]): Rate card data from Firestore
            case_title (str): Title of the business case
            
        Returns:
            Dict[str, Any]: Cost calculation response
        """
        total_cost = 0
        role_costs = []
        
        # Use default rate from rate card
        default_rate = rate_card.get("defaultOverallRate", 100)
        currency = "USD"
        
        # Calculate cost for each role
        roles = effort_breakdown.get("roles", [])
        for role_data in roles:
            role_name = role_data.get("role", "Unknown")
            hours = role_data.get("hours", 0)
            
            # Try to find specific role rate, fallback to default
            role_rate = default_rate
            role_rates = rate_card.get("roles", [])
            for rate_info in role_rates:
                if rate_info.get("roleName") == role_name:
                    role_rate = rate_info.get("hourlyRate", default_rate)
                    break
            
            role_cost = hours * role_rate
            total_cost += role_cost
            
            role_costs.append({
                "role": role_name,
                "hours": hours,
                "hourly_rate": role_rate,
                "total_cost": role_cost,
                "currency": currency
            })
        
        cost_data = {
            "estimated_cost": total_cost,
            "currency": currency,
            "rate_card_used": rate_card.get("name", "Default Rate Card"),
            "role_breakdown": role_costs,
            "calculation_method": "rate_card_based",
            "notes": f"Cost calculated using rate card: {rate_card.get('description', 'No description available')}"
        }
        
        logger.info(f"[CostAnalystAgent] Successfully calculated cost for {case_title}: ${total_cost:,.2f}")
        print(f"[CostAnalystAgent] Generated cost estimate: ${total_cost:,.2f} using rate card")
        
        return {
            "status": "success",
            "message": "Cost calculation completed successfully using rate card",
            "cost_estimate": cost_data
        }

    async def _calculate_with_default_rates(self, effort_breakdown: Dict[str, Any], case_title: str) -> Dict[str, Any]:
        """
        Calculates cost using hardcoded default rates.
        
        Args:
            effort_breakdown (Dict[str, Any]): The effort breakdown
            case_title (str): Title of the business case
            
        Returns:
            Dict[str, Any]: Cost calculation response
        """
        # Default rates per role (hardcoded fallback)
        default_rates = {
            "Developer": 100,
            "Product Manager": 120,
            "QA Engineer": 85,
            "DevOps Engineer": 110,
            "UI/UX Designer": 95
        }
        
        total_cost = 0
        role_costs = []
        currency = "USD"
        
        # Calculate cost for each role
        roles = effort_breakdown.get("roles", [])
        for role_data in roles:
            role_name = role_data.get("role", "Unknown")
            hours = role_data.get("hours", 0)
            
            # Get rate for this role or use default
            role_rate = default_rates.get(role_name, 100)
            role_cost = hours * role_rate
            total_cost += role_cost
            
            role_costs.append({
                "role": role_name,
                "hours": hours,
                "hourly_rate": role_rate,
                "total_cost": role_cost,
                "currency": currency
            })
        
        cost_data = {
            "estimated_cost": total_cost,
            "currency": currency,
            "rate_card_used": "Default Placeholder Rates",
            "role_breakdown": role_costs,
            "calculation_method": "hardcoded_defaults",
            "notes": "Initial placeholder cost estimate using hardcoded default rates. Consider configuring a rate card in Firestore for more accurate estimates."
        }
        
        logger.info(f"[CostAnalystAgent] Successfully calculated cost for {case_title}: ${total_cost:,.2f}")
        print(f"[CostAnalystAgent] Generated cost estimate: ${total_cost:,.2f} using default rates")
        
        return {
            "status": "success",
            "message": "Cost calculation completed successfully using default rates",
            "cost_estimate": cost_data
        }

    def get_status(self) -> Dict[str, str]:
        """Get the current status of the cost analyst agent"""
        return {
            "name": self.name,
            "status": self.status,
            "description": self.description
        } 