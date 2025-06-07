"""
Architect Agent for generating system design proposals based on PRDs.
Enhanced with PRD analysis and structured component recommendations.
"""

from typing import Dict, Any, List, Optional
import uuid
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models
from pydantic import ValidationError

from ..core.config import settings
from ..models.agent_models import (
    GenerateSystemDesignInput,
    GenerateSystemDesignOutput,
    SystemDesignDraft,
    PrdAnalysis,
    AgentStatus
)
import logging
import re
import json
from datetime import datetime
import asyncio
import functools

# Set up logging
logger = logging.getLogger(__name__)


def timeout_handler(timeout_seconds: int):
    """Decorator to add timeout protection to async methods"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_seconds)
            except asyncio.TimeoutError:
                logger.error(f"[ArchitectAgent] {func.__name__} timed out after {timeout_seconds} seconds")
                raise TimeoutError(f"Operation timed out after {timeout_seconds} seconds")
        return wrapper
    return decorator


class ArchitectAgent:
    """
    The Architect Agent is responsible for generating system design proposals
    based on approved Product Requirements Documents (PRDs).

    Enhanced with PRD analysis capabilities to provide more structured and
    specific architectural recommendations based on actual PRD content.
    """

    def __init__(self):
        self.name = "Architect Agent"
        self.description = (
            "Generates system design proposals based on PRDs with enhanced analysis."
        )
        self.status = "initialized"

        # Use configuration from settings
        self.project_id = settings.google_cloud_project_id or "drfirst-business-case-gen"
        self.location = settings.vertex_ai_location
        self.model_name = settings.vertex_ai_model_name or "gemini-2.0-flash-lite"

        # Timeout and retry configuration
        self.prd_analysis_timeout = 120  # 2 minutes
        self.system_design_timeout = 300  # 5 minutes
        self.max_retries = 2
        self.max_prd_length = 50000  # characters

        try:
            # Use centralized VertexAI service
            from app.services.vertex_ai_service import vertex_ai_service
            vertex_ai_service.initialize()
            
            if vertex_ai_service.is_initialized:
                self.model = GenerativeModel(self.model_name)
                logger.info(
                    f"ArchitectAgent: Vertex AI initialized successfully with model {self.model_name}."
                )
                self.status = "available"
            else:
                logger.error("ArchitectAgent: VertexAI service not initialized")
                self.model = None
                self.status = "error"
        except Exception as e:
            logger.error(f"ArchitectAgent: Failed to initialize with VertexAI service: {e}")
            self.model = None
            self.status = "error"

    @timeout_handler(120)  # 2 minute timeout for PRD analysis
    async def analyze_prd_content(self, prd_content: str) -> Dict[str, Any]:
        """
        Analyze PRD content to extract key architectural requirements.

        Args:
            prd_content (str): The PRD content to analyze

        Returns:
            Dict[str, Any]: Analysis results including features, entities, complexity, etc.
        """
        logger.info("[ArchitectAgent] Starting PRD analysis...")
        
        if not self.model:
            return {"error": "Model not available"}

        # Truncate oversized PRDs
        if len(prd_content) > self.max_prd_length:
            logger.warning(f"[ArchitectAgent] PRD too large ({len(prd_content)} chars), truncating to {self.max_prd_length}")
            prd_content = prd_content[:self.max_prd_length] + "\n\n[Content truncated for processing...]"

        try:
            analysis_prompt = """Analyze the following PRD content and extract key architectural information:

--- PRD Content ---
{prd_content}
--- End PRD Content ---

Please provide a structured analysis in JSON format with the following sections:

{{
  "key_features": ["list of main features/capabilities"],
  "user_roles": ["list of user types/roles"],
  "data_entities": ["list of main data objects/entities"],
  "external_integrations": ["list of external systems mentioned"],
  "functional_requirements": ["key functional requirements"],
  "non_functional_requirements": ["performance, security, compliance requirements"],
  "complexity_indicators": {{
    "user_roles_count": number,
    "features_count": number,
    "integrations_count": number,
    "estimated_complexity": "low|medium|high"
  }},
  "api_needs": ["suggested API endpoints based on user journeys"],
  "data_storage_needs": ["database/storage requirements identified"]
}}

