"""
Architect Agent for generating system design proposals based on PRDs.
Enhanced with PRD analysis and structured component recommendations.
"""

from typing import Dict, Any, List, Optional
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models
from ..core.config import settings
import logging
import re
import json
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

class ArchitectAgent:
    """
    The Architect Agent is responsible for generating system design proposals
    based on approved Product Requirements Documents (PRDs).
    
    Enhanced with PRD analysis capabilities to provide more structured and
    specific architectural recommendations based on actual PRD content.
    """

    def __init__(self):
        self.name = "Architect Agent"
        self.description = "Generates system design proposals based on PRDs with enhanced analysis."
        self.status = "initialized"
        
        # Use configuration from settings
        self.project_id = settings.google_cloud_project_id or "drfirst-genai-01"
        self.location = settings.vertex_ai_location
        self.model_name = settings.vertex_ai_model_name or "gemini-2.0-flash-lite"
        
        try:
            vertexai.init(project=self.project_id, location=self.location)
            self.model = GenerativeModel(self.model_name)
            print(f"ArchitectAgent: Vertex AI initialized successfully with model {self.model_name}.")
            self.status = "available"
        except Exception as e:
            print(f"ArchitectAgent: Failed to initialize Vertex AI: {e}")
            self.model = None
            self.status = "error"

    async def analyze_prd_content(self, prd_content: str) -> Dict[str, Any]:
        """
        Analyze PRD content to extract key architectural requirements.
        
        Args:
            prd_content (str): The PRD content to analyze
            
        Returns:
            Dict[str, Any]: Analysis results including features, entities, complexity, etc.
        """
        if not self.model:
            return {"error": "Model not available"}
        
        try:
            analysis_prompt = f"""Analyze the following PRD content and extract key architectural information:

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

Focus on extracting concrete, actionable architectural information that will guide system design decisions."""

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
                    json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
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
        if len(prd_content) > 10000 or any(keyword in content_lower for keyword in 
                                           ['integration', 'api', 'real-time', 'scalability']):
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
                "estimated_complexity": complexity
            },
            "api_needs": ["RESTful API endpoints"],
            "data_storage_needs": ["Database storage required"]
        }

    async def generate_system_design(self, prd_content: str, case_title: str) -> Dict[str, Any]:
        """
        Generates an enhanced system design proposal based on PRD analysis.
        
        Args:
            prd_content (str): The content of the approved PRD
            case_title (str): Title of the business case
            
        Returns:
            Dict[str, Any]: Response containing status and enhanced system design content
        """
        print(f"[ArchitectAgent] Received request to generate enhanced system design for: {case_title}")
        
        if not self.model:
            return {
                "status": "error",
                "message": "ArchitectAgent not properly initialized with Vertex AI model.",
                "system_design_draft": None
            }

        try:
            # First, analyze the PRD content
            prd_analysis = await self.analyze_prd_content(prd_content)
            
            # Generate enhanced system design prompt based on analysis
            system_design_prompt = self._create_enhanced_design_prompt(
                prd_content, case_title, prd_analysis
            )

            # Use generation settings optimized for technical content
            generation_config = {
                "max_output_tokens": 8192,  # Allow for comprehensive design
                "temperature": 0.3,  # Lower temperature for more structured output
                "top_p": 0.8,
                "top_k": 40,
            }
            
            safety_settings = {
                generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
            
            logger.info(f"[ArchitectAgent] Generating enhanced system design for case: {case_title}")
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
                    "generated_by": "ArchitectAgent (Enhanced)",
                    "version": "v2",
                    "generated_at": datetime.now().isoformat(),
                    "prd_analysis": prd_analysis
                }
                
                logger.info(f"[ArchitectAgent] Successfully generated enhanced system design for {case_title}")
                print(f"[ArchitectAgent] Generated enhanced system design ({len(system_design_content)} characters)")
                
                return {
                    "status": "success",
                    "message": "Enhanced system design generated successfully",
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
            error_msg = f"Error generating enhanced system design: {str(e)}"
            logger.error(f"[ArchitectAgent] {error_msg} for case {case_title}")
            print(f"[ArchitectAgent] {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "system_design_draft": None
            }

    def _create_enhanced_design_prompt(self, prd_content: str, case_title: str, analysis: Dict[str, Any]) -> str:
        """
        Create an enhanced system design prompt based on PRD analysis.
        """
        complexity = analysis.get("complexity_indicators", {}).get("estimated_complexity", "medium")
        features = analysis.get("key_features", [])
        integrations = analysis.get("external_integrations", [])
        api_needs = analysis.get("api_needs", [])
        
        return f"""You are a Senior Software Architect with expertise in healthcare technology and cloud-based systems. Based on the following approved PRD and its analysis for the project titled '{case_title}', generate a comprehensive, actionable system design.

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