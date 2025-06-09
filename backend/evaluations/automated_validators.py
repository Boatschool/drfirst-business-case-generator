"""
Automated Metric Validators for DrFirst Business Case Generator AI Agents

This module provides validation functions for automated metrics defined in EVAL-1.2.
Currently supports ProductManagerAgent and PlannerAgent validation.

Author: AI/ML Evaluation Specialist
Task: EVAL-2.1 - Implement Automated Metric Validators
"""

import logging
import re
from typing import Dict, Any, List, Optional
import json
import markdown
from jsonschema import validate, ValidationError, Draft7Validator

# Configure logging
logger = logging.getLogger(__name__)


def validate_prd_structural_completeness(markdown_text: str) -> bool:
    """
    Validates that a ProductManagerAgent PRD output contains all required sections.
    
    Args:
        markdown_text (str): The Markdown text output from ProductManagerAgent
        
    Returns:
        bool: True if all required sections are present, False otherwise
        
    Based on evaluation_metrics_definition.md and golden_datasets_v1.json requirements.
    """
    # Define standard required sections for PRD
    required_sections = [
        "Introduction",
        "Problem Statement", 
        "Goals",
        "Key Features",
        "Technical Requirements",
        "Acceptance Criteria"
    ]
    
    logger.info(f"Validating PRD structural completeness for {len(required_sections)} required sections")
    
    missing_sections = []
    
    for section in required_sections:
        # Check for section headers in various formats:
        # ## Section Name, # Section Name, ### Section Name, etc.
        # Use case-insensitive matching
        pattern = rf'^#+\s*{re.escape(section)}\s*$'
        if not re.search(pattern, markdown_text, re.MULTILINE | re.IGNORECASE):
            missing_sections.append(section)
    
    if missing_sections:
        logger.warning(f"PRD structural validation failed. Missing sections: {missing_sections}")
        return False
    
    logger.info("PRD structural validation passed - all required sections present")
    return True


def validate_markdown_syntax(markdown_text: str) -> bool:
    """
    Validates that the provided text is syntactically valid Markdown.
    
    Args:
        markdown_text (str): The Markdown text to validate
        
    Returns:
        bool: True if Markdown is syntactically valid, False otherwise
    """
    logger.info("Validating Markdown syntax")
    
    try:
        # Attempt to parse the markdown text
        md = markdown.Markdown(
            extensions=['extra', 'codehilite', 'toc'],
            extension_configs={}
        )
        
        # Convert to HTML - if this succeeds without exception, markdown is valid
        html_output = md.convert(markdown_text)
        
        # Basic sanity check - ensure we got some HTML output
        if not html_output or html_output.strip() == "":
            logger.warning("Markdown validation failed - no HTML output generated")
            return False
            
        logger.info("Markdown syntax validation passed")
        return True
        
    except Exception as e:
        logger.error(f"Markdown validation failed with error: {str(e)}")
        return False


