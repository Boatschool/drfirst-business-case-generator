"""
Financial Model Agent for consolidating cost estimates and value projections.
"""

from typing import Dict, Any
import logging

# Set up logging
logger = logging.getLogger(__name__)


class FinancialModelAgent:
    """
    The Financial Model Agent is responsible for consolidating approved cost estimates
    and value projections into a comprehensive financial summary with calculated metrics.
    """

    def __init__(self):
        self.name = "Financial Model Agent"
        self.description = (
            "Consolidates cost and value projections, calculates financial metrics."
        )
        self.status = "initialized"

        print("FinancialModelAgent: Initialized successfully.")
        self.status = "available"

    async def generate_financial_summary(
        self,
        cost_estimate: Dict[str, Any],
        value_projection: Dict[str, Any],
        case_title: str,
    ) -> Dict[str, Any]:
        """
        Generates a comprehensive financial summary by consolidating cost estimates and value projections.

        Args:
            cost_estimate (Dict[str, Any]): The approved cost estimate data
            value_projection (Dict[str, Any]): The approved value projection data
            case_title (str): Title of the business case

        Returns:
            Dict[str, Any]: Response containing status and financial summary
        """
        print(f"[FinancialModelAgent] Generating financial summary for: {case_title}")

        try:
            # Extract key figures from cost estimate
            total_cost = self._extract_total_cost(cost_estimate)
            cost_currency = cost_estimate.get("currency", "USD")

            # Extract key figures from value projection
            value_scenarios = self._extract_value_scenarios(value_projection)
            value_currency = value_projection.get("currency", "USD")

            # Validate currency consistency
            if cost_currency != value_currency:
                logger.warning(
                    f"[FinancialModelAgent] Currency mismatch: Cost ({cost_currency}) vs Value ({value_currency})"
                )
                # For V1, we'll continue with a warning but use the cost currency as primary

            primary_currency = cost_currency

            # Calculate basic financial metrics
            financial_metrics = self._calculate_financial_metrics(
                total_cost, value_scenarios, primary_currency
            )

            # Construct the financial summary
            summary_data = {
                "total_estimated_cost": total_cost,
                "currency": primary_currency,
                "value_scenarios": value_scenarios,
                "financial_metrics": financial_metrics,
                "cost_breakdown_source": cost_estimate.get(
                    "rate_card_used", "Default rates"
                ),
                "value_methodology": value_projection.get(
                    "methodology", "Standard projection"
                ),
                "notes": "Initial financial summary based on approved estimates.",
                "generated_timestamp": None,  # Will be set by orchestrator
            }

            logger.info(
                f"[FinancialModelAgent] Successfully generated financial summary for {case_title}"
            )
            return {"status": "success", "financial_summary": summary_data}

        except Exception as e:
            error_msg = f"Error generating financial summary: {str(e)}"
            logger.error(f"[FinancialModelAgent] {error_msg} for case {case_title}")
            print(f"[FinancialModelAgent] {error_msg}")
            return {"status": "error", "message": error_msg, "financial_summary": None}

    def _extract_total_cost(self, cost_estimate: Dict[str, Any]) -> float:
        """
        Extracts the total cost from the cost estimate data.

        Args:
            cost_estimate (Dict[str, Any]): Cost estimate data

        Returns:
            float: Total estimated cost

        Raises:
            ValueError: If estimated_cost is not found or invalid
        """
        estimated_cost = cost_estimate.get("estimated_cost")

        if estimated_cost is None:
            raise ValueError("Missing 'estimated_cost' in cost estimate data")

        if not isinstance(estimated_cost, (int, float)):
            raise ValueError(f"Invalid estimated_cost type: {type(estimated_cost)}")

        if estimated_cost < 0:
            raise ValueError(
                f"Invalid estimated_cost value: {estimated_cost} (cannot be negative)"
            )

        return float(estimated_cost)

    def _extract_value_scenarios(
        self, value_projection: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Extracts value scenarios from the value projection data.

        Args:
            value_projection (Dict[str, Any]): Value projection data

        Returns:
            Dict[str, float]: Dictionary mapping scenario names to values

        Raises:
            ValueError: If scenarios data is invalid or missing
        """
        scenarios = value_projection.get("scenarios", [])

        if not scenarios:
            raise ValueError("Missing or empty 'scenarios' in value projection data")

        value_scenarios = {}

        for scenario in scenarios:
            case_name = scenario.get("case", "Unknown")
            value = scenario.get("value")

            if value is None:
                logger.warning(
                    f"[FinancialModelAgent] Missing value for scenario '{case_name}', skipping"
                )
                continue

            if not isinstance(value, (int, float)):
                logger.warning(
                    f"[FinancialModelAgent] Invalid value type for scenario '{case_name}': {type(value)}, skipping"
                )
                continue

            value_scenarios[case_name] = float(value)

        if not value_scenarios:
            raise ValueError("No valid scenarios found in value projection data")

        return value_scenarios

    def _calculate_financial_metrics(
        self, total_cost: float, value_scenarios: Dict[str, float], currency: str
    ) -> Dict[str, Any]:
        """
        Calculates basic financial metrics based on cost and value data.

        Args:
            total_cost (float): Total estimated cost
            value_scenarios (Dict[str, float]): Value scenarios (e.g., Low, Base, High)
            currency (str): Currency for calculations

        Returns:
            Dict[str, Any]: Dictionary containing calculated financial metrics
        """
        metrics = {}

        # Calculate metrics for each scenario
        for scenario_name, scenario_value in value_scenarios.items():
            scenario_key = scenario_name.lower().replace(" ", "_")

            # Net Value calculation
            net_value = scenario_value - total_cost
            metrics[f"net_value_{scenario_key}"] = round(net_value, 2)

            # ROI calculation (Return on Investment)
            if total_cost > 0:
                roi_percentage = (net_value / total_cost) * 100
                metrics[f"roi_{scenario_key}_percentage"] = round(roi_percentage, 2)
            else:
                metrics[f"roi_{scenario_key}_percentage"] = "N/A (zero cost)"
                logger.warning(
                    "[FinancialModelAgent] Cannot calculate ROI: total cost is zero"
                )

            # Break-even point (simplified)
            if scenario_value > 0:
                breakeven_ratio = total_cost / scenario_value
                metrics[f"breakeven_ratio_{scenario_key}"] = round(breakeven_ratio, 4)
            else:
                metrics[f"breakeven_ratio_{scenario_key}"] = "N/A (zero value)"

        # Overall summary metrics (using Base case if available, otherwise first scenario)
        base_scenario_value = value_scenarios.get("Base") or value_scenarios.get("base")
        if not base_scenario_value:
            # Fallback to first available scenario
            base_scenario_value = next(iter(value_scenarios.values()))
            base_scenario_name = next(iter(value_scenarios.keys()))
            logger.info(
                f"[FinancialModelAgent] No 'Base' scenario found, using '{base_scenario_name}' for primary metrics"
            )

        # Primary metrics (for display/summary purposes)
        primary_net_value = base_scenario_value - total_cost
        metrics["primary_net_value"] = round(primary_net_value, 2)

        if total_cost > 0:
            primary_roi = (primary_net_value / total_cost) * 100
            metrics["primary_roi_percentage"] = round(primary_roi, 2)
        else:
            metrics["primary_roi_percentage"] = "N/A (zero cost)"

        # Payback period (V1 placeholder - would need cash flow projections for accurate calculation)
        if base_scenario_value > 0:
            # Simple payback period assuming value is annual benefit
            simple_payback_years = total_cost / base_scenario_value
            metrics["simple_payback_period_years"] = round(simple_payback_years, 2)
            metrics["payback_period_note"] = (
                "Simplified calculation assuming annual benefits equal to projected value"
            )
        else:
            metrics["simple_payback_period_years"] = "N/A"
            metrics["payback_period_note"] = (
                "Cannot calculate: zero or negative projected value"
            )

        return metrics

    def get_status(self) -> Dict[str, str]:
        """
        Returns the current status of the Financial Model Agent.

        Returns:
            Dict[str, str]: Status information
        """
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status,
        }
