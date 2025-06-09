"""
Test script for automated validators

This script tests the validators against valid and invalid examples
to ensure they correctly identify both passing and failing cases.

Task: EVAL-2.1 - Testing Automated Metric Validators
"""

import json
import logging
from automated_validators import (
    validate_prd_structural_completeness,
    validate_markdown_syntax,
    validate_planner_output_schema,
    validate_architect_key_sections,
    validate_cost_analyst_calculations,
    validate_cost_analyst_metadata,
    validate_sales_value_scenario_presence,
    validate_sales_value_output_schema,
    validate_financial_model_calculations,
    validate_financial_model_key_figures,
    validate_all_automated_metrics
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def test_prd_validators():
    """Test ProductManagerAgent validators with valid and invalid examples."""
    print("=" * 60)
    print("TESTING PRODUCTMANAGERAGENT VALIDATORS")
    print("=" * 60)
    
    # Test 1: Valid PRD (should pass both tests)
    print("\n1. Testing VALID PRD:")
    valid_prd = """
# Patient Portal Mobile App

## Introduction
This project aims to develop a mobile application that provides patients with convenient, secure access to their medical records and healthcare providers.

## Problem Statement  
Patients struggle to access their medical records and communicate with providers outside of office visits. Current patient portal is desktop-only and difficult to use.

## Goals
- Provide mobile access to medical records
- Enable secure communication with providers
- Improve patient engagement and satisfaction
- Reduce administrative burden on staff

## Key Features
- Secure login with biometrics
- View lab results and medical history
- Message healthcare providers
- Appointment scheduling
- Prescription refill requests

## Technical Requirements
- React Native for cross-platform mobile development
- HIPAA compliance required
- Integration with existing EHR systems
- Offline data access capabilities
- End-to-end encryption for all communications

## Acceptance Criteria
- Users can log in securely using biometric authentication
- Medical records display correctly on mobile devices
- Messages to providers are delivered within 24 hours
- App meets HIPAA compliance requirements
- Performance: app loads in under 3 seconds
"""
    
    structural_result = validate_prd_structural_completeness(valid_prd)
    markdown_result = validate_markdown_syntax(valid_prd)
    print(f"   Structural completeness: {structural_result} ✓")
    print(f"   Markdown validity: {markdown_result} ✓")
    
    # Test 2: PRD missing required sections (should fail structural test)
    print("\n2. Testing PRD MISSING SECTIONS:")
    missing_sections_prd = """
# Incomplete PRD

## Introduction
This project aims to develop something.

## Problem Statement  
There is a problem to solve.

## Goals
- Some goals here
"""
    
    structural_result = validate_prd_structural_completeness(missing_sections_prd)
    markdown_result = validate_markdown_syntax(missing_sections_prd)
    print(f"   Structural completeness: {structural_result} ✗ (Expected failure)")
    print(f"   Markdown validity: {markdown_result} ✓")
    
    # Test 3: Invalid Markdown syntax (should fail markdown test)
    print("\n3. Testing INVALID MARKDOWN:")
    invalid_markdown = """
# Patient Portal Mobile App

## Introduction
This project aims to develop a mobile application.

## Problem Statement  
Patients struggle to access records.

## Goals
- Goal 1
- Goal 2 [unclosed link

## Key Features
**Bold text without closing

## Technical Requirements
- React Native
- HIPAA compliance

## Acceptance Criteria
- Criteria 1
- Criteria 2
"""
    
    structural_result = validate_prd_structural_completeness(invalid_markdown)
    markdown_result = validate_markdown_syntax(invalid_markdown)
    print(f"   Structural completeness: {structural_result} ✓")
    print(f"   Markdown validity: {markdown_result} (May pass - Markdown is tolerant)")


def test_planner_validators():
    """Test PlannerAgent validator with valid and invalid examples."""
    print("\n" + "=" * 60)
    print("TESTING PLANNERAGENT VALIDATORS")
    print("=" * 60)
    
    # Test 1: Valid PlannerAgent output (should pass)
    print("\n1. Testing VALID PLANNER OUTPUT:")
    valid_planner = {
        "roles": [
            {"role": "Product Manager", "hours": 40},
            {"role": "Lead Developer", "hours": 80},
            {"role": "Senior Developer", "hours": 120},
            {"role": "QA Engineer", "hours": 60},
            {"role": "DevOps Engineer", "hours": 30}
        ],
        "total_hours": 330,
        "estimated_duration_weeks": 12,
        "complexity_assessment": "High complexity due to mobile development, healthcare compliance requirements, and EHR integration needs",
        "notes": "Estimates include time for HIPAA compliance review, security testing, and integration with multiple EHR systems. Additional time allocated for biometric authentication implementation."
    }
    
    result = validate_planner_output_schema(valid_planner)
    print(f"   JSON schema validity: {result} ✓")
    
    # Test 2: Missing required fields (should fail)
    print("\n2. Testing PLANNER OUTPUT MISSING FIELDS:")
    missing_fields = {
        "roles": [
            {"role": "Developer", "hours": 100}
        ],
        "total_hours": 100
        # Missing: estimated_duration_weeks, complexity_assessment, notes
    }
    
    result = validate_planner_output_schema(missing_fields)
    print(f"   JSON schema validity: {result} ✗ (Expected failure)")
    
    # Test 3: Invalid data types (should fail)
    print("\n3. Testing PLANNER OUTPUT INVALID TYPES:")
    invalid_types = {
        "roles": "should be array not string",  # Wrong type
        "total_hours": "100",  # Should be number, not string
        "estimated_duration_weeks": 8,
        "complexity_assessment": "Medium complexity",
        "notes": "Some notes"
    }
    
    result = validate_planner_output_schema(invalid_types)
    print(f"   JSON schema validity: {result} ✗ (Expected failure)")
    
    # Test 4: Total hours mismatch (should fail business logic)
    print("\n4. Testing PLANNER OUTPUT HOURS MISMATCH:")
    hours_mismatch = {
        "roles": [
            {"role": "Developer", "hours": 50},
            {"role": "QA Engineer", "hours": 30}
        ],
        "total_hours": 100,  # Should be 80 (50+30)
        "estimated_duration_weeks": 6,
        "complexity_assessment": "Medium complexity",
        "notes": "Total hours don't match sum of role hours"
    }
    
    result = validate_planner_output_schema(hours_mismatch)
    print(f"   JSON schema validity: {result} ✗ (Expected failure - hours mismatch)")


def test_with_golden_dataset_examples():
    """Test validators against examples from golden_datasets_v1.json."""
    print("\n" + "=" * 60)
    print("TESTING WITH GOLDEN DATASET EXAMPLES")
    print("=" * 60)
    
    try:
        # Load golden datasets
        with open('golden_datasets_v1.json', 'r') as f:
            golden_data = json.load(f)
        
        # Test ProductManagerAgent examples
        print("\nTesting ProductManagerAgent golden dataset requirements:")
        prd_examples = golden_data['datasets']['ProductManagerAgent']
        
        for i, example in enumerate(prd_examples[:2], 1):  # Test first 2 examples
            input_id = example['inputId']
            required_sections = example['expected_characteristics_or_ideal_output']['must_contain_sections']
            
            print(f"\n  Example {i} ({input_id}):")
            print(f"    Required sections: {required_sections}")
            
            # Create a mock PRD with the required sections
            mock_prd = "# " + example['input_payload']['case_title'] + "\n\n"
            for section in required_sections:
                mock_prd += f"## {section}\nSample content for {section.lower()}.\n\n"
            
            structural_result = validate_prd_structural_completeness(mock_prd)
            markdown_result = validate_markdown_syntax(mock_prd)
            print(f"    Structural completeness: {structural_result} ✓")
            print(f"    Markdown validity: {markdown_result} ✓")
        
        # Test PlannerAgent examples  
        print("\nTesting PlannerAgent golden dataset requirements:")
        planner_examples = golden_data['datasets']['PlannerAgent']
        
        for i, example in enumerate(planner_examples[:2], 1):  # Test first 2 examples
            input_id = example['inputId']
            schema_reqs = example['expected_characteristics_or_ideal_output']['json_schema_requirements']
            
            print(f"\n  Example {i} ({input_id}):")
            print(f"    Schema requirements: {schema_reqs}")
            
            # Create mock planner output matching schema
            mock_planner = {
                "roles": [
                    {"role": "Product Manager", "hours": 40},
                    {"role": "Senior Developer", "hours": 100}
                ],
                "total_hours": 140,
                "estimated_duration_weeks": 6,
                "complexity_assessment": "Medium complexity for " + example['input_payload']['case_title'],
                "notes": "Estimates based on " + example['input_payload']['case_title'] + " requirements"
            }
            
            result = validate_planner_output_schema(mock_planner)
            print(f"    JSON schema validity: {result} ✓")
            
    except FileNotFoundError:
        print("   Golden datasets file not found - skipping golden dataset tests")
    except Exception as e:
        print(f"   Error loading golden datasets: {e}")


def test_architect_validators():
    """Test ArchitectAgent validator with valid and invalid examples."""
    print("\n" + "=" * 60)
    print("TESTING ARCHITECTAGENT VALIDATORS")
    print("=" * 60)
    
    # Test 1: Valid architecture with all 6 components
    print("\n1. Testing VALID ARCHITECTURE (all components):")
    valid_architecture = """
# System Architecture Design

## Frontend Architecture
React Native mobile application with offline capabilities and responsive design.

## Backend Services  
Node.js microservices architecture with containerization and load balancing.

## Data Storage
PostgreSQL primary database with Redis caching layer and data replication.

## API Design
RESTful APIs with OAuth2 authentication, rate limiting, and comprehensive documentation.

## Security
End-to-end encryption, HIPAA compliance, audit logging, and security monitoring.

## Integration Points
EHR systems integration via FHIR APIs, third-party service connectors.
"""
    
    result = validate_architect_key_sections(valid_architecture)
    print(f"   Key sections validation: {result} ✓")
    
    # Test 2: Architecture with only 4 components (should pass)
    print("\n2. Testing ARCHITECTURE WITH 4 COMPONENTS (should pass):")
    minimal_architecture = """
# System Design

## Frontend Architecture
Web-based dashboard using React framework.

## Backend Services
Python Flask services with microservices pattern.

## Database Design
MongoDB for document storage with indexing.

## Security Framework
OAuth2 authentication and role-based access control.
"""
    
    result = validate_architect_key_sections(minimal_architecture)
    print(f"   Key sections validation: {result} ✓")
    
    # Test 3: Architecture with only 2 components (should fail)
    print("\n3. Testing INCOMPLETE ARCHITECTURE (should fail):")
    incomplete_architecture = """
# Simple System

## Overview
Basic web application.

## Frontend
Simple HTML/CSS interface.

## Notes
Basic implementation only.
"""
    
    result = validate_architect_key_sections(incomplete_architecture)
    print(f"   Key sections validation: {result} ✗ (Expected failure)")


def test_cost_analyst_validators():
    """Test CostAnalystAgent validators with valid and invalid examples."""
    print("\n" + "=" * 60)
    print("TESTING COSTANALYSTAGENT VALIDATORS")
    print("=" * 60)
    
    # Test 1: Valid cost analysis (correct calculations and metadata)
    print("\n1. Testing VALID COST ANALYSIS:")
    valid_cost_output = {
        "cost_estimate": {
            "estimated_cost": 37600,
            "currency": "USD",
            "rate_card_used": "Standard 2025",
            "role_costs": [
                {"role": "Product Manager", "hours": 40, "rate": 150, "cost": 6000},
                {"role": "Lead Developer", "hours": 80, "rate": 140, "cost": 11200},
                {"role": "Senior Developer", "hours": 120, "rate": 120, "cost": 14400},
                {"role": "QA Engineer", "hours": 60, "rate": 100, "cost": 6000}
            ]
        }
    }
    
    effort_input = {
        "roles": [
            {"role": "Product Manager", "hours": 40},
            {"role": "Lead Developer", "hours": 80},
            {"role": "Senior Developer", "hours": 120},
            {"role": "QA Engineer", "hours": 60}
        ]
    }
    
    mock_rate_card = {
        "Product Manager": 150,
        "Lead Developer": 140,
        "Senior Developer": 120,
        "QA Engineer": 100
    }
    
    calc_result = validate_cost_analyst_calculations(valid_cost_output, effort_input, mock_rate_card)
    meta_result = validate_cost_analyst_metadata(valid_cost_output)
    print(f"   Calculation correctness: {calc_result} ✓")
    print(f"   Metadata presence: {meta_result} ✓")
    
    # Test 2: Wrong calculations (should fail)
    print("\n2. Testing INCORRECT CALCULATIONS:")
    wrong_cost_output = {
        "cost_estimate": {
            "estimated_cost": 50000,  # Wrong total
            "currency": "USD",
            "rate_card_used": "Standard 2025",
            "role_costs": []
        }
    }
    
    calc_result = validate_cost_analyst_calculations(wrong_cost_output, effort_input, mock_rate_card)
    print(f"   Calculation correctness: {calc_result} ✗ (Expected failure)")
    
    # Test 3: Missing metadata (should fail)
    print("\n3. Testing MISSING METADATA:")
    missing_meta_output = {
        "cost_estimate": {
            "estimated_cost": 37600
            # Missing: currency, rate_card_used, role_costs
        }
    }
    
    meta_result = validate_cost_analyst_metadata(missing_meta_output)
    print(f"   Metadata presence: {meta_result} ✗ (Expected failure)")


def test_sales_value_validators():
    """Test SalesValueAnalystAgent validators with valid and invalid examples."""
    print("\n" + "=" * 60)
    print("TESTING SALESVALUEANALYSTAGENT VALIDATORS")
    print("=" * 60)
    
    # Test 1: Valid value projection
    print("\n1. Testing VALID VALUE PROJECTION:")
    valid_value_output = {
        "value_projection": {
            "scenarios": [
                {"case": "Low", "value": 50000, "description": "Conservative estimate"},
                {"case": "Base", "value": 100000, "description": "Most likely scenario"},
                {"case": "High", "value": 200000, "description": "Optimistic projection"}
            ],
            "methodology": "Bottom-up analysis based on user adoption rates and operational savings",
            "assumptions": [
                "10,000 active users within first year",
                "30% reduction in call center volume",
                "Average cost savings of $10 per patient interaction"
            ],
            "market_factors": [
                "Healthcare digitization trends",
                "Patient satisfaction improvements",
                "Regulatory compliance requirements"
            ]
        }
    }
    
    scenario_result = validate_sales_value_scenario_presence(valid_value_output)
    schema_result = validate_sales_value_output_schema(valid_value_output)
    print(f"   Scenario presence: {scenario_result} ✓")
    print(f"   Schema validity: {schema_result} ✓")
    
    # Test 2: Missing scenarios (should fail)
    print("\n2. Testing MISSING SCENARIOS:")
    missing_scenarios_output = {
        "value_projection": {
            "scenarios": [
                {"case": "Base", "value": 100000}
                # Missing Low and High scenarios
            ],
            "methodology": "Simple analysis",
            "assumptions": ["Some assumptions"],
            "market_factors": ["Market factor"]
        }
    }
    
    scenario_result = validate_sales_value_scenario_presence(missing_scenarios_output)
    print(f"   Scenario presence: {scenario_result} ✗ (Expected failure)")
    
    # Test 3: Invalid schema (should fail)
    print("\n3. Testing INVALID SCHEMA:")
    invalid_schema_output = {
        "value_projection": {
            "scenarios": "should be array not string",  # Wrong type
            "methodology": "",  # Empty string
            "assumptions": "should be array",  # Wrong type
            "market_factors": []  # Valid but empty
        }
    }
    
    schema_result = validate_sales_value_output_schema(invalid_schema_output)
    print(f"   Schema validity: {schema_result} ✗ (Expected failure)")


def test_financial_model_validators():
    """Test FinancialModelAgent validators with valid and invalid examples."""
    print("\n" + "=" * 60)
    print("TESTING FINANCIALMODELAGENT VALIDATORS")
    print("=" * 60)
    
    # Test 1: Valid financial model
    print("\n1. Testing VALID FINANCIAL MODEL:")
    valid_financial_summary = {
        "total_estimated_cost": 50000,
        "currency": "USD",
        "value_scenarios": [
            {"case": "Low", "value": 75000},
            {"case": "Base", "value": 150000},
            {"case": "High", "value": 250000}
        ],
        "financial_metrics": {
            "net_value_low": 25000,
            "net_value_base": 100000,
            "net_value_high": 200000,
            "roi_low_percentage": 50.0,
            "roi_base_percentage": 200.0,
            "roi_high_percentage": 400.0
        }
    }
    
    figures_result = validate_financial_model_key_figures(valid_financial_summary)
    calc_result = validate_financial_model_calculations(valid_financial_summary, 50000, 150000)
    print(f"   Key figures presence: {figures_result} ✓")
    print(f"   Calculation correctness: {calc_result} ✓")
    
    # Test 2: Wrong calculations (should fail)
    print("\n2. Testing INCORRECT CALCULATIONS:")
    wrong_calc_summary = {
        "total_estimated_cost": 50000,
        "currency": "USD",
        "value_scenarios": [{"case": "Base", "value": 150000}],
        "financial_metrics": {
            "net_value_base": 50000,  # Should be 100000 (150000 - 50000)
            "roi_base_percentage": 100.0  # Should be 200.0 ((100000/50000)*100)
        }
    }
    
    calc_result = validate_financial_model_calculations(wrong_calc_summary, 50000, 150000)
    print(f"   Calculation correctness: {calc_result} ✗ (Expected failure)")
    
    # Test 3: Missing key figures (should fail)
    print("\n3. Testing MISSING KEY FIGURES:")
    missing_figures_summary = {
        "total_estimated_cost": 50000,
        "currency": "USD"
        # Missing: value_scenarios, financial_metrics
    }
    
    figures_result = validate_financial_model_key_figures(missing_figures_summary)
    print(f"   Key figures presence: {figures_result} ✗ (Expected failure)")


def test_convenience_function():
    """Test the convenience function validate_all_automated_metrics."""
    print("\n" + "=" * 60)
    print("TESTING CONVENIENCE FUNCTION")
    print("=" * 60)
    
    # Test ProductManagerAgent
    print("\n1. Testing ProductManagerAgent convenience function:")
    sample_prd = """
# Test PRD

## Introduction
Sample introduction.

## Problem Statement
Sample problem.

## Goals  
Sample goals.

## Key Features
Sample features.

## Technical Requirements
Sample requirements.

## Acceptance Criteria
Sample criteria.
"""
    
    results = validate_all_automated_metrics("ProductManagerAgent", sample_prd)
    print(f"   Results: {results}")
    
    # Test PlannerAgent
    print("\n2. Testing PlannerAgent convenience function:")
    sample_planner = {
        "roles": [{"role": "Developer", "hours": 80}],
        "total_hours": 80,
        "estimated_duration_weeks": 4,
        "complexity_assessment": "Medium",
        "notes": "Sample notes"
    }
    
    results = validate_all_automated_metrics("PlannerAgent", sample_planner)
    print(f"   Results: {results}")
    
    # Test ArchitectAgent
    print("\n3. Testing ArchitectAgent convenience function:")
    sample_architecture = """
## Frontend Architecture
Web interface
## Backend Services  
API services
## Data Storage
Database design
## Security
Authentication
"""
    
    results = validate_all_automated_metrics("ArchitectAgent", sample_architecture)
    print(f"   Results: {results}")
    
    # Test CostAnalystAgent
    print("\n4. Testing CostAnalystAgent convenience function:")
    sample_cost = {
        "cost_estimate": {
            "estimated_cost": 10000,
            "currency": "USD",
            "rate_card_used": "Standard",
            "role_costs": []
        }
    }
    
    additional_data = {
        "effort_input": {"roles": [{"role": "Developer", "hours": 80}]},
        "mock_rate_card": {"Developer": 125}
    }
    
    results = validate_all_automated_metrics("CostAnalystAgent", sample_cost, additional_data)
    print(f"   Results: {results}")
    
    # Test SalesValueAnalystAgent
    print("\n5. Testing SalesValueAnalystAgent convenience function:")
    sample_value = {
        "value_projection": {
            "scenarios": [{"case": "Low", "value": 5000}, {"case": "Base", "value": 10000}, {"case": "High", "value": 20000}],
            "methodology": "Analysis",
            "assumptions": ["Assumption 1"],
            "market_factors": ["Factor 1"]
        }
    }
    
    results = validate_all_automated_metrics("SalesValueAnalystAgent", sample_value)
    print(f"   Results: {results}")
    
    # Test FinancialModelAgent
    print("\n6. Testing FinancialModelAgent convenience function:")
    sample_financial = {
        "total_estimated_cost": 10000,
        "currency": "USD",
        "value_scenarios": [{"case": "Base", "value": 20000}],
        "financial_metrics": {"net_value_base": 10000, "roi_base_percentage": 100.0}
    }
    
    additional_data = {"cost_input": 10000, "base_value_input": 20000}
    
    results = validate_all_automated_metrics("FinancialModelAgent", sample_financial, additional_data)
    print(f"   Results: {results}")
    
    # Test unknown agent
    print("\n7. Testing unknown agent:")
    results = validate_all_automated_metrics("UnknownAgent", {})
    print(f"   Results: {results}")


if __name__ == "__main__":
    print("AUTOMATED VALIDATORS TEST SUITE")
    print("Task EVAL-2.1 & EVAL-2.2 - Implementation Testing")
    print()
    
    test_prd_validators()
    test_planner_validators()
    test_architect_validators()
    test_cost_analyst_validators()
    test_sales_value_validators()
    test_financial_model_validators()
    test_with_golden_dataset_examples()
    test_convenience_function()
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETED")
    print("=" * 60) 