def validate_planner_output_schema(planner_output: Dict[str, Any]) -> bool:
    """
    Validates that PlannerAgent output conforms to the expected JSON schema.
    
    Args:
        planner_output (Dict[str, Any]): The JSON output from PlannerAgent
        
    Returns:
        bool: True if output conforms to schema, False otherwise
        
    Expected schema based on evaluation_metrics_definition.md:
    - roles: array of objects with 'role' (string) and 'hours' (number)
    - total_hours: number
    - estimated_duration_weeks: number
    - complexity_assessment: string
    - notes: string
    """
    logger.info("Validating PlannerAgent output schema")
    
    # Define the expected JSON schema
    schema = {
        "type": "object",
        "properties": {
            "roles": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "role": {"type": "string"},
                        "hours": {"type": "number", "minimum": 0}
                    },
                    "required": ["role", "hours"],
                    "additionalProperties": True
                },
                "minItems": 1
            },
            "total_hours": {
                "type": "number",
                "minimum": 0
            },
            "estimated_duration_weeks": {
                "type": "number", 
                "minimum": 0
            },
            "complexity_assessment": {
                "type": "string",
                "minLength": 1
            },
            "notes": {
                "type": "string"
            }
        },
        "required": ["roles", "total_hours", "estimated_duration_weeks", "complexity_assessment", "notes"],
        "additionalProperties": True
    }
    
    try:
        # Validate the planner output against the schema
        validate(instance=planner_output, schema=schema)
        
        # Additional business logic validation
        # Verify that total_hours matches sum of role hours (with tolerance for floating point)
        calculated_total = sum(role.get('hours', 0) for role in planner_output.get('roles', []))
        reported_total = planner_output.get('total_hours', 0)
        
        # Allow small floating point differences (within 0.1 hours)
        if abs(calculated_total - reported_total) > 0.1:
            logger.error(f"Total hours mismatch: calculated={calculated_total}, reported={reported_total}")
            return False
        
        logger.info("PlannerAgent schema validation passed")
        return True
        
    except ValidationError as e:
        logger.error(f"PlannerAgent schema validation failed: {e.message}")
        logger.error(f"Failed at path: {' -> '.join(str(p) for p in e.absolute_path)}")
        return False
    except Exception as e:
        logger.error(f"PlannerAgent validation failed with unexpected error: {str(e)}")
        return False


def get_prd_required_sections() -> List[str]:
    """
    Returns the list of required sections for PRD validation.
    Useful for testing and external reference.
    
    Returns:
        List[str]: List of required section names
    """
    return [
        "Introduction",
        "Problem Statement", 
        "Goals",
        "Key Features",
        "Technical Requirements",
        "Acceptance Criteria"
    ]


def get_planner_schema() -> Dict[str, Any]:
    """
    Returns the JSON schema used for PlannerAgent validation.
    Useful for testing and external reference.
    
    Returns:
        Dict[str, Any]: The JSON schema dictionary
    """
    return {
        "type": "object",
        "properties": {
            "roles": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "role": {"type": "string"},
                        "hours": {"type": "number", "minimum": 0}
                    },
                    "required": ["role", "hours"],
                    "additionalProperties": True
                },
                "minItems": 1
            },
            "total_hours": {
                "type": "number",
                "minimum": 0
            },
            "estimated_duration_weeks": {
                "type": "number", 
                "minimum": 0
            },
            "complexity_assessment": {
                "type": "string",
                "minLength": 1
            },
            "notes": {
                "type": "string"
            }
        },
        "required": ["roles", "total_hours", "estimated_duration_weeks", "complexity_assessment", "notes"],
        "additionalProperties": True
    }


