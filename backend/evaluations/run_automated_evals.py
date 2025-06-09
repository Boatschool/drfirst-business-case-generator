#!/usr/bin/env python3
"""
Automated Evaluation Runner Script for DrFirst Agentic Business Case Generator

This script orchestrates the process of running agents against golden datasets,
applying automated validators, and collecting results for comprehensive evaluation reporting.

Usage:
    python run_automated_evals.py [--output-format json|csv] [--output-file filename]
"""

import json
import logging
import asyncio
import uuid
import time
import sys
import os
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

# Add the backend app to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Set required environment variables if missing (for testing purposes)
if 'SECRET_KEY' not in os.environ:
    os.environ['SECRET_KEY'] = 'test-secret-key-for-evaluation-runner'

# Import Firestore client for persistence
from google.cloud import firestore

# Import all agent classes
from app.agents.product_manager_agent import ProductManagerAgent
from app.agents.architect_agent import ArchitectAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.cost_analyst_agent import CostAnalystAgent
from app.agents.sales_value_analyst_agent import SalesValueAnalystAgent
from app.agents.financial_model_agent import FinancialModelAgent

# Import all validator functions
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

# Import agent input models for validation
from app.models.agent_models import (
    DraftPrdInput,
    GenerateSystemDesignInput
)

# Import services for initialization
from app.services.vertex_ai_service import vertex_ai_service
from app.core.config import settings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('automated_evaluation.log')
    ]
)
logger = logging.getLogger(__name__)

# Firestore collection names
AUTOMATED_EVAL_RESULTS_COLLECTION = "automatedEvaluationResults"
AUTOMATED_EVAL_RUNS_COLLECTION = "automatedEvaluationRuns"


