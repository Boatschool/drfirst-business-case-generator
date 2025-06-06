"""
Orchestrator Agent for coordinating business case generation
"""

import logging
from typing import Dict, Any, List, Optional
import asyncio
from enum import Enum
import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field
from app.core.config import settings
from app.core.dependencies import get_db, get_array_union
from app.core.database import DatabaseClient
from app.core.logging_config import (
    log_agent_operation, 
    log_business_case_operation,
    log_error_with_context,
    log_performance_metric
)

# Import ProductManagerAgent
from .product_manager_agent import ProductManagerAgent

# Import ArchitectAgent
from .architect_agent import ArchitectAgent

# Import PlannerAgent
from .planner_agent import PlannerAgent

# Import CostAnalystAgent
from .cost_analyst_agent import CostAnalystAgent

# Import SalesValueAnalystAgent
from .sales_value_analyst_agent import SalesValueAnalystAgent

# Import FinancialModelAgent
from .financial_model_agent import FinancialModelAgent

# Import Firestore models for job tracking
from app.models.firestore_models import Job, JobStatus

# Import constants
from app.core.constants import MessageTypes, MessageSources, Collections


class BusinessCaseStatus(Enum):
    """Represents the various states of a business case lifecycle."""

    INTAKE = "INTAKE"
    PRD_DRAFTING = "PRD_DRAFTING"
    PRD_REVIEW = "PRD_REVIEW"
    PRD_APPROVED = "PRD_APPROVED"
    PRD_REJECTED = "PRD_REJECTED"
    SYSTEM_DESIGN_DRAFTING = "SYSTEM_DESIGN_DRAFTING"
    SYSTEM_DESIGN_DRAFTED = "SYSTEM_DESIGN_DRAFTED"
    SYSTEM_DESIGN_PENDING_REVIEW = "SYSTEM_DESIGN_PENDING_REVIEW"
    SYSTEM_DESIGN_APPROVED = "SYSTEM_DESIGN_APPROVED"
    SYSTEM_DESIGN_REJECTED = "SYSTEM_DESIGN_REJECTED"
    PLANNING_IN_PROGRESS = "PLANNING_IN_PROGRESS"
    PLANNING_COMPLETE = "PLANNING_COMPLETE"
    EFFORT_PENDING_REVIEW = "EFFORT_PENDING_REVIEW"
    EFFORT_APPROVED = "EFFORT_APPROVED"
    EFFORT_REJECTED = "EFFORT_REJECTED"
    COSTING_IN_PROGRESS = "COSTING_IN_PROGRESS"
    COSTING_COMPLETE = "COSTING_COMPLETE"
    COSTING_PENDING_REVIEW = "COSTING_PENDING_REVIEW"
    COSTING_APPROVED = "COSTING_APPROVED"
    COSTING_REJECTED = "COSTING_REJECTED"
    VALUE_ANALYSIS_IN_PROGRESS = "VALUE_ANALYSIS_IN_PROGRESS"
    VALUE_ANALYSIS_COMPLETE = "VALUE_ANALYSIS_COMPLETE"
    VALUE_PENDING_REVIEW = "VALUE_PENDING_REVIEW"
    VALUE_APPROVED = "VALUE_APPROVED"
    VALUE_REJECTED = "VALUE_REJECTED"
    FINANCIAL_MODEL_IN_PROGRESS = "FINANCIAL_MODEL_IN_PROGRESS"
    FINANCIAL_MODEL_COMPLETE = "FINANCIAL_MODEL_COMPLETE"
    FINANCIAL_ANALYSIS = "FINANCIAL_ANALYSIS"
    FINAL_REVIEW = "FINAL_REVIEW"
    PENDING_FINAL_APPROVAL = "PENDING_FINAL_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