Focus on extracting concrete, actionable architectural information that will guide system design decisions.""".format(prd_content=prd_content)

            response = await self.model.generate_content_async(
                [analysis_prompt],
                generation_config={
                    "max_output_tokens": 2048,
                    "temperature": 0.2,
                    "top_p": 0.8,
                },
                stream=False,
            )

            if response.candidates and response.candidates[0].content.parts:
                analysis_text = response.candidates[0].content.parts[0].text.strip()

                # Try to extract JSON from the response
                try:
                    # Find JSON block in the response
                    json_match = re.search(r"\{.*\}", analysis_text, re.DOTALL)
                    if json_match:
                        analysis_data = json.loads(json_match.group())
                        logger.info("[ArchitectAgent] PRD analysis completed successfully")
                        return analysis_data
                    else:
                        # Fallback to basic analysis
                        return self._fallback_prd_analysis(prd_content)
                except json.JSONDecodeError:
                    logger.warning("[ArchitectAgent] Could not parse PRD analysis JSON, using fallback")
                    return self._fallback_prd_analysis(prd_content)
            else:
                return self._fallback_prd_analysis(prd_content)

        except Exception as e:
            logger.error(f"[ArchitectAgent] Error in PRD analysis: {str(e)}")
            return self._fallback_prd_analysis(prd_content)

    def _fallback_prd_analysis(self, prd_content: str) -> Dict[str, Any]:
        """
        Fallback PRD analysis using simple text parsing.
        """
        # Simple keyword-based analysis
        content_lower = prd_content.lower()

        # Estimate complexity based on content length and keywords
        complexity = "low"
        if len(prd_content) > 5000:
            complexity = "medium"
        if len(prd_content) > 10000 or any(
            keyword in content_lower
            for keyword in ["integration", "api", "real-time", "scalability"]
        ):
            complexity = "high"

        return {
            "key_features": ["Feature analysis requires AI model"],
            "user_roles": ["Multiple user types identified"],
            "data_entities": ["Data entities require analysis"],
            "external_integrations": ["Integration needs identified"],
            "functional_requirements": ["Requirements analysis needed"],
            "non_functional_requirements": ["Performance and security considerations"],
            "complexity_indicators": {
                "user_roles_count": 3,
                "features_count": 5,
                "integrations_count": 2,
                "estimated_complexity": complexity,
            },
            "api_needs": ["RESTful API endpoints"],
            "data_storage_needs": ["Database storage required"],
        }

    async def _generate_with_retry(self, prompt: str, config: dict, attempt: int = 1) -> Optional[str]:
        """
        Generate content with retry logic and timeout protection.
        """
        try:
            logger.info(f"[ArchitectAgent] Generation attempt {attempt}/{self.max_retries + 1}")
            
            # Apply timeout to the actual Vertex AI call
            response = await asyncio.wait_for(
                self.model.generate_content_async(
                    [prompt],
                    generation_config=config,
                    safety_settings={
                        generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                        generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    },
                    stream=False,
                ),
                timeout=self.system_design_timeout
            )

            if response.candidates and response.candidates[0].content.parts:
                content = response.candidates[0].content.parts[0].text.strip()
                logger.info(f"[ArchitectAgent] Successfully generated content ({len(content)} characters)")
                return content
            else:
                logger.warning(f"[ArchitectAgent] No content generated on attempt {attempt}")
                if attempt <= self.max_retries:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    return await self._generate_with_retry(prompt, config, attempt + 1)
                return None

        except asyncio.TimeoutError:
            logger.error(f"[ArchitectAgent] Vertex AI call timed out on attempt {attempt}")
            if attempt <= self.max_retries:
                await asyncio.sleep(2 ** attempt)
                return await self._generate_with_retry(prompt, config, attempt + 1)
            raise TimeoutError(f"System design generation timed out after {self.max_retries + 1} attempts")
        
        except Exception as e:
            logger.error(f"[ArchitectAgent] Error on attempt {attempt}: {str(e)}")
            if attempt <= self.max_retries:
                await asyncio.sleep(2 ** attempt)
                return await self._generate_with_retry(prompt, config, attempt + 1)
            raise e

    async def generate_system_design(
        self, input_data: GenerateSystemDesignInput
    ) -> GenerateSystemDesignOutput:
        """
        Generates an enhanced system design proposal based on PRD analysis.
        Now includes timeout protection, progress tracking, and retry logic.

        Args:
            input_data: GenerateSystemDesignInput with PRD content and case details

        Returns:
            GenerateSystemDesignOutput: Response containing status and enhanced system design content
        """
        # Generate operation ID for tracking
        operation_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # Validate input
            if not isinstance(input_data, GenerateSystemDesignInput):
                input_data = GenerateSystemDesignInput(**input_data)
        except ValidationError as e:
            return GenerateSystemDesignOutput(
                status=AgentStatus.ERROR,
                message=f"Input validation failed: {str(e)}",
                operation_id=operation_id,
                system_design_draft=None
            )
        
        # Extract values from validated input
        prd_content = input_data.prd_content
        case_title = input_data.case_title
        
        logger.info(f"[ArchitectAgent] Starting system design generation for: {case_title}")

        if not self.model:
            return GenerateSystemDesignOutput(
                status=AgentStatus.ERROR,
                message="ArchitectAgent not properly initialized with Vertex AI model.",
                operation_id=operation_id,
                system_design_draft=None
            )

        try:
            # Step 1: Analyze PRD with timeout protection
            logger.info("[ArchitectAgent] Step 1/2: Analyzing PRD content...")
            prd_analysis = await self.analyze_prd_content(prd_content)
            
            if "error" in prd_analysis:
                logger.error(f"[ArchitectAgent] PRD analysis failed: {prd_analysis['error']}")
                duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
                return GenerateSystemDesignOutput(
                    status=AgentStatus.ERROR,
                    message=f"PRD analysis failed: {prd_analysis['error']}",
                    operation_id=operation_id,
                    duration_ms=duration_ms,
                    system_design_draft=None
                )

            # Step 2: Generate system design with timeout and retry
            logger.info("[ArchitectAgent] Step 2/2: Generating system design...")
            system_design_prompt = self._create_enhanced_design_prompt(
                prd_content, case_title, prd_analysis
            )

            generation_config = {
                "max_output_tokens": 8192,
                "temperature": 0.3,
                "top_p": 0.8,
                "top_k": 40,
            }

            # Generate with retry and timeout protection
            system_design_content = await self._generate_with_retry(
                system_design_prompt, generation_config
            )

            if system_design_content:
                # Calculate duration
                duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
                
                # Create PrdAnalysis object
                prd_analysis_obj = PrdAnalysis(**prd_analysis)
                
                # Create SystemDesignDraft object
                system_design_draft = SystemDesignDraft(
                    content_markdown=system_design_content,
                    generated_by="ArchitectAgent (Enhanced with Timeout Protection)",
                    version="v2.1",
                    generated_at=datetime.now().isoformat(),
                    prd_analysis=prd_analysis_obj,
                    generation_metadata={
                        "prd_length": len(prd_content),
                        "analysis_status": "success",
                        "timeout_config": {
                            "prd_analysis_timeout": self.prd_analysis_timeout,
                            "system_design_timeout": self.system_design_timeout,
                            "max_retries": self.max_retries
                        }
                    }
                )

                logger.info(f"[ArchitectAgent] Successfully generated system design for {case_title}")
                logger.info(f"[ArchitectAgent] Generated content length: {len(system_design_content)} characters")

                return GenerateSystemDesignOutput(
                    status=AgentStatus.SUCCESS,
                    message="Enhanced system design generated successfully with timeout protection",
                    operation_id=operation_id,
                    duration_ms=duration_ms,
                    system_design_draft=system_design_draft,
                    new_status="SYSTEM_DESIGN_DRAFTED"
                )
            else:
                logger.error(f"[ArchitectAgent] Failed to generate system design content for {case_title}")
                duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
                return GenerateSystemDesignOutput(
                    status=AgentStatus.ERROR,
                    message="No system design content generated after retries",
                    operation_id=operation_id,
                    duration_ms=duration_ms,
                    system_design_draft=None
                )

        except TimeoutError as e:
            error_msg = f"System design generation timed out: {str(e)}"
            logger.error(f"[ArchitectAgent] {error_msg} for case {case_title}")
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return GenerateSystemDesignOutput(
                status=AgentStatus.TIMEOUT,
                message=error_msg,
                operation_id=operation_id,
                duration_ms=duration_ms,
                system_design_draft=None
            )
        except Exception as e:
            error_msg = f"Error generating enhanced system design: {str(e)}"
            logger.error(f"[ArchitectAgent] {error_msg} for case {case_title}")
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return GenerateSystemDesignOutput(
                status=AgentStatus.ERROR,
                message=error_msg,
                operation_id=operation_id,
                duration_ms=duration_ms,
                system_design_draft=None
            )

    def _create_enhanced_design_prompt(
        self, prd_content: str, case_title: str, analysis: Dict[str, Any]
    ) -> str:
        """
        Create an enhanced system design prompt based on PRD analysis.
        """
        complexity = analysis.get("complexity_indicators", {}).get(
            "estimated_complexity", "medium"
        )
        features = analysis.get("key_features", [])
        integrations = analysis.get("external_integrations", [])
        api_needs = analysis.get("api_needs", [])

        return """You are a Senior Software Architect with expertise in healthcare technology and cloud-based systems. Based on the following approved PRD and its analysis for the project titled '{case_title}', generate a comprehensive, actionable system design.

