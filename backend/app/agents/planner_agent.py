"""
Planner Agent for estimating development effort based on PRDs and system designs.
"""

from typing import Dict, Any, Optional
import json
import re
import time
from vertexai.generative_models import GenerativeModel
import vertexai.preview.generative_models as generative_models
from ..core.config import settings
from ..core.agent_logging import create_agent_logger
from ..services.vertex_ai_service import VertexAIService
import logging

# Set up logging
logger = logging.getLogger(__name__)


class PlannerAgent:
    """
    The Planner Agent is responsible for estimating development effort by role
    based on approved PRDs and system design documents using AI-powered analysis.
    """

    def __init__(self):
        self.name = "Planner Agent"
        self.description = "Estimates development effort by role using AI analysis of PRD and System Design content."
        self.status = "initialized"

        # Use configuration from settings
        self.project_id = settings.google_cloud_project_id or "drfirst-genai-01"
        self.location = settings.vertex_ai_location
        self.model_name = settings.vertex_ai_model_name or "gemini-2.0-flash-lite"

        try:
            # Use centralized VertexAI service
            from app.services.vertex_ai_service import vertex_ai_service
            vertex_ai_service.initialize()
            
            if vertex_ai_service.is_initialized:
                self.model = GenerativeModel(self.model_name)
                logger.info(
                    f"PlannerAgent: Vertex AI initialized successfully with model {self.model_name}."
                )
            else:
                logger.error("PlannerAgent: VertexAI service not initialized")
                self.model = None
        except Exception as e:
            logger.info(f"PlannerAgent: Failed to initialize with VertexAI service: {e}")
            self.model = None

        logger.info("PlannerAgent: Initialized successfully.")
        self.status = "available"

    async def estimate_effort(
        self, prd_content: str, system_design_content: str, case_title: str, case_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Estimates development effort based on PRD and system design content using AI analysis.

        Args:
            prd_content (str): The content of the approved PRD
            system_design_content (str): The content of the system design
            case_title (str): Title of the business case
            case_id (str, optional): Business case ID for logging

        Returns:
            Dict[str, Any]: Response containing status and effort breakdown
        """
        # Create agent logger
        agent_logger = create_agent_logger("PlannerAgent", case_id)
        
        # Prepare input payload for logging
        input_payload = {
            "prd_content_length": len(prd_content) if prd_content else 0,
            "system_design_content_length": len(system_design_content) if system_design_content else 0,
            "case_title": case_title,
            "has_prd_content": bool(prd_content),
            "has_system_design_content": bool(system_design_content)
        }
        
        # Use logging context manager
        with agent_logger.log_method_execution(
            method_name="estimate_effort",
            input_payload=input_payload
        ) as log_context:
            
            logger.info(f"[PlannerAgent] Received request to estimate effort for: {case_title}")

            try:
                effort_data = None
                methodology = "keyword_based"  # Default fallback
                
                # First try AI-powered estimation
                if self.model:
                    # Get the log_llm function from the context
                    log_llm_func = getattr(log_context, 'log_llm', None)
                    effort_data = await self._ai_effort_estimation(
                        prd_content, system_design_content, case_title, log_llm_func
                    )
                    if effort_data:
                        methodology = "ai_powered"
                        logger.info(
                            f"[PlannerAgent] AI-powered effort estimation completed for {case_title}: {effort_data['total_hours']} total hours"
                        )

                # Fallback to keyword-based estimation if AI fails
                if not effort_data:
                    logger.info(
                        f"[PlannerAgent] Falling back to keyword-based estimation for {case_title}"
                    )
                    effort_data = await self._keyword_effort_estimation(
                        prd_content, system_design_content, case_title
                    )
                    methodology = "keyword_based"

                logger.info(
                    f"[PlannerAgent] {methodology.replace('_', ' ').title()} effort estimation completed for {case_title}: {effort_data['total_hours']} total hours"
                )

                # Prepare output payload
                output_payload = {
                    "status": "success",
                    "message": f"{methodology.replace('_', ' ').title()} effort estimation completed successfully",
                    "effort_breakdown": effort_data,
                    "methodology": methodology,
                    "total_hours": effort_data['total_hours'],
                    "roles_count": len(effort_data['roles'])
                }

                return output_payload

            except Exception as e:
                error_msg = f"Error estimating effort: {str(e)}"
                logger.error(f"[PlannerAgent] {error_msg} for case {case_title}")
                
                # Return error response for logging context
                return {
                    "status": "error", 
                    "message": error_msg, 
                    "effort_breakdown": None,
                    "methodology": "failed"
                }

    async def _ai_effort_estimation(
        self, prd_content: str, system_design_content: str, case_title: str, log_llm_func
    ) -> Dict[str, Any]:
        """
        Use AI to analyze PRD and System Design content for effort estimation.

        Args:
            log_llm_func: LLM logging function from parent context

        Returns:
            Dict[str, Any]: Effort breakdown or None if AI estimation fails
        """
        try:
            # Use centralized content truncation with proper logging
            truncated_prd, prd_was_truncated = VertexAIService.truncate_content(
                prd_content or "No PRD content provided", 6000
            )
            truncated_system_design, sd_was_truncated = VertexAIService.truncate_content(
                system_design_content or "No System Design content provided", 6000
            )
            
            if prd_was_truncated:
                logger.warning("[PlannerAgent] PRD content was truncated for analysis")
            if sd_was_truncated:
                logger.warning("[PlannerAgent] System Design content was truncated for analysis")

            prompt = f"""You are a Senior Project Planner with expertise in healthcare technology projects at DrFirst. Your role is to provide accurate development effort estimates based on technical requirements and industry best practices.

**Project Information:**
- **Title**: {case_title}

--- PRD Content ---
{truncated_prd}

--- System Design Content ---
{truncated_system_design}

**Your Task:**
Analyze the provided PRD and System Design documents to estimate development effort in hours for each role. Consider the following factors:

1. **Technical Complexity**: Features, integrations, UI requirements, data handling, security needs
2. **Healthcare Compliance**: HIPAA, HL7, FHIR, and other healthcare industry standards
3. **Development Phases**: Planning, development, testing, deployment, and documentation
4. **Team Roles**: Product Manager, Lead Developer, Senior Developer, Junior Developer, QA Engineer, DevOps Engineer, UI/UX Designer
5. **Project Scope**: Include realistic buffer time for healthcare project complexities

**Output Requirements:**
Respond ONLY with a valid JSON object in this exact format (no additional text, markdown, or explanations):

{{
  "roles": [
    {{"role": "Product Manager", "hours": <number>}},
    {{"role": "Lead Developer", "hours": <number>}},
    {{"role": "Senior Developer", "hours": <number>}},
    {{"role": "Junior Developer", "hours": <number>}},
    {{"role": "QA Engineer", "hours": <number>}},
    {{"role": "DevOps Engineer", "hours": <number>}},
    {{"role": "UI/UX Designer", "hours": <number>}}
  ],
  "total_hours": <sum_of_all_hours>,
  "estimated_duration_weeks": <number>,
  "complexity_assessment": "<Low|Medium|High|Very High>",
  "notes": "<brief rationale for the estimate in 1-2 sentences>"
}}

**Important**: Ensure your response is valid JSON only. No markdown formatting or additional text."""

            # Configure generation settings for structured output
            generation_config = {
                "max_output_tokens": 1024,
                "temperature": 0.2,  # Low temperature for consistent, structured output
                "top_p": 0.8,
                "top_k": 20,
            }

            logger.info("[PlannerAgent] Calling AI model for effort estimation...")
            
            # Use centralized retry logic for robust LLM call
            response_text = await VertexAIService.generate_with_retry(
                model=self.model,
                prompt=prompt,
                generation_config=generation_config,
                model_name=self.model_name,
                max_retries=2,
                timeout_seconds=120,
                log_llm_call=log_llm_func,
                agent_name="PlannerAgent"
            )

            if response_text:
                logger.info(f"[PlannerAgent] AI response received: {response_text[:200]}...")

                # Use centralized JSON extraction
                effort_data = VertexAIService.extract_json_from_text(response_text)
                
                if effort_data and self._validate_effort_data(effort_data):
                    logger.info("[PlannerAgent] Successfully parsed and validated AI effort estimation")
                    return effort_data
                else:
                    logger.warning("[PlannerAgent] Failed to extract valid JSON from AI response")
                    logger.debug(f"[PlannerAgent] Raw response: {response_text}")
                    return None
            else:
                logger.warning("[PlannerAgent] No valid response from AI model after retries")
                return None

        except Exception as e:
            logger.error(f"[PlannerAgent] Error in AI effort estimation: {str(e)}")
            return None

    async def _keyword_effort_estimation(
        self, prd_content: str, system_design_content: str, case_title: str
    ) -> Dict[str, Any]:
        """
        Fallback keyword-based effort estimation when AI is not available.

        Returns:
            Dict[str, Any]: Effort breakdown based on keyword analysis
        """
        # Combine content for analysis
        combined_content = f"{prd_content} {system_design_content}".lower()

        # Define complexity keywords and their impact weights
        complexity_indicators = {
            # High complexity features
            "machine learning": 80,
            "ai integration": 80,
            "natural language": 60,
            "real-time": 50,
            "microservices": 60,
            "distributed": 50,
            "blockchain": 100,
            "encryption": 40,
            "hipaa": 30,
            # Medium complexity features
            "api integration": 30,
            "database": 25,
            "authentication": 25,
            "mobile app": 40,
            "web application": 30,
            "dashboard": 25,
            "reporting": 30,
            "notification": 20,
            "search": 25,
            # Basic features
            "crud operations": 15,
            "form": 10,
            "validation": 10,
            "user management": 20,
            "admin panel": 25,
            "email": 15,
            # Integration complexity
            "third party": 35,
            "external api": 35,
            "hl7": 40,
            "fhir": 40,
            "ehr integration": 60,
            "payment": 45,
            # Technical complexity
            "scalability": 30,
            "performance": 25,
            "caching": 20,
            "load balancing": 35,
            "monitoring": 25,
            "logging": 15,
        }

        # Count keyword occurrences and calculate base effort
        total_complexity_score = 0
        found_keywords = []

        for keyword, weight in complexity_indicators.items():
            count = combined_content.count(keyword)
            if count > 0:
                total_complexity_score += weight * count
                found_keywords.append(f"{keyword} ({count}x)")

        # Base hours by role for a simple project
        base_hours = {
            "Product Manager": 15,
            "Lead Developer": 25,
            "Senior Developer": 40,
            "Junior Developer": 20,
            "QA Engineer": 20,
            "DevOps Engineer": 10,
            "UI/UX Designer": 15,
        }

        # Apply complexity multiplier
        if total_complexity_score < 50:
            complexity = "Low"
            multiplier = 1.0
        elif total_complexity_score < 150:
            complexity = "Medium"
            multiplier = 1.5
        elif total_complexity_score < 300:
            complexity = "High"
            multiplier = 2.2
        else:
            complexity = "Very High"
            multiplier = 3.0

        # Calculate final effort
        roles = []
        total_hours = 0

        for role, base_hour in base_hours.items():
            hours = int(base_hour * multiplier)
            roles.append({"role": role, "hours": hours})
            total_hours += hours

        # Estimate duration (assuming 35 hours per week total capacity across team)
        estimated_weeks = max(2, int(total_hours / 35))

        notes = (
            f"Keyword-based estimation (complexity score: {total_complexity_score}). "
        )
        if found_keywords:
            notes += f"Key indicators: {', '.join(found_keywords[:5])}"
        else:
            notes += "Standard baseline estimate applied."

        return {
            "roles": roles,
            "total_hours": total_hours,
            "estimated_duration_weeks": estimated_weeks,
            "complexity_assessment": complexity,
            "notes": notes,
        }

    def _validate_effort_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate the structure of effort estimation data.

        Args:
            data: The effort data to validate

        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = [
            "roles",
            "total_hours",
            "estimated_duration_weeks",
            "complexity_assessment",
            "notes",
        ]

        # Check required fields exist
        for field in required_fields:
            if field not in data:
                logger.info(f"[PlannerAgent] Missing required field: {field}")
                return False

        # Check roles structure
        if not isinstance(data["roles"], list) or len(data["roles"]) == 0:
            logger.info("[PlannerAgent] Invalid roles structure")
            return False

        for role_data in data["roles"]:
            if (
                not isinstance(role_data, dict)
                or "role" not in role_data
                or "hours" not in role_data
            ):
                logger.info("[PlannerAgent] Invalid role data structure")
                return False
            if (
                not isinstance(role_data["hours"], (int, float))
                or role_data["hours"] < 0
            ):
                logger.info("[PlannerAgent] Invalid hours value")
                return False

        # Check other fields
        if not isinstance(data["total_hours"], (int, float)) or data["total_hours"] < 0:
            logger.info("[PlannerAgent] Invalid total_hours")
            return False

        if (
            not isinstance(data["estimated_duration_weeks"], (int, float))
            or data["estimated_duration_weeks"] < 0
        ):
            logger.info("[PlannerAgent] Invalid estimated_duration_weeks")
            return False

        valid_complexity = ["Low", "Medium", "High", "Very High"]
        if data["complexity_assessment"] not in valid_complexity:
            logger.info("[PlannerAgent] Invalid complexity_assessment")
            return False

        return True

    def get_status(self) -> Dict[str, str]:
        """Get the current status of the planner agent"""
        return {
            "name": self.name,
            "status": self.status,
            "description": self.description,
        }
