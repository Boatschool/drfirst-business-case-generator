# DrFirst Business Case Generator - Evaluation Metrics Definition

## Overview

This document defines initial evaluation metrics for each of the 6 core AI agents in the DrFirst Business Case Generator. These metrics provide a foundation for both automated and human evaluation processes to assess agent performance, accuracy, and output quality.

**Document Version**: v1.0  
**Date**: June 7, 2025  
**Related Tasks**: EVAL-1.1 (Agent Logging), EVAL-1.2 (Metrics & Golden Datasets)

---

## Evaluation Metric Categories

- **Automated**: Metrics that can be checked programmatically through code
- **Human**: Metrics that require human judgment and expertise

---

## Agent Evaluation Metrics

### 1. ProductManagerAgent (PRD Generation)

**Purpose**: Generates Product Requirements Documents (PRDs) from problem statements, titles, and reference links.

#### Metrics:

**Metric 1: Structural Completeness** *(Automated)*
- **Description**: Verifies that the generated PRD contains all standard required sections
- **Measurement**: Boolean check for presence of key sections (Introduction, Goals, Key Features, Technical Requirements, Acceptance Criteria, etc.)
- **Implementation**: Regex/parsing to identify markdown headers and required content blocks
- **Success Criteria**: All required sections present = Pass, Missing sections = Fail

**Metric 2: Markdown Validity** *(Automated)*
- **Description**: Ensures the output is syntactically valid Markdown
- **Measurement**: Parse output with Markdown linter/parser
- **Implementation**: Use Python markdown library or dedicated linter
- **Success Criteria**: Valid markdown syntax = Pass, Syntax errors = Fail

**Metric 3: Content Relevance & Quality** *(Human)*
- **Description**: Assesses how relevant and high-quality the content is within each section given the input
- **Measurement**: Human evaluator rates on 1-5 scale
- **Evaluation Criteria**:
  - 5: Excellent - Highly relevant, comprehensive, well-structured
  - 4: Good - Relevant with minor gaps or improvements needed
  - 3: Average - Adequate but lacking depth or some relevance
  - 2: Poor - Limited relevance or significant quality issues
  - 1: Very Poor - Irrelevant or very low quality content

---

### 2. ArchitectAgent (System Design Generation)

**Purpose**: Generates system architecture designs from approved PRDs.

#### Metrics:

**Metric 1: Presence of Key Architectural Sections** *(Automated)*
- **Description**: Checks for mention of essential architectural components
- **Measurement**: Boolean check for presence of key terms/sections
- **Key Components**: Data Storage, API Design, Frontend Architecture, Backend Services, Security, Integration Points
- **Implementation**: Text analysis for architectural keywords and section headers
- **Success Criteria**: Presence of 4+ out of 6 key components = Pass

**Metric 2: Plausibility & Appropriateness** *(Human)*
- **Description**: Evaluates whether the suggested architecture is suitable and realistic for the given PRD
- **Measurement**: Human evaluator rates on 1-5 scale
- **Evaluation Criteria**:
  - 5: Excellent - Highly appropriate, well-matched to requirements
  - 4: Good - Appropriate with minor adjustments needed
  - 3: Average - Generally suitable but some concerns
  - 2: Poor - Questionable fit or significant issues
  - 1: Very Poor - Inappropriate or unrealistic architecture

**Metric 3: Clarity & Understandability** *(Human)*
- **Description**: Assesses how clearly the system design is explained and documented
- **Measurement**: Human evaluator rates on 1-5 scale
- **Evaluation Criteria**:
  - 5: Excellent - Very clear, well-organized, easy to understand
  - 4: Good - Clear with minor areas needing clarification
  - 3: Average - Generally understandable but some complexity
  - 2: Poor - Difficult to follow or understand
  - 1: Very Poor - Confusing or unclear documentation

---

### 3. PlannerAgent (Effort Estimation)

**Purpose**: Estimates development effort by role based on PRD and system design content.

#### Metrics:

**Metric 1: JSON Output Validity** *(Automated)*
- **Description**: Verifies that the output conforms to the expected JSON schema
- **Measurement**: JSON schema validation
- **Required Fields**: roles (array), total_hours (number), estimated_duration_weeks (number), complexity_assessment (string), notes (string)
- **Implementation**: JSON schema validator with defined effort estimation schema
- **Success Criteria**: Valid JSON matching schema = Pass, Invalid/malformed = Fail

**Metric 2: Reasonableness of Hours** *(Human)*
- **Description**: Evaluates whether estimated hours for each role are within believable ranges
- **Measurement**: Human evaluator rates on 1-5 scale
- **Evaluation Criteria**:
  - 5: Excellent - All estimates very reasonable and well-balanced
  - 4: Good - Most estimates reasonable with minor questions
  - 3: Average - Generally reasonable but some outliers
  - 2: Poor - Several unrealistic estimates
  - 1: Very Poor - Most estimates unrealistic or unreasonable

**Metric 3: Quality of Rationale** *(Human)*
- **Description**: Assesses whether the provided rationale is sensible and justifies the estimates
- **Measurement**: Human evaluator rates on 1-5 scale
- **Evaluation Criteria**:
  - 5: Excellent - Clear, detailed, well-justified rationale
  - 4: Good - Good rationale with minor gaps
  - 3: Average - Adequate explanation but lacking detail
  - 2: Poor - Weak or poorly justified rationale
  - 1: Very Poor - No clear rationale or completely unjustified

---

### 4. CostAnalystAgent (Cost Calculation)