class AutomatedEvaluationRunner:
    """
    Main class for orchestrating automated evaluations of all agents.
    """
    
    def __init__(self):
        self.agents = {}
        self.golden_datasets = None
        self.results = []
        self.evaluation_id = str(uuid.uuid4())  # This serves as eval_run_id
        self.start_time = datetime.now(timezone.utc)
        self.firestore_client = None
        self.dataset_file_used = None
        
        # Agent method mapping
        self.agent_methods = {
            "ProductManagerAgent": "draft_prd",
            "ArchitectAgent": "generate_system_design", 
            "PlannerAgent": "estimate_effort",
            "CostAnalystAgent": "calculate_cost",
            "SalesValueAnalystAgent": "analyze_value",
            "FinancialModelAgent": "generate_financial_model"
        }
        
        logger.info(f"🔬 [EVAL-RUNNER] Initialized with evaluation ID: {self.evaluation_id}")

    def initialize_firestore_client(self) -> bool:
        """
        Initialize Firestore client for persisting evaluation results.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            logger.info("🔥 [EVAL-RUNNER] Initializing Firestore client...")
            
            # Initialize Firestore client - assumes GOOGLE_APPLICATION_CREDENTIALS is set
            # or running in an environment with Application Default Credentials (ADC)
            self.firestore_client = firestore.Client()
            
            logger.info("✅ [EVAL-RUNNER] Firestore client initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ [EVAL-RUNNER] Failed to initialize Firestore client: {e}")
            logger.warning("⚠️ [EVAL-RUNNER] Evaluation will continue without Firestore persistence")
            self.firestore_client = None
            return False

    async def initialize_services(self) -> bool:
        """
        Initialize all necessary services that agents depend on.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        logger.info("🔧 [EVAL-RUNNER] Initializing global services...")
        
        try:
            # Initialize VertexAI service
            success = vertex_ai_service.initialize(
                project_id=settings.google_cloud_project_id,
                location=settings.vertex_ai_location
            )
            
            if success:
                logger.info("✅ [EVAL-RUNNER] VertexAI service initialized successfully")
            else:
                logger.error("❌ [EVAL-RUNNER] Failed to initialize VertexAI service")
                return False
            
            # Initialize Firestore client for evaluation result persistence
            self.initialize_firestore_client()
            # Note: Firestore initialization failure doesn't prevent evaluation execution
                
            return True
            
        except Exception as e:
            logger.error(f"❌ [EVAL-RUNNER] Service initialization failed: {e}")
            return False

    async def initialize_agents(self) -> bool:
        """
        Initialize all agent instances.
        
        Returns:
            bool: True if all agents initialized successfully, False otherwise
        """
        logger.info("🤖 [EVAL-RUNNER] Initializing all agents...")
        
        agent_classes = {
            "ProductManagerAgent": ProductManagerAgent,
            "ArchitectAgent": ArchitectAgent,
            "PlannerAgent": PlannerAgent,
            "CostAnalystAgent": CostAnalystAgent,
            "SalesValueAnalystAgent": SalesValueAnalystAgent,
            "FinancialModelAgent": FinancialModelAgent
        }
        
        initialization_results = {}
        
        for agent_name, agent_class in agent_classes.items():
            try:
                logger.info(f"🔄 [EVAL-RUNNER] Initializing {agent_name}...")
                agent_instance = agent_class()
                self.agents[agent_name] = agent_instance
                initialization_results[agent_name] = "SUCCESS"
                logger.info(f"✅ [EVAL-RUNNER] {agent_name} initialized successfully")
            except Exception as e:
                logger.error(f"❌ [EVAL-RUNNER] Failed to initialize {agent_name}: {e}")
                initialization_results[agent_name] = f"ERROR: {str(e)}"
                # Don't return False immediately - continue with other agents
        
        # Check if we have at least some agents initialized
        successful_agents = [name for name, result in initialization_results.items() 
                           if result == "SUCCESS"]
        
        logger.info(f"📊 [EVAL-RUNNER] Agent initialization summary:")
        for agent_name, result in initialization_results.items():
            status_emoji = "✅" if result == "SUCCESS" else "❌"
            logger.info(f"  {status_emoji} {agent_name}: {result}")
        
        if successful_agents:
            logger.info(f"🎉 [EVAL-RUNNER] Successfully initialized {len(successful_agents)}/{len(agent_classes)} agents")
            return True
        else:
            logger.error("💥 [EVAL-RUNNER] No agents could be initialized")
            return False

    def load_golden_datasets(self, dataset_path: str = "golden_datasets_v1.json") -> bool:
        """
        Load golden datasets from JSON file.
        
        Args:
            dataset_path (str): Path to the golden datasets file
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        logger.info(f"📁 [EVAL-RUNNER] Loading golden datasets from: {dataset_path}")
        
        try:
            with open(dataset_path, 'r', encoding='utf-8') as file:
                self.golden_datasets = json.load(file)
            
            # Store the dataset file used for summary reporting
            self.dataset_file_used = dataset_path
            
            # Validate the structure
            if 'datasets' not in self.golden_datasets:
                raise ValueError("Golden datasets file missing 'datasets' key")
            
            # Count total examples
            total_examples = 0
            agent_counts = {}
            for agent_name, examples in self.golden_datasets['datasets'].items():
                count = len(examples)
                agent_counts[agent_name] = count
                total_examples += count
            
            logger.info(f"📊 [EVAL-RUNNER] Loaded golden datasets successfully:")
            logger.info(f"  📈 Total examples: {total_examples}")
            for agent_name, count in agent_counts.items():
                logger.info(f"  🤖 {agent_name}: {count} examples")
            
            return True
            
        except FileNotFoundError:
            logger.error(f"❌ [EVAL-RUNNER] Golden datasets file not found: {dataset_path}")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"❌ [EVAL-RUNNER] Invalid JSON in golden datasets: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ [EVAL-RUNNER] Error loading golden datasets: {e}")
            return False

    async def invoke_agent(self, agent_name: str, input_payload: Dict[str, Any], 
                          input_id: str) -> Dict[str, Any]:
        """
        Invoke a specific agent with the given input payload.
        
        Args:
            agent_name (str): Name of the agent to invoke
            input_payload (Dict[str, Any]): Input data for the agent
            input_id (str): Unique identifier for this input
            
        Returns:
            Dict[str, Any]: Result containing status, output, and metadata
        """
        logger.info(f"🚀 [EVAL-RUNNER] Invoking {agent_name} for input {input_id}")
        
        if agent_name not in self.agents:
            return {
                "status": "ERROR",
                "error_message": f"Agent {agent_name} not initialized",
                "live_agent_output": None,
                "execution_time_ms": 0
            }
        
        agent = self.agents[agent_name]
        method_name = self.agent_methods.get(agent_name)
        
        if not method_name:
            return {
                "status": "ERROR", 
                "error_message": f"No method mapping found for {agent_name}",
                "live_agent_output": None,
                "execution_time_ms": 0
            }
        
        if not hasattr(agent, method_name):
            return {
                "status": "ERROR",
                "error_message": f"Method {method_name} not found on {agent_name}",
                "live_agent_output": None,
                "execution_time_ms": 0
            }
        
        start_time = time.time()
        
        try:
            method = getattr(agent, method_name)
            
            # Prepare method arguments based on agent type
            if agent_name == "ProductManagerAgent":
                # Convert to DraftPrdInput model
                validated_input = DraftPrdInput(**input_payload)
                result = await method(validated_input, case_id=input_id)
                
            elif agent_name == "ArchitectAgent":
                # Convert to GenerateSystemDesignInput model
                validated_input = GenerateSystemDesignInput(**input_payload)
                result = await method(validated_input, case_id=input_id)
                
            elif agent_name == "PlannerAgent":
                # Direct method call with keyword arguments
                result = await method(
                    prd_content=input_payload.get("prd_content", ""),
                    system_design_content=input_payload.get("system_design_content", ""),
                    case_title=input_payload.get("case_title", ""),
                    case_id=input_id
                )
                
            elif agent_name == "CostAnalystAgent":
                result = await method(
                    effort_breakdown=input_payload.get("effort_breakdown", {}),
                    case_title=input_payload.get("case_title", ""),
                    case_id=input_id
                )
                
            elif agent_name == "SalesValueAnalystAgent":
                result = await method(
                    prd_content=input_payload.get("prd_content", ""),
                    case_title=input_payload.get("case_title", ""),
                    case_id=input_id
                )
                
            elif agent_name == "FinancialModelAgent":
                result = await method(
                    cost_estimate=input_payload.get("cost_estimate", {}),
                    value_projection=input_payload.get("value_projection", {}),
                    case_title=input_payload.get("case_title", ""),
                    case_id=input_id
                )
                
            else:
                return {
                    "status": "ERROR",
                    "error_message": f"Unknown agent type: {agent_name}",
                    "live_agent_output": None,
                    "execution_time_ms": 0
                }
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            logger.info(f"✅ [EVAL-RUNNER] {agent_name} completed for {input_id} in {execution_time_ms}ms")
            
            return {
                "status": "SUCCESS",
                "error_message": None,
                "live_agent_output": result,
                "execution_time_ms": execution_time_ms
            }
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            error_message = f"Error invoking {agent_name}: {str(e)}"
            logger.error(f"❌ [EVAL-RUNNER] {error_message} for {input_id}")
            
            return {
                "status": "ERROR",
                "error_message": error_message,
                "live_agent_output": None,
                "execution_time_ms": execution_time_ms
            }

    def prepare_additional_data(self, agent_name: str, 
                               expected_output_values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare additional data needed for specific validators.
        
        Args:
            agent_name (str): Name of the agent
            expected_output_values (Dict[str, Any]): Expected output values from golden dataset
            
        Returns:
            Dict[str, Any]: Additional data for validators
        """
        additional_data = {}
        
        if agent_name == "CostAnalystAgent":
            # Mock rate card for cost analyst validation
            additional_data["mock_rate_card"] = {
                "Product Manager": 150,
                "Lead Developer": 180,
                "Senior Developer": 160,
                "Junior Developer": 120,
                "QA Engineer": 130,
                "DevOps Engineer": 170,
                "UI/UX Designer": 140
            }
            
        elif agent_name == "FinancialModelAgent":
            # Extract input cost and value for financial model validation
            if "expected_input_cost" in expected_output_values:
                additional_data["input_cost"] = expected_output_values["expected_input_cost"]
            else:
                additional_data["input_cost"] = 50000  # Default for validation
                
            if "expected_input_value" in expected_output_values:
                additional_data["input_value"] = expected_output_values["expected_input_value"]
            else:
                additional_data["input_value"] = {"Base": 75000}  # Default for validation
        
        return additional_data

    async def run_automated_validators(self, agent_name: str, live_output: Any,
                                     additional_data: Dict[str, Any] = None) -> Dict[str, bool]:
        """
        Run automated validators for a specific agent's output.
        
        Args:
            agent_name (str): Name of the agent
            live_output (Any): The live output from the agent
            additional_data (Dict[str, Any]): Additional data for validation
            
        Returns:
            Dict[str, bool]: Validation results (metric_name -> pass/fail)
        """
        logger.info(f"🔍 [EVAL-RUNNER] Running automated validators for {agent_name}")
        
        try:
            # Extract the appropriate content based on agent type
            validation_input = self._extract_validation_input(agent_name, live_output)
            
            validation_results = validate_all_automated_metrics(
                agent_name=agent_name,
                output_data=validation_input,
                additional_data=additional_data or {}
            )
            
            passed_count = sum(1 for result in validation_results.values() if result)
            total_count = len(validation_results)
            
            logger.info(f"📊 [EVAL-RUNNER] {agent_name} validation: {passed_count}/{total_count} metrics passed")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"❌ [EVAL-RUNNER] Validation error for {agent_name}: {e}")
            return {"validation_error": False}

    def _extract_validation_input(self, agent_name: str, live_output: Any) -> Any:
        """
        Extract the appropriate input for validation based on agent type.
        
        Args:
            agent_name (str): Name of the agent
            live_output (Any): The raw agent output
            
        Returns:
            Any: Processed input for validation
        """
        if not live_output:
            return None
            
        # Handle different agent output structures
        if agent_name == "ProductManagerAgent":
            # Extract markdown content from PRD draft
            if hasattr(live_output, 'prd_draft') and live_output.prd_draft:
                return live_output.prd_draft.content_markdown
            elif isinstance(live_output, dict) and 'prd_draft' in live_output:
                prd_draft = live_output['prd_draft']
                if isinstance(prd_draft, dict) and 'content_markdown' in prd_draft:
                    return prd_draft['content_markdown']
            return None
            
        elif agent_name == "ArchitectAgent":
            # Extract markdown content from system design
            if hasattr(live_output, 'system_design_draft') and live_output.system_design_draft:
                return live_output.system_design_draft.content_markdown
            elif isinstance(live_output, dict) and 'system_design_draft' in live_output:
                design_draft = live_output['system_design_draft']
                if isinstance(design_draft, dict) and 'content_markdown' in design_draft:
                    return design_draft['content_markdown']
            return None
            
        elif agent_name == "PlannerAgent":
            # Extract effort breakdown for JSON validation
            if isinstance(live_output, dict):
                if 'effort_breakdown' in live_output:
                    return live_output['effort_breakdown']
                elif 'status' in live_output and live_output['status'] == 'success':
                    # Try to find the effort data in the response
                    for key, value in live_output.items():
                        if isinstance(value, dict) and 'total_hours' in value:
                            return value
            return live_output
            
        elif agent_name == "CostAnalystAgent":
            # Return the full output for cost analysis validation
            return live_output
            
        elif agent_name == "SalesValueAnalystAgent":
            # Return the full output for sales value validation
            return live_output
            
        elif agent_name == "FinancialModelAgent":
            # Return the full output for financial model validation
            return live_output
            
        else:
            # Default: return the full output
            return live_output

    async def save_evaluation_result_to_firestore(self, result_data: Dict[str, Any]) -> bool:
        """
        Save individual evaluation result to Firestore.
        
        Args:
            result_data (Dict[str, Any]): Complete result for one golden dataset entry
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        if not self.firestore_client:
            logger.debug("🔥 [EVAL-RUNNER] Firestore client not available, skipping result persistence")
            return False
        
        try:
            # Generate unique document ID
            doc_id = f"{self.evaluation_id}_{result_data['inputId']}"
            
            # Prepare document data for Firestore
            doc_data = {
                "eval_run_id": self.evaluation_id,
                "golden_dataset_inputId": result_data["inputId"],
                "agent_name": result_data["agentName"],
                "case_id": result_data.get("case_id"),  # May be None
                "trace_id": result_data.get("trace_id"),  # May be None
                "timestamp": datetime.now(timezone.utc),
                "input_payload_summary": result_data.get("input_payload_summary", ""),
                "live_agent_output_summary_or_ref": result_data.get("live_agent_output_summary", ""),
                "validation_results": result_data.get("validation_results", {}),
                "overall_automated_eval_passed": result_data.get("overall_automated_eval_passed", False),
                "agent_run_status": result_data.get("status_of_agent_run", "ERROR"),
                "agent_error_message": result_data.get("agent_error_message", ""),
                "execution_time_ms": result_data.get("execution_time_ms", 0),
                "processed_at": result_data.get("processed_at", datetime.now(timezone.utc).isoformat())
            }
            
            # Get document reference and save
            doc_ref = self.firestore_client.collection(AUTOMATED_EVAL_RESULTS_COLLECTION).document(doc_id)
            doc_ref.set(doc_data)
            
            logger.debug(f"✅ [EVAL-RUNNER] Saved evaluation result to Firestore: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ [EVAL-RUNNER] Failed to save evaluation result to Firestore: {e}")
            return False

    async def save_evaluation_run_summary_to_firestore(self, summary_data: Dict[str, Any]) -> bool:
        """
        Save overall evaluation run summary to Firestore.
        
        Args:
            summary_data (Dict[str, Any]): Complete summary for the evaluation run
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        if not self.firestore_client:
            logger.debug("🔥 [EVAL-RUNNER] Firestore client not available, skipping run summary persistence")
            return False
        
        try:
            # Prepare run summary document
            run_summary_data = {
                "eval_run_id": self.evaluation_id,
                "run_timestamp_start": self.start_time,
                "run_timestamp_end": datetime.now(timezone.utc),
                "total_examples_processed": summary_data["evaluation_summary"]["total_examples_processed"],
                "successful_agent_runs": summary_data["evaluation_summary"]["successful_agent_runs"],
                "failed_agent_runs": summary_data["evaluation_summary"]["failed_agent_runs"],
                "overall_validation_passed_count": summary_data["evaluation_summary"]["overall_validation_passed"],
                "dataset_file_used": self.dataset_file_used or "unknown",
                "success_rate_percentage": summary_data["evaluation_summary"]["success_rate_percentage"],
                "validation_pass_rate_percentage": summary_data["evaluation_summary"]["validation_pass_rate_percentage"],
                "total_evaluation_time_seconds": summary_data["evaluation_summary"]["total_evaluation_time_seconds"],
                "agent_specific_statistics": summary_data.get("agent_specific_statistics", {})
            }
            
            # Save to Firestore using eval_run_id as document ID
            doc_ref = self.firestore_client.collection(AUTOMATED_EVAL_RUNS_COLLECTION).document(self.evaluation_id)
            doc_ref.set(run_summary_data)
            
            logger.info(f"✅ [EVAL-RUNNER] Saved evaluation run summary to Firestore: {self.evaluation_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ [EVAL-RUNNER] Failed to save evaluation run summary to Firestore: {e}")
            return False

    async def process_golden_dataset_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single golden dataset entry.
        
        Args:
            entry (Dict[str, Any]): Golden dataset entry
            
        Returns:
            Dict[str, Any]: Complete result for this entry
        """
        input_id = entry["inputId"]
        agent_name = entry["agentName"]
        input_payload = entry["input_payload"]
        expected_output_values = entry.get("expected_output_values", {})
        
        logger.info(f"🔄 [EVAL-RUNNER] Processing {input_id} ({agent_name})")
        
        # Invoke the agent
        invoke_result = await self.invoke_agent(agent_name, input_payload, input_id)
        
        # Prepare additional data for validators
        additional_data = self.prepare_additional_data(agent_name, expected_output_values)
        
        # Run automated validators if agent invocation was successful
        validation_results = {}
        overall_automated_eval_passed = False
        
        if invoke_result["status"] == "SUCCESS" and invoke_result["live_agent_output"]:
            validation_results = await self.run_automated_validators(
                agent_name, 
                invoke_result["live_agent_output"],
                additional_data
            )
            overall_automated_eval_passed = all(validation_results.values())
        else:
            logger.warning(f"⚠️ [EVAL-RUNNER] Skipping validation for {input_id} due to agent failure")
        
        # Compile complete result
        result = {
            "inputId": input_id,
            "agentName": agent_name,
            "status_of_agent_run": invoke_result["status"],
            "agent_error_message": invoke_result["error_message"],
            "execution_time_ms": invoke_result["execution_time_ms"],
            "live_agent_output_generated": invoke_result["live_agent_output"] is not None,
            "validation_results": validation_results,
            "overall_automated_eval_passed": overall_automated_eval_passed,
            "processed_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Log result summary
        status_emoji = "✅" if overall_automated_eval_passed else "❌"
        logger.info(f"{status_emoji} [EVAL-RUNNER] {input_id}: {invoke_result['status']}, "
                   f"Validation: {overall_automated_eval_passed}")
        
        # Save result to Firestore
        await self.save_evaluation_result_to_firestore(result)
        
        return result

    async def run_all_evaluations(self) -> List[Dict[str, Any]]:
        """
        Run evaluations for all entries in the golden datasets.
        
        Returns:
            List[Dict[str, Any]]: List of all evaluation results
        """
        logger.info("🚀 [EVAL-RUNNER] Starting automated evaluations for all golden dataset entries")
        
        if not self.golden_datasets:
            logger.error("❌ [EVAL-RUNNER] No golden datasets loaded")
            return []
        
        all_entries = []
        for agent_name, entries in self.golden_datasets["datasets"].items():
            for entry in entries:
                all_entries.append(entry)
        
        logger.info(f"📊 [EVAL-RUNNER] Processing {len(all_entries)} total entries")
        
        results = []
        for i, entry in enumerate(all_entries, 1):
            logger.info(f"🔄 [EVAL-RUNNER] === Processing entry {i}/{len(all_entries)} ===")
            
            try:
                result = await self.process_golden_dataset_entry(entry)
                results.append(result)
            except Exception as e:
                logger.error(f"💥 [EVAL-RUNNER] Fatal error processing {entry.get('inputId', 'unknown')}: {e}")
                # Create error result
                error_result = {
                    "inputId": entry.get("inputId", "unknown"),
                    "agentName": entry.get("agentName", "unknown"),
                    "status_of_agent_run": "ERROR",
                    "agent_error_message": f"Fatal processing error: {str(e)}",
                    "execution_time_ms": 0,
                    "live_agent_output_generated": False,
                    "validation_results": {},
                    "overall_automated_eval_passed": False,
                    "processed_at": datetime.now(timezone.utc).isoformat()
                }
                results.append(error_result)
        
        self.results = results
        logger.info(f"🏁 [EVAL-RUNNER] Completed processing all {len(results)} entries")
        
        return results

    def generate_summary_statistics(self) -> Dict[str, Any]:
        """
        Generate comprehensive summary statistics from evaluation results.
        
        Returns:
            Dict[str, Any]: Summary statistics
        """
        if not self.results:
            return {"error": "No results available for summary"}
        
        total_examples = len(self.results)
        successful_runs = len([r for r in self.results if r["status_of_agent_run"] == "SUCCESS"])
        failed_runs = total_examples - successful_runs
        
        overall_passed = len([r for r in self.results if r["overall_automated_eval_passed"]])
        overall_failed = total_examples - overall_passed
        
        # Agent-specific statistics
        agent_stats = {}
        for result in self.results:
            agent_name = result["agentName"]
            if agent_name not in agent_stats:
                agent_stats[agent_name] = {
                    "total": 0,
                    "successful_runs": 0,
                    "validation_passed": 0,
                    "avg_execution_time_ms": 0,
                    "execution_times": []
                }
            
            stats = agent_stats[agent_name]
            stats["total"] += 1
            
            if result["status_of_agent_run"] == "SUCCESS":
                stats["successful_runs"] += 1
            
            if result["overall_automated_eval_passed"]:
                stats["validation_passed"] += 1
            
            if result["execution_time_ms"] > 0:
                stats["execution_times"].append(result["execution_time_ms"])
        
        # Calculate average execution times
        for agent_name, stats in agent_stats.items():
            if stats["execution_times"]:
                stats["avg_execution_time_ms"] = int(sum(stats["execution_times"]) / len(stats["execution_times"]))
            del stats["execution_times"]  # Remove raw data from summary
        
        total_time = datetime.now(timezone.utc) - self.start_time
        
        summary = {
            "evaluation_summary": {
                "evaluation_id": self.evaluation_id,
                "total_examples_processed": total_examples,
                "successful_agent_runs": successful_runs,
                "failed_agent_runs": failed_runs,
                "overall_validation_passed": overall_passed,
                "overall_validation_failed": overall_failed,
                "success_rate_percentage": round((successful_runs / total_examples) * 100, 2) if total_examples > 0 else 0,
                "validation_pass_rate_percentage": round((overall_passed / total_examples) * 100, 2) if total_examples > 0 else 0,
                "total_evaluation_time_seconds": int(total_time.total_seconds()),
                "evaluation_completed_at": datetime.now(timezone.utc).isoformat()
            },
            "agent_specific_statistics": agent_stats,
            "detailed_results": self.results
        }
        
        return summary

    def save_results_json(self, filename: str = None, summary: Dict[str, Any] = None) -> str:
        """
        Save results to JSON file.
        
        Args:
            filename (str): Optional custom filename
            summary (Dict[str, Any]): Optional pre-generated summary to avoid regeneration
            
        Returns:
            str: Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"automated_eval_report_{self.evaluation_id}_{timestamp}.json"
        
        if summary is None:
            summary = self.generate_summary_statistics()
        
        # Add eval_run_id to the summary for correlation
        summary["eval_run_id"] = self.evaluation_id
        
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(summary, file, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 [EVAL-RUNNER] Results saved to: {filename}")
        return filename

    def save_results_csv(self, filename: str = None) -> str:
        """
        Save results to CSV file.
        
        Args:
            filename (str): Optional custom filename
            
        Returns:
            str: Path to saved file
        """
        import csv
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"automated_eval_report_{self.evaluation_id}_{timestamp}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            if not self.results:
                writer = csv.writer(file)
                writer.writerow(["Error", "No results available"])
                return filename
            
            # Define CSV headers
            headers = [
                "eval_run_id", "inputId", "agentName", "status_of_agent_run", "agent_error_message",
                "execution_time_ms", "live_agent_output_generated", 
                "overall_automated_eval_passed", "processed_at"
            ]
            
            # Add validation result columns
            all_validation_keys = set()
            for result in self.results:
                all_validation_keys.update(result.get("validation_results", {}).keys())
            
            validation_headers = sorted(list(all_validation_keys))
            headers.extend(validation_headers)
            
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            
            for result in self.results:
                row = {
                    "eval_run_id": self.evaluation_id,
                    "inputId": result["inputId"],
                    "agentName": result["agentName"],
                    "status_of_agent_run": result["status_of_agent_run"],
                    "agent_error_message": result.get("agent_error_message", ""),
                    "execution_time_ms": result["execution_time_ms"],
                    "live_agent_output_generated": result["live_agent_output_generated"],
                    "overall_automated_eval_passed": result["overall_automated_eval_passed"],
                    "processed_at": result["processed_at"]
                }
                
                # Add validation results
                validation_results = result.get("validation_results", {})
                for key in validation_headers:
                    row[key] = validation_results.get(key, "")
                
                writer.writerow(row)
        
        logger.info(f"💾 [EVAL-RUNNER] CSV results saved to: {filename}")
        return filename


async def main():
    """
    Main execution function.
    """
    parser = argparse.ArgumentParser(description="Automated Evaluation Runner for DrFirst Agents")
    parser.add_argument("--output-format", choices=["json", "csv", "both"], default="json",
                       help="Output format for results (default: json)")
    parser.add_argument("--output-file", type=str, help="Custom output filename (without extension)")
    parser.add_argument("--dataset-path", type=str, default="golden_datasets_v1.json",
                       help="Path to golden datasets file")
    
    args = parser.parse_args()
    
    logger.info("🔬 [EVAL-RUNNER] === DrFirst Automated Evaluation Runner Started ===")
    
    runner = AutomatedEvaluationRunner()
    
    try:
        # Step 1: Initialize services
        logger.info("🔧 [EVAL-RUNNER] Step 1/5: Initializing services...")
        if not await runner.initialize_services():
            logger.error("💥 [EVAL-RUNNER] Service initialization failed")
            return 1
        
        # Step 2: Initialize agents
        logger.info("🤖 [EVAL-RUNNER] Step 2/5: Initializing agents...")
        if not await runner.initialize_agents():
            logger.error("💥 [EVAL-RUNNER] Agent initialization failed")
            return 1
        
        # Step 3: Load golden datasets
        logger.info("📁 [EVAL-RUNNER] Step 3/5: Loading golden datasets...")
        if not runner.load_golden_datasets(args.dataset_path):
            logger.error("💥 [EVAL-RUNNER] Failed to load golden datasets")
            return 1
        
        # Step 4: Run evaluations
        logger.info("🚀 [EVAL-RUNNER] Step 4/5: Running automated evaluations...")
        await runner.run_all_evaluations()
        
        # Step 5: Generate and save results
        logger.info("💾 [EVAL-RUNNER] Step 5/5: Generating and saving results...")
        
        # Generate summary statistics first
        summary = runner.generate_summary_statistics()
        
        # Save run summary to Firestore
        await runner.save_evaluation_run_summary_to_firestore(summary)
        
        if args.output_format in ["json", "both"]:
            json_file = args.output_file + ".json" if args.output_file else None
            json_path = runner.save_results_json(json_file, summary)
            print(f"📊 JSON report saved: {json_path}")
        
        if args.output_format in ["csv", "both"]:
            csv_file = args.output_file + ".csv" if args.output_file else None
            csv_path = runner.save_results_csv(csv_file)
            print(f"📊 CSV report saved: {csv_path}")
        
        # Print summary to console
        eval_summary = summary["evaluation_summary"]
        
        print("\n" + "="*60)
        print("📋 AUTOMATED EVALUATION SUMMARY")
        print("="*60)
        print(f"🆔 Evaluation ID: {eval_summary['evaluation_id']}")
        print(f"📊 Total Examples: {eval_summary['total_examples_processed']}")
        print(f"✅ Successful Runs: {eval_summary['successful_agent_runs']}")
        print(f"❌ Failed Runs: {eval_summary['failed_agent_runs']}")
        print(f"🎯 Validation Passed: {eval_summary['overall_validation_passed']}")
        print(f"📈 Success Rate: {eval_summary['success_rate_percentage']}%")
        print(f"🏆 Validation Pass Rate: {eval_summary['validation_pass_rate_percentage']}%")
        print(f"⏱️ Total Time: {eval_summary['total_evaluation_time_seconds']} seconds")
        
        # Show Firestore persistence status
        if runner.firestore_client:
            print(f"🔥 Firestore: Results persisted to collections:")
            print(f"   📄 Individual results: {AUTOMATED_EVAL_RESULTS_COLLECTION}")
            print(f"   📋 Run summary: {AUTOMATED_EVAL_RUNS_COLLECTION}")
        else:
            print(f"⚠️ Firestore: Results NOT persisted (client unavailable)")
            
        print("="*60)
        
        # Agent-specific summary
        print("\n🤖 AGENT-SPECIFIC RESULTS:")
        for agent_name, stats in summary["agent_specific_statistics"].items():
            success_rate = (stats["successful_runs"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            validation_rate = (stats["validation_passed"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            print(f"  {agent_name}:")
            print(f"    📊 Examples: {stats['total']}")
            print(f"    ✅ Success Rate: {success_rate:.1f}%")
            print(f"    🎯 Validation Rate: {validation_rate:.1f}%")
            print(f"    ⏱️ Avg Time: {stats['avg_execution_time_ms']}ms")
        
        logger.info("🎉 [EVAL-RUNNER] === Automated Evaluation Completed Successfully ===")
        return 0
        
    except KeyboardInterrupt:
        logger.info("⏹️ [EVAL-RUNNER] Evaluation interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"💥 [EVAL-RUNNER] Fatal error: {e}")
        return 1


if __name__ == "__main__":
    # Run the async main function
    exit_code = asyncio.run(main())
    sys.exit(exit_code)