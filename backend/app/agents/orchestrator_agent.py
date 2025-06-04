"""
Orchestrator Agent for coordinating business case generation
"""

from typing import Dict, Any, List, Optional
import asyncio
from enum import Enum
import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field
from google.cloud import firestore
from app.core.config import settings

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
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

# Pydantic model for Firestore data
class BusinessCaseData(BaseModel):
    case_id: str = Field(..., description="Unique ID for the business case")
    user_id: str = Field(..., description="ID of the user who initiated the case")
    title: str = Field(..., description="Title of the business case")
    problem_statement: str = Field(..., description="Problem statement for the case")
    relevant_links: List[Dict[str, str]] = Field(default_factory=list, description="Relevant links provided by user")
    status: BusinessCaseStatus = Field(BusinessCaseStatus.INTAKE, description="Current status of the business case")
    history: List[Dict[str, Any]] = Field(default_factory=list, description="History of agent interactions and status changes")
    prd_draft: Optional[Dict[str, Any]] = Field(None, description="Generated PRD draft content")
    system_design_v1_draft: Optional[Dict[str, Any]] = Field(None, description="Generated system design draft content")
    effort_estimate_v1: Optional[Dict[str, Any]] = Field(None, description="Generated effort estimate from PlannerAgent")
    cost_estimate_v1: Optional[Dict[str, Any]] = Field(None, description="Generated cost estimate from CostAnalystAgent")
    value_projection_v1: Optional[Dict[str, Any]] = Field(None, description="Generated value projection from SalesValueAnalystAgent")
    financial_summary_v1: Optional[Dict[str, Any]] = Field(None, description="Generated financial summary from FinancialModelAgent")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_firestore_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary suitable for Firestore storage"""
        data = self.model_dump()
        # Convert enum to string value
        data['status'] = self.status.value
        return data

class EchoTool:
    """A simple tool that echoes back the input string."""
    def __init__(self, name: str = "EchoTool", description: str = "Echoes input back to the user."):
        self.name = name
        self.description = description

    async def run(self, input_string: str) -> str:
        """Takes an input string and returns it."""
        print(f"[EchoTool] Received: {input_string}")
        return input_string

class OrchestratorAgent:
    """
    The main orchestrator agent that coordinates the business case generation process
    by managing other specialized agents.
    """
    
    def __init__(self):
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
        try:
            self.db = firestore.Client(project=settings.firebase_project_id)
            print("OrchestratorAgent: Firestore client initialized successfully.")
        except Exception as e:
            print(f"OrchestratorAgent: Failed to initialize Firestore client: {e}")
            self.db = None
    
    async def handle_request(self, request_type: str, payload: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Main entry point for handling various requests to the Orchestrator Agent.
        Routes requests to the appropriate tool or method based on request_type.
        """
        if not self.db:
            return {"status": "error", "message": "Firestore client not initialized. Cannot process request.", "result": None}

        if request_type == "echo":
            input_text = payload.get("input_text")
            if input_text is None:
                return {
                    "status": "error",
                    "message": "Missing 'input_text' in payload for echo request.",
                    "result": None
                }
            try:
                echoed_text = await self.run_echo_tool(input_text)
                return {
                    "status": "success",
                    "message": "Echo request processed successfully.",
                    "result": echoed_text
                }
            except Exception as e:
                # Log the exception e
                return {
                    "status": "error",
                    "message": f"Error processing echo request: {str(e)}",
                    "result": None
                }
        elif request_type == "initiate_case":
            problem_statement = payload.get("problemStatement")
            project_title = payload.get("projectTitle", "Untitled Business Case")
            relevant_links = payload.get("relevantLinks", [])

            if not problem_statement:
                return {
                    "status": "error",
                    "message": "Missing 'problemStatement' in payload for initiate_case request.",
                    "result": None
                }
            
            case_id = str(uuid.uuid4())
            
            current_time = datetime.now(timezone.utc)
            initial_status_message = f"Case initiated. Current status: {BusinessCaseStatus.INTAKE.value}"
            
            case_history = [
                {
                    "timestamp": current_time.isoformat(),
                    "source": "AGENT",
                    "type": "STATUS_UPDATE",
                    "content": initial_status_message
                }
            ]

            case_data = BusinessCaseData(
                case_id=case_id,
                user_id=user_id,
                title=project_title,
                problem_statement=problem_statement,
                relevant_links=relevant_links if isinstance(relevant_links, list) else [],
                status=BusinessCaseStatus.INTAKE,
                history=case_history,
                created_at=current_time,
                updated_at=current_time
            )

            case_doc_ref = self.db.collection("businessCases").document(case_id)
            try:
                await asyncio.to_thread(case_doc_ref.set, case_data.to_firestore_dict())
                print(f"Case {case_id} for user {user_id} stored in Firestore with status INTAKE.")
            except Exception as e:
                print(f"Error storing initial case {case_id} in Firestore: {e}")
                return {"status": "error", "message": f"Failed to store business case: {str(e)}", "result": None}

            # Now, invoke ProductManagerAgent to draft PRD
            print(f"OrchestratorAgent: Invoking ProductManagerAgent for case {case_id}...")
            prd_response = await self.product_manager_agent.draft_prd(
                problem_statement=case_data.problem_statement,
                case_title=case_data.title,
                relevant_links=case_data.relevant_links
            )

            updated_at_time = datetime.now(timezone.utc)
            if prd_response.get("status") == "success" and prd_response.get("prd_draft"):
                case_data.prd_draft = prd_response["prd_draft"]
                case_data.status = BusinessCaseStatus.PRD_DRAFTING
                case_data.updated_at = updated_at_time
                
                prd_draft_message = "Initial PRD draft generated by Product Manager Agent."
                case_data.history.append({
                    "timestamp": updated_at_time.isoformat(),
                    "source": "AGENT",
                    "type": "STATUS_UPDATE",
                    "content": f"Status updated to {BusinessCaseStatus.PRD_DRAFTING.value}. {prd_draft_message}"
                })
                case_data.history.append({
                    "timestamp": updated_at_time.isoformat(),
                    "source": "PRODUCT_MANAGER_AGENT", 
                    "type": "PRD_DRAFT",
                    "content": prd_response["prd_draft"]["content_markdown"]
                })
                
                try:
                    await asyncio.to_thread(case_doc_ref.update, {
                        "prd_draft": case_data.prd_draft,
                        "status": case_data.status.value,
                        "history": case_data.history,
                        "updated_at": case_data.updated_at
                    })
                    print(f"Case {case_id} updated with PRD draft and status {case_data.status.value}.")
                    initial_user_message = f"Business case '{case_data.title}' initiated (ID: {case_id}). Problem: '{case_data.problem_statement}'. PRD drafting has begun."
                except Exception as e:
                    print(f"Error updating case {case_id} with PRD draft: {e}")
                    initial_user_message = f"Business case '{case_data.title}' initiated (ID: {case_id}). Problem: '{case_data.problem_statement}'. Error occurred during PRD draft storage."
            else:
                prd_error_message = prd_response.get("message", "Failed to generate PRD draft.")
                print(f"OrchestratorAgent: ProductManagerAgent failed for case {case_id}: {prd_error_message}")
                case_data.history.append({
                    "timestamp": updated_at_time.isoformat(),
                    "source": "ORCHESTRATOR_AGENT",
                    "type": "ERROR",
                    "content": f"Failed to generate PRD draft: {prd_error_message}"
                })
                try:
                    await asyncio.to_thread(case_doc_ref.update, {"history": case_data.history, "updated_at": updated_at_time})
                except Exception as e:
                    print(f"Error updating case {case_id} history with PRD error: {e}")
                initial_user_message = f"Business case '{case_data.title}' initiated (ID: {case_id}). Problem: '{case_data.problem_statement}'. PRD draft generation encountered an error."

            return {
                "status": "success", 
                "message": initial_user_message,
                "caseId": case_id,
                "initialMessage": initial_user_message 
            }
        # TODO: Add handlers for other request_types as functionality expands
        # (e.g., "generate_business_case", "get_case_status")
        else:
            return {
                "status": "error",
                "message": f"Unknown request_type: {request_type}",
                "result": None
            }
    
    async def generate_business_case(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method to orchestrate the business case generation process
        """
        # TODO: Implement orchestration logic with ADK
        return {
            "status": "in_progress",
            "message": "Business case generation started",
            "job_id": "placeholder_job_id"
        }
    
    async def run_echo_tool(self, input_text: str) -> str:
        """Runs the EchoTool with the provided input text."""
        return await self.echo_tool.run(input_text)
    
    async def coordinate_agents(self, task_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Coordinate multiple agents to work on different aspects of the business case
        """
        # TODO: Implement agent coordination logic
        return []
    
    async def handle_prd_approval(self, case_id: str) -> Dict[str, Any]:
        """
        Handle the system design generation process after PRD approval.
        This method is called when a PRD is approved to initiate the next phase.
        
        Args:
            case_id (str): The ID of the business case with approved PRD
            
        Returns:
            Dict[str, Any]: Response indicating success/failure of system design generation
        """
        print(f"[OrchestratorAgent] Handling PRD approval for case {case_id}")
        
        if not self.db:
            return {"status": "error", "message": "Firestore client not initialized"}
        
        try:
            # Retrieve case data from Firestore
            case_doc_ref = self.db.collection("businessCases").document(case_id)
            doc_snapshot = await asyncio.to_thread(case_doc_ref.get)
            
            if not doc_snapshot.exists:
                return {"status": "error", "message": f"Business case {case_id} not found"}
            
            case_data = doc_snapshot.to_dict()
            if not case_data:
                return {"status": "error", "message": f"Business case {case_id} data is empty"}
            
            # Verify PRD is approved
            current_status = case_data.get("status")
            if current_status != BusinessCaseStatus.PRD_APPROVED.value:
                return {"status": "error", "message": f"Case status is {current_status}, not PRD_APPROVED"}
            
            # Extract PRD content and case title
            prd_draft = case_data.get("prd_draft")
            if not prd_draft or not prd_draft.get("content_markdown"):
                return {"status": "error", "message": "No PRD content found for system design generation"}
            
            approved_prd_content = prd_draft["content_markdown"]
            case_title = case_data.get("title", "Untitled Business Case")
            
            print(f"[OrchestratorAgent] Invoking ArchitectAgent for case {case_id}...")
            
            # Update status to SYSTEM_DESIGN_DRAFTING first
            current_time = datetime.now(timezone.utc)
            update_data = {
                "status": BusinessCaseStatus.SYSTEM_DESIGN_DRAFTING.value,
                "updated_at": current_time,
                "history": firestore.ArrayUnion([{
                    "timestamp": current_time.isoformat(),
                    "source": "ORCHESTRATOR_AGENT",
                    "type": "STATUS_UPDATE", 
                    "content": f"Status updated to {BusinessCaseStatus.SYSTEM_DESIGN_DRAFTING.value}. Architect Agent initiated for system design generation."
                }])
            }
            await asyncio.to_thread(case_doc_ref.update, update_data)
            
            # Invoke ArchitectAgent to generate system design
            design_response = await self.architect_agent.generate_system_design(
                prd_content=approved_prd_content,
                case_title=case_title
            )
            
            updated_at_time = datetime.now(timezone.utc)
            
            if design_response.get("status") == "success" and design_response.get("system_design_draft"):
                # System design generated successfully
                system_design_draft = design_response["system_design_draft"]
                
                # Update case with system design and change status to SYSTEM_DESIGN_DRAFTED
                update_data = {
                    "system_design_v1_draft": system_design_draft,
                    "status": BusinessCaseStatus.SYSTEM_DESIGN_DRAFTED.value,
                    "updated_at": updated_at_time,
                    "history": firestore.ArrayUnion([
                        {
                            "timestamp": updated_at_time.isoformat(),
                            "source": "ARCHITECT_AGENT",
                            "type": "SYSTEM_DESIGN_DRAFT",
                            "content": f"System design draft generated. Length: {len(system_design_draft.get('content_markdown', ''))} characters"
                        },
                        {
                            "timestamp": updated_at_time.isoformat(),
                            "source": "ORCHESTRATOR_AGENT",
                            "type": "STATUS_UPDATE",
                            "content": f"Status updated to {BusinessCaseStatus.SYSTEM_DESIGN_DRAFTED.value}. System design draft completed."
                        }
                    ])
                }
                
                await asyncio.to_thread(case_doc_ref.update, update_data)
                
                print(f"[OrchestratorAgent] System design generated successfully for case {case_id}")
                
                # Continue to effort estimation phase
                effort_result = await self._handle_effort_estimation(case_id, case_doc_ref, approved_prd_content, system_design_draft["content_markdown"], case_title)
                if effort_result["status"] == "success":
                    # Continue to cost estimation phase
                    cost_result = await self._handle_cost_estimation(case_id, case_doc_ref, effort_result["effort_breakdown"], case_title)
                    if cost_result["status"] == "success":
                        # Continue to value analysis phase
                        value_result = await self._handle_value_analysis(case_id, case_doc_ref, approved_prd_content, case_title)
                        return value_result
                    else:
                        return cost_result
                else:
                    return effort_result
                
            else:
                # System design generation failed
                error_message = design_response.get("message", "Failed to generate system design")
                print(f"[OrchestratorAgent] ArchitectAgent failed for case {case_id}: {error_message}")
                
                # Update with error information and revert status
                update_data = {
                    "status": BusinessCaseStatus.PRD_APPROVED.value,  # Revert to PRD_APPROVED
                    "updated_at": updated_at_time,
                    "history": firestore.ArrayUnion([{
                        "timestamp": updated_at_time.isoformat(),
                        "source": "ORCHESTRATOR_AGENT",
                        "type": "ERROR",
                        "content": f"System design generation failed: {error_message}"
                    }])
                }
                
                await asyncio.to_thread(case_doc_ref.update, update_data)
                
                return {
                    "status": "error",
                    "message": f"System design generation failed: {error_message}",
                    "case_id": case_id
                }
                
        except Exception as e:
            error_msg = f"Error in handle_prd_approval for case {case_id}: {str(e)}"
            print(f"[OrchestratorAgent] {error_msg}")
            return {"status": "error", "message": error_msg}

    async def _handle_effort_estimation(self, case_id: str, case_doc_ref, prd_content: str, system_design_content: str, case_title: str) -> Dict[str, Any]:
        """
        Handle effort estimation using PlannerAgent after system design is complete.
        
        Args:
            case_id (str): The business case ID
            case_doc_ref: Firestore document reference
            prd_content (str): PRD content
            system_design_content (str): System design content
            case_title (str): Case title
            
        Returns:
            Dict[str, Any]: Result of effort estimation
        """
        print(f"[OrchestratorAgent] Starting effort estimation for case {case_id}")
        
        try:
            # Update status to PLANNING_IN_PROGRESS
            current_time = datetime.now(timezone.utc)
            update_data = {
                "status": BusinessCaseStatus.PLANNING_IN_PROGRESS.value,
                "updated_at": current_time,
                "history": firestore.ArrayUnion([{
                    "timestamp": current_time.isoformat(),
                    "source": "ORCHESTRATOR_AGENT",
                    "type": "STATUS_UPDATE",
                    "content": f"Status updated to {BusinessCaseStatus.PLANNING_IN_PROGRESS.value}. PlannerAgent initiated for effort estimation."
                }])
            }
            await asyncio.to_thread(case_doc_ref.update, update_data)
            
            # Invoke PlannerAgent
            effort_response = await self.planner_agent.estimate_effort(
                prd_content=prd_content,
                system_design_content=system_design_content,
                case_title=case_title
            )
            
            updated_at_time = datetime.now(timezone.utc)
            
            if effort_response.get("status") == "success" and effort_response.get("effort_breakdown"):
                # Effort estimation successful
                effort_breakdown = effort_response["effort_breakdown"]
                
                # Update case with effort estimate and change status to PLANNING_COMPLETE
                update_data = {
                    "effort_estimate_v1": effort_breakdown,
                    "status": BusinessCaseStatus.PLANNING_COMPLETE.value,
                    "updated_at": updated_at_time,
                    "history": firestore.ArrayUnion([
                        {
                            "timestamp": updated_at_time.isoformat(),
                            "source": "PLANNER_AGENT",
                            "type": "EFFORT_ESTIMATE",
                            "content": f"Effort estimation completed. Total hours: {effort_breakdown.get('total_hours', 'Unknown')}"
                        },
                        {
                            "timestamp": updated_at_time.isoformat(),
                            "source": "ORCHESTRATOR_AGENT",
                            "type": "STATUS_UPDATE",
                            "content": f"Status updated to {BusinessCaseStatus.PLANNING_COMPLETE.value}. Effort estimation completed."
                        }
                    ])
                }
                
                await asyncio.to_thread(case_doc_ref.update, update_data)
                
                print(f"[OrchestratorAgent] Effort estimation completed successfully for case {case_id}")
                return {
                    "status": "success",
                    "message": "Effort estimation completed successfully",
                    "case_id": case_id,
                    "effort_breakdown": effort_breakdown,
                    "new_status": BusinessCaseStatus.PLANNING_COMPLETE.value
                }
                
            else:
                # Effort estimation failed
                error_message = effort_response.get("message", "Failed to estimate effort")
                print(f"[OrchestratorAgent] PlannerAgent failed for case {case_id}: {error_message}")
                
                # Update with error information
                update_data = {
                    "status": BusinessCaseStatus.SYSTEM_DESIGN_DRAFTED.value,  # Revert to previous status
                    "updated_at": updated_at_time,
                    "history": firestore.ArrayUnion([{
                        "timestamp": updated_at_time.isoformat(),
                        "source": "ORCHESTRATOR_AGENT",
                        "type": "ERROR",
                        "content": f"Effort estimation failed: {error_message}"
                    }])
                }
                
                await asyncio.to_thread(case_doc_ref.update, update_data)
                
                return {
                    "status": "error",
                    "message": f"Effort estimation failed: {error_message}",
                    "case_id": case_id
                }
                
        except Exception as e:
            error_msg = f"Error in effort estimation for case {case_id}: {str(e)}"
            print(f"[OrchestratorAgent] {error_msg}")
            return {"status": "error", "message": error_msg}

    async def _handle_cost_estimation(self, case_id: str, case_doc_ref, effort_breakdown: Dict[str, Any], case_title: str) -> Dict[str, Any]:
        """
        Handle cost estimation using CostAnalystAgent after effort estimation is complete.
        
        Args:
            case_id (str): The business case ID
            case_doc_ref: Firestore document reference
            effort_breakdown (Dict[str, Any]): Effort breakdown from PlannerAgent
            case_title (str): Case title
            
        Returns:
            Dict[str, Any]: Result of cost estimation
        """
        print(f"[OrchestratorAgent] Starting cost estimation for case {case_id}")
        
        try:
            # Update status to COSTING_IN_PROGRESS
            current_time = datetime.now(timezone.utc)
            update_data = {
                "status": BusinessCaseStatus.COSTING_IN_PROGRESS.value,
                "updated_at": current_time,
                "history": firestore.ArrayUnion([{
                    "timestamp": current_time.isoformat(),
                    "source": "ORCHESTRATOR_AGENT",
                    "type": "STATUS_UPDATE",
                    "content": f"Status updated to {BusinessCaseStatus.COSTING_IN_PROGRESS.value}. CostAnalystAgent initiated for cost estimation."
                }])
            }
            await asyncio.to_thread(case_doc_ref.update, update_data)
            
            # Invoke CostAnalystAgent
            cost_response = await self.cost_analyst_agent.calculate_cost(
                effort_breakdown=effort_breakdown,
                case_title=case_title
            )
            
            updated_at_time = datetime.now(timezone.utc)
            
            if cost_response.get("status") == "success" and cost_response.get("cost_estimate"):
                # Cost estimation successful
                cost_estimate = cost_response["cost_estimate"]
                
                # Update case with cost estimate and change status to COSTING_COMPLETE
                update_data = {
                    "cost_estimate_v1": cost_estimate,
                    "status": BusinessCaseStatus.COSTING_COMPLETE.value,
                    "updated_at": updated_at_time,
                    "history": firestore.ArrayUnion([
                        {
                            "timestamp": updated_at_time.isoformat(),
                            "source": "COST_ANALYST_AGENT",
                            "type": "COST_ESTIMATE",
                            "content": f"Cost estimation completed. Total cost: ${cost_estimate.get('estimated_cost', 'Unknown'):,.2f} {cost_estimate.get('currency', 'USD')}"
                        },
                        {
                            "timestamp": updated_at_time.isoformat(),
                            "source": "ORCHESTRATOR_AGENT",
                            "type": "STATUS_UPDATE",
                            "content": f"Status updated to {BusinessCaseStatus.COSTING_COMPLETE.value}. Cost estimation completed."
                        }
                    ])
                }
                
                await asyncio.to_thread(case_doc_ref.update, update_data)
                
                print(f"[OrchestratorAgent] Cost estimation completed successfully for case {case_id}")
                return {
                    "status": "success",
                    "message": "Complete business case financial analysis generated successfully",
                    "case_id": case_id,
                    "cost_estimate": cost_estimate,
                    "new_status": BusinessCaseStatus.COSTING_COMPLETE.value
                }
                
            else:
                # Cost estimation failed
                error_message = cost_response.get("message", "Failed to estimate cost")
                print(f"[OrchestratorAgent] CostAnalystAgent failed for case {case_id}: {error_message}")
                
                # Update with error information
                update_data = {
                    "status": BusinessCaseStatus.PLANNING_COMPLETE.value,  # Revert to previous status
                    "updated_at": updated_at_time,
                    "history": firestore.ArrayUnion([{
                        "timestamp": updated_at_time.isoformat(),
                        "source": "ORCHESTRATOR_AGENT",
                        "type": "ERROR",
                        "content": f"Cost estimation failed: {error_message}"
                    }])
                }
                
                await asyncio.to_thread(case_doc_ref.update, update_data)
                
                return {
                    "status": "error",
                    "message": f"Cost estimation failed: {error_message}",
                    "case_id": case_id
                }
                
        except Exception as e:
            error_msg = f"Error in cost estimation for case {case_id}: {str(e)}"
            print(f"[OrchestratorAgent] {error_msg}")
            return {"status": "error", "message": error_msg}

    async def _handle_value_analysis(self, case_id: str, case_doc_ref, prd_content: str, case_title: str) -> Dict[str, Any]:
        """
        Handle value analysis using SalesValueAnalystAgent after cost estimation is complete.
        
        Args:
            case_id (str): The business case ID
            case_doc_ref: Firestore document reference
            prd_content (str): PRD content for value analysis
            case_title (str): Case title
            
        Returns:
            Dict[str, Any]: Result of value analysis
        """
        print(f"[OrchestratorAgent] Starting value analysis for case {case_id}")
        
        try:
            # Update status to VALUE_ANALYSIS_IN_PROGRESS
            current_time = datetime.now(timezone.utc)
            update_data = {
                "status": BusinessCaseStatus.VALUE_ANALYSIS_IN_PROGRESS.value,
                "updated_at": current_time,
                "history": firestore.ArrayUnion([{
                    "timestamp": current_time.isoformat(),
                    "source": "ORCHESTRATOR_AGENT",
                    "type": "STATUS_UPDATE",
                    "content": f"Status updated to {BusinessCaseStatus.VALUE_ANALYSIS_IN_PROGRESS.value}. SalesValueAnalystAgent initiated for value projection."
                }])
            }
            await asyncio.to_thread(case_doc_ref.update, update_data)
            
            # Invoke SalesValueAnalystAgent
            value_response = await self.sales_value_analyst_agent.project_value(
                prd_content=prd_content,
                case_title=case_title
            )
            
            updated_at_time = datetime.now(timezone.utc)
            
            if value_response.get("status") == "success" and value_response.get("value_projection"):
                # Value analysis successful
                value_projection = value_response["value_projection"]
                
                # Update case with value projection and change status to VALUE_ANALYSIS_COMPLETE
                update_data = {
                    "value_projection_v1": value_projection,
                    "status": BusinessCaseStatus.VALUE_ANALYSIS_COMPLETE.value,
                    "updated_at": updated_at_time,
                    "history": firestore.ArrayUnion([
                        {
                            "timestamp": updated_at_time.isoformat(),
                            "source": "SALES_VALUE_ANALYST_AGENT",
                            "type": "VALUE_PROJECTION",
                            "content": f"Value analysis completed. Base scenario: ${value_projection.get('scenarios', [{}])[1].get('value', 'Unknown'):,.0f} {value_projection.get('currency', 'USD')}" if len(value_projection.get('scenarios', [])) > 1 else f"Value projection completed using {value_projection.get('template_used', 'unknown template')}"
                        },
                        {
                            "timestamp": updated_at_time.isoformat(),
                            "source": "ORCHESTRATOR_AGENT",
                            "type": "STATUS_UPDATE",
                            "content": f"Status updated to {BusinessCaseStatus.VALUE_ANALYSIS_COMPLETE.value}. Complete financial analysis generated (effort, cost, and value)."
                        }
                    ])
                }
                
                await asyncio.to_thread(case_doc_ref.update, update_data)
                
                print(f"[OrchestratorAgent] Value analysis completed successfully for case {case_id}")
                return {
                    "status": "success",
                    "message": "Complete business case financial analysis generated successfully (effort, cost, and value)",
                    "case_id": case_id,
                    "value_projection": value_projection,
                    "new_status": BusinessCaseStatus.VALUE_ANALYSIS_COMPLETE.value
                }
                
            else:
                # Value analysis failed
                error_message = value_response.get("message", "Failed to project value")
                print(f"[OrchestratorAgent] SalesValueAnalystAgent failed for case {case_id}: {error_message}")
                
                # Update with error information
                update_data = {
                    "status": BusinessCaseStatus.COSTING_COMPLETE.value,  # Revert to previous status
                    "updated_at": updated_at_time,
                    "history": firestore.ArrayUnion([{
                        "timestamp": updated_at_time.isoformat(),
                        "source": "ORCHESTRATOR_AGENT",
                        "type": "ERROR",
                        "content": f"Value analysis failed: {error_message}"
                    }])
                }
                
                await asyncio.to_thread(case_doc_ref.update, update_data)
                
                return {
                    "status": "error",
                    "message": f"Value analysis failed: {error_message}",
                    "case_id": case_id
                }
                
        except Exception as e:
            error_msg = f"Error in value analysis for case {case_id}: {str(e)}"
            print(f"[OrchestratorAgent] {error_msg}")
            return {"status": "error", "message": error_msg}

    def get_status(self) -> Dict[str, str]:
        """Get the current status of the orchestrator agent"""
        return {
            "name": self.name,
            "status": self.status,
            "description": self.description
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
                return {"status": "error", "message": f"Business case {case_id} not found"}
            
            case_data = doc_snapshot.to_dict()
            if not case_data:
                return {"status": "error", "message": f"Business case {case_id} data is empty"}
            
            current_status = case_data.get("status")
            cost_estimate = case_data.get("cost_estimate_v1")
            value_projection = case_data.get("value_projection_v1")
            
            print(f"[OrchestratorAgent] Checking financial model trigger for case {case_id}")
            print(f"[OrchestratorAgent] Current status: {current_status}")
            print(f"[OrchestratorAgent] Cost estimate exists: {cost_estimate is not None}")
            print(f"[OrchestratorAgent] Value projection exists: {value_projection is not None}")
            
            # Check if both are approved
            if current_status == BusinessCaseStatus.COSTING_APPROVED.value:
                # Cost was just approved, check if value is also approved
                case_doc_ref_refresh = self.db.collection("businessCases").document(case_id)
                doc_snapshot_refresh = await asyncio.to_thread(case_doc_ref_refresh.get)
                case_data_refresh = doc_snapshot_refresh.to_dict()
                
                # Look for VALUE_APPROVED in the history or check if there's a value approval workflow completed
                value_approved = False
                for history_item in case_data_refresh.get("history", []):
                    if history_item.get("messageType") == "VALUE_PROJECTION_APPROVAL":
                        value_approved = True
                        break
                
                if value_approved and cost_estimate and value_projection:
                    print(f"[OrchestratorAgent] Both cost and value are approved, triggering financial model for case {case_id}")
                    return await self._generate_financial_model(case_id, case_doc_ref, cost_estimate, value_projection, case_data.get("title", "Unknown"))
                else:
                    print(f"[OrchestratorAgent] Cost approved but value not yet approved for case {case_id}")
                    return {"status": "success", "message": "Cost approved, waiting for value approval"}
                    
            elif current_status == BusinessCaseStatus.VALUE_APPROVED.value:
                # Value was just approved, check if cost is also approved
                case_doc_ref_refresh = self.db.collection("businessCases").document(case_id)
                doc_snapshot_refresh = await asyncio.to_thread(case_doc_ref_refresh.get)
                case_data_refresh = doc_snapshot_refresh.to_dict()
                
                # Look for COSTING_APPROVED in the history
                cost_approved = False
                for history_item in case_data_refresh.get("history", []):
                    if history_item.get("messageType") == "COST_ESTIMATE_APPROVAL":
                        cost_approved = True
                        break
                
                if cost_approved and cost_estimate and value_projection:
                    print(f"[OrchestratorAgent] Both cost and value are approved, triggering financial model for case {case_id}")
                    return await self._generate_financial_model(case_id, case_doc_ref, cost_estimate, value_projection, case_data.get("title", "Unknown"))
                else:
                    print(f"[OrchestratorAgent] Value approved but cost not yet approved for case {case_id}")
                    return {"status": "success", "message": "Value approved, waiting for cost approval"}
            else:
                print(f"[OrchestratorAgent] Neither cost nor value approval status detected for case {case_id}")
                return {"status": "success", "message": "No action needed - financial model not ready"}
                
        except Exception as e:
            error_msg = f"Error checking financial model trigger for case {case_id}: {str(e)}"
            print(f"[OrchestratorAgent] {error_msg}")
            return {"status": "error", "message": error_msg}

    async def _generate_financial_model(self, case_id: str, case_doc_ref, cost_estimate: Dict[str, Any], value_projection: Dict[str, Any], case_title: str) -> Dict[str, Any]:
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
        print(f"[OrchestratorAgent] Starting financial model generation for case {case_id}")
        
        try:
            # Update status to FINANCIAL_MODEL_IN_PROGRESS
            current_time = datetime.now(timezone.utc)
            update_data = {
                "status": BusinessCaseStatus.FINANCIAL_MODEL_IN_PROGRESS.value,
                "updated_at": current_time,
                "history": firestore.ArrayUnion([{
                    "timestamp": current_time.isoformat(),
                    "source": "ORCHESTRATOR_AGENT",
                    "type": "STATUS_UPDATE",
                    "content": f"Status updated to {BusinessCaseStatus.FINANCIAL_MODEL_IN_PROGRESS.value}. FinancialModelAgent initiated for financial summary generation."
                }])
            }
            await asyncio.to_thread(case_doc_ref.update, update_data)
            
            # Invoke FinancialModelAgent
            financial_response = await self.financial_model_agent.generate_financial_summary(
                cost_estimate=cost_estimate,
                value_projection=value_projection,
                case_title=case_title
            )
            
            updated_at_time = datetime.now(timezone.utc)
            
            if financial_response.get("status") == "success" and financial_response.get("financial_summary"):
                # Financial model generation successful
                financial_summary = financial_response["financial_summary"]
                
                # Add timestamp to the financial summary
                financial_summary["generated_timestamp"] = updated_at_time.isoformat()
                
                # Extract key metrics for history logging
                primary_roi = financial_summary.get("financial_metrics", {}).get("primary_roi_percentage", "Unknown")
                primary_net_value = financial_summary.get("financial_metrics", {}).get("primary_net_value", "Unknown")
                currency = financial_summary.get("currency", "USD")
                
                # Update case with financial summary and change status to FINANCIAL_MODEL_COMPLETE
                update_data = {
                    "financial_summary_v1": financial_summary,
                    "status": BusinessCaseStatus.FINANCIAL_MODEL_COMPLETE.value,
                    "updated_at": updated_at_time,
                    "history": firestore.ArrayUnion([
                        {
                            "timestamp": updated_at_time.isoformat(),
                            "source": "FINANCIAL_MODEL_AGENT",
                            "type": "FINANCIAL_SUMMARY",
                            "content": f"Financial summary generated. ROI: {primary_roi}%, Net Value: {primary_net_value} {currency}"
                        },
                        {
                            "timestamp": updated_at_time.isoformat(),
                            "source": "ORCHESTRATOR_AGENT",
                            "type": "STATUS_UPDATE",
                            "content": f"Status updated to {BusinessCaseStatus.FINANCIAL_MODEL_COMPLETE.value}. Complete financial model generated."
                        }
                    ])
                }
                
                await asyncio.to_thread(case_doc_ref.update, update_data)
                
                print(f"[OrchestratorAgent] Financial model generation completed successfully for case {case_id}")
                return {
                    "status": "success",
                    "message": "Financial model generated successfully",
                    "case_id": case_id,
                    "financial_summary": financial_summary,
                    "new_status": BusinessCaseStatus.FINANCIAL_MODEL_COMPLETE.value
                }
                
            else:
                # Financial model generation failed
                error_message = financial_response.get("message", "Failed to generate financial model")
                print(f"[OrchestratorAgent] FinancialModelAgent failed for case {case_id}: {error_message}")
                
                # Update with error information - revert to a stable state
                update_data = {
                    "status": BusinessCaseStatus.VALUE_APPROVED.value,  # Revert to stable state
                    "updated_at": updated_at_time,
                    "history": firestore.ArrayUnion([{
                        "timestamp": updated_at_time.isoformat(),
                        "source": "ORCHESTRATOR_AGENT",
                        "type": "ERROR",
                        "content": f"Financial model generation failed: {error_message}"
                    }])
                }
                
                await asyncio.to_thread(case_doc_ref.update, update_data)
                
                return {
                    "status": "error",
                    "message": f"Financial model generation failed: {error_message}",
                    "case_id": case_id
                }
                
        except Exception as e:
            error_msg = f"Error in financial model generation for case {case_id}: {str(e)}"
            print(f"[OrchestratorAgent] {error_msg}")
            return {"status": "error", "message": error_msg} 