--- PRD Content ---
{prd_content}
--- End PRD Content ---

--- PRD Analysis Summary ---
Project Complexity: {complexity}
Key Features: {', '.join(features[:5]) if features else 'Analysis pending'}
External Integrations: {', '.join(integrations[:3]) if integrations else 'None identified'}
Estimated API Endpoints Needed: {len(api_needs) if api_needs else 'TBD'}
--- End Analysis ---

Please provide a structured system design that includes:

## 1. **Architecture Overview**
   - High-level architecture pattern recommendation with rationale
   - Key architectural principles and design philosophy
   - Overall system topology and communication patterns

## 2. **Component Architecture**
   ### Core Services/Components
   - **List each major component with specific responsibilities**
   - **Data flow between components**
   - **Inter-service communication patterns**

   ### Suggested Microservices (if applicable)
   - Service breakdown based on identified features
   - Service boundaries and responsibilities
   - Dependencies and communication protocols

## 3. **API Design Recommendations**
   ### RESTful API Endpoints
   - Specific endpoint suggestions based on user journeys
   - Request/response data models
   - Authentication and authorization strategy

   ### Example API Structure:
   ```
   GET /api/v1/resource
   POST /api/v1/resource
   PUT /api/v1/resource/{{id}}
   DELETE /api/v1/resource/{{id}}
   ```