# Pydantic model for Firestore data
class BusinessCaseData(BaseModel):
    case_id: str = Field(..., description="Unique ID for the business case")
    user_id: str = Field(..., description="ID of the user who initiated the case")
    title: str = Field(..., description="Title of the business case")
    problem_statement: str = Field(..., description="Problem statement for the case")
    relevant_links: List[Dict[str, str]] = Field(
        default_factory=list, description="Relevant links provided by user"
    )
    status: BusinessCaseStatus = Field(
        BusinessCaseStatus.INTAKE, description="Current status of the business case"
    )
    history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="History of agent interactions and status changes",
    )
    prd_draft: Optional[Dict[str, Any]] = Field(
        None, description="Generated PRD draft content"
    )
    system_design_v1_draft: Optional[Dict[str, Any]] = Field(
        None, description="Generated system design draft content"
    )
    effort_estimate_v1: Optional[Dict[str, Any]] = Field(
        None, description="Generated effort estimate from PlannerAgent"
    )
    cost_estimate_v1: Optional[Dict[str, Any]] = Field(
        None, description="Generated cost estimate from CostAnalystAgent"
    )
    value_projection_v1: Optional[Dict[str, Any]] = Field(
        None, description="Generated value projection from SalesValueAnalystAgent"
    )
    financial_summary_v1: Optional[Dict[str, Any]] = Field(
        None, description="Generated financial summary from FinancialModelAgent"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_firestore_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary suitable for Firestore storage"""
        data = self.model_dump()
        # Convert enum to string value
        data["status"] = self.status.value
        return data


class EchoTool:
    """A simple tool that echoes back the input string."""

    def __init__(
        self,
        name: str = "EchoTool",
        description: str = "Echoes input back to the user.",
    ):
        self.name = name
        self.description = description

    async def run(self, input_string: str) -> str:
        """Takes an input string and returns it."""
        logger = logging.getLogger(__name__)
        logger.debug(f"[EchoTool] Received: {input_string}")
        return input_string


class OrchestratorAgent:
    """
    The main orchestrator agent that coordinates the business case generation process
    by managing other specialized agents.
    """

    def __init__(self, db: Optional[DatabaseClient] = None):
        self.name = "Orchestrator Agent"
        self.description = "Coordinates the business case generation process"
        self.status = "initialized"
        self.echo_tool = EchoTool()
        self.product_manager_agent = ProductManagerAgent()
        self.architect_agent = ArchitectAgent()
        self.planner_agent = PlannerAgent()
        self.cost_analyst_agent = CostAnalystAgent()
        self.sales_value_analyst_agent = SalesValueAnalystAgent()
        self.financial_model_agent = FinancialModelAgent()
        self.logger = logging.getLogger(__name__)

        # Use dependency injection for database client
        self.db = db if db is not None else get_db()
        self.logger.info("OrchestratorAgent: Database client initialized successfully.")

    async def handle_request(
        self, request_type: str, payload: Dict[str, Any], user_id: str
    ) -> Dict[str, Any]:
        """
        Main entry point for handling various requests to the Orchestrator Agent.
        Routes requests to the appropriate tool or method based on request_type.
        """
        if not self.db:
            return {
                "status": "error",
                "message": "Firestore client not initialized. Cannot process request.",
                "result": None,
            }

        if request_type == "echo":
            input_text = payload.get("input_text")
            if input_text is None:
                return {
                    "status": "error",
                    "message": "Missing 'input_text' in payload for echo request.",
                    "result": None,
                }
            try:
                echoed_text = await self.run_echo_tool(input_text)
                return {
                    "status": "success",
                    "message": "Echo request processed successfully.",
                    "result": echoed_text,
                }
            except Exception as e:
                # Log the exception e
                return {
                    "status": "error",
                    "message": f"Error processing echo request: {str(e)}",
                    "result": None,
                }
        elif request_type == "initiate_case":
            problem_statement = payload.get("problemStatement")
            project_title = payload.get("projectTitle", "Untitled Business Case")
            relevant_links = payload.get("relevantLinks", [])

            if not problem_statement:
                return {
                    "status": "error",
                    "message": "Missing 'problemStatement' in payload for initiate_case request.",
                    "result": None,
                }

            case_id = str(uuid.uuid4())

            current_time = datetime.now(timezone.utc)
            initial_status_message = (
                f"Case initiated. Current status: {BusinessCaseStatus.INTAKE.value}"
            )

            case_history = [
                {
                    "timestamp": current_time.isoformat(),
                    "source": "AGENT",
                    "type": "STATUS_UPDATE",
                    "content": initial_status_message,
                }
            ]

            case_data = BusinessCaseData(
                case_id=case_id,
                user_id=user_id,
                title=project_title,
                problem_statement=problem_statement,
                relevant_links=(
                    relevant_links if isinstance(relevant_links, list) else []
                ),
                status=BusinessCaseStatus.INTAKE,
                history=case_history,
                created_at=current_time,
                updated_at=current_time,
            )

            case_doc_ref = self.db.collection(Collections.BUSINESS_CASES).document(case_id)
            try:
                await asyncio.to_thread(case_doc_ref.set, case_data.to_firestore_dict())
                case_logger = log_business_case_operation(
                    self.logger, case_id, user_id, "create_initial_case"
                )
                case_logger.info(
                    "Business case stored in Firestore with INTAKE status",
                    extra={'status': BusinessCaseStatus.INTAKE.value}
                )
            except Exception as e:
                case_logger = log_business_case_operation(
                    self.logger, case_id, user_id, "create_initial_case"
                )
                log_error_with_context(
                    case_logger, 
                    "Failed to store initial business case in Firestore", 
                    e,
                    {'case_id': case_id, 'user_id': user_id}
                )
                return {
                    "status": "error",
                    "message": f"Failed to store business case: {str(e)}",
                    "result": None,
                }

            # Now, invoke ProductManagerAgent to draft PRD
            case_logger = log_business_case_operation(
                self.logger, case_id, user_id, "prd_generation"
            )
            case_logger.info("Invoking ProductManagerAgent to draft PRD")
            try:
                prd_response = await self.product_manager_agent.draft_prd(
                    problem_statement=case_data.problem_statement,
                    case_title=case_data.title,
                    relevant_links=case_data.relevant_links,
                )
                case_logger.info(f"PRD response status: {prd_response.get('status')}")
                if prd_response.get("status") == "error":
                    case_logger.error(f"PRD generation failed: {prd_response.get('message')}")
            except Exception as prd_exc:
                case_logger.error(f"Exception during PRD generation: {str(prd_exc)}")
                prd_response = {
                    "status": "error",
                    "message": f"Exception during PRD generation: {str(prd_exc)}"
                }

            updated_at_time = datetime.now(timezone.utc)
            if prd_response.get("status") == "success" and prd_response.get(
                "prd_draft"
            ):
                case_data.prd_draft = prd_response["prd_draft"]
                case_data.status = BusinessCaseStatus.PRD_DRAFTING
                case_data.updated_at = updated_at_time

                prd_draft_message = (
                    "Initial PRD draft generated by Product Manager Agent."
                )
                case_data.history.append(
                    {
                        "timestamp": updated_at_time.isoformat(),
                        "source": MessageSources.ORCHESTRATOR_AGENT,
                        "type": MessageTypes.STATUS_UPDATE,
                        "content": f"Status updated to {BusinessCaseStatus.PRD_DRAFTING.value}. {prd_draft_message}",
                    }
                )
                case_data.history.append(
                    {
                        "timestamp": updated_at_time.isoformat(),
                        "source": MessageSources.PRD_AGENT,
                        "type": MessageTypes.PRD_SUBMISSION,
                        "content": prd_response["prd_draft"]["content_markdown"],
                    }
                )

                try:
                    await asyncio.to_thread(
                        case_doc_ref.update,
                        {
                            "prd_draft": case_data.prd_draft,
                            "status": case_data.status.value,
                            "history": case_data.history,
                            "updated_at": case_data.updated_at,
                        },
                    )
                    case_logger.info(
                        "Case updated with PRD draft and status",
                        extra={'new_status': case_data.status.value}
                    )
                    initial_user_message = f"Business case '{case_data.title}' initiated (ID: {case_id}). Problem: '{case_data.problem_statement}'. PRD drafting has begun."
                except Exception as e:
                    log_error_with_context(
                        case_logger, 
                        "Failed to update case with PRD draft", 
                        e,
                        {'new_status': case_data.status.value}
                    )
                    initial_user_message = f"Business case '{case_data.title}' initiated (ID: {case_id}). Problem: '{case_data.problem_statement}'. Error occurred during PRD draft storage."
            else:
                prd_error_message = prd_response.get(
                    "message", "Failed to generate PRD draft."
                )
                case_logger.error(
                    "ProductManagerAgent failed to generate PRD draft",
                    extra={'error_message': prd_error_message}
                )
                case_data.history.append(
                    {
                        "timestamp": updated_at_time.isoformat(),
                        "source": MessageSources.ORCHESTRATOR_AGENT,
                        "type": MessageTypes.AGENT_ERROR,
                        "content": f"Failed to generate PRD draft: {prd_error_message}",
                    }
                )
                try:
                    await asyncio.to_thread(
                        case_doc_ref.update,
                        {"history": case_data.history, "updated_at": updated_at_time},
                    )
                except Exception as e:
                    log_error_with_context(
                        case_logger, 
                        "Failed to update case history with PRD error", 
                        e
                    )
                initial_user_message = f"Business case '{case_data.title}' initiated (ID: {case_id}). Problem: '{case_data.problem_statement}'. PRD draft generation encountered an error."

            return {
                "status": "success",
                "message": initial_user_message,
                "caseId": case_id,
                "initialMessage": initial_user_message,
            }
        elif request_type == "generate_business_case":
            # Handle business case generation with job tracking
            requirements = payload.get("requirements", {})
            title = payload.get("title", "Business Case Generation")
            
            # Create a job for tracking
            job_id = str(uuid.uuid4())
            current_time = datetime.now(timezone.utc)
            
            job = Job(
                id=job_id,
                job_type="business_case_generation",
                status=JobStatus.PENDING,
                user_uid=user_id,
                progress=0,
                created_at=current_time,
                updated_at=current_time,
                metadata={
                    "title": title,
                    "requirements": requirements,
                    "request_type": "generate_business_case"
                }
            )
            
            # Store job in Firestore
            try:
                job_ref = self.db.collection(Collections.JOBS).document(job_id)
                await asyncio.to_thread(job_ref.set, job.model_dump(exclude_none=True, exclude={"id"}))
                
                # Update job to IN_PROGRESS and start generation
                await asyncio.to_thread(job_ref.update, {
                    "status": JobStatus.IN_PROGRESS.value,
                    "started_at": current_time,
                    "progress": 10
                })
                
                # Trigger the business case generation workflow
                generation_result = await self.generate_business_case(requirements)
                
                # Update job with result
                if generation_result.get("status") == "success":
                    await asyncio.to_thread(job_ref.update, {
                        "status": JobStatus.COMPLETED.value,
                        "completed_at": datetime.now(timezone.utc),
                        "progress": 100,
                        "business_case_id": generation_result.get("case_id")
                    })
                else:
                    await asyncio.to_thread(job_ref.update, {
                        "status": JobStatus.FAILED.value,
                        "completed_at": datetime.now(timezone.utc),
                        "error_message": generation_result.get("message", "Unknown error")
                    })
                
                return {
                    "status": "success",
                    "message": "Business case generation started",
                    "job_id": job_id,
                    "result": generation_result
                }
                
            except Exception as e:
                job_logger = log_agent_operation(
                    logger, "OrchestratorAgent", job_id, "create_job"
                )
                log_error_with_context(
                    job_logger, 
                    "Failed to create business case generation job", 
                    e,
                    {'job_id': job_id, 'user_id': user_id}
                )
                return {
                    "status": "error",
                    "message": f"Failed to create generation job: {str(e)}",
                    "result": None,
                }
        elif request_type == "get_case_status":
            # Get status of a business case
            case_id = payload.get("case_id")
            if not case_id:
                return {
                    "status": "error",
                    "message": "Missing 'case_id' in payload for get_case_status request.",
                    "result": None,
                }
            
            try:
                case_ref = self.db.collection(Collections.BUSINESS_CASES).document(case_id)
                doc = await asyncio.to_thread(case_ref.get)
                
                if not doc.exists:
                    return {
                        "status": "error",
                        "message": f"Business case {case_id} not found",
                        "result": None,
                    }
                
                case_data = doc.to_dict()
                return {
                    "status": "success",
                    "message": "Case status retrieved successfully",
                    "result": {
                        "case_id": case_id,
                        "status": case_data.get("status"),
                        "title": case_data.get("title"),
                        "updated_at": case_data.get("updated_at"),
                        "history": case_data.get("history", [])
                    }
                }
                
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Error retrieving case status: {str(e)}",
                    "result": None,
                }
        elif request_type == "get_job_status":
            # Get status of a job
            job_id = payload.get("job_id")
            if not job_id:
                return {
                    "status": "error",
                    "message": "Missing 'job_id' in payload for get_job_status request.",
                    "result": None,
                }
            
            try:
                job_ref = self.db.collection("jobs").document(job_id)
                doc = await asyncio.to_thread(job_ref.get)
                
                if not doc.exists:
                    return {
                        "status": "error",
                        "message": f"Job {job_id} not found",
                        "result": None,
                    }
                
                job_data = doc.to_dict()
                return {
                    "status": "success",
                    "message": "Job status retrieved successfully",
                    "result": {
                        "job_id": job_id,
                        "status": job_data.get("status"),
                        "progress": job_data.get("progress", 0),
                        "business_case_id": job_data.get("business_case_id"),
                        "error_message": job_data.get("error_message"),
                        "created_at": job_data.get("created_at"),
                        "updated_at": job_data.get("updated_at")
                    }
                }
                
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Error retrieving job status: {str(e)}",
                    "result": None,
                }
        else:
            return {
                "status": "error",
                "message": f"Unknown request_type: {request_type}",
                "result": None,
            }

    async def generate_business_case(
        self, requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main method to orchestrate the business case generation process.
        This method implements the full business case generation workflow.
        """
        try:
            # Extract requirements
            problem_statement = requirements.get("problemStatement") or requirements.get("description")
            title = requirements.get("title", "Generated Business Case")
            relevant_links = requirements.get("relevantLinks", [])
            user_id = requirements.get("user_id", "system")
            
            if not problem_statement:
                return {
                    "status": "error",
                    "message": "Missing problem statement in requirements",
                }
            
            # Create the business case using existing initiate_case logic
            initiate_payload = {
                "problemStatement": problem_statement,
                "projectTitle": title,
                "relevantLinks": relevant_links
            }
            
            # Call the existing initiate_case logic
            result = await self.handle_request("initiate_case", initiate_payload, user_id)
            
            if result.get("status") == "success":
                return {
                    "status": "success",
                    "message": "Business case generation completed successfully",
                    "case_id": result.get("caseId"),
                    "details": result.get("initialMessage")
                }
            else:
                return {
                    "status": "error",
                    "message": result.get("message", "Failed to generate business case"),
                }
                
        except Exception as e:
            orchestrator_logger = log_agent_operation(
                logger, "OrchestratorAgent", "unknown", "generate_business_case"
            )
            log_error_with_context(
                orchestrator_logger, 
                "Business case generation failed", 
                e,
                {'requirements': str(requirements)}
            )
            return {
                "status": "error",
                "message": f"Business case generation failed: {str(e)}",
            }

    async def run_echo_tool(self, input_text: str) -> str:
        """Runs the EchoTool with the provided input text."""
        return await self.echo_tool.run(input_text)

    async def coordinate_agents(
        self, task_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Coordinate multiple agents to work on different aspects of the business case.
        This method can run agents in parallel or sequence based on the task requirements.
        """
        try:
            task_type = task_data.get("task_type", "sequential")
            agents_to_run = task_data.get("agents", [])
            case_data = task_data.get("case_data", {})
            
            results = []
            
            if task_type == "parallel":
                # Run multiple agents in parallel for independent tasks
                tasks = []
                
                for agent_config in agents_to_run:
                    agent_name = agent_config.get("agent")
                    agent_task = agent_config.get("task")
                    agent_payload = agent_config.get("payload", {})
                    
                    if agent_name == "product_manager" and agent_task == "draft_prd":
                        task = self.product_manager_agent.draft_prd(
                            problem_statement=agent_payload.get("problem_statement", ""),
                            case_title=agent_payload.get("case_title", ""),
                            relevant_links=agent_payload.get("relevant_links", [])
                        )
                        tasks.append(task)
                    elif agent_name == "architect" and agent_task == "generate_system_design":
                        task = self.architect_agent.generate_system_design(
                            prd_content=agent_payload.get("prd_content", ""),
                            case_title=agent_payload.get("case_title", "")
                        )
                        tasks.append(task)
                    elif agent_name == "planner" and agent_task == "estimate_effort":
                        task = self.planner_agent.estimate_effort(
                            prd_content=agent_payload.get("prd_content", ""),
                            system_design_content=agent_payload.get("system_design_content", ""),
                            case_title=agent_payload.get("case_title", "")
                        )
                        tasks.append(task)
                    elif agent_name == "cost_analyst" and agent_task == "estimate_costs":
                        task = self.cost_analyst_agent.estimate_costs(
                            effort_breakdown=agent_payload.get("effort_breakdown", {}),
                            case_title=agent_payload.get("case_title", "")
                        )
                        tasks.append(task)
                    elif agent_name == "sales_value_analyst" and agent_task == "analyze_value":
                        task = self.sales_value_analyst_agent.analyze_value(
                            prd_content=agent_payload.get("prd_content", ""),
                            case_title=agent_payload.get("case_title", "")
                        )
                        tasks.append(task)
                    elif agent_name == "financial_model" and agent_task == "generate_model":
                        task = self.financial_model_agent.generate_financial_model(
                            cost_estimate=agent_payload.get("cost_estimate", {}),
                            value_projection=agent_payload.get("value_projection", {}),
                            case_title=agent_payload.get("case_title", "")
                        )
                        tasks.append(task)
                
                # Run all tasks in parallel
                if tasks:
                    parallel_results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    for i, result in enumerate(parallel_results):
                        if isinstance(result, Exception):
                            results.append({
                                "agent": agents_to_run[i].get("agent"),
                                "status": "error",
                                "message": str(result)
                            })
                        else:
                            results.append({
                                "agent": agents_to_run[i].get("agent"),
                                "status": "success",
                                "result": result
                            })
            
            elif task_type == "sequential":
                # Run agents in sequence (default behavior)
                for agent_config in agents_to_run:
                    agent_name = agent_config.get("agent")
                    agent_task = agent_config.get("task")
                    agent_payload = agent_config.get("payload", {})
                    
                    try:
                        if agent_name == "product_manager" and agent_task == "draft_prd":
                            result = await self.product_manager_agent.draft_prd(
                                problem_statement=agent_payload.get("problem_statement", ""),
                                case_title=agent_payload.get("case_title", ""),
                                relevant_links=agent_payload.get("relevant_links", [])
                            )
                        elif agent_name == "architect" and agent_task == "generate_system_design":
                            result = await self.architect_agent.generate_system_design(
                                prd_content=agent_payload.get("prd_content", ""),
                                case_title=agent_payload.get("case_title", "")
                            )
                        elif agent_name == "planner" and agent_task == "estimate_effort":
                            result = await self.planner_agent.estimate_effort(
                                prd_content=agent_payload.get("prd_content", ""),
                                system_design_content=agent_payload.get("system_design_content", ""),
                                case_title=agent_payload.get("case_title", "")
                            )
                        elif agent_name == "cost_analyst" and agent_task == "estimate_costs":
                            result = await self.cost_analyst_agent.estimate_costs(
                                effort_breakdown=agent_payload.get("effort_breakdown", {}),
                                case_title=agent_payload.get("case_title", "")
                            )
                        elif agent_name == "sales_value_analyst" and agent_task == "analyze_value":
                            result = await self.sales_value_analyst_agent.analyze_value(
                                prd_content=agent_payload.get("prd_content", ""),
                                case_title=agent_payload.get("case_title", "")
                            )
                        elif agent_name == "financial_model" and agent_task == "generate_model":
                            result = await self.financial_model_agent.generate_financial_model(
                                cost_estimate=agent_payload.get("cost_estimate", {}),
                                value_projection=agent_payload.get("value_projection", {}),
                                case_title=agent_payload.get("case_title", "")
                            )
                        else:
                            result = {
                                "status": "error",
                                "message": f"Unknown agent/task combination: {agent_name}/{agent_task}"
                            }
                        
                        results.append({
                            "agent": agent_name,
                            "task": agent_task,
                            "status": "success" if result.get("status") == "success" else "error",
                            "result": result
                        })
                        
                    except Exception as e:
                        results.append({
                            "agent": agent_name,
                            "task": agent_task,
                            "status": "error",
                            "message": str(e)
                        })
            
            return results
            
        except Exception as e:
            orchestrator_logger = log_agent_operation(
                logger, "OrchestratorAgent", "unknown", "coordinate_agents"
            )
            log_error_with_context(
                orchestrator_logger, 
                "Agent coordination failed", 
                e,
                {'task_data': str(task_data)}
            )
            return [{
                "status": "error",
                "message": f"Agent coordination failed: {str(e)}"
            }]

    def get_status(self) -> Dict[str, str]:
        """Get the current status of the orchestrator agent"""
        return {
            "name": self.name,
            "status": self.status,
            "description": self.description,
        }

    async def handle_prd_approval(self, case_id: str) -> Dict[str, Any]:
        """
        Handle PRD approval by triggering System Design generation.
        
        Args:
            case_id (str): The business case ID
            
        Returns:
            Dict[str, Any]: Result of the system design generation trigger
        """
        try:
            orchestrator_logger = log_agent_operation(
                logger, "OrchestratorAgent", case_id, "handle_prd_approval"
            )
            orchestrator_logger.info(f"Handling PRD approval for case {case_id}")
            
            # Get the business case
            case_doc_ref = self.db.collection("businessCases").document(case_id)
            doc_snapshot = await asyncio.to_thread(case_doc_ref.get)
            
            if not doc_snapshot.exists:
                return {
                    "status": "error",
                    "message": f"Business case {case_id} not found",
                }
            
            case_data = doc_snapshot.to_dict()
            
            # Verify PRD is approved
            if case_data.get("status") != BusinessCaseStatus.PRD_APPROVED.value:
                return {
                    "status": "error",
                    "message": f"Case status is {case_data.get('status')}, expected PRD_APPROVED",
                }
            
            # Check if PRD draft exists
            prd_draft = case_data.get("prd_draft")
            if not prd_draft or not prd_draft.get("content_markdown"):
                return {
                    "status": "error",
                    "message": "PRD draft content not found",
                }
            
            # Trigger System Design generation
            orchestrator_logger.info(f"Triggering system design generation for case {case_id}")
            
            # Update status to SYSTEM_DESIGN_DRAFTING
            current_time = datetime.now(timezone.utc)
            update_data = {
                "status": BusinessCaseStatus.SYSTEM_DESIGN_DRAFTING.value,
                "updated_at": current_time,
                "history": get_array_union([
                    {
                        "timestamp": current_time.isoformat(),
                        "source": "ORCHESTRATOR_AGENT", 
                        "type": "STATUS_UPDATE",
                        "content": f"Status updated to {BusinessCaseStatus.SYSTEM_DESIGN_DRAFTING.value}. ArchitectAgent initiated for system design generation.",
                    }
                ]),
            }
            await asyncio.to_thread(case_doc_ref.update, update_data)
            
            # Generate system design using ArchitectAgent
            system_design_response = await self.architect_agent.generate_system_design(
                prd_content=prd_draft.get("content_markdown"),
                case_title=case_data.get("title", "Unknown"),
                problem_statement=case_data.get("problem_statement", ""),
            )
            
            updated_at_time = datetime.now(timezone.utc)
            
            if system_design_response.get("status") == "success" and system_design_response.get("system_design"):
                # System design generation successful
                system_design = system_design_response["system_design"]
                
                # Add metadata to system design
                system_design["generated_by"] = "ArchitectAgent"
                system_design["version"] = "v1"
                system_design["generated_timestamp"] = updated_at_time.isoformat()
                
                # Update case with system design and change status to SYSTEM_DESIGN_DRAFTED
                update_data = {
                    "system_design_v1_draft": system_design,
                    "status": BusinessCaseStatus.SYSTEM_DESIGN_DRAFTED.value,
                    "updated_at": updated_at_time,
                    "history": get_array_union([
                        {
                            "timestamp": updated_at_time.isoformat(),
                            "source": "ARCHITECT_AGENT",
                            "type": "SYSTEM_DESIGN",
                            "content": f"System design generated for {case_data.get('title', 'Unknown')}",
                        },
                        {
                            "timestamp": updated_at_time.isoformat(),
                            "source": "ORCHESTRATOR_AGENT",
                            "type": "STATUS_UPDATE", 
                            "content": f"Status updated to {BusinessCaseStatus.SYSTEM_DESIGN_DRAFTED.value}. System design generation completed.",
                        }
                    ]),
                }
                
                await asyncio.to_thread(case_doc_ref.update, update_data)
                
                orchestrator_logger.info(f"System design generation completed successfully for case {case_id}")
                
                # Now trigger planning (effort estimation) after system design is complete
                try:
                    orchestrator_logger.info(f"Triggering planning/effort estimation for case {case_id}")
                    
                    # Update status to PLANNING_IN_PROGRESS
                    planning_time = datetime.now(timezone.utc)
                    planning_update_data = {
                        "status": BusinessCaseStatus.PLANNING_IN_PROGRESS.value,
                        "updated_at": planning_time,
                        "history": get_array_union([
                            {
                                "timestamp": planning_time.isoformat(),
                                "source": "ORCHESTRATOR_AGENT",
                                "type": "STATUS_UPDATE",
                                "content": f"Status updated to {BusinessCaseStatus.PLANNING_IN_PROGRESS.value}. PlannerAgent initiated for effort estimation.",
                            }
                        ]),
                    }
                    await asyncio.to_thread(case_doc_ref.update, planning_update_data)
                    
                    # Trigger effort estimation using PlannerAgent
                    effort_response = await self.planner_agent.generate_effort_estimate(
                        system_design_content=system_design,
                        case_title=case_data.get("title", "Unknown"),
                        problem_statement=case_data.get("problem_statement", ""),
                    )
                    
                    effort_time = datetime.now(timezone.utc)
                    
                    if effort_response.get("status") == "success" and effort_response.get("effort_estimate"):
                        # Effort estimation successful
                        effort_estimate = effort_response["effort_estimate"]
                        effort_estimate["generated_by"] = "PlannerAgent"
                        effort_estimate["version"] = "v1"
                        effort_estimate["generated_timestamp"] = effort_time.isoformat()
                        
                        # Update case with effort estimate and change status to PLANNING_COMPLETE
                        effort_update_data = {
                            "effort_estimate_v1": effort_estimate,
                            "status": BusinessCaseStatus.PLANNING_COMPLETE.value,
                            "updated_at": effort_time,
                            "history": get_array_union([
                                {
                                    "timestamp": effort_time.isoformat(),
                                    "source": "PLANNER_AGENT",
                                    "type": "EFFORT_ESTIMATE",
                                    "content": f"Effort estimate generated for {case_data.get('title', 'Unknown')}",
                                },
                                {
                                    "timestamp": effort_time.isoformat(),
                                    "source": "ORCHESTRATOR_AGENT",
                                    "type": "STATUS_UPDATE",
                                    "content": f"Status updated to {BusinessCaseStatus.PLANNING_COMPLETE.value}. Effort estimation completed.",
                                }
                            ]),
                        }
                        
                        await asyncio.to_thread(case_doc_ref.update, effort_update_data)
                        orchestrator_logger.info(f"Effort estimation completed successfully for case {case_id}")
                        
                        return {
                            "status": "success",
                            "message": "System design and effort estimation generated successfully",
                            "case_id": case_id,
                            "new_status": BusinessCaseStatus.PLANNING_COMPLETE.value,
                        }
                    else:
                        # Effort estimation failed - revert to SYSTEM_DESIGN_DRAFTED
                        error_message = effort_response.get("message", "Failed to generate effort estimate")
                        orchestrator_logger.warning(f"Effort estimation failed for case {case_id}: {error_message}")
                        
                        revert_update_data = {
                            "status": BusinessCaseStatus.SYSTEM_DESIGN_DRAFTED.value,
                            "updated_at": effort_time,
                            "history": get_array_union([
                                {
                                    "timestamp": effort_time.isoformat(),
                                    "source": "ORCHESTRATOR_AGENT",
                                    "type": "WARNING",
                                    "content": f"Effort estimation failed: {error_message}. Status reverted to SYSTEM_DESIGN_DRAFTED.",
                                }
                            ]),
                        }
                        
                        await asyncio.to_thread(case_doc_ref.update, revert_update_data)
                        
                        return {
                            "status": "success",
                            "message": "System design generated successfully, but effort estimation failed",
                            "case_id": case_id,
                            "new_status": BusinessCaseStatus.SYSTEM_DESIGN_DRAFTED.value,
                            "effort_estimation_error": error_message,
                        }
                        
                except Exception as planning_error:
                    orchestrator_logger.warning(f"Error in effort estimation for case {case_id}: {str(planning_error)}")
                    return {
                        "status": "success",
                        "message": "System design generated successfully, but effort estimation could not be initiated",
                        "case_id": case_id,
                        "new_status": BusinessCaseStatus.SYSTEM_DESIGN_DRAFTED.value,
                        "effort_estimation_error": str(planning_error),
                    }
            else:
                # System design generation failed
                error_message = system_design_response.get("message", "Failed to generate system design")
                log_error_with_context(
                    orchestrator_logger, 
                    f"ArchitectAgent failed for case {case_id}", 
                    Exception(error_message),
                    {'case_id': case_id, 'error_message': error_message}
                )
                
                # Update with error information - revert to PRD_APPROVED state
                update_data = {
                    "status": BusinessCaseStatus.PRD_APPROVED.value,
                    "updated_at": updated_at_time,
                    "history": get_array_union([
                        {
                            "timestamp": updated_at_time.isoformat(),
                            "source": "ORCHESTRATOR_AGENT",
                            "type": "ERROR",
                            "content": f"System design generation failed: {error_message}",
                        }
                    ]),
                }
                
                await asyncio.to_thread(case_doc_ref.update, update_data)
                
                return {
                    "status": "error",
                    "message": f"System design generation failed: {error_message}",
                    "case_id": case_id,
                }
                
        except Exception as e:
            orchestrator_logger = log_agent_operation(
                logger, "OrchestratorAgent", case_id, "handle_prd_approval"
            )
            log_error_with_context(
                orchestrator_logger, 
                f"Error handling PRD approval for case {case_id}", 
                e,
                {'case_id': case_id}
            )
            return {
                "status": "error",
                "message": f"Error handling PRD approval: {str(e)}",
            }

    async def check_and_trigger_financial_model(self, case_id: str) -> Dict[str, Any]:
        """
        Check if both cost estimate and value projection are approved, and if so,
        trigger the FinancialModelAgent to generate a financial summary.

        Args:
            case_id (str): The business case ID

        Returns:
            Dict[str, Any]: Result of the check and potential financial model generation
        """
        if not self.db:
            return {"status": "error", "message": "Firestore client not initialized"}

        try:
            # Get the latest case data
            case_doc_ref = self.db.collection("businessCases").document(case_id)
            doc_snapshot = await asyncio.to_thread(case_doc_ref.get)

            if not doc_snapshot.exists:
                return {
                    "status": "error",
                    "message": f"Business case {case_id} not found",
                }

            case_data = doc_snapshot.to_dict()
            if not case_data:
                return {
                    "status": "error",
                    "message": f"Business case {case_id} data is empty",
                }

            current_status = case_data.get("status")
            cost_estimate = case_data.get("cost_estimate_v1")
            value_projection = case_data.get("value_projection_v1")

            print(
                f"[OrchestratorAgent] Checking financial model trigger for case {case_id}"
            )
            print(f"[OrchestratorAgent] Current status: {current_status}")
            print(
                f"[OrchestratorAgent] Cost estimate exists: {cost_estimate is not None}"
            )
            print(
                f"[OrchestratorAgent] Value projection exists: {value_projection is not None}"
            )

            # Check if both are approved
            if current_status == BusinessCaseStatus.COSTING_APPROVED.value:
                # Cost was just approved, check if value is also approved
                case_doc_ref_refresh = self.db.collection("businessCases").document(
                    case_id
                )
                doc_snapshot_refresh = await asyncio.to_thread(case_doc_ref_refresh.get)
                case_data_refresh = doc_snapshot_refresh.to_dict()

                # Look for VALUE_APPROVED in the history or check if there's a value approval workflow completed
                value_approved = False
                for history_item in case_data_refresh.get("history", []):
                    if history_item.get("messageType") == "VALUE_PROJECTION_APPROVAL":
                        value_approved = True
                        break

                if value_approved and cost_estimate and value_projection:
                    print(
                        f"[OrchestratorAgent] Both cost and value are approved, triggering financial model for case {case_id}"
                    )
                    return await self._generate_financial_model(
                        case_id,
                        case_doc_ref,
                        cost_estimate,
                        value_projection,
                        case_data.get("title", "Unknown"),
                    )
                else:
                    print(
                        f"[OrchestratorAgent] Cost approved but value not yet approved for case {case_id}"
                    )
                    return {
                        "status": "success",
                        "message": "Cost approved, waiting for value approval",
                    }

            elif current_status == BusinessCaseStatus.VALUE_APPROVED.value:
                # Value was just approved, check if cost is also approved
                case_doc_ref_refresh = self.db.collection("businessCases").document(
                    case_id
                )
                doc_snapshot_refresh = await asyncio.to_thread(case_doc_ref_refresh.get)
                case_data_refresh = doc_snapshot_refresh.to_dict()

                # Look for COSTING_APPROVED in the history
                cost_approved = False
                for history_item in case_data_refresh.get("history", []):
                    if history_item.get("messageType") == "COST_ESTIMATE_APPROVAL":
                        cost_approved = True
                        break

                if cost_approved and cost_estimate and value_projection:
                    print(
                        f"[OrchestratorAgent] Both cost and value are approved, triggering financial model for case {case_id}"
                    )
                    return await self._generate_financial_model(
                        case_id,
                        case_doc_ref,
                        cost_estimate,
                        value_projection,
                        case_data.get("title", "Unknown"),
                    )
                else:
                    print(
                        f"[OrchestratorAgent] Value approved but cost not yet approved for case {case_id}"
                    )
                    return {
                        "status": "success",
                        "message": "Value approved, waiting for cost approval",
                    }
            else:
                print(
                    f"[OrchestratorAgent] Neither cost nor value approval status detected for case {case_id}"
                )
                return {
                    "status": "success",
                    "message": "No action needed - financial model not ready",
                }

        except Exception as e:
            error_msg = (
                f"Error checking financial model trigger for case {case_id}: {str(e)}"
            )
            print(f"[OrchestratorAgent] {error_msg}")
            return {"status": "error", "message": error_msg}

    async def _generate_financial_model(
        self,
        case_id: str,
        case_doc_ref,
        cost_estimate: Dict[str, Any],
        value_projection: Dict[str, Any],
        case_title: str,
    ) -> Dict[str, Any]:
        """
        Generate financial model using the FinancialModelAgent.

        Args:
            case_id (str): The business case ID
            case_doc_ref: Firestore document reference
            cost_estimate (Dict[str, Any]): Approved cost estimate data
            value_projection (Dict[str, Any]): Approved value projection data
            case_title (str): Case title

        Returns:
            Dict[str, Any]: Result of financial model generation
        """
        print(
            f"[OrchestratorAgent] Starting financial model generation for case {case_id}"
        )

        try:
            # Update status to FINANCIAL_MODEL_IN_PROGRESS
            current_time = datetime.now(timezone.utc)
            update_data = {
                "status": BusinessCaseStatus.FINANCIAL_MODEL_IN_PROGRESS.value,
                "updated_at": current_time,
                "history": get_array_union(
                    [
                        {
                            "timestamp": current_time.isoformat(),
                            "source": "ORCHESTRATOR_AGENT",
                            "type": "STATUS_UPDATE",
                            "content": f"Status updated to {BusinessCaseStatus.FINANCIAL_MODEL_IN_PROGRESS.value}. FinancialModelAgent initiated for financial summary generation.",
                        }
                    ]
                ),
            }
            await asyncio.to_thread(case_doc_ref.update, update_data)

            # Invoke FinancialModelAgent
            financial_response = (
                await self.financial_model_agent.generate_financial_summary(
                    cost_estimate=cost_estimate,
                    value_projection=value_projection,
                    case_title=case_title,
                )
            )

            updated_at_time = datetime.now(timezone.utc)

            if financial_response.get("status") == "success" and financial_response.get(
                "financial_summary"
            ):
                # Financial model generation successful
                financial_summary = financial_response["financial_summary"]

                # Add timestamp to the financial summary
                financial_summary["generated_timestamp"] = updated_at_time.isoformat()

                # Extract key metrics for history logging
                primary_roi = financial_summary.get("financial_metrics", {}).get(
                    "primary_roi_percentage", "Unknown"
                )
                primary_net_value = financial_summary.get("financial_metrics", {}).get(
                    "primary_net_value", "Unknown"
                )
                currency = financial_summary.get("currency", "USD")

                # Update case with financial summary and change status to FINANCIAL_MODEL_COMPLETE
                update_data = {
                    "financial_summary_v1": financial_summary,
                    "status": BusinessCaseStatus.FINANCIAL_MODEL_COMPLETE.value,
                    "updated_at": updated_at_time,
                    "history": get_array_union(
                        [
                            {
                                "timestamp": updated_at_time.isoformat(),
                                "source": "FINANCIAL_MODEL_AGENT",
                                "type": "FINANCIAL_SUMMARY",
                                "content": f"Financial summary generated. ROI: {primary_roi}%, Net Value: {primary_net_value} {currency}",
                            },
                            {
                                "timestamp": updated_at_time.isoformat(),
                                "source": "ORCHESTRATOR_AGENT",
                                "type": "STATUS_UPDATE",
                                "content": f"Status updated to {BusinessCaseStatus.FINANCIAL_MODEL_COMPLETE.value}. Complete financial model generated.",
                            },
                        ]
                    ),
                }

                await asyncio.to_thread(case_doc_ref.update, update_data)

                print(
                    f"[OrchestratorAgent] Financial model generation completed successfully for case {case_id}"
                )
                return {
                    "status": "success",
                    "message": "Financial model generated successfully",
                    "case_id": case_id,
                    "financial_summary": financial_summary,
                    "new_status": BusinessCaseStatus.FINANCIAL_MODEL_COMPLETE.value,
                }

            else:
                # Financial model generation failed
                error_message = financial_response.get(
                    "message", "Failed to generate financial model"
                )
                print(
                    f"[OrchestratorAgent] FinancialModelAgent failed for case {case_id}: {error_message}"
                )

                # Update with error information - revert to a stable state
                update_data = {
                    "status": BusinessCaseStatus.VALUE_APPROVED.value,  # Revert to stable state
                    "updated_at": updated_at_time,
                    "history": get_array_union(
                        [
                            {
                                "timestamp": updated_at_time.isoformat(),
                                "source": "ORCHESTRATOR_AGENT",
                                "type": "ERROR",
                                "content": f"Financial model generation failed: {error_message}",
                            }
                        ]
                    ),
                }

                await asyncio.to_thread(case_doc_ref.update, update_data)

                return {
                    "status": "error",
                    "message": f"Financial model generation failed: {error_message}",
                    "case_id": case_id,
                }

        except Exception as e:
            error_msg = (
                f"Error in financial model generation for case {case_id}: {str(e)}"
            )
            print(f"[OrchestratorAgent] {error_msg}")
            return {"status": "error", "message": error_msg}
