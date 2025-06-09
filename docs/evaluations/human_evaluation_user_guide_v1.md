# Human Evaluation Web UI - User Guide v1.0

**Document Version**: v1.0  
**Date**: January 8, 2025  
**Target Audience**: Human Evaluators at DrFirst  
**Related System**: DrFirst Business Case Generator - Human Evaluation Interface

---

## 📖 Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Human Evaluation Interface Overview](#human-evaluation-interface-overview)
4. [Performing an Evaluation - Step-by-Step](#performing-an-evaluation---step-by-step)
5. [Evaluation Best Practices](#evaluation-best-practices)
6. [Frequently Asked Questions (FAQ)](#frequently-asked-questions-faq)
7. [Troubleshooting & Support](#troubleshooting--support)

---

## 🎯 Introduction

### Purpose of Human Evaluation

The DrFirst Business Case Generator uses AI agents to automatically create various business case components including Product Requirements Documents (PRDs), system architecture designs, effort estimates, and financial projections. While these AI agents are sophisticated, human evaluation is essential to:

- **Assess Quality**: Evaluate the relevance, accuracy, and usefulness of AI-generated content
- **Identify Improvements**: Provide feedback to enhance agent performance over time
- **Ensure Standards**: Maintain high-quality output standards for business-critical documents
- **Guide Development**: Inform future improvements to the AI agent system

### Your Role as an Evaluator

As a human evaluator, you play a crucial role in:
- Systematically reviewing AI agent outputs using defined metrics and rubrics
- Providing objective, constructive feedback through scores and detailed comments
- Ensuring consistent evaluation standards across different agent types and scenarios
- Contributing to the continuous improvement of the AI agent system

### What You'll Be Evaluating

You will evaluate outputs from six different AI agents, each with specific responsibilities:

- **ProductManagerAgent**: Generates Product Requirements Documents (PRDs)
- **ArchitectAgent**: Creates system architecture designs
- **PlannerAgent**: Provides effort estimation and project planning
- **SalesValueAnalystAgent**: Develops value projections and business cases
- **CostAnalystAgent**: Calculates cost estimates and financial analysis
- **FinancialModelAgent**: Creates comprehensive financial summaries

Each agent type has specific evaluation metrics tailored to their output type and purpose.

---

## 🚀 Getting Started

### Accessing the Evaluation UI

#### Prerequisites
- You must have an **admin role** account in the DrFirst Business Case Generator system
- Access to the web application at the designated URL
- Familiarity with the evaluation guidelines and rubrics

#### Step-by-Step Access
1. **Login to the Application**
   - Navigate to the DrFirst Business Case Generator web application
   - Click "Sign In" and authenticate using your Google account
   - Ensure your account has admin privileges (contact your administrator if needed)

2. **Navigate to Evaluations**
   - After successful login, look for the **"Evaluations"** button in the top navigation bar
   - The Evaluations link is only visible to users with admin roles
   - Click on **"Evaluations"** to access the human evaluation interface

3. **Verify Access**
   - You should see the Human Evaluation Interface with available evaluation tasks
   - If you encounter access denied errors, contact your system administrator

### Required Reference Materials

Before beginning evaluations, ensure you have access to these important documents:

- **📋 [Human Evaluation Guidelines v1](../../backend/evaluations/human_evaluation_guidelines_v1.md)**: Contains detailed rubrics and scoring principles for each metric
- **📊 [Evaluation Metrics Definition](../../backend/evaluations/evaluation_metrics_definition.md)**: Provides comprehensive definitions of all evaluation metrics and their applications
- **🎯 Agent Specifications**: Understanding of what each agent is designed to produce

> **💡 Pro Tip**: Keep the Human Evaluation Guidelines document open in a separate tab for quick reference while evaluating.

---

## 🖥️ Human Evaluation Interface Overview

### Layout Description

The Human Evaluation Interface consists of two main areas:

#### 📋 Task Selection Area (Left Sidebar)
- **Purpose**: Displays all available evaluation tasks
- **Content**: Shows a list of pending evaluations with:
  - Unique evaluation ID (e.g., `EVAL_20250607_PRODUCTMANAGER_PRD_SIMPLE_001`)
  - Agent name badge (color-coded for easy identification)
  - Input summary preview
  - Task counter showing total available tasks

#### 📝 Main Evaluation Area (Right Panel)
- **Purpose**: Displays detailed task information and evaluation form
- **Content**: Shows when a task is selected:
  - **Task Context Section**: Collapsible panel with agent information and input details
  - **Agent Output Section**: Collapsible panel containing the complete agent output to evaluate
  - **Evaluation Metrics Section**: Dynamic form with agent-specific rating fields and comment areas
  - **Overall Assessment Section**: Overall quality score and general comments
  - **Submit Button**: Finalizes and saves the evaluation

### Visual Indicators

- **🟢 Selected Task**: Highlighted in the task list with distinct background color
- **⭐ Rating Stars**: Interactive 1-5 star ratings with descriptive labels
- **🔄 Loading States**: Spinning indicators during data loading and submission
- **✅ Success Messages**: Green alerts confirming successful submissions
- **❌ Error Messages**: Red alerts indicating issues or validation errors

---

## 📋 Performing an Evaluation - Step-by-Step

### Step 1: Selecting an Evaluation Task

1. **Browse Available Tasks**
   - Review the task list in the left sidebar
   - Each task shows:
     - Evaluation ID (unique identifier)
     - Agent name (in a colored badge)
     - Brief input summary

2. **Choose a Task**
   - Click on any task in the list to select it
   - The selected task will be highlighted
   - The main evaluation area will load the task details

3. **Understand Task Priority**
   - Tasks can be completed in any order
   - Consider starting with agent types you're most familiar with
   - All tasks should be completed for a comprehensive evaluation

### Step 2: Reviewing Task Details

#### Understanding the Context Display
1. **Expand the "Task Context" Section** (if not already expanded)
   - Review the **Agent** being evaluated
   - Read the **Input Summary** to understand what the agent was asked to do
   - Note any specific requirements or constraints mentioned

2. **Examine Original Requirements**
   - Pay attention to the problem statement and goals
   - Understand the expected deliverables
   - Consider the complexity and scope of the request

#### Understanding the Agent Output
1. **Expand the "Agent Output to Evaluate" Section**
   - This contains the complete output generated by the AI agent
   - The content may be lengthy - use the scrollable area to review all content
   - Pay attention to:
     - **Structure and Organization**: How well the content is organized
     - **Completeness**: Whether all required elements are present
     - **Quality and Relevance**: How well the content addresses the input requirements

### Step 3: Using the Dynamic Evaluation Form

#### Understanding Metric Variation
The evaluation metrics shown will automatically change based on the agent type:

- **ProductManagerAgent**: Content Relevance & Quality
- **ArchitectAgent**: Plausibility & Appropriateness, Clarity & Understandability
- **PlannerAgent**: Reasonableness of Hours, Quality of Rationale
- **SalesValueAnalystAgent**: Plausibility of Projections

#### Scoring Each Metric

1. **Review the Metric Definition**
   - Refer to the [Human Evaluation Guidelines](../../backend/evaluations/human_evaluation_guidelines_v1.md) for detailed rubrics
   - Understand what each score level (1-5) means for the specific metric

2. **Assign a Score**
   - Click on the appropriate star rating (1-5)
   - Rating descriptions:
     - ⭐ **1 - Very Poor**: Significant issues, unusable content
     - ⭐⭐ **2 - Poor**: Major problems, limited value
     - ⭐⭐⭐ **3 - Average**: Adequate quality, some issues
     - ⭐⭐⭐⭐ **4 - Good**: High quality, minor improvements needed
     - ⭐⭐⭐⭐⭐ **5 - Excellent**: Outstanding quality, meets all criteria

3. **Add Detailed Comments**
   - **Required for scores below 4**: Explain specific issues and areas for improvement
   - **Recommended for all scores**: Provide constructive feedback
   - **Focus on specifics**: Cite examples from the agent output
   - **Be constructive**: Suggest improvements rather than just identifying problems

#### Comment Writing Guidelines

**Good Comment Examples:**
- ✅ "The PRD structure is well-organized, but lacks specific acceptance criteria for the mobile interface requirements. Consider adding measurable success metrics."
- ✅ "The architecture appropriately addresses scalability concerns through microservices design. The security considerations section could benefit from more detail on data encryption."

**Poor Comment Examples:**
- ❌ "Looks good" (too generic)
- ❌ "This is wrong" (not constructive or specific)
- ❌ "I don't like this approach" (subjective without justification)

### Step 4: Providing Overall Assessment

#### Overall Quality Score
1. **Consider All Metrics Holistically**
   - Don't simply average the individual metric scores
   - Consider the overall usefulness and quality of the agent output
   - Think about whether this output would be valuable in a real business context

2. **Assign Overall Score**
   - Use the same 1-5 star scale
   - This score represents your comprehensive assessment of the agent's performance on this task

#### Overall Comments
1. **Summarize Key Strengths**
   - Highlight what the agent did well
   - Note any particularly impressive aspects

2. **Identify Major Areas for Improvement**
   - Focus on the most important issues
   - Prioritize feedback that would have the biggest impact

3. **Provide Context**
   - Consider the complexity of the task
   - Note any challenging aspects the agent handled well or poorly

### Step 5: Submitting the Evaluation

1. **Review Your Evaluation**
   - Ensure all required metrics have scores (you cannot submit with missing scores)
   - Verify that your comments are clear and constructive
   - Double-check that your overall assessment reflects your detailed evaluation

2. **Submit the Evaluation**
   - Click the **"Submit Evaluation"** button at the bottom of the form
   - The system will validate your input and show a loading indicator
   - Upon successful submission:
     - You'll see a green success message with a submission ID
     - The completed task will be removed from the task list
     - The form will be cleared for the next evaluation

3. **Handle Potential Issues**
   - **Missing Scores**: You'll see an error message indicating which metrics need scores
   - **Network Issues**: Try refreshing the page and resubmitting
   - **Validation Errors**: Check that all required fields are completed

---

## 🎯 Evaluation Best Practices

### Consistency in Evaluation

1. **Apply Rubrics Uniformly**
   - Use the same standards for all evaluations of the same agent type
   - Refer to the evaluation guidelines consistently
   - Don't let the order of evaluation affect your scoring

2. **Calibrate Your Scoring**
   - Start with a few evaluations to understand the scoring scale
   - Adjust your standards if you find yourself consistently scoring too high or too low
   - Consider the full range of the 1-5 scale

### Maintaining Objectivity

1. **Focus on Defined Metrics**
   - Evaluate based on the specific metrics provided, not personal preferences
   - Consider the agent's intended purpose and constraints
   - Separate content quality from personal domain expertise

2. **Avoid Bias**
   - Don't let previous evaluations influence current ones
   - Consider each task independently
   - Base scores on the actual output, not expectations

### Providing Valuable Feedback

1. **Be Specific and Actionable**
   - Point to specific sections or elements in the agent output
   - Suggest concrete improvements rather than general criticisms
   - Explain the reasoning behind your scores

2. **Balance Criticism with Recognition**
   - Acknowledge what the agent did well
   - Provide constructive criticism for areas needing improvement
   - Consider the difficulty of the task when evaluating performance

---

## ❓ Frequently Asked Questions (FAQ)

### Q1: What if I'm unsure how to score a particular metric?

**A:** Refer to the detailed rubrics in the [Human Evaluation Guidelines v1](../../backend/evaluations/human_evaluation_guidelines_v1.md). Each metric has specific criteria for each score level (1-5). If you're still unsure after reviewing the guidelines:
- Note your uncertainty in the comments section
- Choose the score that best matches your assessment
- Consult with the evaluation lead or team for clarification
- Document your reasoning in the comments for future reference

### Q2: What if the agent output is completely irrelevant or nonsensical for the given input?

**A:** This is valuable data! Handle it as follows:
- Score relevant metrics very low (typically 1 - Very Poor)
- Clearly explain in the comments why the output is irrelevant or problematic
- Provide specific examples of what's wrong (e.g., "Output discusses mobile app development when the input requested financial analysis")
- In overall comments, summarize the fundamental mismatch between input and output
- Don't hesitate to give low scores - this feedback helps improve the AI agents

### Q3: Can I save a partially completed evaluation and come back to it later?

**A:** Currently, the V1 evaluation interface does **not** include a "save draft" feature. Evaluations should be completed and submitted in one session. To manage this:
- Plan sufficient time to complete each evaluation (typically 10-20 minutes per task)
- If you need to stop mid-evaluation, take notes externally and restart the task later
- The system will preserve your task list, so you can return to incomplete tasks
- Future versions may include draft-saving functionality

### Q4: What if I make a mistake after submitting an evaluation?

**A:** Currently, submitted evaluations **cannot be edited or deleted** through the web interface. To handle mistakes:
- **Prevention**: Carefully review all scores and comments before clicking "Submit Evaluation"
- **Minor Errors**: Small mistakes (like typos in comments) generally don't require action
- **Major Errors**: If you discover a significant error that could affect analysis:
  - Document the error and correction needed
  - Contact the evaluation lead immediately with the submission ID (provided after submission)
  - The evaluation team can make corrections in the database if necessary

### Q5: Where can I find detailed definitions for each agent and what they are supposed to do?

**A:** Comprehensive agent information is available in:
- **[Evaluation Metrics Definition](../../backend/evaluations/evaluation_metrics_definition.md)**: Describes each agent's purpose and evaluation criteria
- **Project System Design Documentation**: Detailed technical specifications for each agent
- **Agent Specifications**: Individual agent capabilities and intended outputs

For quick reference:
- **ProductManagerAgent**: Creates Product Requirements Documents (PRDs)
- **ArchitectAgent**: Designs system architecture and technical specifications
- **PlannerAgent**: Provides effort estimation and resource planning
- **SalesValueAnalystAgent**: Develops value propositions and business cases
- **CostAnalystAgent**: Calculates cost estimates and financial analysis
- **FinancialModelAgent**: Creates comprehensive financial models and summaries

### Q6: Who do I contact if I encounter technical issues with the evaluation UI?

**A:** For technical support with the evaluation interface:
- **Primary Contact**: Evaluation Team Lead - [contact information to be provided]
- **IT Support**: DrFirst IT Support Channel/Email - [contact information to be provided]
- **System Administrator**: Admin contact for user access issues - [contact information to be provided]

**Common Issues to Report:**
- Login or authentication problems
- Missing or incorrect evaluation tasks
- UI functionality not working (buttons, forms, etc.)
- Submission failures or errors
- Data loading issues

**When Reporting Issues:**
- Include your username/email
- Describe the specific problem and steps to reproduce it
- Note any error messages received
- Include the browser and version you're using

### Q7: How many evaluations am I expected to complete?

**A:** Evaluation workload expectations will be communicated by the evaluation lead for each evaluation round. Factors include:
- **Total available tasks**: Number of agent outputs prepared for evaluation
- **Evaluation team size**: How many evaluators are participating
- **Timeline**: Deadline for completing the evaluation round
- **Individual capacity**: Your availability and other responsibilities

**Typical expectations:**
- Quality over quantity - thorough evaluations are more valuable than rushed ones
- Consistent participation across evaluation rounds
- Completion within the specified timeframe
- Communication if you cannot meet assigned expectations

### Q8: What if the "Agent Output to Evaluate" is very long?

**A:** Long agent outputs are common, especially for complex tasks. Handle them effectively:

**Review Strategy:**
- **Scan for Structure**: Look for headers, sections, and organization first
- **Focus on Key Sections**: Prioritize sections most relevant to the evaluation metrics
- **Use Scrolling**: The interface provides scrollable areas for long content

**Evaluation Approach:**
- **Don't Penalize Length**: Length alone isn't necessarily good or bad
- **Assess Completeness**: Longer outputs may be more comprehensive
- **Consider Relevance**: Evaluate whether the length adds value or includes unnecessary content
- **Focus on Metrics**: Keep evaluation criteria in mind rather than trying to read every word

**If Length is Problematic:**
- Note in comments if the output is unnecessarily verbose
- Consider if conciseness would improve the output for its intended use
- Evaluate based on the specific metrics provided, not general length preferences

### Q9: What if I disagree with the evaluation metrics or think something important is missing?

**A:** The evaluation metrics are carefully designed based on research and expert input, but feedback is valuable:

**For Current Evaluations:**
- Complete evaluations using the provided metrics
- Note additional observations in the overall comments section
- Document specific suggestions for metric improvements

**For Future Improvements:**
- Provide detailed feedback to the evaluation lead
- Suggest specific additional metrics or modifications
- Explain the business value of your proposed changes
- Consider how suggestions would apply across different agent types

### Q10: How do I know if my evaluations are being done correctly?

**A:** Quality indicators for good evaluations:

**Self-Assessment Checklist:**
- ✅ You're consistently referring to the evaluation guidelines
- ✅ Your scores vary appropriately (not all 3s or all 5s)
- ✅ Your comments provide specific, actionable feedback
- ✅ You can explain your reasoning for each score
- ✅ You're considering the agent's intended purpose

**Feedback Mechanisms:**
- The evaluation lead may provide feedback on evaluation quality
- Periodic calibration sessions help ensure consistency
- Statistical analysis can identify outlier patterns
- Follow-up discussions help clarify evaluation approaches

---

## 🔧 Troubleshooting & Support

### Common Technical Issues

#### Authentication Problems
- **Symptom**: Cannot access the evaluation interface
- **Solution**: Verify you have admin role privileges, clear browser cache, or contact IT support

#### Loading Issues
- **Symptom**: Tasks not loading or interface appears broken
- **Solution**: Refresh the page, check internet connection, try a different browser

#### Submission Failures
- **Symptom**: Evaluation won't submit or shows error messages
- **Solution**: Check that all required fields are completed, try submitting again, contact support if persistent

### Browser Compatibility

**Recommended Browsers:**
- Chrome (latest version)
- Firefox (latest version)
- Safari (latest version)
- Edge (latest version)

**Browser Settings:**
- Enable JavaScript
- Allow cookies from the application domain
- Disable ad blockers that might interfere with the interface

### Performance Tips

- **Close unnecessary browser tabs** to improve performance
- **Use a stable internet connection** for best experience
- **Clear browser cache** if experiencing persistent issues
- **Disable browser extensions** that might interfere with the application

### Getting Additional Help

#### For Evaluation Process Questions:
- **Evaluation Lead**: [Name/Contact to be provided]
- **Evaluation Team**: [Email/Slack Channel to be provided]
- **Documentation**: Reference the Human Evaluation Guidelines and Metrics Definition documents

#### For Technical Support:
- **Application Support**: [Contact Information to be provided]
- **IT Helpdesk**: [Contact Information to be provided]
- **System Administrator**: [Contact Information to be provided]

#### For Training and Onboarding:
- **Evaluation Training Sessions**: [Schedule/Contact to be provided]
- **One-on-One Support**: Available upon request
- **Documentation Updates**: Suggest improvements to this guide

---

## 📚 Additional Resources

- **[Human Evaluation Guidelines v1](../../backend/evaluations/human_evaluation_guidelines_v1.md)**: Detailed rubrics and scoring principles
- **[Evaluation Metrics Definition](../../backend/evaluations/evaluation_metrics_definition.md)**: Comprehensive metric definitions
- **[Project Documentation](../../README.md)**: Overview of the DrFirst Business Case Generator system
- **[System Architecture](../../docs/)**: Technical details about the AI agent system

---

**Document Information:**
- **Created**: January 8, 2025
- **Version**: 1.0
- **Next Review**: To be scheduled based on user feedback
- **Document Owner**: Evaluation Team Lead
- **Feedback**: Please provide suggestions for improving this guide to the evaluation team 