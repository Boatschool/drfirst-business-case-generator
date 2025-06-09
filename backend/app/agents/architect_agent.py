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
from ..services.vertex_ai_service import VertexAIService
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
    async def analyze_prd_content(self, prd_content: str, log_llm_call=None, trace_id=None) -> Dict[str, Any]:
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

        # Use centralized content truncation
        prd_content, was_truncated = VertexAIService.truncate_content(
            prd_content, self.max_prd_length
        )
        if was_truncated:
            logger.warning(f"[ArchitectAgent] PRD content was truncated to {self.max_prd_length} characters")

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

            generation_config = {
                "max_output_tokens": 2048,
                "temperature": 0.2,
                "top_p": 0.8,
            }
            
            # Use centralized retry logic for robust LLM call
            analysis_text = await VertexAIService.generate_with_retry(
                model=self.model,
                prompt=analysis_prompt,
                generation_config=generation_config,
                model_name=self.model_name,
                max_retries=self.max_retries,
                timeout_seconds=self.prd_analysis_timeout,
                log_llm_call=log_llm_call,
                agent_name="ArchitectAgent"
            )

            if analysis_text:
                # Use centralized JSON extraction
                analysis_data = VertexAIService.extract_json_from_text(analysis_text)
                
                if analysis_data:
                    # Sanitize data to match PrdAnalysis model expectations
                    sanitized_data = self._sanitize_prd_analysis(analysis_data)
                    logger.info("[ArchitectAgent] PRD analysis completed successfully with robust parsing")
                    return sanitized_data
                else:
                    logger.warning("[ArchitectAgent] Could not extract JSON from PRD analysis, using fallback")
                    return self._fallback_prd_analysis(prd_content)
            else:
                logger.warning("[ArchitectAgent] No response from PRD analysis after retries, using fallback")
                return self._fallback_prd_analysis(prd_content)

        except Exception as e:
            logger.error(f"[ArchitectAgent] Error in PRD analysis: {str(e)}")
            
            # Log LLM interaction error if logging function provided
            if log_llm_call:
                log_llm_call(
                    model_name=self.model_name,
                    prompt=analysis_prompt,
                    parameters=generation_config,
                    error=str(e)
                )
            
            return self._fallback_prd_analysis(prd_content)

    def _sanitize_prd_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize PRD analysis data to match PrdAnalysis model expectations.
        Converts complex objects to strings where needed.
        """
        def _convert_to_string_list(data_list: List) -> List[str]:
            """Convert a list of mixed types to a list of strings."""
            result = []
            for item in data_list:
                if isinstance(item, dict):
                    # Extract meaningful text from dict
                    if 'endpoint' in item and 'description' in item:
                        result.append(f"{item['endpoint']}: {item['description']}")
                    elif 'name' in item:
                        result.append(str(item['name']))
                    else:
                        # Convert dict to a meaningful string
                        result.append(str(item))
                elif isinstance(item, str):
                    result.append(item)
                else:
                    result.append(str(item))
            return result

        # Make a copy to avoid modifying the original
        sanitized = analysis_data.copy()
        
        # Ensure all list fields are strings
        list_fields = [
            'key_features', 'user_roles', 'data_entities', 'external_integrations',
            'functional_requirements', 'non_functional_requirements', 'api_needs', 'data_storage_needs'
        ]
        
        for field in list_fields:
            if field in sanitized and isinstance(sanitized[field], list):
                sanitized[field] = _convert_to_string_list(sanitized[field])
        
        return sanitized

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



    async def generate_system_design(
        self, input_data: GenerateSystemDesignInput, case_id: Optional[str] = None
    ) -> GenerateSystemDesignOutput:
        """
        Generates an enhanced system design proposal based on PRD analysis.
        Now includes timeout protection, progress tracking, and retry logic.

        Args:
            input_data: GenerateSystemDesignInput with PRD content and case details
            case_id: Optional case ID for tracking

        Returns:
            GenerateSystemDesignOutput: Response containing status and enhanced system design content
        """
        import time
        
        # Import the agent logging utilities
        from ..core.agent_logging import create_agent_logger
        
        # Create enhanced logger for this operation
        agent_logger = create_agent_logger("ArchitectAgent", case_id)
        
        try:
            # Validate input
            if not isinstance(input_data, GenerateSystemDesignInput):
                input_data = GenerateSystemDesignInput(**input_data)
        except ValidationError as e:
            return GenerateSystemDesignOutput(
                status=AgentStatus.ERROR,
                message=f"Input validation failed: {str(e)}",
                operation_id=str(uuid.uuid4()),
                system_design_draft=None
            )
        
        # Extract values from validated input
        prd_content = input_data.prd_content
        case_title = input_data.case_title
        
        # Prepare input payload for logging
        input_payload = {
            "case_title": case_title,
            "prd_content_length": len(prd_content),
            "case_id": case_id,
            "max_prd_length": self.max_prd_length
        }
        
        # Use context manager for comprehensive logging
        start_time = time.time()
        with agent_logger.log_method_execution('generate_system_design', input_payload, case_id) as ctx:
            trace_id = ctx['trace_id']
            log_llm_call = ctx['log_llm']

            if not self.model:
                return GenerateSystemDesignOutput(
                    status=AgentStatus.ERROR,
                    message="ArchitectAgent not properly initialized with Vertex AI model.",
                    operation_id=trace_id,
                    system_design_draft=None
                )

            # Step 1: Analyze PRD with timeout protection
            logger.info("[ArchitectAgent] Step 1/2: Analyzing PRD content...")
            prd_analysis = await self.analyze_prd_content(prd_content, log_llm_call, trace_id)
            
            if "error" in prd_analysis:
                logger.error(f"[ArchitectAgent] PRD analysis failed: {prd_analysis['error']}")
                return GenerateSystemDesignOutput(
                    status=AgentStatus.ERROR,
                    message=f"PRD analysis failed: {prd_analysis['error']}",
                    operation_id=trace_id,
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

            # Generate with centralized retry and timeout protection
            system_design_content = await VertexAIService.generate_with_retry(
                model=self.model,
                prompt=system_design_prompt,
                generation_config=generation_config,
                model_name=self.model_name,
                max_retries=self.max_retries,
                timeout_seconds=self.system_design_timeout,
                log_llm_call=log_llm_call,
                agent_name="ArchitectAgent"
            )

            if system_design_content:
                # Calculate duration
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Create PrdAnalysis object
                prd_analysis_obj = PrdAnalysis(**prd_analysis)
                
                # Create SystemDesignDraft object
                system_design_draft = SystemDesignDraft(
                    content_markdown=system_design_content,
                    generated_by="ArchitectAgent (Enhanced with Robust Retry Logic)",
                    version="v2.2",
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

                # Calculate total execution time and log method completion
                total_execution_time_ms = (time.time() - start_time) * 1000
                
                # Prepare output payload for logging
                output_payload = {
                    "status": "SUCCESS",
                    "system_design_length": len(system_design_content),
                    "model_used": self.model_name,
                    "prd_analysis_status": "success"
                }
                
                # Log successful method completion
                agent_logger.log_method_end(
                    trace_id=trace_id,
                    method_name='generate_system_design',
                    output_payload=output_payload,
                    execution_time_ms=total_execution_time_ms,
                    status="SUCCESS"
                )
                
                return GenerateSystemDesignOutput(
                    status=AgentStatus.SUCCESS,
                    message="Enhanced system design generated successfully with timeout protection",
                    operation_id=trace_id,
                    duration_ms=int(total_execution_time_ms),
                    system_design_draft=system_design_draft,
                    new_status="SYSTEM_DESIGN_DRAFTED"
                )
            else:
                logger.error(f"[ArchitectAgent] Failed to generate system design content for {case_title}")
                return GenerateSystemDesignOutput(
                    status=AgentStatus.ERROR,
                    message="No system design content generated after retries",
                    operation_id=trace_id,
                    system_design_draft=None
                )

            # Note: Exception handling will be managed by the context manager

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
