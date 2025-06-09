"""
Cost Analyst Agent for applying rate cards to generate cost estimates.
"""

from typing import Dict, Any, Optional
import asyncio
import logging
from app.core.config import settings
from app.core.dependencies import get_db
from app.core.database import DatabaseClient
from app.core.constants import BusinessRules, Collections
from app.core.logging_config import log_agent_operation, log_error_with_context, log_performance_metric
from app.core.agent_logging import create_agent_logger

# Set up logging
logger = logging.getLogger(__name__)


class CostAnalystAgent:
    """
    The Cost Analyst Agent is responsible for applying rate cards to effort estimates
    to generate financial cost projections for business cases.
    """

    def __init__(self, db: Optional[DatabaseClient] = None):
        self.name = "Cost Analyst Agent"
        self.description = "Applies rate card to generate cost estimates."
        self.status = "initialized"

        # Use dependency injection for database client
        self.db = db if db is not None else get_db()
        logger.info("CostAnalystAgent: Database client initialized successfully.")
        logger.info("CostAnalystAgent: Initialized successfully.")
        self.status = "available"

    async def estimate_costs(
        self, effort_breakdown: Dict[str, Any], case_title: str, case_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Public interface for cost estimation that matches function calling expectations.
        Delegates to calculate_cost method with enhanced logging.

        Args:
            effort_breakdown (Dict[str, Any]): The effort breakdown from PlannerAgent
            case_title (str): Title of the business case
            case_id (str, optional): Business case ID for logging

        Returns:
            Dict[str, Any]: Response containing status and cost estimate
        """
        return await self.calculate_cost(
            effort_breakdown=effort_breakdown,
            case_title=case_title,
            case_id=case_id
        )

    async def calculate_cost(
        self, effort_breakdown: Dict[str, Any], case_title: str, case_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculates cost estimates based on effort breakdown and rate cards.

        Args:
            effort_breakdown (Dict[str, Any]): The effort breakdown from PlannerAgent
            case_title (str): Title of the business case
            case_id (str, optional): Business case ID for logging

        Returns:
            Dict[str, Any]: Response containing status and cost estimate
        """
        # Create agent logger
        agent_logger = create_agent_logger("CostAnalystAgent", case_id)
        
        # Prepare input payload for logging
        input_payload = {
            "case_title": case_title,
            "roles_count": len(effort_breakdown.get('roles', [])),
            "total_hours": sum(role.get('hours', 0) for role in effort_breakdown.get('roles', [])),
            "has_effort_breakdown": bool(effort_breakdown),
            "effort_breakdown_keys": list(effort_breakdown.keys()) if effort_breakdown else []
        }
        
        # Use logging context manager
        with agent_logger.log_method_execution(
            method_name="calculate_cost",
            input_payload=input_payload
        ) as log_context:
            
            agent_logger = log_agent_operation(
                logger, "CostAnalystAgent", case_title, "calculate_cost"
            )
            agent_logger.info(
                "Received cost calculation request",
                extra={
                    'roles_count': len(effort_breakdown.get('roles', [])),
                    'total_hours': sum(role.get('hours', 0) for role in effort_breakdown.get('roles', []))
                }
            )

            if not self.db:
                agent_logger.warning("Firestore client not available, using default rates")
                result = await self._calculate_with_default_rates(
                    effort_breakdown, case_title
                )
                return result

            try:
                # Attempt to fetch rate card from Firestore
                rate_card = await self._fetch_rate_card()

                if rate_card:
                    result = await self._calculate_with_rate_card(
                        effort_breakdown, rate_card, case_title
                    )
                    return result
                else:
                    logger.info(
                        "[CostAnalystAgent] No rate card found, using default rates"
                    )
                    result = await self._calculate_with_default_rates(
                        effort_breakdown, case_title
                    )
                    return result

            except Exception as e:
                log_error_with_context(
                    agent_logger,
                    "Cost calculation failed",
                    e,
                    {
                        'effort_breakdown': str(effort_breakdown),
                        'case_title': case_title
                    }
                )
                return {
                    "status": "error", 
                    "message": f"Error calculating cost: {str(e)}", 
                    "cost_estimate": None
                }

    async def _fetch_rate_card(self) -> Dict[str, Any]:
        """
        Fetches an active default rate card from Firestore.
        Strategy:
        1. Query for active rate cards (isActive == true)
        2. Prefer rate cards with isDefault == true
        3. Fallback to most recently updated active rate card
        4. Return None if no active rate cards found

        Returns:
            Dict[str, Any]: Rate card data or None if not found
        """
        try:
            # Query for active rate cards
            rate_cards_ref = self.db.collection(Collections.RATE_CARDS)
            active_cards_query = rate_cards_ref.where("isActive", "==", True)

            # Execute query
            docs = await asyncio.to_thread(lambda: list(active_cards_query.stream()))

            if not docs:
                logger.warning(
                    "[CostAnalystAgent] No active rate cards found in Firestore"
                )
                return None

            logger.info(f"[CostAnalystAgent] Found {len(docs)} active rate card(s)")

            # Convert documents to list with metadata
            rate_cards = []
            for doc in docs:
                rate_card_data = doc.to_dict()
                rate_card_data["id"] = doc.id  # Add document ID
                rate_cards.append(rate_card_data)

            # Strategy 1: Look for rate cards explicitly marked as default
            default_cards = [
                card for card in rate_cards if card.get("isDefault", False)
            ]
            if default_cards:
                selected_card = default_cards[0]  # Use first default card
                logger.info(
                    f"[CostAnalystAgent] Using default rate card: {selected_card.get('name', 'Unknown')} (ID: {selected_card['id']})"
                )
                return selected_card

            # Strategy 2: Use most recently updated active rate card
            # Sort by updated_at in descending order (most recent first)
            sorted_cards = sorted(
                rate_cards, key=lambda x: x.get("updated_at", ""), reverse=True
            )
            selected_card = sorted_cards[0]

            logger.info(
                f"[CostAnalystAgent] Using most recent active rate card: {selected_card.get('name', 'Unknown')} (ID: {selected_card['id']})"
            )
            return selected_card

        except Exception as e:
            logger.error(f"[CostAnalystAgent] Error fetching rate card: {e}")
            return None

    async def _calculate_with_rate_card(
        self,
        effort_breakdown: Dict[str, Any],
        rate_card: Dict[str, Any],
        case_title: str,
    ) -> Dict[str, Any]:
        """
        Calculates cost using a Firestore rate card with detailed role matching and warnings.

        Args:
            effort_breakdown (Dict[str, Any]): The effort breakdown
            rate_card (Dict[str, Any]): Rate card data from Firestore
            case_title (str): Title of the business case

        Returns:
            Dict[str, Any]: Cost calculation response
        """
        total_cost = 0
        role_costs = []
        warnings = []

        # Extract rate card information
        default_rate = rate_card.get("defaultOverallRate", BusinessRules.DEFAULT_HOURLY_RATE)
        currency = rate_card.get("currency", "USD")
        rate_card_name = rate_card.get("name", "Unknown Rate Card")
        rate_card_id = rate_card.get("id", "unknown")

        # Build a mapping of role names to rates for efficient lookup
        role_rate_map = {}
        for rate_info in rate_card.get("roles", []):
            role_name = rate_info.get("roleName")
            if role_name:
                role_rate_map[role_name] = rate_info.get("hourlyRate", default_rate)

        logger.info(
            f"[CostAnalystAgent] Rate card '{rate_card_name}' has rates for {len(role_rate_map)} roles"
        )

        # Calculate cost for each role in the effort breakdown
        roles = effort_breakdown.get("roles", [])
        for role_data in roles:
            role_name = role_data.get("role", "Unknown")
            hours = role_data.get("hours", 0)

            # Find the appropriate rate for this role
            if role_name in role_rate_map:
                # Exact match found
                role_rate = role_rate_map[role_name]
                rate_source = "specific_rate"
            else:
                # No exact match, try fuzzy matching for common variations
                role_rate, was_fuzzy_matched = self._find_fuzzy_rate_match(
                    role_name, role_rate_map, default_rate
                )
                if was_fuzzy_matched:
                    # Found fuzzy match
                    rate_source = "fuzzy_match"
                else:
                    # Used default rate due to no match
                    rate_source = "default_rate"
                    warning_msg = f"No specific rate found for role '{role_name}', using default rate ${default_rate}/hour"
                    warnings.append(warning_msg)
                    logger.warning(f"[CostAnalystAgent] {warning_msg}")

            role_cost = hours * role_rate
            total_cost += role_cost

            role_costs.append(
                {
                    "role": role_name,
                    "hours": hours,
                    "hourly_rate": role_rate,
                    "total_cost": role_cost,
                    "currency": currency,
                    "rate_source": rate_source,
                }
            )

        # Build notes with warnings and summary
        notes_parts = [
            f"Cost calculated using rate card: {rate_card.get('description', 'No description available')}"
        ]
        if warnings:
            notes_parts.append(f"Warnings: {'; '.join(warnings)}")

        cost_data = {
            "estimated_cost": total_cost,
            "currency": currency,
            "rate_card_used": rate_card_name,
            "rate_card_id": rate_card_id,
            "breakdown_by_role": role_costs,  # Enhanced breakdown with rate source info
            "calculation_method": "rate_card_based",
            "warnings": warnings,
            "notes": " | ".join(notes_parts),
        }

        logger.info(
            f"[CostAnalystAgent] Successfully calculated cost for {case_title}: ${total_cost:,.2f} using rate card '{rate_card_name}'"
        )
        if warnings:
            logger.info(
                f"[CostAnalystAgent] Generated {len(warnings)} warning(s) during calculation"
            )

        logger.info(
            f"[CostAnalystAgent] Generated cost estimate: ${total_cost:,.2f} using rate card '{rate_card_name}'"
        )

        return {
            "status": "success",
            "message": "Cost calculation completed successfully using rate card",
            "cost_estimate": cost_data,
        }

    def _find_fuzzy_rate_match(
        self, role_name: str, role_rate_map: Dict[str, float], default_rate: float
    ) -> tuple[float, bool]:
        """
        Attempts to find a fuzzy match for role names to handle common variations.

        Args:
            role_name (str): The role name to match
            role_rate_map (Dict[str, float]): Map of role names to rates
            default_rate (float): Default rate to use if no match found

        Returns:
            tuple[float, bool]: (matched_rate, was_fuzzy_matched)
        """
        # Normalize the role name for comparison
        normalized_role = role_name.lower().strip()

        # Define common role name mappings and variations
        role_mappings = {
            # Developer variations
            "lead developer": ["developer"],
            "senior developer": ["developer"],
            "junior developer": ["developer"],
            "software developer": ["developer"],
            "software engineer": ["developer"],
            "engineer": ["developer"],
            # QA variations
            "qa engineer": ["qe engineer", "quality engineer", "test engineer"],
            "quality engineer": ["qa engineer"],
            "test engineer": ["qa engineer"],
            "tester": ["qa engineer"],
            # DevOps variations
            "devops engineer": ["devops", "sre", "infrastructure engineer"],
            "sre": ["devops engineer"],
            "infrastructure engineer": ["devops engineer"],
            # Design variations
            "ui/ux designer": ["designer", "ux designer", "ui designer"],
            "ux designer": ["ui/ux designer", "designer"],
            "ui designer": ["ui/ux designer", "designer"],
            "designer": ["ui/ux designer"],
            # Management variations
            "product manager": ["pm", "project manager"],
            "project manager": ["product manager", "pm"],
            "pm": ["product manager"],
        }

        # First, try exact match (case insensitive)
        for existing_role in role_rate_map.keys():
            if existing_role.lower() == normalized_role:
                logger.info(
                    f"[CostAnalystAgent] Found case-insensitive match for '{role_name}' -> '{existing_role}'"
                )
                return role_rate_map[existing_role], True

        # Second, try fuzzy matching using mappings
        potential_matches = role_mappings.get(normalized_role, [])
        logger.debug(
            f"[CostAnalystAgent] Looking for '{normalized_role}', potential matches: {potential_matches}"
        )
        for potential_match in potential_matches:
            for existing_role in role_rate_map.keys():
                if existing_role.lower() == potential_match.lower():
                    logger.info(
                        f"[CostAnalystAgent] Found fuzzy match for '{role_name}' -> '{existing_role}' via '{potential_match}'"
                    )
                    return role_rate_map[existing_role], True

        # Third, try reverse mapping (check if current role matches any mapping values)
        for mapped_role, variations in role_mappings.items():
            if normalized_role in [v.lower() for v in variations]:
                for existing_role in role_rate_map.keys():
                    if existing_role.lower() == mapped_role.lower():
                        logger.info(
                            f"[CostAnalystAgent] Found reverse fuzzy match for '{role_name}' -> '{existing_role}' via '{mapped_role}'"
                        )
                        return role_rate_map[existing_role], True

        # Fourth, try partial matching (contains)
        for existing_role in role_rate_map.keys():
            existing_normalized = existing_role.lower()
            # Check if either contains the other (but avoid very short matches)
            if len(existing_normalized) > 3 and len(normalized_role) > 3:
                if (
                    normalized_role in existing_normalized
                    or existing_normalized in normalized_role
                ):
                    logger.info(
                        f"[CostAnalystAgent] Found partial match for '{role_name}' -> '{existing_role}'"
                    )
                    return role_rate_map[existing_role], True

        # Fifth, try word-based matching for developer variations
        normalized_words = set(normalized_role.split())
        for existing_role in role_rate_map.keys():
            existing_words = set(existing_role.lower().split())
            # Check for overlap in key words
            if "developer" in normalized_words and "developer" in existing_words:
                logger.info(
                    f"[CostAnalystAgent] Found word-based match for '{role_name}' -> '{existing_role}' (both contain 'developer')"
                )
                return role_rate_map[existing_role], True
            if "engineer" in normalized_words and (
                "engineer" in existing_words or "developer" in existing_words
            ):
                logger.info(
                    f"[CostAnalystAgent] Found word-based match for '{role_name}' -> '{existing_role}' (engineer/developer match)"
                )
                return role_rate_map[existing_role], True

        # No match found, return default rate
        return default_rate, False

    async def _calculate_with_default_rates(
        self, effort_breakdown: Dict[str, Any], case_title: str
    ) -> Dict[str, Any]:
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
            "Developer": BusinessRules.DEFAULT_HOURLY_RATE,
            "Product Manager": 120,
            "QA Engineer": 85,
            "DevOps Engineer": 110,
            "UI/UX Designer": 95,
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
            role_rate = default_rates.get(role_name, BusinessRules.DEFAULT_HOURLY_RATE)
            role_cost = hours * role_rate
            total_cost += role_cost

            role_costs.append(
                {
                    "role": role_name,
                    "hours": hours,
                    "hourly_rate": role_rate,
                    "total_cost": role_cost,
                    "currency": currency,
                }
            )

        cost_data = {
            "estimated_cost": total_cost,
            "currency": currency,
            "rate_card_used": "Default Placeholder Rates",
            "breakdown_by_role": role_costs,
            "calculation_method": "hardcoded_defaults",
            "warnings": [],
            "notes": "Initial placeholder cost estimate using hardcoded default rates. Consider configuring a rate card in Firestore for more accurate estimates.",
        }

        logger.info(
            f"[CostAnalystAgent] Successfully calculated cost for {case_title}: ${total_cost:,.2f}"
        )
        logger.info(
            f"[CostAnalystAgent] Generated cost estimate: ${total_cost:,.2f} using default rates"
        )

        return {
            "status": "success",
            "message": "Cost calculation completed successfully using default rates",
            "cost_estimate": cost_data,
        }

    def get_status(self) -> Dict[str, str]:
        """Get the current status of the cost analyst agent"""
        return {
            "name": self.name,
            "status": self.status,
            "description": self.description,
        }
