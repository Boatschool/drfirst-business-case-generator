"""
Utility to initialize default agent prompts in Firestore.
"""

import logging
from google.cloud import firestore
from ..models.agent_prompt import AgentPromptCreate
from ..services.prompt_service import PromptService
from ..core.constants import Defaults

logger = logging.getLogger(__name__)


async def initialize_default_prompts():
    """Initialize default prompts for all agents if they don't exist."""
    db = firestore.Client()
    prompt_service = PromptService(db)

    # Check if ProductManagerAgent PRD generation prompt exists
    existing_prompt = await prompt_service.get_prompt_by_agent_function(
        "ProductManagerAgent", "prd_generation"
    )

    if not existing_prompt:
        logger.info("Initializing default ProductManagerAgent PRD generation prompt...")

        # Default PRD generation prompt with placeholders
        default_prd_prompt = """You are an experienced Product Manager at DrFirst, a healthcare technology company. You are tasked with creating a comprehensive Product Requirements Document (PRD) based on the information provided below.

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

        prompt_data = AgentPromptCreate(
            agent_name="ProductManagerAgent",
            agent_function="prd_generation",
            title="PRD Generation - Healthcare Business Cases",
            description="Comprehensive prompt for generating structured Product Requirements Documents for DrFirst healthcare technology projects",
            prompt_template=default_prd_prompt,
            category="prd_generation",
            placeholders=["case_title", "problem_statement", "links_context"],
            ai_model_config={
                "temperature": 0.7,
                "max_tokens": Defaults.VERTEX_AI_MAX_TOKENS,
                "top_p": Defaults.VERTEX_AI_TOP_P,
                "top_k": Defaults.VERTEX_AI_TOP_K,
            },
            version_description="Initial default prompt with 8-section structure",
        )

        prompt_id = await prompt_service.create_prompt(prompt_data, "system")
        logger.info(f"✅ Created default ProductManagerAgent prompt with ID: {prompt_id}")
    else:
        logger.info("✅ ProductManagerAgent PRD generation prompt already exists")


# Additional agent prompts can be added here as the system grows
DEFAULT_PROMPTS = [
    {
        "agent_name": "ArchitectAgent",
        "agent_function": "system_design",
        "title": "System Design Generation",
        "description": "Generate technical system design documents based on approved PRDs",
        "prompt_template": """You are a Senior Software Architect at DrFirst. Generate a comprehensive system design based on the approved PRD.

**Input PRD:**
{prd_content}

**System Design Requirements:**
Create a structured system design document that includes:
1. Architecture Overview
2. Key Components & Services
3. Data Models & Storage
4. Integration Points
5. Security Considerations
6. Scalability & Performance
7. Technology Stack
8. Deployment Strategy

Use DrFirst's cloud-first, microservices architecture patterns. Consider HIPAA compliance and healthcare data requirements.

Generate the system design now:""",
        "category": "system_design",
        "placeholders": ["prd_content"],
    }
]
