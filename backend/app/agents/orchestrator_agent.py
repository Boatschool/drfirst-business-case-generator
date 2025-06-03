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

class BusinessCaseStatus(Enum):
    """Represents the various states of a business case lifecycle."""
    INTAKE = "INTAKE"
    PRD_DRAFTING = "PRD_DRAFTING"
    PRD_REVIEW = "PRD_REVIEW"
    PRD_APPROVED = "PRD_APPROVED"
    PRD_REJECTED = "PRD_REJECTED"
    SYSTEM_DESIGN_DRAFTING = "SYSTEM_DESIGN_DRAFTING"
    SYSTEM_DESIGN_REVIEW = "SYSTEM_DESIGN_REVIEW"
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
    
    def get_status(self) -> Dict[str, str]:
        """Get the current status of the orchestrator agent"""
        return {
            "name": self.name,
            "status": self.status,
            "description": self.description
        } 