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

class BusinessCaseStatus(Enum):
    """Represents the various states of a business case lifecycle."""
    INTAKE = "INTAKE"
    PRD_DRAFTING = "PRD_DRAFTING"
    PRD_REVIEW = "PRD_REVIEW"
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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

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
        try:
            self.db = firestore.Client()
            print("Firestore client initialized successfully.")
        except Exception as e:
            print(f"Failed to initialize Firestore client: {e}")
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
            
            initial_message = f"Business case '{project_title}' initiated with ID: {case_id}. The problem stated is: '{problem_statement}'. Let's begin structuring the PRD."
            
            case_history = [
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "source": "AGENT",
                    "type": "STATUS_UPDATE",
                    "content": f"Case initiated. Current status: {BusinessCaseStatus.INTAKE.value}"
                },
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "source": "AGENT",
                    "type": "MESSAGE",
                    "content": initial_message
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
            )

            try:
                case_doc_ref = self.db.collection("businessCases").document(case_id)
                await asyncio.to_thread(case_doc_ref.set, case_data.model_dump())
                print(f"Case {case_id} for user {user_id} stored in Firestore.")
            except Exception as e:
                print(f"Error storing case {case_id} in Firestore: {e}")
                # Log the exception e
                return {
                    "status": "error",
                    "message": f"Failed to store business case in database: {str(e)}",
                    "result": None
                }

            return {
                "status": "success",
                "message": f"Case '{project_title}' initiated successfully and stored.",
                "caseId": case_id,
                "initialMessage": initial_message
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