"""
Sales/Value Analyst Agent for generating potential revenue or value scenarios.
Enhanced with Vertex AI integration and detailed pricing template usage.
"""

from typing import Dict, Any, List, Optional
import asyncio
import logging
import json
import re
import time
from vertexai.generative_models import GenerativeModel
import vertexai.preview.generative_models as generative_models
from google.cloud import firestore
from app.core.config import settings
from app.core.agent_logging import create_agent_logger
from app.services.vertex_ai_service import VertexAIService

# Set up logging
logger = logging.getLogger(__name__)


class SalesValueAnalystAgent:
    """
    The Sales/Value Analyst Agent is responsible for generating potential revenue
    or value scenarios for business cases based on PRD content and pricing templates.
    Enhanced with Vertex AI integration for intelligent value projection generation.
    """

    def __init__(self):
        self.name = "Sales/Value Analyst Agent"
        self.description = "Calculates potential revenue or value scenarios using AI and pricing templates."
        self.status = "initialized"

        # Use configuration from settings
        self.project_id = (
            settings.google_cloud_project_id or "drfirst-business-case-gen"
        )
        self.location = settings.vertex_ai_location
        self.model_name = settings.vertex_ai_model_name or "gemini-2.0-flash-lite"

        # Initialize Vertex AI for intelligent value projection using centralized service
        try:
            from app.services.vertex_ai_service import vertex_ai_service
            vertex_ai_service.initialize()
            
            if vertex_ai_service.is_initialized:
                self.model = GenerativeModel(self.model_name)
                logger.info(
                    f"SalesValueAnalystAgent: Vertex AI initialized successfully with model {self.model_name}."
                )
                self.vertex_ai_available = True
            else:
                logger.error("SalesValueAnalystAgent: VertexAI service not initialized")
                self.model = None
                self.vertex_ai_available = False
        except Exception as e:
            logger.info(f"SalesValueAnalystAgent: Failed to initialize with VertexAI service: {e}")
            self.model = None
            self.vertex_ai_available = False

        # Initialize Firestore client for pricing template access
        try:
            self.db = firestore.Client(project=settings.firebase_project_id)
            logger.info("SalesValueAnalystAgent: Firestore client initialized successfully.")
        except Exception as e:
            logger.info(f"SalesValueAnalystAgent: Failed to initialize Firestore client: {e}")
            self.db = None

        logger.info("SalesValueAnalystAgent: Initialized successfully.")
        self.status = "available"

    async def analyze_value(
        self, prd_content: str, case_title: str, case_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Public interface for value analysis that matches function calling expectations.
        Delegates to project_value method with enhanced logging.

        Args:
            prd_content (str): The PRD content to analyze
            case_title (str): Title of the business case
            case_id (str, optional): Business case ID for logging

        Returns:
            Dict[str, Any]: Response containing status and value projection
        """
        return await self.project_value(
            prd_content=prd_content,
            case_title=case_title,
            case_id=case_id
        )

    async def project_value(
        self, prd_content: str, case_title: str, case_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Projects value/revenue scenarios based on PRD content and case details.
        Enhanced with AI-powered analysis using pricing templates.

        Args:
            prd_content (str): The PRD content to analyze
            case_title (str): Title of the business case
            case_id (str, optional): Business case ID for logging

        Returns:
            Dict[str, Any]: Response containing status and value projection
        """
        # Create agent logger
        agent_logger = create_agent_logger("SalesValueAnalystAgent", case_id)
        
        # Prepare input payload for logging
        input_payload = {
            "case_title": case_title,
            "prd_content_length": len(prd_content) if prd_content else 0,
            "has_prd_content": bool(prd_content),
            "vertex_ai_available": self.vertex_ai_available,
            "firestore_available": bool(self.db)
        }
        
        # Use logging context manager
        with agent_logger.log_method_execution(
            method_name="project_value",
            input_payload=input_payload
        ) as log_context:
            
            logger.info(
                f"[SalesValueAnalystAgent] Received request to project value for: {case_title}"
            )

            if not self.db:
                logger.warning(
                    "[SalesValueAnalystAgent] Firestore client not available, using default scenarios"
                )
                result = await self._project_with_default_scenarios(prd_content, case_title)
                return result

            try:
                # Attempt to fetch pricing template from Firestore
                pricing_template = await self._fetch_pricing_template()

                if pricing_template:
                    result = await self._project_with_template(
                        prd_content, pricing_template, case_title, log_context
                    )
                    return result
                else:
                    logger.info(
                        "[SalesValueAnalystAgent] No pricing template found, using default scenarios"
                    )
                    result = await self._project_with_default_scenarios(
                        prd_content, case_title
                    )
                    return result

            except Exception as e:
                error_msg = f"Error projecting value: {str(e)}"
                logger.error(f"[SalesValueAnalystAgent] {error_msg} for case {case_title}")
                return {"status": "error", "message": error_msg, "value_projection": None}

    async def _fetch_pricing_template(self) -> Optional[Dict[str, Any]]:
        """
        Fetches an active pricing template from Firestore with enhanced selection strategy.

        Strategy:
        1. Look for active + default templates first
        2. Fall back to any active template
        3. Fall back to specific document lookup

        Returns:
            Dict[str, Any]: Pricing template data or None if not found
        """
        try:
            templates_ref = self.db.collection("pricingTemplates")

            # Strategy 1: Look for active + default templates
            logger.info(
                "[SalesValueAnalystAgent] Looking for active + default pricing templates"
            )
            active_default_query = templates_ref.where("isActive", "==", True).where(
                "isDefault", "==", True
            )
            active_default_docs = await asyncio.to_thread(
                lambda: list(active_default_query.limit(1).stream())
            )

            if active_default_docs:
                template_data = active_default_docs[0].to_dict()
                template_data["id"] = active_default_docs[0].id
                logger.info(
                    f"[SalesValueAnalystAgent] Found active + default template: {template_data.get('name', 'Unknown')}"
                )
                return template_data

            # Strategy 2: Look for any active template
            logger.info(
                "[SalesValueAnalystAgent] Looking for any active pricing template"
            )
            active_query = templates_ref.where("isActive", "==", True)
            active_docs = await asyncio.to_thread(
                lambda: list(active_query.limit(1).stream())
            )

            if active_docs:
                template_data = active_docs[0].to_dict()
                template_data["id"] = active_docs[0].id
                logger.info(
                    f"[SalesValueAnalystAgent] Found active template: {template_data.get('name', 'Unknown')}"
                )
                return template_data

            # Strategy 3: Fall back to specific document lookup
            logger.info(
                "[SalesValueAnalystAgent] Looking for specific default template document"
            )
            template_ref = templates_ref.document("default_value_projection")
            doc_snapshot = await asyncio.to_thread(template_ref.get)

            if doc_snapshot.exists:
                template_data = doc_snapshot.to_dict()
                template_data["id"] = doc_snapshot.id
                logger.info(
                    f"[SalesValueAnalystAgent] Found specific template: {template_data.get('name', 'Unknown')}"
                )
                return template_data
            else:
                logger.warning(
                    "[SalesValueAnalystAgent] No pricing templates found in any strategy"
                )
                return None

        except Exception as e:
            logger.error(
                f"[SalesValueAnalystAgent] Error fetching pricing template: {e}"
            )
            return None

    async def _project_with_template(
        self, prd_content: str, template: Dict[str, Any], case_title: str, log_context
    ) -> Dict[str, Any]:
        """
        Projects value using a Firestore pricing template.
        Enhanced to try AI-powered generation first, then fall back to template-based values.

        Args:
            prd_content (str): The PRD content
            template (Dict[str, Any]): Pricing template data from Firestore
            case_title (str): Title of the business case
            log_context: Logging context manager from parent method

        Returns:
            Dict[str, Any]: Value projection response
        """
        logger.info(
            f"[SalesValueAnalystAgent] Using template '{template.get('name', 'Unknown')}' for value projection"
        )

        # Try AI-powered generation first if available
        if self.vertex_ai_available and self.model:
            try:
                logger.info(
                    "[SalesValueAnalystAgent] Attempting AI-powered value projection"
                )
                ai_result = await self._project_with_ai_template(
                    prd_content, template, case_title, log_context.log_llm
                )
                if ai_result and ai_result.get("status") == "success":
                    logger.info(
                        "[SalesValueAnalystAgent] AI-powered projection successful"
                    )
                    return ai_result
                else:
                    logger.warning(
                        "[SalesValueAnalystAgent] AI-powered projection failed, falling back to template-based"
                    )
            except Exception as e:
                logger.warning(
                    f"[SalesValueAnalystAgent] AI generation error: {str(e)}, falling back to template-based"
                )

        # Fall back to template-based generation
        return await self._project_with_template_fallback(
            prd_content, template, case_title
        )

    async def _project_with_ai_template(
        self, prd_content: str, template: Dict[str, Any], case_title: str, log_llm: bool
    ) -> Dict[str, Any]:
        """
        Uses Vertex AI to generate intelligent value projections based on template guidance.

        Args:
            prd_content (str): The PRD content
            template (Dict[str, Any]): Pricing template data
            case_title (str): Title of the business case
            log_llm (bool): Whether to log LLM calls

        Returns:
            Dict[str, Any]: AI-generated value projection response
        """
        try:
            # Extract key information from PRD and template
            prd_summary = self._extract_prd_summary(prd_content)
            template_structure = template.get("structureDefinition", {})
            template_type = template_structure.get("type", "LowBaseHigh")
            template_guidance = template.get("guidance", {})
            template_metadata = template.get("metadata", {})

            # Construct AI prompt for value projection
            prompt = f"""You are an experienced Sales/Value Analyst at DrFirst, a leading healthcare technology company. Your expertise lies in projecting realistic business value and revenue scenarios for healthcare technology solutions.

**Business Case Information:**
- **Title**: {case_title}
- **PRD Summary**: {prd_summary}

**Value Projection Template Guidance:**
- **Template**: {template.get('name', 'Unknown Template')}
- **Description**: {template.get('description', 'No description available')}
- **Structure Type**: {template_type}
- **Industry Focus**: {template_metadata.get('industry_focus', 'healthcare technology')}

**Template-Specific Guidance:**
{self._format_template_guidance(template_guidance, template_structure)}

**Your Task:**
Analyze the PRD content and template guidance to generate realistic value projections for this healthcare technology business case. Consider these critical factors:

1. **Operational Efficiency**: Time savings, workflow improvements, automation benefits
2. **Revenue Generation**: New revenue streams, market expansion opportunities
3. **Cost Reduction**: Operational cost savings, productivity improvements, resource optimization
4. **Healthcare Market Dynamics**: Adoption rates, regulatory compliance benefits, patient outcomes
5. **Implementation Factors**: Timeline, scaling potential, integration complexity
6. **Risk Assessment**: Market uncertainties, competitive landscape, regulatory changes

**Output Requirements:**
Respond ONLY with a valid JSON object in this exact format (no additional text, markdown, or explanations):

{{
  "scenarios": [
    {{"case": "Low", "value": <number>, "description": "<detailed rationale>"}},
    {{"case": "Base", "value": <number>, "description": "<detailed rationale>"}},
    {{"case": "High", "value": <number>, "description": "<detailed rationale>"}}
  ],
  "methodology": "<brief description of valuation approach>",
  "assumptions": ["<assumption 1>", "<assumption 2>", "<assumption 3>"],
  "market_factors": ["<factor 1>", "<factor 2>"],
  "notes": "<additional insights and considerations>"
}}

**Critical Guidelines:**
- All values must be in USD and realistic for healthcare technology projects
- Ensure Low < Base < High scenario values with meaningful 20-50% differences
- Descriptions must be specific and justify the value estimates with concrete reasoning
- Consider healthcare industry context, regulatory requirements, and compliance benefits
- Base estimates on actual PRD content and realistic business case scope
- Include specific healthcare value drivers (patient outcomes, compliance, efficiency)

**Important**: Respond with valid JSON only. No markdown formatting or additional text."""

            # Generate AI response with robust retry logic
            generation_config = {
                "max_output_tokens": settings.vertex_ai_max_tokens,
                "temperature": 0.4,  # More conservative for financial projections
                "top_p": 0.8,
                "top_k": 20,
            }

            logger.info("[SalesValueAnalystAgent] Sending prompt to Vertex AI")
            
            # Use centralized retry logic for robust LLM call
            ai_response_text = await VertexAIService.generate_with_retry(
                model=self.model,
                prompt=prompt,
                generation_config=generation_config,
                model_name=self.model_name,
                max_retries=3,  # More retries for financial projections
                timeout_seconds=150,  # Longer timeout for complex financial analysis
                log_llm_call=log_llm if log_llm else None,
                agent_name="SalesValueAnalystAgent"
            )

            if ai_response_text:
                logger.info(
                    f"[SalesValueAnalystAgent] Received AI response ({len(ai_response_text)} characters)"
                )

                # Parse AI response into structured format using centralized JSON extraction
                value_data = await self._parse_ai_response(ai_response_text, template)

                if value_data:
                    logger.info(
                        "[SalesValueAnalystAgent] Successfully parsed AI response"
                    )
                    return {
                        "status": "success",
                        "message": "AI-powered value projection completed successfully using pricing template with robust retry logic",
                        "value_projection": value_data,
                    }
                else:
                    logger.warning(
                        "[SalesValueAnalystAgent] Failed to parse AI response, attempting manual extraction"
                    )
                    # Try manual extraction as fallback
                    manual_data = self._manual_extract_scenarios(ai_response_text, template)
                    if manual_data:
                        logger.info("[SalesValueAnalystAgent] Manual extraction successful")
                        return {
                            "status": "success", 
                            "message": "Value projection completed with manual parsing fallback",
                            "value_projection": manual_data
                        }
                    return {"status": "error", "message": "Failed to parse AI response with both methods"}
            else:
                logger.warning("[SalesValueAnalystAgent] No content in AI response after all retries")
                return {"status": "error", "message": "No content generated by AI after retries"}

        except Exception as e:
            logger.error(f"[SalesValueAnalystAgent] Error in AI generation: {str(e)}")
            return {"status": "error", "message": f"AI generation failed: {str(e)}"}

    def _extract_prd_summary(self, prd_content: str) -> str:
        """
        Extracts key information from PRD content for AI prompts.

        Args:
            prd_content (str): Full PRD content

        Returns:
            str: Concise summary of key PRD elements
        """
        if not prd_content or len(prd_content.strip()) < 50:
            return "No detailed PRD content available for analysis."

        # Extract key sections using simple heuristics
        lines = prd_content.split("\n")
        summary_parts = []
        current_section = ""

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for section headers
            if line.startswith("#") and any(
                keyword in line.lower()
                for keyword in [
                    "problem",
                    "goal",
                    "objective",
                    "solution",
                    "feature",
                    "user",
                ]
            ):
                current_section = line
            elif current_section and len(line) > 20 and not line.startswith("#"):
                # Add content from relevant sections
                summary_parts.append(f"{current_section}: {line[:200]}")
                current_section = ""  # Reset to avoid duplicates

        if summary_parts:
            return " | ".join(summary_parts[:4])  # Limit to top 4 sections
        else:
            # Fallback: take first 500 characters
            return prd_content[:500] + "..." if len(prd_content) > 500 else prd_content

    def _format_template_guidance(
        self, guidance: Dict[str, Any], structure: Dict[str, Any]
    ) -> str:
        """
        Formats template guidance for AI prompts.

        Args:
            guidance (Dict[str, Any]): Template guidance object
            structure (Dict[str, Any]): Template structure definition

        Returns:
            str: Formatted guidance text
        """
        guidance_text = ""

        if guidance:
            for key, value in guidance.items():
                guidance_text += f"- **{key.replace('_', ' ').title()}**: {value}\n"

        if structure.get("notes"):
            guidance_text += f"- **Template Notes**: {structure['notes']}\n"

        if structure.get("scenarios"):
            guidance_text += f"- **Reference Scenarios**: {len(structure['scenarios'])} scenarios defined\n"

        return (
            guidance_text
            if guidance_text
            else "No specific guidance provided in template."
        )

    async def _parse_ai_response(
        self, ai_text: str, template: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Parses AI response text into structured value projection format.

        Args:
            ai_text (str): Raw AI response text
            template (Dict[str, Any]): Template data for fallback

        Returns:
            Dict[str, Any]: Structured value projection data or None if parsing fails
        """
        try:
            # Use centralized JSON extraction with robust error handling
            parsed_data = VertexAIService.extract_json_from_text(ai_text, log_raw_text=True)
            
            if parsed_data and "scenarios" in parsed_data and isinstance(parsed_data["scenarios"], list):
                # Enhance with template information
                parsed_data["template_used"] = template.get("name", "AI-Enhanced Template")
                parsed_data["currency"] = "USD"

                # Ensure required fields exist
                if "methodology" not in parsed_data:
                    parsed_data["methodology"] = (
                        "AI-powered value projection with template guidance and robust parsing"
                    )
                if "assumptions" not in parsed_data:
                    parsed_data["assumptions"] = [
                        "AI-generated assumptions based on PRD analysis"
                    ]

                logger.info(
                    f"[SalesValueAnalystAgent] Successfully parsed JSON with {len(parsed_data['scenarios'])} scenarios"
                )
                return parsed_data
            else:
                # Fallback: manual extraction
                logger.warning(
                    "[SalesValueAnalystAgent] Centralized JSON parsing failed, attempting manual extraction"
                )
                return self._manual_extract_scenarios(ai_text, template)

        except Exception as e:
            logger.error(f"[SalesValueAnalystAgent] Error parsing AI response: {e}")
            logger.debug(f"[SalesValueAnalystAgent] Raw AI response: {ai_text[:500]}...")
            return self._manual_extract_scenarios(ai_text, template)

    def _manual_extract_scenarios(
        self, ai_text: str, template: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Manually extracts scenarios from AI text when JSON parsing fails.

        Args:
            ai_text (str): AI response text
            template (Dict[str, Any]): Template data

        Returns:
            Dict[str, Any]: Extracted value projection or None
        """
        try:
            scenarios = []

            # Look for value patterns in text
            value_patterns = [
                r"(?:Low|Conservative).*?[\$]?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
                r"(?:Base|Baseline|Most likely).*?[\$]?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
                r"(?:High|Optimistic).*?[\$]?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
            ]

            scenario_names = ["Low", "Base", "High"]

            for i, pattern in enumerate(value_patterns):
                match = re.search(pattern, ai_text, re.IGNORECASE)
                if match:
                    value_str = match.group(1).replace(",", "")
                    try:
                        value = int(float(value_str))
                        scenarios.append(
                            {
                                "case": scenario_names[i],
                                "value": value,
                                "description": f"AI-generated {scenario_names[i].lower()} estimate extracted from analysis",
                            }
                        )
                    except ValueError:
                        continue

            if scenarios:
                return {
                    "scenarios": scenarios,
                    "currency": "USD",
                    "template_used": template.get("name", "AI-Enhanced Template"),
                    "methodology": "AI-powered value projection with manual extraction",
                    "assumptions": [
                        "Extracted from AI analysis",
                        "Healthcare technology value factors",
                    ],
                    "notes": "Values extracted from AI response text analysis",
                }

            return None

        except Exception as e:
            logger.error(f"[SalesValueAnalystAgent] Manual extraction error: {e}")
            return None

    async def _project_with_template_fallback(
        self, prd_content: str, template: Dict[str, Any], case_title: str
    ) -> Dict[str, Any]:
        """
        Projects value using template-based hardcoded scenarios (enhanced fallback).

        Args:
            prd_content (str): The PRD content
            template (Dict[str, Any]): Pricing template data from Firestore
            case_title (str): Title of the business case

        Returns:
            Dict[str, Any]: Value projection response
        """
        # Use template structure to guide value scenarios
        template_structure = template.get("structureDefinition", {})
        template_type = template_structure.get("type", "LowBaseHigh")

        if template_type == "LowBaseHigh":
            # Check if template has predefined scenarios
            predefined_scenarios = template_structure.get("scenarios", [])

            if predefined_scenarios and len(predefined_scenarios) >= 3:
                # Use template's predefined scenarios
                scenarios = []
                for scenario in predefined_scenarios[:3]:  # Take first 3
                    scenarios.append(
                        {
                            "case": scenario.get("case", "Unknown").title(),
                            "value": scenario.get("value", 10000),
                            "description": scenario.get(
                                "description", "Template-defined scenario"
                            ),
                        }
                    )
            else:
                # Use default scenarios with template context
                scenarios = [
                    {
                        "case": "Low",
                        "value": 5000,
                        "description": "Conservative estimate based on minimal adoption and template guidance.",
                    },
                    {
                        "case": "Base",
                        "value": 15000,
                        "description": "Most likely estimate based on expected adoption and template framework.",
                    },
                    {
                        "case": "High",
                        "value": 30000,
                        "description": "Optimistic estimate based on high adoption and template opportunities.",
                    },
                ]

            value_data = {
                "scenarios": scenarios,
                "currency": "USD",
                "template_used": template.get("name", "Unknown Template"),
                "methodology": "Template-guided scenario modeling with structured definition",
                "assumptions": [
                    "Value based on template guidance and industry patterns",
                    "Healthcare technology adoption estimates",
                    "Template-defined market penetration factors",
                ],
                "notes": f"Value projection based on template '{template.get('name', 'Unknown')}' guidance and PRD analysis.",
            }
        else:
            # Fallback for other template types
            value_data = {
                "scenarios": [
                    {
                        "case": "Baseline",
                        "value": 12000,
                        "description": f"Standard value estimate using {template_type} methodology.",
                    }
                ],
                "currency": "USD",
                "template_used": template.get("name", "Unknown Template"),
                "methodology": f"Template-guided {template_type} estimation",
                "notes": f"Value projection using {template_type} methodology from template.",
            }

        logger.info(
            f"[SalesValueAnalystAgent] Successfully projected value for {case_title} using template fallback"
        )
        logger.info(
            f"[SalesValueAnalystAgent] Generated value projection using template: {template.get('name', 'Unknown')}"
        )

        return {
            "status": "success",
            "message": "Value projection completed successfully using enhanced pricing template",
            "value_projection": value_data,
        }

    async def _project_with_default_scenarios(
        self, prd_content: str, case_title: str
    ) -> Dict[str, Any]:
        """
        Projects value using hardcoded default scenarios.

        Args:
            prd_content (str): The PRD content
            case_title (str): Title of the business case

        Returns:
            Dict[str, Any]: Value projection response
        """
        # Default placeholder value scenarios
        value_data = {
            "scenarios": [
                {"case": "Low", "value": 5000, "description": "Conservative estimate."},
                {
                    "case": "Base",
                    "value": 15000,
                    "description": "Most likely estimate.",
                },
                {"case": "High", "value": 30000, "description": "Optimistic estimate."},
            ],
            "currency": "USD",
            "template_used": "Default Placeholder Template",
            "methodology": "Hardcoded scenario modeling (placeholder)",
            "assumptions": [
                "Basic healthcare technology value assumptions",
                "Standard ROI expectations for development projects",
                "Conservative market adoption estimates",
            ],
            "notes": "Initial placeholder value projection. Will be refined with real market data and business analysis.",
        }

        logger.info(
            f"[SalesValueAnalystAgent] Successfully projected value for {case_title} using defaults"
        )
        logger.info(
            f"[SalesValueAnalystAgent] Generated default value projection for case: {case_title}"
        )

        return {
            "status": "success",
            "message": "Value projection completed successfully using default scenarios",
            "value_projection": value_data,
        }

    def get_status(self) -> Dict[str, str]:
        """Get the current status of the Sales/Value Analyst Agent"""
        return {
            "name": self.name,
            "status": self.status,
            "description": self.description,
            "vertex_ai_available": str(self.vertex_ai_available),
            "model": self.model_name if self.vertex_ai_available else "Not available",
        }
