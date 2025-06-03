"""
Product Manager Agent for handling PRD generation and related tasks.
"""

from typing import Dict, Any, List
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models
from ..core.config import settings

class ProductManagerAgent:
    """
    The Product Manager Agent is responsible for generating and managing
    Product Requirements Documents (PRDs) and related product artifacts.
    """

    def __init__(self):
        self.name = "Product Manager Agent"
        self.description = "Generates and manages Product Requirements Documents (PRDs)."
        self.status = "initialized"
        
        # Use configuration from settings instead of hardcoded values
        self.project_id = settings.google_cloud_project_id or "drfirst-genai-01"
        self.location = settings.vertex_ai_location
        self.model_name = settings.vertex_ai_model_name or "gemini-1.0-pro-001"
        
        try:
            vertexai.init(project=self.project_id, location=self.location)
            self.model = GenerativeModel(self.model_name)
            print(f"ProductManagerAgent: Vertex AI initialized successfully with model {self.model_name}.")
        except Exception as e:
            print(f"ProductManagerAgent: Failed to initialize Vertex AI: {e}")
            self.model = None

    async def draft_prd(self, problem_statement: str, case_title: str, relevant_links: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Generates a comprehensive, structured PRD based on the provided problem statement and title using Vertex AI.
        Returns a Markdown-formatted PRD with clear sections.
        """
        print(f"[ProductManagerAgent] Received request to draft PRD for: {case_title}")
        print(f"[ProductManagerAgent] Problem Statement: {problem_statement}")

        if not self.model:
            return {
                "status": "error",
                "message": "ProductManagerAgent not properly initialized with Vertex AI model.",
                "prd_draft": None
            }

        # Format relevant links for the prompt
        links_context = ""
        if relevant_links:
            links_context += "\n\nAdditional Context from Relevant Links:\n"
            for link_item in relevant_links:
                link_name = link_item.get('name', 'Unnamed Link')
                link_url = link_item.get('url', 'No URL provided')
                links_context += f"- **{link_name}**: {link_url}\n"
            links_context += "\nNote: Consider the context and information from these links when generating the PRD sections.\n"

        # Enhanced prompt for structured PRD generation
        prompt = f"""You are an experienced Product Manager at DrFirst, a healthcare technology company. You are tasked with creating a comprehensive Product Requirements Document (PRD) based on the information provided below.

**Business Case Information:**
- **Title**: {case_title}
- **Problem Statement**: {problem_statement}{links_context}

**Instructions:**
Generate a well-structured PRD document in Markdown format. The PRD should be comprehensive yet concise, suitable as a starting point for development teams and stakeholders. Use the following structure with these exact headings:

# PRD: {case_title}

## 1. Introduction / Problem Statement
Provide a clear overview of the problem this product/feature addresses, the business context, and why this solution is needed now. Include the impact of not solving this problem.

## 2. Goals / Objectives
List 3-4 SMART (Specific, Measurable, Achievable, Relevant, Time-bound) goals that this product/feature aims to achieve. Focus on business outcomes and user value.

## 3. Target Audience / Users
Clearly define the primary and secondary user personas who will benefit from this solution. Include their key characteristics, needs, and pain points relevant to this product.

## 4. Proposed Solution / Scope
Describe the high-level solution approach. Clearly define what is IN SCOPE and OUT OF SCOPE for this product/feature. Include key assumptions and constraints.

## 5. Key Features / User Stories
List 5-8 specific features or user stories using the format: "As a [user type], I want [action/feature] so that [benefit/outcome]." Prioritize the most critical features.

## 6. Success Metrics / KPIs
Define 3-5 measurable success criteria that will indicate the product is achieving its goals. Include both quantitative metrics and qualitative indicators.

## 7. Technical Considerations / Dependencies
Identify any known technical requirements, constraints, integration needs, or dependencies that could impact the solution design or implementation.

## 8. Open Questions / Risks
List 3-5 open questions that need to be resolved and potential risks that should be monitored or mitigated during development.

**Writing Guidelines:**
- Be specific and actionable while maintaining appropriate level of detail for a PRD
- Use healthcare/DrFirst context when relevant
- If specific details cannot be inferred from the problem statement, use placeholders like "[To be determined]" or "[Needs stakeholder input]"
- Ensure each section provides value and isn't just placeholder text
- Keep the overall document between 800-1200 words
- Use professional, clear language appropriate for technical and business stakeholders

Generate the PRD now:"""

        generation_config = {
            "max_output_tokens": settings.vertex_ai_max_tokens,
            "temperature": settings.vertex_ai_temperature,
            "top_p": settings.vertex_ai_top_p,
            "top_k": settings.vertex_ai_top_k,
        }
        
        safety_settings = {
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }

        try:
            print(f"[ProductManagerAgent] Sending enhanced prompt to Vertex AI model: {self.model_name}")
            response = await self.model.generate_content_async(
                [prompt],
                generation_config=generation_config,
                safety_settings=safety_settings,
                stream=False,
            )
            
            if response.candidates and response.candidates[0].content.parts:
                prd_draft_content = response.candidates[0].content.parts[0].text
                print(f"[ProductManagerAgent] Successfully received structured PRD draft from Vertex AI.")
                print(f"[ProductManagerAgent] PRD draft length: {len(prd_draft_content)} characters")
                
                return {
                    "status": "success",
                    "message": "Structured PRD draft generated successfully by Vertex AI.",
                    "prd_draft": {
                        "title": case_title,
                        "content_markdown": prd_draft_content,
                        "version": "1.0.0_structured",
                        "generated_with": f"Vertex AI {self.model_name}",
                        "sections": [
                            "Introduction / Problem Statement",
                            "Goals / Objectives", 
                            "Target Audience / Users",
                            "Proposed Solution / Scope",
                            "Key Features / User Stories",
                            "Success Metrics / KPIs",
                            "Technical Considerations / Dependencies",
                            "Open Questions / Risks"
                        ]
                    }
                }
            else:
                finish_reason = response.candidates[0].finish_reason if response.candidates else 'Unknown'
                safety_ratings = response.candidates[0].safety_ratings if response.candidates else 'N/A'
                message = f"Vertex AI returned no content. Finish Reason: {finish_reason}. Safety Ratings: {safety_ratings}"
                if response.prompt_feedback:
                     message += f" Prompt Feedback: {response.prompt_feedback.block_reason}"
                     if response.prompt_feedback.block_reason_message:
                         message += f" ({response.prompt_feedback.block_reason_message})"
                print(f"[ProductManagerAgent] Error: {message}")
                return {
                    "status": "error",
                    "message": message,
                    "prd_draft": None
                }

        except Exception as e:
            print(f"[ProductManagerAgent] Error generating PRD with Vertex AI: {e}")
            return {
                "status": "error",
                "message": f"An error occurred while generating the PRD with Vertex AI: {str(e)}",
                "prd_draft": None
            }

    def get_status(self) -> Dict[str, str]:
        """Get the current status of the Product Manager agent."""
        return {
            "name": self.name,
            "status": self.status,
            "description": self.description,
            "model": self.model_name,
            "project": self.project_id,
            "location": self.location
        } 