def validate_all_automated_metrics(agent_name: str, output_data: Any, additional_data: Dict[str, Any] = None) -> Dict[str, bool]:
    """
    Convenience function to run all relevant automated validations for a given agent.
    
    Args:
        agent_name (str): Name of the agent (ProductManagerAgent, PlannerAgent, ArchitectAgent, etc.)
        output_data (Any): The agent's output data
        additional_data (Dict[str, Any], optional): Additional data needed for validation (e.g., rate cards, input data)
        
    Returns:
        Dict[str, bool]: Dictionary mapping metric names to validation results
    """
    results = {}
    additional_data = additional_data or {}
    
    if agent_name == "ProductManagerAgent":
        if isinstance(output_data, str):
            results["structural_completeness"] = validate_prd_structural_completeness(output_data)
            results["markdown_validity"] = validate_markdown_syntax(output_data)
        else:
            logger.error("ProductManagerAgent output must be a string (Markdown)")
            results["structural_completeness"] = False
            results["markdown_validity"] = False
            
    elif agent_name == "PlannerAgent":
        if isinstance(output_data, dict):
            results["json_output_validity"] = validate_planner_output_schema(output_data)
        else:
            logger.error("PlannerAgent output must be a dictionary (JSON)")
            results["json_output_validity"] = False
            
    elif agent_name == "ArchitectAgent":
        if isinstance(output_data, str):
            results["key_architectural_sections"] = validate_architect_key_sections(output_data)
        else:
            logger.error("ArchitectAgent output must be a string (Markdown)")
            results["key_architectural_sections"] = False
            
    elif agent_name == "CostAnalystAgent":
        if isinstance(output_data, dict):
            results["metadata_presence"] = validate_cost_analyst_metadata(output_data)
            
            # Calculation validation requires additional data
            if "effort_input" in additional_data and "mock_rate_card" in additional_data:
                results["calculation_correctness"] = validate_cost_analyst_calculations(
                    output_data, 
                    additional_data["effort_input"], 
                    additional_data["mock_rate_card"]
                )
            else:
                logger.warning("CostAnalyst calculation validation skipped - missing effort_input or mock_rate_card")
                results["calculation_correctness"] = None
        else:
            logger.error("CostAnalystAgent output must be a dictionary (JSON)")
            results["metadata_presence"] = False
            results["calculation_correctness"] = False
            
    elif agent_name == "SalesValueAnalystAgent":
        if isinstance(output_data, dict):
            results["scenario_presence"] = validate_sales_value_scenario_presence(output_data)
            results["json_output_validity"] = validate_sales_value_output_schema(output_data)
        else:
            logger.error("SalesValueAnalystAgent output must be a dictionary (JSON)")
            results["scenario_presence"] = False
            results["json_output_validity"] = False
            
    elif agent_name == "FinancialModelAgent":
        if isinstance(output_data, dict):
            results["key_figures_presence"] = validate_financial_model_key_figures(output_data)
            
            # Calculation validation requires additional data
            if "cost_input" in additional_data and "base_value_input" in additional_data:
                results["calculation_correctness"] = validate_financial_model_calculations(
                    output_data,
                    additional_data["cost_input"],
                    additional_data["base_value_input"]
                )
            else:
                logger.warning("FinancialModel calculation validation skipped - missing cost_input or base_value_input")
                results["calculation_correctness"] = None
        else:
            logger.error("FinancialModelAgent output must be a dictionary (JSON)")
            results["key_figures_presence"] = False
            results["calculation_correctness"] = False
    else:
        logger.warning(f"Unknown agent name: {agent_name}")
    
    return results


def validate_architect_key_sections(markdown_text: str) -> bool:
    """
    Validates that ArchitectAgent output contains key architectural sections.
    
    Args:
        markdown_text (str): The Markdown text output from ArchitectAgent
        
    Returns:
        bool: True if at least 4 out of 6 key architectural components are present, False otherwise
        
    Based on evaluation_metrics_definition.md: Data Storage, API Design, Frontend Architecture, 
    Backend Services, Security, Integration Points
    """
    logger.info("Validating ArchitectAgent key architectural sections")
    
    # Define key architectural components to check for
    key_components = [
        "Data Storage",
        "API Design", 
        "Frontend Architecture",
        "Backend Services",
        "Security",
        "Integration Points"
    ]
    
    # Also check for alternative phrasings
    alternative_patterns = {
        "Data Storage": ["database", "data store", "storage", "persistence"],
        "API Design": ["api", "rest", "endpoint", "interface"],
        "Frontend Architecture": ["frontend", "front-end", "ui", "user interface", "client"],
        "Backend Services": ["backend", "back-end", "server", "service"],
        "Security": ["security", "authentication", "authorization", "encryption"],
        "Integration Points": ["integration", "connector", "interface", "interoperability"]
    }
    
    found_components = []
    
    for component in key_components:
        # Check for exact section header match
        pattern = rf'^#+\s*{re.escape(component)}\s*$'
        if re.search(pattern, markdown_text, re.MULTILINE | re.IGNORECASE):
            found_components.append(component)
            continue
            
        # Check for alternative keywords in content
        component_found = False
        for alt_pattern in alternative_patterns.get(component, []):
            if re.search(rf'\b{re.escape(alt_pattern)}\b', markdown_text, re.IGNORECASE):
                found_components.append(component)
                component_found = True
                break
        
        if component_found:
            continue
    
    # Remove duplicates while preserving order
    found_components = list(dict.fromkeys(found_components))
    missing_components = [comp for comp in key_components if comp not in found_components]
    
    # Success criteria: 4+ out of 6 components
    success = len(found_components) >= 4
    
    if success:
        logger.info(f"ArchitectAgent validation passed - found {len(found_components)}/6 components: {found_components}")
    else:
        logger.warning(f"ArchitectAgent validation failed - found only {len(found_components)}/6 components. Missing: {missing_components}")
    
    return success