**Purpose**: Applies rate cards to effort estimates to generate financial cost projections.

#### Metrics:

**Metric 1: Calculation Correctness** *(Automated)*
- **Description**: Verifies mathematical accuracy of cost calculations given input effort and rate card
- **Measurement**: Programmatic verification of (hours × rates) calculations
- **Implementation**: Mock rate card with known values, verify total cost calculation
- **Success Criteria**: Calculated cost matches expected mathematical result = Pass, Incorrect calculation = Fail

**Metric 2: Currency & Rate Card Info Presence** *(Automated)*
- **Description**: Ensures required metadata fields are correctly populated in output
- **Measurement**: Check for presence and validity of required fields
- **Required Fields**: currency, rate_card_used, estimated_cost, role_costs (array)
- **Implementation**: Field presence validation and data type checking
- **Success Criteria**: All required fields present and properly formatted = Pass, Missing/invalid fields = Fail

---

### 5. SalesValueAnalystAgent (Value Projection)

**Purpose**: Projects business value and revenue scenarios based on PRD content and pricing templates.

#### Metrics:

**Metric 1: Scenario Presence** *(Automated)*
- **Description**: Verifies that expected value scenarios are present in the output
- **Measurement**: Check for presence of Low, Base, High scenarios (or template-defined scenarios)
- **Implementation**: Parse output JSON/text for scenario structure
- **Success Criteria**: All expected scenarios present = Pass, Missing scenarios = Fail

**Metric 2: JSON Output Validity** *(Automated)*
- **Description**: Ensures output conforms to expected value projection JSON structure
- **Measurement**: JSON schema validation
- **Required Fields**: scenarios (array), methodology (string), assumptions (array), market_factors (array)
- **Implementation**: JSON schema validator for value projection format
- **Success Criteria**: Valid JSON matching schema = Pass, Invalid/malformed = Fail

**Metric 3: Plausibility of Projections** *(Human)*
- **Description**: Evaluates whether projected values and descriptions are believable given the PRD and template
- **Measurement**: Human evaluator rates on 1-5 scale
- **Evaluation Criteria**:
  - 5: Excellent - Highly plausible and well-reasoned projections
  - 4: Good - Generally plausible with minor concerns
  - 3: Average - Somewhat plausible but questionable elements
  - 2: Poor - Several implausible projections or weak reasoning
  - 1: Very Poor - Unrealistic or completely implausible projections

---

### 6. FinancialModelAgent (Financial Summary)

**Purpose**: Consolidates approved cost estimates and value projections into comprehensive financial summaries.

#### Metrics:

**Metric 1: Metric Calculation Correctness** *(Automated)*
- **Description**: Verifies accuracy of calculated financial metrics
- **Measurement**: Programmatic verification of financial calculations
- **Key Calculations**: 
  - Net Value = Value - Cost
  - ROI = ((Net Value / Cost) × 100)
  - Scenario comparisons
- **Implementation**: Mathematical validation against known inputs
- **Success Criteria**: All calculations mathematically correct = Pass, Calculation errors = Fail

**Metric 2: Presence of Key Figures** *(Automated)*
- **Description**: Ensures all essential financial figures are included in the summary
- **Measurement**: Check for presence of required financial metrics
- **Required Figures**: total_estimated_cost, currency, value_scenarios, financial_metrics (with ROI calculations)
- **Implementation**: Field presence validation and structure checking
- **Success Criteria**: All required figures present = Pass, Missing key figures = Fail

---

## Implementation Guidelines

### Automated Metrics Implementation

1. **JSON Schema Validation**: Use Python jsonschema library
2. **Markdown Parsing**: Use Python markdown library or CommonMark
3. **Mathematical Verification**: Implement calculation checkers with tolerance for floating-point precision
4. **Text Analysis**: Use regex patterns and keyword matching for structural checks

### Human Evaluation Guidelines

1. **Rating Scale Consistency**: Provide detailed rubrics for 1-5 scales
2. **Evaluator Training**: Ensure evaluators understand domain context
3. **Inter-rater Reliability**: Use multiple evaluators for critical assessments
4. **Evaluation Templates**: Create standardized forms for consistent rating

### Evaluation Workflow

1. **Automated Pre-screening**: Run all automated metrics first
2. **Human Evaluation**: Only proceed to human evaluation if automated checks pass
3. **Scoring Aggregation**: Combine automated (pass/fail) and human (1-5) scores
4. **Threshold Setting**: Define minimum acceptable scores for each metric

---

## Future Enhancements

### Additional Metrics to Consider

- **Response Time Performance**: Agent execution speed
- **Consistency**: Multiple runs with same input produce similar outputs
- **Factual Accuracy**: Verification against known data sources
- **Bias Detection**: Analysis for potential biases in outputs
- **User Satisfaction**: End-user feedback on output quality

### Evaluation Automation

- **Continuous Evaluation**: Integrate metrics into CI/CD pipeline
- **A/B Testing Support**: Compare different agent versions
- **Real-time Monitoring**: Track metrics in production
- **Automated Reporting**: Generate evaluation dashboards

---

## Conclusion

These initial evaluation metrics provide a comprehensive framework for assessing the performance and quality of all 6 AI agents in the DrFirst Business Case Generator. The combination of automated and human evaluation ensures both technical accuracy and qualitative assessment of outputs.

The metrics are designed to be:
- **Measurable**: Clear criteria for success/failure
- **Relevant**: Aligned with business objectives and user needs
- **Actionable**: Results can guide improvements and optimizations
- **Scalable**: Can be expanded and refined over time 