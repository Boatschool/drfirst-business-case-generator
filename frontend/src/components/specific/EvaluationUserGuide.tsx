import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Paper,
  Divider,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Star as StarIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Book as BookIcon,
  Assignment as AssignmentIcon,
} from '@mui/icons-material';

const EvaluationUserGuide: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        <BookIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Evaluation Center User Guide
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Version 2.0 - Complete guide for monitoring and evaluating AI agent performance
      </Typography>

      {/* Introduction Section */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom color="primary">
            🎯 Introduction
          </Typography>
          
          <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
            Purpose of Human Evaluation
          </Typography>
          <Typography variant="body1" paragraph>
            The DrFirst Business Case Generator uses AI agents to automatically create various business case components including Product Requirements Documents (PRDs), system architecture designs, effort estimates, and financial projections. While these AI agents are sophisticated, human evaluation is essential to:
          </Typography>
          
          <List dense>
            <ListItem>
              <ListItemIcon><CheckCircleIcon color="primary" /></ListItemIcon>
              <ListItemText primary="Assess Quality: Evaluate the relevance, accuracy, and usefulness of AI-generated content" />
            </ListItem>
            <ListItem>
              <ListItemIcon><CheckCircleIcon color="primary" /></ListItemIcon>
              <ListItemText primary="Identify Improvements: Provide feedback to enhance agent performance over time" />
            </ListItem>
            <ListItem>
              <ListItemIcon><CheckCircleIcon color="primary" /></ListItemIcon>
              <ListItemText primary="Ensure Standards: Maintain high-quality output standards for business-critical documents" />
            </ListItem>
            <ListItem>
              <ListItemIcon><CheckCircleIcon color="primary" /></ListItemIcon>
              <ListItemText primary="Guide Development: Inform future improvements to the AI agent system" />
            </ListItem>
          </List>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            What You'll Be Evaluating
          </Typography>
          <Typography variant="body1" paragraph>
            You will evaluate outputs from six different AI agents, each with specific responsibilities:
          </Typography>
          
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
            <Chip label="ProductManagerAgent" color="primary" variant="outlined" />
            <Chip label="ArchitectAgent" color="secondary" variant="outlined" />
            <Chip label="PlannerAgent" color="success" variant="outlined" />
            <Chip label="SalesValueAnalystAgent" color="warning" variant="outlined" />
            <Chip label="CostAnalystAgent" color="error" variant="outlined" />
            <Chip label="FinancialModelAgent" color="info" variant="outlined" />
          </Box>
        </CardContent>
      </Card>

      {/* Dashboard Guide Section */}
      <Accordion sx={{ mb: 2 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">📊 Using the Evaluation Dashboard</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="h6" gutterBottom>
            Dashboard Overview
          </Typography>
          <Typography variant="body1" paragraph>
            The unified Evaluation Dashboard provides a comprehensive view of all evaluation activities in one location. It combines both automated evaluation metrics and human evaluation insights to give you a complete picture of AI agent performance.
          </Typography>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            Dashboard Sections
          </Typography>
          
          <Paper sx={{ p: 2, mb: 2, bgcolor: 'primary.50' }}>
            <Typography variant="h6" gutterBottom color="primary">
              🤖 Automated Evaluation Metrics
            </Typography>
            <Typography variant="body2" paragraph>
              This section shows system-generated performance data from automated test runs:
            </Typography>
            <List dense>
              <ListItem>
                <ListItemIcon><CheckCircleIcon color="primary" /></ListItemIcon>
                <ListItemText primary="Total Evaluation Runs: Number of completed automated test runs" />
              </ListItem>
              <ListItem>
                <ListItemIcon><CheckCircleIcon color="primary" /></ListItemIcon>
                <ListItemText primary="Examples Processed: Total number of test cases evaluated" />
              </ListItem>
              <ListItem>
                <ListItemIcon><CheckCircleIcon color="primary" /></ListItemIcon>
                <ListItemText primary="Success Rate: Percentage of successful agent completions" />
              </ListItem>
              <ListItem>
                <ListItemIcon><CheckCircleIcon color="primary" /></ListItemIcon>
                <ListItemText primary="Validation Pass Rate: Percentage of outputs meeting quality criteria" />
              </ListItem>
            </List>
          </Paper>

          <Paper sx={{ p: 2, mb: 2, bgcolor: 'secondary.50' }}>
            <Typography variant="h6" gutterBottom color="secondary">
              👥 Human Evaluation Insights
            </Typography>
            <Typography variant="body2" paragraph>
              This section displays results from human evaluator assessments:
            </Typography>
            <List dense>
              <ListItem>
                <ListItemIcon><CheckCircleIcon color="secondary" /></ListItemIcon>
                <ListItemText primary="Total Evaluations: Number of completed human evaluations" />
              </ListItem>
              <ListItem>
                <ListItemIcon><CheckCircleIcon color="secondary" /></ListItemIcon>
                <ListItemText primary="Unique Evaluators: Count of different people who have performed evaluations" />
              </ListItem>
              <ListItem>
                <ListItemIcon><CheckCircleIcon color="secondary" /></ListItemIcon>
                <ListItemText primary="Average Score: Mean quality rating across all human evaluations" />
              </ListItem>
              <ListItem>
                <ListItemIcon><CheckCircleIcon color="secondary" /></ListItemIcon>
                <ListItemText primary="Score Distribution: Breakdown of ratings (1-5 stars)" />
              </ListItem>
            </List>
          </Paper>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            How to Use the Dashboard
          </Typography>
          <List>
            <ListItem>
              <ListItemText 
                primary="1. Access the Dashboard"
                secondary="Navigate to Evaluations → Dashboard tab to view the unified performance metrics"
              />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="2. Monitor Overview Metrics"
                secondary="Review the summary cards at the top to get a quick snapshot of system performance"
              />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="3. Analyze Trends"
                secondary="Compare automated vs human evaluation results to identify patterns and areas for improvement"
              />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="4. Drill Down to Details"
                secondary="Click 'VIEW DETAILS' on evaluation runs or 'View' on human evaluations to see comprehensive information"
              />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="5. Filter and Sort"
                secondary="Use filtering options in the human evaluation section to find specific evaluations by agent or evaluator"
              />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="6. Refresh Data"
                secondary="Click the 'REFRESH' button in the top-right to get the latest data"
              />
            </ListItem>
          </List>

          <Alert severity="info" sx={{ mt: 2 }}>
            <Typography variant="body2">
              <strong>Pro Tip:</strong> The dashboard automatically loads both automated and human evaluation data simultaneously. If either section shows errors or empty data, this is normal when no evaluations of that type have been completed yet.
            </Typography>
          </Alert>
        </AccordionDetails>
      </Accordion>

      {/* Getting Started Section */}
      <Accordion sx={{ mb: 2 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">🚀 Getting Started with Human Evaluations</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="h6" gutterBottom>
            Prerequisites
          </Typography>
          <List dense>
            <ListItem>
              <ListItemIcon><CheckCircleIcon color="primary" /></ListItemIcon>
              <ListItemText primary="You must have an admin role account in the DrFirst Business Case Generator system" />
            </ListItem>
            <ListItem>
              <ListItemIcon><CheckCircleIcon color="primary" /></ListItemIcon>
              <ListItemText primary="Access to the web application at the designated URL" />
            </ListItem>
            <ListItem>
              <ListItemIcon><CheckCircleIcon color="primary" /></ListItemIcon>
              <ListItemText primary="Familiarity with the evaluation guidelines and rubrics" />
            </ListItem>
          </List>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            Step-by-Step Access
          </Typography>
          <List>
            <ListItem>
              <ListItemText 
                primary="1. Login to the Application"
                secondary="Navigate to the DrFirst Business Case Generator web application, click 'Sign In' and authenticate using your Google account"
              />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="2. Navigate to Evaluations"
                secondary="After successful login, look for the 'Evaluations' button in the top navigation bar (only visible to admin users)"
              />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="3. Verify Access"
                secondary="You should see the Human Evaluation Interface with available evaluation tasks"
              />
            </ListItem>
          </List>
        </AccordionDetails>
      </Accordion>

      {/* Interface Overview Section */}
      <Accordion sx={{ mb: 2 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">🖥️ Interface Overview</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body1" paragraph>
            The Evaluation Center consists of three main tabs:
          </Typography>
          
          <Paper sx={{ p: 2, mb: 2, bgcolor: 'info.50' }}>
            <Typography variant="h6" gutterBottom color="info">
              📊 Dashboard Tab
            </Typography>
            <Typography variant="body2">
              Unified view of automated evaluation metrics and human evaluation insights for comprehensive performance monitoring.
            </Typography>
          </Paper>

          <Paper sx={{ p: 2, mb: 2, bgcolor: 'primary.50' }}>
            <Typography variant="h6" gutterBottom color="primary">
              📝 Human Evaluations Tab
            </Typography>
            <Typography variant="body2">
              Interactive interface for performing human evaluations with task selection and detailed evaluation forms.
            </Typography>
          </Paper>

          <Paper sx={{ p: 2, mb: 2, bgcolor: 'secondary.50' }}>
            <Typography variant="h6" gutterBottom color="secondary">
              📚 User Guide Tab
            </Typography>
            <Typography variant="body2">
              This comprehensive guide covering dashboard usage, human evaluation procedures, and troubleshooting.
            </Typography>
          </Paper>

          <Divider sx={{ my: 2 }} />

          <Typography variant="body1" paragraph>
            <strong>For Human Evaluations specifically,</strong> the interface consists of two main areas:
          </Typography>
          
          <Paper sx={{ p: 2, mb: 2, bgcolor: 'primary.50' }}>
            <Typography variant="h6" gutterBottom color="primary">
              📋 Task Selection Area (Left Sidebar)
            </Typography>
            <Typography variant="body2">
              Displays all available evaluation tasks with unique evaluation IDs, agent name badges, and input summary previews.
            </Typography>
          </Paper>

          <Paper sx={{ p: 2, bgcolor: 'secondary.50' }}>
            <Typography variant="h6" gutterBottom color="secondary">
              📝 Main Evaluation Area (Right Panel)
            </Typography>
            <Typography variant="body2">
              Shows detailed task information and evaluation form including task context, agent output, evaluation metrics, and overall assessment sections.
            </Typography>
          </Paper>
        </AccordionDetails>
      </Accordion>

      {/* Step-by-Step Evaluation Process */}
      <Accordion sx={{ mb: 2 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">📋 Performing an Evaluation - Step-by-Step</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="h6" gutterBottom>
            Step 1: Selecting an Evaluation Task
          </Typography>
          <List dense>
            <ListItem>
              <ListItemText primary="Browse available tasks in the left sidebar" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Each task shows evaluation ID, agent name badge, and input summary" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Click on any task to select it - the task will be highlighted" />
            </ListItem>
          </List>

          <Divider sx={{ my: 2 }} />

          <Typography variant="h6" gutterBottom>
            Step 2: Reviewing Task Details
          </Typography>
          <List dense>
            <ListItem>
              <ListItemText primary="Expand the 'Task Context' section to understand what the agent was asked to do" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Review the 'Agent Output to Evaluate' section - this contains the complete output generated by the AI agent" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Pay attention to structure, completeness, quality, and relevance" />
            </ListItem>
          </List>

          <Divider sx={{ my: 2 }} />

          <Typography variant="h6" gutterBottom>
            Step 3: Using the Dynamic Evaluation Form
          </Typography>
          <Alert severity="info" sx={{ mb: 2 }}>
            Evaluation metrics change automatically based on the agent type being evaluated
          </Alert>
          
          <Typography variant="body1" paragraph>
            <strong>Scoring Guidelines:</strong>
          </Typography>
          <List dense>
            <ListItem>
              <ListItemIcon><StarIcon /></ListItemIcon>
              <ListItemText primary="⭐ 1 - Very Poor: Significant issues, unusable content" />
            </ListItem>
            <ListItem>
              <ListItemIcon><StarIcon /></ListItemIcon>
              <ListItemText primary="⭐⭐ 2 - Poor: Major problems, limited value" />
            </ListItem>
            <ListItem>
              <ListItemIcon><StarIcon /></ListItemIcon>
              <ListItemText primary="⭐⭐⭐ 3 - Average: Adequate quality, some issues" />
            </ListItem>
            <ListItem>
              <ListItemIcon><StarIcon /></ListItemIcon>
              <ListItemText primary="⭐⭐⭐⭐ 4 - Good: High quality, minor improvements needed" />
            </ListItem>
            <ListItem>
              <ListItemIcon><StarIcon /></ListItemIcon>
              <ListItemText primary="⭐⭐⭐⭐⭐ 5 - Excellent: Outstanding quality, meets all criteria" />
            </ListItem>
          </List>
        </AccordionDetails>
      </Accordion>

      {/* Best Practices Section */}
      <Accordion sx={{ mb: 2 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">🎯 Evaluation Best Practices</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="h6" gutterBottom>
            Consistency in Evaluation
          </Typography>
          <List dense sx={{ mb: 2 }}>
            <ListItem>
              <ListItemIcon><CheckCircleIcon color="success" /></ListItemIcon>
              <ListItemText primary="Apply rubrics uniformly across all evaluations of the same agent type" />
            </ListItem>
            <ListItem>
              <ListItemIcon><CheckCircleIcon color="success" /></ListItemIcon>
              <ListItemText primary="Use the full range of the 1-5 scale appropriately" />
            </ListItem>
            <ListItem>
              <ListItemIcon><CheckCircleIcon color="success" /></ListItemIcon>
              <ListItemText primary="Don't let the order of evaluation affect your scoring" />
            </ListItem>
          </List>

          <Typography variant="h6" gutterBottom>
            Providing Valuable Feedback
          </Typography>
          <List dense>
            <ListItem>
              <ListItemIcon><CheckCircleIcon color="success" /></ListItemIcon>
              <ListItemText primary="Be specific and actionable in your comments" />
            </ListItem>
            <ListItem>
              <ListItemIcon><CheckCircleIcon color="success" /></ListItemIcon>
              <ListItemText primary="Point to specific sections or elements in the agent output" />
            </ListItem>
            <ListItem>
              <ListItemIcon><CheckCircleIcon color="success" /></ListItemIcon>
              <ListItemText primary="Balance criticism with recognition of what the agent did well" />
            </ListItem>
          </List>

          <Alert severity="success" sx={{ mt: 2 }}>
            <Typography variant="body2">
              <strong>Good Comment Example:</strong> "The PRD structure is well-organized, but lacks specific acceptance criteria for the mobile interface requirements. Consider adding measurable success metrics."
            </Typography>
          </Alert>

          <Alert severity="warning" sx={{ mt: 1 }}>
            <Typography variant="body2">
              <strong>Poor Comment Example:</strong> "Looks good" (too generic, not constructive)
            </Typography>
          </Alert>
        </AccordionDetails>
      </Accordion>

      {/* FAQ Section */}
      <Accordion sx={{ mb: 2 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">❓ Frequently Asked Questions</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="h6" gutterBottom>
            Q: What if I'm unsure how to score a particular metric?
          </Typography>
          <Typography variant="body1" paragraph>
            Refer to the detailed rubrics in the Human Evaluation Guidelines. Each metric has specific criteria for each score level (1-5). If still unsure, note your uncertainty in the comments section and choose the score that best matches your assessment.
          </Typography>

          <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
            Q: What if the agent output is completely irrelevant?
          </Typography>
          <Typography variant="body1" paragraph>
            This is valuable data! Score relevant metrics very low (typically 1 - Very Poor) and clearly explain in the comments why the output is irrelevant or problematic. Provide specific examples and don't hesitate to give low scores.
          </Typography>

          <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
            Q: Can I save a partially completed evaluation?
          </Typography>
          <Typography variant="body1" paragraph>
            Currently, the V1 evaluation interface does not include a "save draft" feature. Evaluations should be completed and submitted in one session. Plan sufficient time (typically 10-20 minutes per task).
          </Typography>

          <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
            Q: What if I make a mistake after submitting?
          </Typography>
          <Typography variant="body1" paragraph>
            Submitted evaluations cannot be edited through the web interface. For major errors that could affect analysis, contact the evaluation lead immediately with the submission ID provided after submission.
          </Typography>
        </AccordionDetails>
      </Accordion>

      {/* Troubleshooting Section */}
      <Accordion sx={{ mb: 2 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">🔧 Troubleshooting & Support</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="h6" gutterBottom>
            Common Technical Issues
          </Typography>
          
          <Paper sx={{ p: 2, mb: 2, bgcolor: 'error.50' }}>
            <Typography variant="subtitle1" gutterBottom>
              <WarningIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Authentication Problems
            </Typography>
            <Typography variant="body2">
              <strong>Symptom:</strong> Cannot access the evaluation interface<br />
              <strong>Solution:</strong> Verify you have admin role privileges, clear browser cache, or contact IT support
            </Typography>
          </Paper>

          <Paper sx={{ p: 2, mb: 2, bgcolor: 'warning.50' }}>
            <Typography variant="subtitle1" gutterBottom>
              <WarningIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Loading Issues
            </Typography>
            <Typography variant="body2">
              <strong>Symptom:</strong> Tasks not loading or interface appears broken<br />
              <strong>Solution:</strong> Refresh the page, check internet connection, try a different browser
            </Typography>
          </Paper>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            Browser Compatibility
          </Typography>
          <Typography variant="body1" paragraph>
            <strong>Recommended Browsers:</strong> Chrome, Firefox, Safari, Edge (latest versions)
          </Typography>
          <Typography variant="body2">
            Ensure JavaScript is enabled, cookies are allowed, and ad blockers that might interfere with the interface are disabled.
          </Typography>
        </AccordionDetails>
      </Accordion>

      {/* Additional Resources */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom color="primary">
            <BookIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Additional Resources
          </Typography>
          <List>
            <ListItem>
              <ListItemIcon><AssignmentIcon color="primary" /></ListItemIcon>
              <ListItemText 
                primary="Human Evaluation Guidelines v1" 
                secondary="Detailed rubrics and scoring principles (backend/evaluations/human_evaluation_guidelines_v1.md)"
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><AssignmentIcon color="primary" /></ListItemIcon>
              <ListItemText 
                primary="Evaluation Metrics Definition" 
                secondary="Comprehensive metric definitions (backend/evaluations/evaluation_metrics_definition.md)"
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><AssignmentIcon color="primary" /></ListItemIcon>
              <ListItemText 
                primary="Project Documentation" 
                secondary="Overview of the DrFirst Business Case Generator system"
              />
            </ListItem>
          </List>
        </CardContent>
      </Card>

      {/* Document Info */}
      <Alert severity="info" sx={{ mt: 3 }}>
        <Typography variant="body2">
          <strong>Document Information:</strong><br />
          Created: January 8, 2025 | Updated: January 8, 2025 | Version: 2.0<br />
          Document Owner: Evaluation Team Lead<br />
          Latest Changes: Added unified dashboard instructions and updated for consolidated evaluation interface<br />
          Feedback: Please provide suggestions for improving this guide to the evaluation team
        </Typography>
      </Alert>
    </Box>
  );
};

export default EvaluationUserGuide; 