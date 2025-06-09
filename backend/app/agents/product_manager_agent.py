"""
Product Manager Agent for handling PRD generation and related tasks.
"""

from typing import Dict, Any, List, Optional
import uuid
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models
from pydantic import ValidationError

from ..core.config import settings
from ..services.prompt_service import PromptService
from ..services.vertex_ai_service import VertexAIService
from ..utils.web_utils import fetch_web_content
from google.cloud import firestore
from ..models.agent_models import DraftPrdInput, DraftPrdOutput, PrdDraft, AgentStatus
import logging
from datetime import datetime
import time

# Set up logging
logger = logging.getLogger(__name__)


class ProductManagerAgent:
    """
    The Product Manager Agent is responsible for generating and managing
    Product Requirements Documents (PRDs) and related product artifacts.
    """

    def __init__(self, prompt_service: PromptService = None):
        self.name = "ProductManagerAgent"
        self.description = (
            "Generates and manages Product Requirements Documents (PRDs)."
        )
        self.status = "initialized"

        # Use configuration from settings instead of hardcoded values
        self.project_id = settings.google_cloud_project_id or "drfirst-genai-01"
        self.location = settings.vertex_ai_location
        self.model_name = settings.vertex_ai_model_name or "gemini-1.0-pro-001"

        # Log configuration details for debugging
        logger.info(f"ProductManagerAgent: Initializing with project_id={self.project_id}, location={self.location}, model_name={self.model_name}")

        # Initialize prompt service
        if prompt_service:
            self.prompt_service = prompt_service
        else:
            # Fallback initialization
            db = firestore.Client()
            self.prompt_service = PromptService(db)

        try:
            logger.info(f"ProductManagerAgent: Attempting to initialize with centralized VertexAI service")
            # Use centralized VertexAI service
            from app.services.vertex_ai_service import vertex_ai_service
            vertex_ai_service.initialize(project_id=self.project_id, location=self.location)
            
            if vertex_ai_service.is_initialized:
                logger.info(f"ProductManagerAgent: VertexAI service initialized, creating model {self.model_name}")
                self.model = GenerativeModel(self.model_name)
                logger.info(
                    f"ProductManagerAgent: Vertex AI initialized successfully with model {self.model_name}."
                )
            else:
                logger.error("ProductManagerAgent: VertexAI service not initialized")
                self.model = None
        except Exception as e:
            logger.error(f"ProductManagerAgent: Failed to initialize with VertexAI service: {e}")
            logger.error(f"ProductManagerAgent: Project ID: {self.project_id}, Location: {self.location}, Model: {self.model_name}")
            self.model = None

    async def summarize_content(
        self, text_content: str, link_name: str = "content"
    ) -> str:
        """
        Generate a concise summary of text content using Vertex AI with robust retry logic.

        Args:
            text_content (str): The text content to summarize
            link_name (str): Name of the source for context

        Returns:
            str: Concise summary of the content, or empty string if summarization fails
        """
        if not self.model:
            logger.warning("Vertex AI model not available for content summarization")
            return ""

        if not text_content or len(text_content.strip()) < 50:
            logger.info(f"Content from {link_name} too short for summarization")
            return ""

        try:
            # Truncate content to avoid overly long prompts
            truncated_content, was_truncated = VertexAIService.truncate_content(
                text_content, 8000, "\n\n[Content truncated for summarization...]"
            )
            
            if was_truncated:
                logger.warning(f"[ProductManagerAgent] Content from {link_name} was truncated for summarization")

            # Create a focused prompt for summarization
            summarization_prompt = f"""You are a Senior Product Manager analyzing content for business case development. Please analyze the following text content and provide a concise summary focusing on information relevant to a software/technology project or business case:

Text Content:
{truncated_content}

Instructions:
- Extract key points relevant to technology projects, product development, or business requirements
- Focus on problems, solutions, requirements, goals, or technical details
- Provide 2-3 bullet points maximum
- Keep each point under 100 words
- If the content is not relevant to software/technology projects, state "No relevant business/technical information found"
- Be concise and actionable

Summary:"""

            # Use conservative generation settings for summarization
            generation_config = {
                "max_output_tokens": 512,  # Shorter for summaries
                "temperature": 0.3,  # More focused and consistent
                "top_p": 0.8,
                "top_k": 20,
            }

            logger.info(
                f"[ProductManagerAgent] Generating summary for content from: {link_name}"
            )
            
            # Use centralized retry logic with timeout
            summary = await VertexAIService.generate_with_retry(
                model=self.model,
                prompt=summarization_prompt,
                generation_config=generation_config,
                model_name=self.model_name,
                max_retries=2,
                timeout_seconds=60,  # Shorter timeout for summaries
                agent_name="ProductManagerAgent"
            )

            if summary:
                logger.info(
                    f"[ProductManagerAgent] Successfully generated summary for {link_name}"
                )
                return summary.strip()
            else:
                logger.warning(
                    f"[ProductManagerAgent] No summary generated for {link_name}"
                )
                return ""

        except Exception as e:
            logger.error(
                f"[ProductManagerAgent] Error generating summary for {link_name}: {str(e)}"
            )
            return ""

    async def draft_prd(
        self,
        input_data: 'DraftPrdInput',
        case_id: Optional[str] = None,
    ) -> 'DraftPrdOutput':
        """
        Generates a comprehensive, structured PRD based on the provided problem statement and title using Vertex AI.
        Returns a Markdown-formatted PRD with clear sections.
        """
        import time
        
        # Import the agent logging utilities
        from ..core.agent_logging import create_agent_logger
        
        # Create enhanced logger for this operation
        agent_logger = create_agent_logger("ProductManagerAgent", case_id)
        
        try:
            # Validate input
            if not isinstance(input_data, DraftPrdInput):
                input_data = DraftPrdInput(**input_data)
        except ValidationError as e:
            return DraftPrdOutput(
                status=AgentStatus.ERROR,
                message=f"Input validation failed: {str(e)}",
                operation_id=str(uuid.uuid4()),
                prd_draft=None
            )
        
        # Extract values from validated input
        case_title = input_data.case_title
        problem_statement = input_data.problem_statement
        relevant_links = input_data.relevant_links
        
        # Prepare input payload for logging
        input_payload = {
            "case_title": case_title,
            "problem_statement": problem_statement,
            "relevant_links": relevant_links,
            "case_id": case_id
        }
        
        # Use context manager for comprehensive logging
        start_time = time.time()
        with agent_logger.log_method_execution('draft_prd', input_payload, case_id) as ctx:
            trace_id = ctx['trace_id']
            log_llm_call = ctx['log_llm']

            if not self.model:
                return DraftPrdOutput(
                    status=AgentStatus.ERROR,
                    message="ProductManagerAgent not properly initialized with Vertex AI model.",
                    operation_id=trace_id,
                    prd_draft=None
                )

            # Process relevant links: fetch content and generate summaries
            links_context = ""
            if relevant_links:
                logger.info(
                    f"[ProductManagerAgent] Processing {len(relevant_links)} relevant links for context..."
                )
                links_context += "\n\nAdditional Context from Relevant Links:\n"

                for link_item in relevant_links:
                    link_name = link_item.get("name", "Unnamed Link")
                    link_url = link_item.get("url", "No URL provided")

                    if not link_url or link_url == "No URL provided":
                        links_context += f"- **{link_name}**: No URL provided\n"
                        continue

                    logger.info(
                        f"[ProductManagerAgent] Fetching content from: {link_name} ({link_url})"
                    )

                    # Attempt to fetch and summarize content from the URL
                    try:
                        web_result = await fetch_web_content(link_url)

                        if web_result["success"] and web_result["content"]:
                            # Generate summary of the fetched content
                            summary = await self.summarize_content(
                                web_result["content"], link_name
                            )

                            if summary and summary.strip():
                                links_context += f"- **{link_name}** ({link_url}):\n"
                                links_context += f"  Content Summary: {summary}\n\n"
                                logger.info(
                                    f"[ProductManagerAgent] Successfully processed content from {link_name}"
                                )
                            else:
                                links_context += f"- **{link_name}** ({link_url}): Content retrieved but no relevant summary generated\n\n"
                                logger.info(
                                    f"[ProductManagerAgent] Content retrieved from {link_name} but summarization failed or not relevant"
                                )
                        else:
                            error_msg = web_result.get("error", "Unknown error")
                            links_context += f"- **{link_name}** ({link_url}): Unable to fetch content - {error_msg}\n\n"
                            logger.info(
                                f"[ProductManagerAgent] Failed to fetch content from {link_name}: {error_msg}"
                            )

                    except Exception as e:
                        error_msg = f"Unexpected error: {str(e)}"
                        links_context += f"- **{link_name}** ({link_url}): {error_msg}\n\n"
                        logger.info(
                            f"[ProductManagerAgent] Unexpected error processing {link_name}: {str(e)}"
                        )

                if links_context.strip() == "Additional Context from Relevant Links:":
                    # No successful content was retrieved
                    links_context += (
                        "No content could be retrieved from the provided links.\n"
                    )
                else:
                    links_context += "Note: Consider the context and information from these links when generating the PRD sections.\n"

            # Try to get configurable prompt from Firestore
            prompt_variables = {
                "case_title": case_title,
                "problem_statement": problem_statement,
                "links_context": links_context,
            }

            configurable_prompt = await self.prompt_service.render_prompt(
                "ProductManagerAgent", "prd_generation", prompt_variables
            )

            if configurable_prompt:
                prompt = configurable_prompt
                logger.info("[ProductManagerAgent] Using configurable prompt from Firestore")
            else:
                logger.info(
                    "[ProductManagerAgent] No configurable prompt found, using fallback default prompt"
                )
                # Fallback to hardcoded prompt
                prompt_template = """You are an experienced Product Manager at DrFirst, a healthcare technology company. You are tasked with creating a comprehensive Product Requirements Document (PRD) based on the information provided below.

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
- **IMPORTANT**: Use proper Markdown formatting with clear headings (##), bullet points (-), and proper line spacing for excellent readability
- Leave blank lines between sections and use consistent formatting throughout

Generate the PRD now:"""

                # Format the prompt template with actual values
                prompt = prompt_template.format(
                    case_title=case_title,
                    problem_statement=problem_statement,
                    links_context=links_context
                )
                logger.info(f"[ProductManagerAgent] Formatted prompt with case_title='{case_title}', problem_statement length={len(problem_statement)}")

            generation_config = {
                "max_output_tokens": settings.vertex_ai_max_tokens,
                "temperature": settings.vertex_ai_temperature,
                "top_p": settings.vertex_ai_top_p,
                "top_k": settings.vertex_ai_top_k,
            }

            try:
                logger.info(
                    f"[ProductManagerAgent] Sending enhanced prompt to Vertex AI model: {self.model_name}"
                )
                
                # Use centralized retry logic with robust error handling
                prd_draft_content = await VertexAIService.generate_with_retry(
                    model=self.model,
                    prompt=prompt,
                    generation_config=generation_config,
                    model_name=self.model_name,
                    max_retries=3,  # More retries for critical PRD generation
                    timeout_seconds=180,  # Longer timeout for PRD generation
                    log_llm_call=log_llm_call,
                    agent_name="ProductManagerAgent"
                )

                if prd_draft_content:
                    logger.info(
                        "[ProductManagerAgent] Successfully received structured PRD draft from Vertex AI."
                    )
                    logger.info(
                        f"[ProductManagerAgent] PRD draft length: {len(prd_draft_content)} characters"
                    )
                    
                    # Create PRD draft object
                    prd_draft = PrdDraft(
                        title=case_title,
                        content_markdown=prd_draft_content,
                        version="1.0.0_structured_robust",
                        generated_with=f"Vertex AI {self.model_name} (with retry logic)",
                        sections=[
                            "Introduction / Problem Statement",
                            "Goals / Objectives",
                            "Target Audience / Users",
                            "Proposed Solution / Scope",
                            "Key Features / User Stories",
                            "Success Metrics / KPIs",
                            "Technical Considerations / Dependencies",
                            "Open Questions / Risks",
                        ],
                        word_count=len(prd_draft_content.split())
                    )
                    
                    # Prepare output payload for logging
                    output_payload = {
                        "status": "SUCCESS",
                        "prd_draft_length": len(prd_draft_content),
                        "word_count": len(prd_draft_content.split()),
                        "model_used": self.model_name
                    }
                    
                    # Calculate total execution time 
                    total_execution_time_ms = (time.time() - start_time) * 1000
                    
                    # Create successful output  
                    return DraftPrdOutput(
                        status=AgentStatus.SUCCESS,
                        message="Structured PRD draft generated successfully with robust retry logic.",
                        operation_id=trace_id,
                        duration_ms=int(total_execution_time_ms),
                        prd_draft=prd_draft,
                        new_status="PRD_DRAFTED"
                    )
                else:
                    message = "Failed to generate PRD content after all retry attempts"
                    logger.error(f"[ProductManagerAgent] {message}")
                    
                    return DraftPrdOutput(
                        status=AgentStatus.ERROR,
                        message=message,
                        operation_id=trace_id,
                        prd_draft=None
                    )

            except Exception as e:
                logger.error(f"[ProductManagerAgent] Error generating PRD with Vertex AI: {e}")
                
                return DraftPrdOutput(
                    status=AgentStatus.ERROR,
                    message=f"An error occurred while generating the PRD with Vertex AI: {str(e)}",
                    operation_id=trace_id,
                    prd_draft=None
                )

    def get_status(self) -> Dict[str, str]:
        """Get the current status of the Product Manager agent."""
        return {
            "name": self.name,
            "status": self.status,
            "description": self.description,
            "model": self.model_name,
            "project": self.project_id,
            "location": self.location,
        }
