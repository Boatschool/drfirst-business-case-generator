#!/usr/bin/env python3
"""
Evaluation Batch Preparation Script
Selects golden dataset examples and runs agents to prepare data for human evaluation.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EvaluationBatchPreparator:
    """Prepares evaluation batches from golden datasets"""
    
    def __init__(self, golden_datasets_path: str = "golden_datasets_v1.json"):
        self.golden_datasets_path = golden_datasets_path
        self.selected_examples = []
        self.evaluation_batch = []
        
    def load_golden_datasets(self) -> Dict[str, Any]:
        """Load golden datasets from JSON file"""
        try:
            with open(self.golden_datasets_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Golden datasets file not found: {self.golden_datasets_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in golden datasets: {e}")
            raise
    
    def select_examples_for_evaluation(self, datasets: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Select a diverse subset of examples for human evaluation.
        Focuses on LLM-based agents: ProductManager, Architect, Planner, SalesValueAnalyst
        """
        selected = []
        
        # Selection criteria: 2-3 examples per LLM-based agent
        selection_plan = {
            "ProductManagerAgent": 3,  # Simple, complex, and integration examples
            "ArchitectAgent": 2,       # Mobile and integration examples
            "PlannerAgent": 2,         # Mobile and integration examples  
            "SalesValueAnalystAgent": 2  # Mobile and integration examples
        }
        
        for agent_name, count in selection_plan.items():
            if agent_name in datasets["datasets"]:
                agent_examples = datasets["datasets"][agent_name]
                
                # Select diverse examples based on input complexity
                if agent_name == "ProductManagerAgent":
                    # Select simple, complex, and integration examples
                    selected_ids = ["prd_simple_001", "prd_complex_002", "prd_integration_004"]
                elif agent_name == "ArchitectAgent":
                    # Select mobile and integration examples
                    selected_ids = ["arch_mobile_001", "arch_integration_002"]
                elif agent_name == "PlannerAgent":
                    # Select mobile and integration examples
                    selected_ids = ["plan_mobile_001", "plan_integration_002"]
                elif agent_name == "SalesValueAnalystAgent":
                    # Select mobile and integration examples
                    selected_ids = ["value_mobile_001", "value_integration_002"]
                
                # Find examples by inputId
                for example in agent_examples:
                    if example["inputId"] in selected_ids:
                        selected.append(example)
                        logger.info(f"Selected {example['inputId']} from {agent_name}")
                        
                        if len([e for e in selected if e["agentName"] == agent_name]) >= count:
                            break
        
        logger.info(f"Selected {len(selected)} examples for evaluation")
        return selected
    
    def generate_eval_id(self, agent_name: str, input_id: str) -> str:
        """Generate unique evaluation ID"""
        timestamp = datetime.now().strftime("%Y%m%d")
        agent_short = agent_name.replace("Agent", "").upper()
        return f"EVAL_{timestamp}_{agent_short}_{input_id.upper()}"
    
    def create_input_summary(self, input_payload: Dict[str, Any]) -> str:
        """Create a concise summary of the input payload"""
        if "case_title" in input_payload:
            title = input_payload["case_title"]
            problem = input_payload.get("problem_statement", "")
            # Truncate problem statement to first 100 characters
            problem_short = problem[:100] + "..." if len(problem) > 100 else problem
            return f"{title} - {problem_short}"
        elif "prd_content" in input_payload:
            prd_content = input_payload["prd_content"]
            # Extract title from markdown or use first line
            lines = prd_content.split('\n')
            title_line = next((line for line in lines if line.startswith('#')), lines[0] if lines else "")
            title = title_line.replace('#', '').strip()
            return f"Architecture for: {title}"
        else:
            # Generic summary
            return str(input_payload)[:150] + "..." if len(str(input_payload)) > 150 else str(input_payload)
    
    def simulate_agent_run(self, example: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate running an agent and return mock output.
        In real implementation, this would call the actual agents.
        """
        agent_name = example["agentName"]
        input_id = example["inputId"]
        
        # Generate mock case_id and trace_id
        case_id = f"case_{uuid.uuid4().hex[:8]}"
        trace_id = f"trace_{uuid.uuid4().hex[:12]}"
        
        # Mock agent outputs (in real implementation, call actual agents)
        mock_outputs = {
            "ProductManagerAgent": self._mock_prd_output(example),
            "ArchitectAgent": self._mock_architecture_output(example),
            "PlannerAgent": self._mock_planning_output(example),
            "SalesValueAnalystAgent": self._mock_value_output(example)
        }
        
        agent_output = mock_outputs.get(agent_name, "Mock output not available")
        
        logger.info(f"Simulated agent run for {agent_name} - {input_id}")
        
        return {
            "case_id": case_id,
            "trace_id": trace_id,
            "agent_output": agent_output,
            "execution_timestamp": datetime.now().isoformat()
        }
    
    def _mock_prd_output(self, example: Dict[str, Any]) -> str:
        """Generate mock PRD output"""
        input_payload = example["input_payload"]
        title = input_payload.get("case_title", "Healthcare Solution")
        problem = input_payload.get("problem_statement", "Business problem to solve")
        
        return f"""# {title} - Product Requirements Document

## Introduction
This project aims to address the identified healthcare challenge through innovative technology solutions.

## Problem Statement
{problem}

## Goals
- Improve healthcare delivery efficiency
- Enhance patient experience and satisfaction
- Ensure regulatory compliance and data security
- Provide measurable business value

## Key Features
- User-friendly interface design
- Secure authentication and authorization
- Integration with existing healthcare systems
- Real-time data processing and analytics
- Comprehensive reporting capabilities

## Technical Requirements
- HIPAA-compliant data handling
- Cloud-based scalable architecture
- Mobile-responsive design
- API-first development approach
- Comprehensive security measures

## Acceptance Criteria
- All features function as specified
- Security audits pass successfully
- Performance meets defined benchmarks
- User testing demonstrates high satisfaction
- Regulatory compliance verified"""
    
    def _mock_architecture_output(self, example: Dict[str, Any]) -> str:
        """Generate mock architecture output"""
        return """# System Architecture Design

## Overview
This document outlines the technical architecture for the healthcare solution.

## Frontend Architecture
- React/React Native for cross-platform compatibility
- Redux for state management
- Responsive design for multiple devices
- Progressive Web App (PWA) capabilities

## Backend Services
- Node.js/Express API server
- Microservices architecture
- Docker containerization
- Kubernetes orchestration

## Data Storage
- PostgreSQL for relational data
- Redis for caching and sessions
- Encrypted storage for PHI data
- Automated backup and recovery

## Security Architecture
- OAuth 2.0 + OIDC authentication
- Role-based access control (RBAC)
- End-to-end encryption
- API rate limiting and monitoring

## Integration Points
- FHIR-compliant healthcare data exchange
- HL7 message processing
- Third-party EHR system integration
- Payment processing integration"""
    
    def _mock_planning_output(self, example: Dict[str, Any]) -> str:
        """Generate mock planning output"""
        return """{
  "roles": [
    {
      "role": "Product Manager",
      "hours": 40,
      "responsibilities": ["Requirements gathering", "Stakeholder coordination", "Project planning"]
    },
    {
      "role": "Lead Developer",
      "hours": 80,
      "responsibilities": ["Architecture design", "Code review", "Technical leadership"]
    },
    {
      "role": "Senior Developer",
      "hours": 160,
      "responsibilities": ["Feature development", "API implementation", "Testing"]
    },
    {
      "role": "QA Engineer",
      "hours": 60,
      "responsibilities": ["Test planning", "Quality assurance", "Bug verification"]
    }
  ],
  "total_hours": 340,
  "estimated_duration_weeks": 8,
  "complexity_assessment": "Medium-High",
  "notes": "Healthcare compliance requirements add complexity. Integration with existing systems requires careful planning and testing."
}"""
    
    def _mock_value_output(self, example: Dict[str, Any]) -> str:
        """Generate mock value analysis output"""
        return """{
  "scenarios": [
    {
      "case": "Low",
      "value": 125000,
      "description": "Conservative adoption with 20% efficiency gains"
    },
    {
      "case": "Base",
      "value": 275000,
      "description": "Expected adoption with 35% efficiency gains"
    },
    {
      "case": "High",
      "value": 450000,
      "description": "Optimal adoption with 50% efficiency gains and expanded use cases"
    }
  ],
  "methodology": "ROI calculation based on operational savings and revenue enhancement",
  "assumptions": [
    "Healthcare provider adoption rate",
    "Efficiency improvement percentages",
    "Market penetration timeline",
    "Competitive landscape stability"
  ],
  "market_factors": [
    "Regulatory environment changes",
    "Technology adoption trends",
    "Healthcare industry consolidation",
    "Patient demand for digital solutions"
  ]
}"""
    
    def prepare_evaluation_batch(self) -> List[Dict[str, Any]]:
        """Prepare complete evaluation batch with agent outputs"""
        # Load golden datasets
        datasets = self.load_golden_datasets()
        
        # Select examples for evaluation
        selected_examples = self.select_examples_for_evaluation(datasets)
        
        # Prepare evaluation batch
        evaluation_batch = []
        
        for example in selected_examples:
            # Generate evaluation ID
            eval_id = self.generate_eval_id(example["agentName"], example["inputId"])
            
            # Create input summary
            input_summary = self.create_input_summary(example["input_payload"])
            
            # Simulate agent run (in real implementation, call actual agents)
            agent_run_result = self.simulate_agent_run(example)
            
            # Create evaluation entry
            eval_entry = {
                "eval_id": eval_id,
                "golden_dataset_inputId": example["inputId"],
                "case_id": agent_run_result["case_id"],
                "trace_id": agent_run_result["trace_id"],
                "agent_name": example["agentName"],
                "input_payload_summary": input_summary,
                "agent_output_to_evaluate": agent_run_result["agent_output"],
                "execution_timestamp": agent_run_result["execution_timestamp"],
                "original_input_payload": example["input_payload"],
                "expected_characteristics": example.get("expected_characteristics_or_ideal_output"),
                "preparation_notes": f"Selected for human evaluation batch 01"
            }
            
            evaluation_batch.append(eval_entry)
            logger.info(f"Prepared evaluation entry: {eval_id}")
        
        return evaluation_batch
    
    def save_evaluation_batch(self, batch: List[Dict[str, Any]], filename: str = "human_eval_batch_01_inputs_outputs.json"):
        """Save evaluation batch to JSON file"""
        batch_data = {
            "metadata": {
                "batch_id": "human_eval_batch_01",
                "creation_date": datetime.now().isoformat(),
                "total_entries": len(batch),
                "agent_distribution": self._get_agent_distribution(batch),
                "description": "First human evaluation batch with selected golden dataset examples"
            },
            "evaluation_entries": batch
        }
        
        with open(filename, 'w') as f:
            json.dump(batch_data, f, indent=2)
        
        logger.info(f"Saved evaluation batch to {filename}")
        return filename
    
    def _get_agent_distribution(self, batch: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of agents in the batch"""
        distribution = {}
        for entry in batch:
            agent_name = entry["agent_name"]
            distribution[agent_name] = distribution.get(agent_name, 0) + 1
        return distribution


def main():
    """Main execution function"""
    logger.info("Starting evaluation batch preparation...")
    
    # Initialize preparator
    preparator = EvaluationBatchPreparator()
    
    try:
        # Prepare evaluation batch
        batch = preparator.prepare_evaluation_batch()
        
        # Save to file
        filename = preparator.save_evaluation_batch(batch)
        
        # Print summary
        print(f"\n✅ Evaluation batch prepared successfully!")
        print(f"📁 Saved to: {filename}")
        print(f"📊 Total entries: {len(batch)}")
        
        # Show agent distribution
        distribution = preparator._get_agent_distribution(batch)
        print(f"🤖 Agent distribution:")
        for agent, count in distribution.items():
            print(f"   - {agent}: {count} examples")
        
        print(f"\n📋 Next steps:")
        print(f"1. Review the generated {filename}")
        print(f"2. Import data to evaluation spreadsheet")
        print(f"3. Begin human evaluation using guidelines")
        
    except Exception as e:
        logger.error(f"Error preparing evaluation batch: {e}")
        raise

if __name__ == "__main__":
    main() 