def validate_cost_analyst_calculations(cost_output: Dict[str, Any], effort_input: Dict[str, Any], mock_rate_card: Dict[str, float]) -> bool:
    """
    Validates mathematical accuracy of CostAnalystAgent cost calculations.
    
    Args:
        cost_output (Dict[str, Any]): Output from CostAnalystAgent
        effort_input (Dict[str, Any]): The effort breakdown input
        mock_rate_card (Dict[str, float]): Rate card with role hourly rates
        
    Returns:
        bool: True if calculations are mathematically correct, False otherwise
    """
    logger.info("Validating CostAnalyst calculation correctness")
    
    try:
        # Calculate expected total cost
        expected_total = 0.0
        role_calculations = {}
        
        for role_data in effort_input.get('roles', []):
            role = role_data.get('role')
            hours = role_data.get('hours', 0)
            
            if role in mock_rate_card:
                role_cost = hours * mock_rate_card[role]
                role_calculations[role] = role_cost
                expected_total += role_cost
                logger.info(f"Expected calculation: {role} = {hours} hours × ${mock_rate_card[role]} = ${role_cost}")
            else:
                logger.warning(f"Role '{role}' not found in rate card")
        
        # Get actual calculated cost from output
        actual_cost = cost_output.get('cost_estimate', {}).get('estimated_cost')
        if actual_cost is None:
            # Try alternative path
            actual_cost = cost_output.get('estimated_cost')
        
        if actual_cost is None:
            logger.error("Could not find estimated_cost in cost output")
            return False
        
        # Compare with tolerance for floating point precision
        tolerance = 0.01
        cost_difference = abs(expected_total - actual_cost)
        
        if cost_difference <= tolerance:
            logger.info(f"CostAnalyst calculation validation passed: expected=${expected_total:.2f}, actual=${actual_cost:.2f}")
            return True
        else:
            logger.error(f"CostAnalyst calculation validation failed: expected=${expected_total:.2f}, actual=${actual_cost:.2f}, difference=${cost_difference:.2f}")
            return False
            
    except Exception as e:
        logger.error(f"CostAnalyst calculation validation failed with error: {str(e)}")
        return False


def validate_cost_analyst_metadata(cost_output: Dict[str, Any]) -> bool:
    """
    Validates presence and format of required metadata fields in CostAnalystAgent output.
    
    Args:
        cost_output (Dict[str, Any]): Output from CostAnalystAgent
        
    Returns:
        bool: True if all required metadata fields are present and valid, False otherwise
    """
    logger.info("Validating CostAnalyst metadata presence")
    
    # Required fields based on evaluation_metrics_definition.md
    required_fields = ["currency", "rate_card_used", "estimated_cost", "role_costs"]
    
    missing_fields = []
    invalid_fields = []
    
    # Check if cost_estimate wrapper exists
    cost_estimate = cost_output.get('cost_estimate', cost_output)
    
    for field in required_fields:
        if field not in cost_estimate:
            missing_fields.append(field)
            continue
        
        value = cost_estimate[field]
        
        # Type validation
        if field == "currency" and not isinstance(value, str):
            invalid_fields.append(f"{field} (should be string, got {type(value).__name__})")
        elif field == "rate_card_used" and not isinstance(value, str):
            invalid_fields.append(f"{field} (should be string, got {type(value).__name__})")
        elif field == "estimated_cost" and not isinstance(value, (int, float)):
            invalid_fields.append(f"{field} (should be number, got {type(value).__name__})")
        elif field == "role_costs" and not isinstance(value, list):
            invalid_fields.append(f"{field} (should be array, got {type(value).__name__})")
    
    if missing_fields or invalid_fields:
        if missing_fields:
            logger.error(f"CostAnalyst metadata validation failed - missing fields: {missing_fields}")
        if invalid_fields:
            logger.error(f"CostAnalyst metadata validation failed - invalid field types: {invalid_fields}")
        return False
    
    logger.info("CostAnalyst metadata validation passed - all required fields present and valid")
    return True


