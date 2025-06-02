"""
Product Manager Agent for handling PRD generation and related tasks.
"""

from typing import Dict, Any, List
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models

# Configuration for Vertex AI
PROJECT_ID = "drfirst-genai-01"  # TODO: Consider moving to config or env variable
LOCATION = "us-central1"    # TODO: Consider moving to config or env variable
MODEL_NAME = "gemini-1.0-pro-001" # Or your preferred model

class ProductManagerAgent:
    """
    The Product Manager Agent is responsible for generating and managing
    Product Requirements Documents (PRDs) and related product artifacts.
    """

    def __init__(self):
        self.name = "Product Manager Agent"
        self.description = "Generates and manages Product Requirements Documents (PRDs)."
        self.status = "initialized"
        
        try:
            vertexai.init(project=PROJECT_ID, location=LOCATION)
            self.model = GenerativeModel(MODEL_NAME)
            print(f"ProductManagerAgent: Vertex AI initialized successfully with model {MODEL_NAME}.")
        except Exception as e:
            print(f"ProductManagerAgent: Failed to initialize Vertex AI: {e}")
            self.model = None

    async def draft_prd(self, problem_statement: str, case_title: str, relevant_links: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Generates a draft PRD based on the provided problem statement and title using Vertex AI.
        """
        print(f"[ProductManagerAgent] Received request to draft PRD for: {case_title}")
        print(f"[ProductManagerAgent] Problem Statement: {problem_statement}")

        if not self.model:
            return {
                "status": "error",
                "message": "ProductManagerAgent not properly initialized with Vertex AI model.",
                "prd_draft": None
            }

        links_text = ""
        if relevant_links:
            links_text += "\n\nConsider these relevant links:\n"
            for link_item in relevant_links:
                links_text += f"- {link_item.get('name', 'Unnamed Link')}: {link_item.get('url', 'No URL provided')}\n"

        prompt = f"""
        Role: You are a Product Manager tasked with creating an initial Product Requirements Document (PRD).
        Business Case Title: {case_title}
        Problem Statement: {problem_statement}
        {links_text}

        Instructions:
        Generate a concise, well-structured PRD draft. The PRD should include the following sections:
        1.  **Introduction**: Briefly describe the product/feature and the problem it solves.
        2.  **Goals**: List 2-3 high-level goals for this product/feature.
        3.  **Target Audience**: Briefly describe the primary users.
        4.  **Key Features/User Stories**: List 3-5 key features or user stories (e.g., As a [user type], I want [action] so that [benefit]).
        5.  **Success Metrics**: Suggest 1-2 key metrics to measure success.
        6.  **Open Questions/Considerations**: List 1-2 open questions or items for further discussion.

        Keep the content for each section brief and to the point, suitable for an initial draft. The overall PRD should be around 300-500 words.
        Format the output in Markdown.
        """

        generation_config = {
            "max_output_tokens": 2048,
            "temperature": 0.7, # Adjusted for more creative but still structured output
            "top_p": 0.95,
        }
        safety_settings = {
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }

        try:
            print(f"[ProductManagerAgent] Sending prompt to Vertex AI model: {MODEL_NAME}")
            response = await self.model.generate_content_async(
                [prompt],
                generation_config=generation_config,
                safety_settings=safety_settings,
                stream=False,
            )
            
            if response.candidates and response.candidates[0].content.parts:
                prd_draft_content = response.candidates[0].content.parts[0].text
                print(f"[ProductManagerAgent] Successfully received PRD draft from Vertex AI.")
                return {
                    "status": "success",
                    "message": "PRD draft generated successfully by Vertex AI.",
                    "prd_draft": {
                        "title": case_title,
                        "content_markdown": prd_draft_content,
                        "version": "0.1.0_vertex_ai"
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
            "description": self.description
        } 