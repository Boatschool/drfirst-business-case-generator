"""
Architect Agent for generating system design proposals based on PRDs.
"""

from typing import Dict, Any, List
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models
from ..core.config import settings
import logging

# Set up logging
logger = logging.getLogger(__name__)

class ArchitectAgent:
    """
    The Architect Agent is responsible for generating system design proposals
    based on approved Product Requirements Documents (PRDs).
    """

    def __init__(self):
        self.name = "Architect Agent"
        self.description = "Generates system design proposals based on PRDs."
        self.status = "initialized"
        
        # Use configuration from settings
        self.project_id = settings.google_cloud_project_id or "drfirst-genai-01"
        self.location = settings.vertex_ai_location
        self.model_name = settings.vertex_ai_model_name or "gemini-1.0-pro-001"
        
        try:
            vertexai.init(project=self.project_id, location=self.location)
            self.model = GenerativeModel(self.model_name)
            print(f"ArchitectAgent: Vertex AI initialized successfully with model {self.model_name}.")
            self.status = "available"
        except Exception as e:
            print(f"ArchitectAgent: Failed to initialize Vertex AI: {e}")
            self.model = None
            self.status = "error"

    async def generate_system_design(self, prd_content: str, case_title: str) -> Dict[str, Any]:
        """
        Generates a system design proposal based on the approved PRD content.
        
        Args:
            prd_content (str): The content of the approved PRD
            case_title (str): Title of the business case
            
        Returns:
            Dict[str, Any]: Response containing status and system design content
        """
        print(f"[ArchitectAgent] Received request to generate system design for: {case_title}")
        
        if not self.model:
            return {
                "status": "error",
                "message": "ArchitectAgent not properly initialized with Vertex AI model.",
                "system_design_draft": None
            }

        try:
            # Construct system design generation prompt
            system_design_prompt = f"""You are a Senior Software Architect with expertise in healthcare technology and cloud-based systems. Based on the following approved PRD for the project titled '{case_title}', generate a comprehensive high-level system design.

--- PRD Content ---
{prd_content}
--- End PRD Content ---

Please provide a structured system design that includes:

1. **Architecture Overview**
   - High-level architecture pattern (microservices, monolithic, serverless, etc.)
   - Key architectural principles and design philosophy

2. **Core Components**
   - Main system components and their responsibilities
   - Data flow between components
   - External integrations and dependencies

3. **Technology Stack Recommendations**
   - Frontend technologies and frameworks
   - Backend technologies and frameworks
   - Database solutions
   - Cloud services and infrastructure

4. **Data Architecture**
   - Data models and storage solutions
   - Data flow and processing patterns
   - Security and compliance considerations

5. **Infrastructure & Deployment**
   - Cloud platform recommendations (preferably Google Cloud Platform)
   - Containerization and orchestration strategy
   - CI/CD pipeline considerations

6. **Security & Compliance**
   - Authentication and authorization approach
   - Data protection and privacy measures
   - Healthcare compliance considerations (HIPAA, etc.)

7. **Scalability & Performance**
   - Scalability strategies
   - Performance optimization approaches
   - Monitoring and observability

8. **Implementation Phases**
   - Suggested development phases
   - Dependencies and critical path items

Please provide specific, actionable recommendations that would be suitable for a healthcare technology company like DrFirst. Focus on proven technologies and patterns that support enterprise-grade applications.

Format your response in clear markdown with headers and bullet points for easy reading."""

            # Use generation settings optimized for technical content
            generation_config = {
                "max_output_tokens": 8192,  # Allow for comprehensive design
                "temperature": 0.4,  # Balanced creativity and consistency
                "top_p": 0.8,
                "top_k": 40,
            }
            
            safety_settings = {
                generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
            
            logger.info(f"[ArchitectAgent] Generating system design for case: {case_title}")
            response = await self.model.generate_content_async(
                [system_design_prompt],
                generation_config=generation_config,
                safety_settings=safety_settings,
                stream=False,
            )
            
            if response.candidates and response.candidates[0].content.parts:
                system_design_content = response.candidates[0].content.parts[0].text.strip()
                
                system_design_draft = {
                    "content_markdown": system_design_content,
                    "generated_by": "ArchitectAgent",
                    "version": "v1",
                    "generated_at": f"{logger.info('System design generation timestamp')}"
                }
                
                logger.info(f"[ArchitectAgent] Successfully generated system design for {case_title}")
                print(f"[ArchitectAgent] Generated system design ({len(system_design_content)} characters)")
                
                return {
                    "status": "success",
                    "message": "System design generated successfully",
                    "system_design_draft": system_design_draft
                }
            else:
                logger.warning(f"[ArchitectAgent] No system design generated for {case_title}")
                return {
                    "status": "error",
                    "message": "No system design content generated by Vertex AI",
                    "system_design_draft": None
                }
                
        except Exception as e:
            error_msg = f"Error generating system design: {str(e)}"
            logger.error(f"[ArchitectAgent] {error_msg} for case {case_title}")
            print(f"[ArchitectAgent] {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "system_design_draft": None
            }

    async def design_architecture(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Legacy method for compatibility - redirects to generate_system_design
        """
        prd_content = requirements.get("prd_content", "")
        case_title = requirements.get("case_title", "Untitled Case")
        return await self.generate_system_design(prd_content, case_title)

    async def estimate_implementation_effort(self, architecture: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate implementation effort and timeline (placeholder for future enhancement)
        """
        return {
            "estimated_duration": "TBD",
            "team_size_recommendation": "TBD", 
            "complexity_assessment": "TBD"
        }

    async def identify_risks(self, technical_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify technical risks and mitigation strategies (placeholder for future enhancement)
        """
        return []

    async def recommend_technologies(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Recommend appropriate technologies and tools (placeholder for future enhancement)
        """
        return []

    def get_status(self) -> Dict[str, str]:
        """Get the current status of the architect agent"""
        return {
            "name": self.name,
            "status": self.status,
            "description": self.description
        } 