def validate_sales_value_scenario_presence(value_output: Dict[str, Any]) -> bool:
    """
    Validates that SalesValueAnalystAgent output contains expected value scenarios.
    
    Args:
        value_output (Dict[str, Any]): Output from SalesValueAnalystAgent
        
    Returns:
        bool: True if expected scenarios (Low, Base, High) are present, False otherwise
    """
    logger.info("Validating SalesValueAnalyst scenario presence")
    
    expected_scenarios = ["Low", "Base", "High"]
    
    # Get scenarios from value_projection or direct scenarios
    scenarios_data = value_output.get('value_projection', {}).get('scenarios', [])
    if not scenarios_data:
        scenarios_data = value_output.get('scenarios', [])
    
    if not scenarios_data:
        logger.error("SalesValueAnalyst validation failed - no scenarios found in output")
        return False
    
    # Extract scenario names/cases
    found_scenarios = []
    for scenario in scenarios_data:
        if isinstance(scenario, dict):
            scenario_name = scenario.get('case', scenario.get('scenario', scenario.get('name')))
            if scenario_name:
                found_scenarios.append(scenario_name)
    
    missing_scenarios = [s for s in expected_scenarios if s not in found_scenarios]
    
    if missing_scenarios:
        logger.error(f"SalesValueAnalyst scenario validation failed - missing scenarios: {missing_scenarios}")
        logger.error(f"Found scenarios: {found_scenarios}")
        return False
    
    logger.info(f"SalesValueAnalyst scenario validation passed - found all required scenarios: {found_scenarios}")
    return True


def validate_sales_value_output_schema(value_output: Dict[str, Any]) -> bool:
    """
    Validates that SalesValueAnalystAgent output conforms to expected JSON schema.
    
    Args:
        value_output (Dict[str, Any]): Output from SalesValueAnalystAgent
        
    Returns:
        bool: True if output conforms to schema, False otherwise
    """
    logger.info("Validating SalesValueAnalyst output schema")
    
    # Define expected schema based on evaluation_metrics_definition.md
    schema = {
        "type": "object",
        "properties": {
            "value_projection": {
                "type": "object",
                "properties": {
                    "scenarios": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "case": {"type": "string"},
                                "value": {"type": "number", "minimum": 0}
                            },
                            "required": ["case", "value"],
                            "additionalProperties": True
                        },
                        "minItems": 1
                    },
                    "methodology": {
                        "type": "string",
                        "minLength": 1
                    },
                    "assumptions": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "market_factors": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["scenarios", "methodology", "assumptions", "market_factors"],
                "additionalProperties": True
            }
        },
        "required": ["value_projection"],
        "additionalProperties": True
    }
    
    try:
        validate(instance=value_output, schema=schema)
        logger.info("SalesValueAnalyst schema validation passed")
        return True
        
    except ValidationError as e:
        logger.error(f"SalesValueAnalyst schema validation failed: {e.message}")
        logger.error(f"Failed at path: {' -> '.join(str(p) for p in e.absolute_path)}")
        return False
    except Exception as e:
        logger.error(f"SalesValueAnalyst validation failed with unexpected error: {str(e)}")
        return False


