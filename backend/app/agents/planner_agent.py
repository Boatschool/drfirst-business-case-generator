"""
Planner Agent for estimating development effort based on PRDs and system designs.
"""

from typing import Dict, Any
import json
import re
import vertexai
from vertexai.generative_models import GenerativeModel
import vertexai.preview.generative_models as generative_models
from ..core.config import settings
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
            vertexai.init(project=self.project_id, location=self.location)
            self.model = GenerativeModel(self.model_name)
            logger.info(
                f"PlannerAgent: Vertex AI initialized successfully with model {self.model_name}."
            )
        except Exception as e:
            logger.info(f"PlannerAgent: Failed to initialize Vertex AI: {e}")
            self.model = None

        logger.info("PlannerAgent: Initialized successfully.")
        self.status = "available"

    async def estimate_effort(
        self, prd_content: str, system_design_content: str, case_title: str
    ) -> Dict[str, Any]:
        """
        Estimates development effort based on PRD and system design content using AI analysis.

        Args:
            prd_content (str): The content of the approved PRD
            system_design_content (str): The content of the system design
            case_title (str): Title of the business case

        Returns:
            Dict[str, Any]: Response containing status and effort breakdown
        """
        logger.info(f"[PlannerAgent] Received request to estimate effort for: {case_title}")

        try:
            # First try AI-powered estimation
            if self.model:
                effort_data = await self._ai_effort_estimation(
                    prd_content, system_design_content, case_title
                )
                if effort_data:
                    logger.info(
                        f"[PlannerAgent] AI-powered effort estimation completed for {case_title}: {effort_data['total_hours']} total hours"
                    )
                    logger.info(
                        f"[PlannerAgent] Generated AI-powered effort estimate: {effort_data['total_hours']} total hours across {len(effort_data['roles'])} roles"
                    )

                    return {
                        "status": "success",
                        "message": "AI-powered effort estimation completed successfully",
                        "effort_breakdown": effort_data,
                    }

            # Fallback to keyword-based estimation if AI fails
            logger.info(
                f"[PlannerAgent] Falling back to keyword-based estimation for {case_title}"
            )
            effort_data = await self._keyword_effort_estimation(
                prd_content, system_design_content, case_title
            )

            logger.info(
                f"[PlannerAgent] Keyword-based effort estimation completed for {case_title}: {effort_data['total_hours']} total hours"
            )
            logger.info(
                f"[PlannerAgent] Generated keyword-based effort estimate: {effort_data['total_hours']} total hours across {len(effort_data['roles'])} roles"
            )

            return {
                "status": "success",
                "message": "Keyword-based effort estimation completed successfully",
                "effort_breakdown": effort_data,
            }

        except Exception as e:
            error_msg = f"Error estimating effort: {str(e)}"
            logger.error(f"[PlannerAgent] {error_msg} for case {case_title}")
            logger.info(f"[PlannerAgent] {error_msg}")
            return {"status": "error", "message": error_msg, "effort_breakdown": None}

    async def _ai_effort_estimation(
        self, prd_content: str, system_design_content: str, case_title: str
    ) -> Dict[str, Any]:
        """
        Use AI to analyze PRD and System Design content for effort estimation.

        Returns:
            Dict[str, Any]: Effort breakdown or None if AI estimation fails
        """
        try:
            # Truncate content to avoid token limits
            max_content_length = 6000
            truncated_prd = (
                prd_content[:max_content_length]
                if prd_content
                else "No PRD content provided"
            )
            truncated_system_design = (
                system_design_content[:max_content_length]
                if system_design_content
                else "No System Design content provided"
            )

            prompt = """You are a Senior Project Planner with expertise in healthcare technology projects. Based on the following PRD and System Design for a project titled '{case_title}', estimate the development effort in hours for each role.

--- PRD Content ---
{truncated_prd}

--- System Design Content ---
{truncated_system_design}

Instructions:
1. Analyze the complexity of features, integrations, UI requirements, data handling, security needs, and technical challenges
2. Consider healthcare industry standards and compliance requirements (HIPAA, HL7, etc.)
3. Estimate effort for these roles: Product Manager, Lead Developer, Senior Developer, Junior Developer, QA Engineer, DevOps Engineer, UI/UX Designer
4. Provide realistic hours that account for planning, development, testing, and deployment
5. Include a complexity assessment (Low, Medium, High, Very High)
6. Estimate project duration in weeks

Respond ONLY with a valid JSON object in this exact format:
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

Make sure your response is valid JSON without any additional text or markdown formatting."""

            # Configure generation settings for structured output
            generation_config = {
                "max_output_tokens": 1024,
                "temperature": 0.2,  # Low temperature for consistent, structured output
                "top_p": 0.8,
                "top_k": 20,
            }

            safety_settings = {
                generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }

            logger.info("[PlannerAgent] Calling AI model for effort estimation...")
            response = await self.model.generate_content_async(
                [prompt],
                generation_config=generation_config,
                safety_settings=safety_settings,
                stream=False,
            )

            if response.candidates and response.candidates[0].content.parts:
                response_text = response.candidates[0].content.parts[0].text.strip()
                logger.info(f"[PlannerAgent] AI response received: {response_text[:200]}...")

                # Parse JSON response
                try:
                    # Clean the response to extract just the JSON
                    json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                        effort_data = json.loads(json_str)

                        # Validate the structure
                        if self._validate_effort_data(effort_data):
                            logger.info(
                                "[PlannerAgent] Successfully parsed AI effort estimation"
                            )
                            return effort_data
                        else:
                            logger.info("[PlannerAgent] AI response validation failed")
                            return None
                    else:
                        logger.info("[PlannerAgent] No valid JSON found in AI response")
                        return None

                except json.JSONDecodeError as e:
                    logger.info(f"[PlannerAgent] Failed to parse AI response as JSON: {e}")
                    return None
            else:
                logger.info("[PlannerAgent] No valid response from AI model")
                return None

        except Exception as e:
            logger.info(f"[PlannerAgent] Error in AI effort estimation: {str(e)}")
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