## 4. **Data Architecture**
   ### Database Design
   - Recommended database type (SQL/NoSQL) with rationale
   - Core entity relationships and schema suggestions
   - Data access patterns and query optimization

   ### Data Storage Strategy
   - Primary data storage solutions
   - Caching strategies
   - Data backup and recovery approaches

## 5. **Technology Stack Recommendations**
   ### Frontend Stack
   - Framework recommendations with rationale
   - State management approach
   - UI component strategy

   ### Backend Stack
   - Runtime and framework recommendations
   - Dependency management
   - Development and testing tools

   ### Infrastructure & Cloud Services
   - Google Cloud Platform service recommendations
   - Containerization strategy (Docker/Kubernetes)
   - CI/CD pipeline architecture

## 6. **Security & Compliance**
   ### Authentication & Authorization
   - Identity provider integration (Google Identity Platform)
   - Role-based access control (RBAC) design
   - API security (OAuth 2.0, JWT tokens)

   ### Healthcare Compliance
   - HIPAA compliance considerations
   - Data encryption (at rest and in transit)
   - Audit logging requirements

## 7. **Scalability & Performance**
   ### Scalability Strategy
   - Horizontal vs vertical scaling approach
   - Auto-scaling configuration
   - Load balancing strategy

   ### Performance Optimization
   - Caching strategies (Redis, CDN)
   - Database optimization
   - Monitoring and alerting

## 8. **Implementation Roadmap**
   ### Phase 1: Foundation (Weeks 1-4)
   - Core infrastructure setup
   - Basic authentication
   - Primary data models

   ### Phase 2: Core Features (Weeks 5-8)
   - Main business logic
   - API implementation
   - Basic UI development

   ### Phase 3: Integration & Enhancement (Weeks 9-12)
   - External integrations
   - Advanced features
   - Performance optimization

## 9. **Risk Assessment & Mitigation**
   - Technical risks identified
   - Mitigation strategies
   - Fallback plans

## 10. **Development & Deployment**
   ### Development Environment
   - Local development setup
   - Testing strategy (unit, integration, e2e)
   - Code quality and review processes

   ### Deployment Strategy
   - Environment promotion (dev → staging → prod)
   - Blue-green or canary deployment
   - Rollback procedures

Provide specific, actionable recommendations that would be suitable for a healthcare technology company like DrFirst. Focus on proven technologies and patterns that support enterprise-grade applications with emphasis on security, compliance, and scalability.

Format your response in clear markdown with headers and bullet points for easy reading. Include code examples and specific configuration recommendations where appropriate."""

    async def design_architecture(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Legacy method for compatibility - redirects to generate_system_design
        """
        prd_content = requirements.get("prd_content", "")
        case_title = requirements.get("case_title", "Untitled Case")
        return await self.generate_system_design(prd_content, case_title)

    async def estimate_implementation_effort(
        self, architecture: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Estimate implementation effort and timeline (placeholder for future enhancement)
        """
        return {
            "estimated_duration": "TBD",
            "team_size_recommendation": "TBD",
            "complexity_assessment": "TBD",
        }

    async def identify_risks(
        self, technical_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Identify technical risks and mitigation strategies (placeholder for future enhancement)
        """
        return []

    async def recommend_technologies(
        self, requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Recommend appropriate technologies and tools (placeholder for future enhancement)
        """
        return []

    def get_status(self) -> Dict[str, str]:
        """Get the current status of the architect agent"""
        return {
            "name": self.name,
            "status": self.status,
            "description": self.description,
        }