def validate_financial_model_calculations(financial_summary: Dict[str, Any], cost_input: float, base_value_input: float) -> bool:
    """
    Validates mathematical accuracy of FinancialModelAgent calculations.
    
    Args:
        financial_summary (Dict[str, Any]): Output from FinancialModelAgent
        cost_input (float): Total estimated cost input
        base_value_input (float): Base projected value input
        
    Returns:
        bool: True if calculations are mathematically correct, False otherwise
    """
    logger.info("Validating FinancialModel calculation correctness")
    
    try:
        # Calculate expected values
        expected_net_value = base_value_input - cost_input
        expected_roi = (expected_net_value / cost_input * 100) if cost_input != 0 else 0
        
        # Get actual values from financial summary
        financial_metrics = financial_summary.get('financial_metrics', {})
        
        actual_net_value = financial_metrics.get('net_value_base', financial_metrics.get('net_value'))
        actual_roi = financial_metrics.get('roi_base_percentage', financial_metrics.get('roi_percentage'))
        
        if actual_net_value is None or actual_roi is None:
            logger.error("Could not find net_value or roi_percentage in financial metrics")
            return False
        
        # Compare with tolerance for floating point precision
        tolerance = 0.01
        net_value_diff = abs(expected_net_value - actual_net_value)
        roi_diff = abs(expected_roi - actual_roi)
        
        if net_value_diff <= tolerance and roi_diff <= tolerance:
            logger.info(f"FinancialModel calculation validation passed:")
            logger.info(f"  Net Value: expected=${expected_net_value:.2f}, actual=${actual_net_value:.2f}")
            logger.info(f"  ROI: expected={expected_roi:.2f}%, actual={actual_roi:.2f}%")
            return True
        else:
            logger.error(f"FinancialModel calculation validation failed:")
            logger.error(f"  Net Value: expected=${expected_net_value:.2f}, actual=${actual_net_value:.2f}, diff=${net_value_diff:.2f}")
            logger.error(f"  ROI: expected={expected_roi:.2f}%, actual={actual_roi:.2f}%, diff={roi_diff:.2f}")
            return False
            
    except Exception as e:
        logger.error(f"FinancialModel calculation validation failed with error: {str(e)}")
        return False


def validate_financial_model_key_figures(financial_summary: Dict[str, Any]) -> bool:
    """
    Validates presence of key figures in FinancialModelAgent output.
    
    Args:
        financial_summary (Dict[str, Any]): Output from FinancialModelAgent
        
    Returns:
        bool: True if all required key figures are present, False otherwise
    """
    logger.info("Validating FinancialModel key figures presence")
    
    # Required fields based on evaluation_metrics_definition.md
    required_fields = ["total_estimated_cost", "currency", "value_scenarios", "financial_metrics"]
    
    missing_fields = []
    invalid_fields = []
    
    for field in required_fields:
        if field not in financial_summary:
            missing_fields.append(field)
            continue
        
        value = financial_summary[field]
        
        # Type validation
        if field == "total_estimated_cost" and not isinstance(value, (int, float)):
            invalid_fields.append(f"{field} (should be number, got {type(value).__name__})")
        elif field == "currency" and not isinstance(value, str):
            invalid_fields.append(f"{field} (should be string, got {type(value).__name__})")
        elif field == "value_scenarios" and not isinstance(value, list):
            invalid_fields.append(f"{field} (should be array, got {type(value).__name__})")
        elif field == "financial_metrics" and not isinstance(value, dict):
            invalid_fields.append(f"{field} (should be object, got {type(value).__name__})")
    
    # Check for ROI calculations in financial_metrics
    if "financial_metrics" in financial_summary:
        metrics = financial_summary["financial_metrics"]
        roi_fields = ["roi_low_percentage", "roi_base_percentage", "roi_high_percentage"]
        found_roi_fields = [f for f in roi_fields if f in metrics]
        
        if not found_roi_fields:
            # Check for alternative ROI field names
            alt_roi_fields = ["roi_percentage", "roi", "return_on_investment"]
            found_alt_roi = [f for f in alt_roi_fields if f in metrics]
            if not found_alt_roi:
                missing_fields.append("ROI calculations in financial_metrics")
    
    if missing_fields or invalid_fields:
        if missing_fields:
            logger.error(f"FinancialModel key figures validation failed - missing fields: {missing_fields}")
        if invalid_fields:
            logger.error(f"FinancialModel key figures validation failed - invalid field types: {invalid_fields}")
        return False
    
    logger.info("FinancialModel key figures validation passed - all required fields present and valid")
    return True


