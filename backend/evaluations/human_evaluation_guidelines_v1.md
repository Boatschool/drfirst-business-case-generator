# Human Evaluation Guidelines v1.0

**Document Version**: v1.0  
**Date**: June 7, 2025  
**Purpose**: Guidelines for human evaluators to assess AI agent outputs

---

## 📋 General Instructions

### Rating Scale (1-5)
- **5 - Excellent**: Exceptional quality, exceeds professional standards
- **4 - Good**: High quality with minor improvements needed
- **3 - Average**: Acceptable, meets basic requirements
- **2 - Poor**: Below average, significant issues
- **1 - Very Poor**: Unacceptable, major problems

### Evaluation Process
1. Review input and expected characteristics from golden dataset
2. Examine agent output completely
3. Apply rubrics for each applicable human metric
4. Provide scores (1-5) and explanatory comments
5. Give overall assessment

---

## 🎯 Agent-Specific Rubrics

### ProductManagerAgent - Content Relevance & Quality

**Score 5 - Excellent**
- Content comprehensively addresses all problem aspects
- Demonstrates deep healthcare domain understanding
- Professional writing suitable for stakeholder presentation
- Considers regulatory requirements (HIPAA, FDA)
- Realistic, actionable technical requirements
- Clear, specific acceptance criteria

**Score 3 - Average**
- Addresses basic problem requirements
- Basic healthcare context understanding
- Adequate writing with some clarity issues
- Limited regulatory consideration
- Basic but achievable technical requirements
- Present but imprecise acceptance criteria

**Score 1 - Very Poor**
- Fails to address core problem
- No healthcare domain understanding
- Unprofessional or incomprehensible writing
- No regulatory consideration
- Missing or impossible technical requirements
- Absent or unusable acceptance criteria

### ArchitectAgent - Plausibility & Appropriateness

**Score 5 - Excellent**
- Highly appropriate for requirements and scale
- Modern, proven technologies suited for healthcare
- Excellent security and compliance understanding
- Well-addressed scalability and performance
- Realistic integration patterns following best practices
- Proportional cost/complexity to business value

**Score 3 - Average**
- Generally suitable with some questionable elements
- Acceptable but potentially sub-optimal technology choices
- Basic healthcare security understanding
- Some scalability considerations present
- Standard integration patterns
- Reasonable cost/complexity ratio

**Score 1 - Very Poor**
- Inappropriate or unrealistic for requirements
- Poor, outdated, or unsuitable technology choices
- No healthcare security/compliance understanding
- No scalability or performance consideration
- Missing or impossible integration patterns
- Disproportionate complexity or over-simplification

### ArchitectAgent - Clarity & Understandability

**Score 5 - Excellent**
- Exceptional clarity and organization
- Accessible to both technical and business audiences
- Clear logical flow from requirements to decisions
- Component relationships clearly explained
- Specific, actionable implementation guidance
- Enables effective development team onboarding

**Score 3 - Average**
- Adequately explained with some unclear areas
- Mostly appropriate technical language
- Basic organization with some concept jumping
- Some component relationships could be clearer
- Limited implementation guidance
- Requires moderate clarification

**Score 1 - Very Poor**
- Poorly explained or incomprehensible
- Excessive jargon without context
- No clear organization or logical flow
- Missing or unclear component relationships
- No practical implementation guidance
- Unusable without complete rewrite

### PlannerAgent - Reasonableness of Hours

**Score 5 - Excellent**
- Highly realistic estimates for scope and complexity
- Excellent understanding of software development workflows
- Considers healthcare compliance, testing, security requirements
- Appropriate buffer for complexity and risk
- Well-balanced role distribution
- Achievable timeline enabling accurate planning

**Score 3 - Average**
- Generally reasonable estimates with some outliers
- Basic software development process understanding
- Limited healthcare-specific requirement consideration
- Some complexity recognition but missing factors
- Reasonable but potentially unoptimized role distribution
- Achievable but possibly optimistic/conservative timeline

**Score 1 - Very Poor**
- Completely unrealistic estimates
- No software development process understanding
- No healthcare domain requirement consideration
- No complexity or risk factor recognition
- Nonsensical role distribution
- Completely unrealistic timeline
- Unusable for any planning purpose

### PlannerAgent - Quality of Rationale

**Score 5 - Excellent**
- Comprehensive justification for all major decisions
- Deep understanding of technical and business complexity
- Clear healthcare domain requirement explanations
- Explicitly addresses risks, dependencies, complexity
- Considers iterative development, testing, QA needs
- Logical, well-structured, professional reasoning
- Instills stakeholder confidence

**Score 3 - Average**
- Basic justification for key decisions
- Adequate complexity factor understanding
- Limited healthcare domain consideration
- Some risk and dependency recognition
- Basic development process understanding
- Generally sound but could be more detailed
- Sufficient for planning purposes

**Score 1 - Very Poor**
- Absent, nonsensical, or completely inadequate reasoning
- No project complexity or requirement understanding
- No domain-specific factor consideration
- No risk, dependency, or QA recognition
- Flawed, contradictory, or missing logic
- Undermines confidence in estimation process
- Unusable for planning or decision-making

### SalesValueAnalystAgent - Plausibility of Projections

**Score 5 - Excellent**
- Highly plausible, grounded in healthcare market realities
- Appropriate scenario range with logical progression
- Excellent healthcare economics understanding
- Clear feature-benefit connections
- Realistic adoption, penetration, competitive consideration
- Clear, defensible assumptions
- Credible to healthcare executives

**Score 3 - Average**
- Reasonable range with some questionable elements
- Appropriate but unsophisticated scenario differentiation
- Basic healthcare economics understanding
- Some feature-benefit connection
- Limited market complexity consideration
- Some stated but partially justified assumptions
- Adequate business case basis

**Score 1 - Very Poor**
- Completely implausible or unjustified projections
- Unrealistic or nonsensical scenarios
- No healthcare business economics understanding
- No meaningful feature-value connection
- No market reality or adoption consideration
- Missing, wrong, or unreasonable assumptions
- Would be rejected by informed stakeholders

---

## 📊 Evaluation Guidelines

### Key Principles
- **Healthcare Context**: Consider domain-specific requirements
- **Business Focus**: Evaluate for real-world utility
- **Professional Standards**: Assess as if for actual business use
- **Consistency**: Apply same standards across evaluations

### Scoring Best Practices
- Use full 1-5 scale range
- Be decisive when between scores
- Focus on business value and utility
- Consider intended audience needs
- Provide specific, constructive comments

### Comment Guidelines
- Reference specific aspects influencing scores
- Suggest improvements for low scores
- Acknowledge both strengths and weaknesses
- Maintain objective, business-focused language

---

**Prepared By**: AI/ML Evaluation Process Designer  
**Date**: June 7, 2025 