if __name__ == "__main__":
    # Basic test examples
    logging.basicConfig(level=logging.INFO)
    
    # Test PRD validation with valid example
    valid_prd = """
# Patient Portal Mobile App

## Introduction
This project aims to develop a mobile application for patient access.

## Problem Statement  
Patients struggle to access their medical records.

## Goals
- Provide mobile access to medical records
- Enable secure communication with providers

## Key Features
- Secure login with biometrics
- View lab results and medical history

## Technical Requirements
- React Native for mobile development
- HIPAA compliance required

## Acceptance Criteria
- Users can log in securely
- Medical records display correctly
"""
    
    print("Testing valid PRD:")
    print(f"Structural completeness: {validate_prd_structural_completeness(valid_prd)}")
    print(f"Markdown validity: {validate_markdown_syntax(valid_prd)}")
    
    # Test PlannerAgent validation with valid example
    valid_planner_output = {
        "roles": [
            {"role": "Product Manager", "hours": 40},
            {"role": "Senior Developer", "hours": 120},
            {"role": "QA Engineer", "hours": 60}
        ],
        "total_hours": 220,
        "estimated_duration_weeks": 8,
        "complexity_assessment": "Medium complexity due to mobile development and healthcare compliance",
        "notes": "Estimates include time for HIPAA compliance review and security testing"
    }
    
    print(f"\nTesting valid PlannerAgent output:")
    print(f"JSON schema validity: {validate_planner_output_schema(valid_planner_output)}")
    
    # Test new validators
    print("\nTesting new validators:")
    
    # Test ArchitectAgent
    architect_text = """
# System Architecture

## Frontend Architecture
React Native mobile application with offline capabilities.

## Backend Services  
Node.js microservices architecture with containerization.

## Data Storage
PostgreSQL primary database with Redis caching layer.

## API Design
RESTful APIs with OAuth2 authentication and rate limiting.

## Security
End-to-end encryption, HIPAA compliance, audit logging.

## Integration Points
EHR systems integration via FHIR APIs.
"""
    print(f"ArchitectAgent key sections: {validate_architect_key_sections(architect_text)}")
    
    # Test CostAnalystAgent
    cost_output = {"cost_estimate": {"estimated_cost": 37600, "currency": "USD", "rate_card_used": "Standard", "role_costs": []}}
    effort_input = {"roles": [{"role": "Product Manager", "hours": 40}, {"role": "Senior Developer", "hours": 120}]}
    mock_rate_card = {"Product Manager": 150, "Senior Developer": 120}
    print(f"CostAnalyst calculations: {validate_cost_analyst_calculations(cost_output, effort_input, mock_rate_card)}")
    print(f"CostAnalyst metadata: {validate_cost_analyst_metadata(cost_output)}")
    
    # Test SalesValueAnalystAgent
    value_output = {
        "value_projection": {
            "scenarios": [{"case": "Low", "value": 50000}, {"case": "Base", "value": 100000}, {"case": "High", "value": 200000}],
            "methodology": "Bottom-up analysis", 
            "assumptions": ["10,000 users"],
            "market_factors": ["Healthcare digitization"]
        }
    }
    print(f"SalesValueAnalyst scenarios: {validate_sales_value_scenario_presence(value_output)}")
    print(f"SalesValueAnalyst schema: {validate_sales_value_output_schema(value_output)}")
    
    # Test FinancialModelAgent
    financial_summary = {
        "total_estimated_cost": 50000,
        "currency": "USD", 
        "value_scenarios": [{"case": "Base", "value": 150000}],
        "financial_metrics": {"net_value_base": 100000, "roi_base_percentage": 200.0}
    }
    print(f"FinancialModel calculations: {validate_financial_model_calculations(financial_summary, 50000, 150000)}")
    print(f"FinancialModel key figures: {validate_financial_model_key_figures(financial_summary)}") 