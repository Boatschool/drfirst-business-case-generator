import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  List,
  ListItemText,
  ListItemButton,
  Divider,
  Alert,
  CircularProgress,
  Chip,
  TextField,
  Rating,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Container,
  Tabs,
  Tab,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Assignment as AssignmentIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Book as BookIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { evaluationService, EvaluationTask, MetricScoreComment } from '../services/EvaluationService';
import EvaluationUserGuide from '../components/specific/EvaluationUserGuide';
import AutomatedEvalDashboardPage from './admin/evaluations/AutomatedEvalDashboardPage';

// Metric display names mapping
const METRIC_DISPLAY_NAMES: Record<string, string> = {
  'Content_Relevance_Quality': 'Content Relevance & Quality',
  'Plausibility_Appropriateness': 'Plausibility & Appropriateness',
  'Clarity_Understandability': 'Clarity & Understandability', 
  'Reasonableness_Hours': 'Reasonableness of Hours',
  'Quality_Rationale': 'Quality of Rationale',
  'Plausibility_Projections': 'Plausibility of Projections',
};

// Rating labels for better UX
const RATING_LABELS: Record<number, string> = {
  1: 'Very Poor',
  2: 'Poor',
  3: 'Average',
  4: 'Good',
  5: 'Excellent',
};

interface EvaluationFormData {
  [metricName: string]: MetricScoreComment;
}

const HumanEvaluationPage: React.FC = () => {
  // Tab state
  const [currentTab, setCurrentTab] = useState(0);
  
  const [tasks, setTasks] = useState<EvaluationTask[]>([]);
  const [selectedTask, setSelectedTask] = useState<EvaluationTask | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Form state
  const [evaluationData, setEvaluationData] = useState<EvaluationFormData>({});
  const [overallScore, setOverallScore] = useState<number>(0);
  const [overallComments, setOverallComments] = useState<string>('');

  // Load evaluation tasks on component mount
  useEffect(() => {
    loadEvaluationTasks();
  }, []);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  const loadEvaluationTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      const taskList = await evaluationService.getEvaluationTasks();
      setTasks(taskList);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load evaluation tasks');
    } finally {
      setLoading(false);
    }
  };

  const handleTaskSelect = (task: EvaluationTask) => {
    setSelectedTask(task);
    setSuccess(null);
    setError(null);
    
    // Initialize form data for the selected task
    const initialData: EvaluationFormData = {};
    task.applicable_metrics.forEach(metric => {
      initialData[metric] = { score: 0, comment: '' };
    });
    setEvaluationData(initialData);
    setOverallScore(0);
    setOverallComments('');
  };

  const handleMetricScoreChange = (metricName: string, score: number) => {
    setEvaluationData(prev => ({
      ...prev,
      [metricName]: {
        ...prev[metricName],
        score
      }
    }));
  };

  const handleMetricCommentChange = (metricName: string, comment: string) => {
    setEvaluationData(prev => ({
      ...prev,
      [metricName]: {
        ...prev[metricName],
        comment
      }
    }));
  };

  const validateForm = (): boolean => {
    if (!selectedTask) return false;
    
    // Check that all metrics have scores > 0
    for (const metric of selectedTask.applicable_metrics) {
      if (!evaluationData[metric] || evaluationData[metric].score === 0) {
        setError(`Please provide a score for ${METRIC_DISPLAY_NAMES[metric] || metric}`);
        return false;
      }
    }
    
    // Check overall score
    if (overallScore === 0) {
      setError('Please provide an overall quality score');
      return false;
    }
    
    return true;
  };

  const handleSubmitEvaluation = async () => {
    if (!selectedTask || !validateForm()) return;
    
    try {
      setSubmitting(true);
      setError(null);
      
      // Convert form data to submission format
      const metricScores: Record<string, MetricScoreComment> = {};
      Object.entries(evaluationData).forEach(([metric, data]) => {
        metricScores[metric] = {
          score: data.score,
          comment: data.comment || ''
        };
      });

      const submission = {
        eval_id: selectedTask.eval_id,
        golden_dataset_inputId: selectedTask.golden_dataset_inputId,
        case_id: selectedTask.case_id,
        trace_id: selectedTask.trace_id,
        agent_name: selectedTask.agent_name,
        metric_scores_and_comments: metricScores,
        overall_quality_score: overallScore,
        overall_comments: overallComments || ''
      };

      const response = await evaluationService.submitEvaluation(submission);
      
      setSuccess(`Evaluation submitted successfully! Submission ID: ${response.submission_id}`);
      
      // Remove the completed task from the list
      setTasks(prev => prev.filter(t => t.eval_id !== selectedTask.eval_id));
      setSelectedTask(null);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit evaluation');
    } finally {
      setSubmitting(false);
    }
  };

  const renderTaskList = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          <AssignmentIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Available Evaluation Tasks ({tasks.length})
        </Typography>
        
        {tasks.length === 0 ? (
          <Alert severity="info">
            No evaluation tasks available. All tasks may have been completed.
          </Alert>
        ) : (
          <List>
            {tasks.map((task, index) => (
              <React.Fragment key={task.eval_id}>
                <ListItemButton 
                  onClick={() => handleTaskSelect(task)}
                  selected={selectedTask?.eval_id === task.eval_id}
                >
                  <ListItemText
                    primary={
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography variant="subtitle2">
                          {task.eval_id}
                        </Typography>
                        <Chip 
                          label={task.agent_name} 
                          size="small" 
                          color="primary" 
                          variant="outlined" 
                        />
                      </Box>
                    }
                    secondary={task.input_payload_summary}
                  />
                </ListItemButton>
                {index < tasks.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        )}
      </CardContent>
    </Card>
  );

  const renderEvaluationForm = () => {
    if (!selectedTask) return null;

    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Evaluate: {selectedTask.eval_id}
          </Typography>
          
          <Grid container spacing={3}>
            {/* Task Context */}
            <Grid item xs={12}>
              <Accordion defaultExpanded>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="subtitle1">Task Context</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Box mb={2}>
                    <Typography variant="subtitle2" gutterBottom>Agent:</Typography>
                    <Chip label={selectedTask.agent_name} color="primary" />
                  </Box>
                  
                  <Box mb={2}>
                    <Typography variant="subtitle2" gutterBottom>Input Summary:</Typography>
                    <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
                      {selectedTask.input_payload_summary}
                    </Typography>
                  </Box>
                </AccordionDetails>
              </Accordion>
            </Grid>

            {/* Agent Output */}
            <Grid item xs={12}>
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="subtitle1">Agent Output to Evaluate</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Paper sx={{ p: 2, bgcolor: 'grey.50', maxHeight: 400, overflow: 'auto' }}>
                    <Typography 
                      variant="body2" 
                      component="pre" 
                      sx={{ 
                        whiteSpace: 'pre-wrap',
                        fontFamily: 'monospace',
                        fontSize: '0.875rem'
                      }}
                    >
                      {selectedTask.agent_output_to_evaluate}
                    </Typography>
                  </Paper>
                </AccordionDetails>
              </Accordion>
            </Grid>

            {/* Evaluation Metrics */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Evaluation Metrics
              </Typography>
              
              {selectedTask.applicable_metrics.map((metric) => (
                <Card key={metric} sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      {METRIC_DISPLAY_NAMES[metric] || metric}
                    </Typography>
                    
                    <Box mb={2}>
                      <Typography component="legend" variant="body2" gutterBottom>
                        Score (1-5):
                      </Typography>
                      <Box display="flex" alignItems="center" gap={2}>
                        <Rating
                          value={evaluationData[metric]?.score || 0}
                          onChange={(_, newValue) => handleMetricScoreChange(metric, newValue || 0)}
                          max={5}
                          size="large"
                        />
                        <Typography variant="body2" color="text.secondary">
                          {evaluationData[metric]?.score > 0 
                            ? RATING_LABELS[evaluationData[metric].score] 
                            : 'Not rated'}
                        </Typography>
                      </Box>
                    </Box>
                    
                    <TextField
                      fullWidth
                      multiline
                      rows={3}
                      label="Comments"
                      value={evaluationData[metric]?.comment || ''}
                      onChange={(e) => handleMetricCommentChange(metric, e.target.value)}
                      placeholder="Provide specific feedback and reasoning for your score..."
                    />
                  </CardContent>
                </Card>
              ))}
            </Grid>

            {/* Overall Assessment */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Overall Assessment
                  </Typography>
                  
                  <Box mb={2}>
                    <Typography component="legend" variant="body2" gutterBottom>
                      Overall Quality Score (1-5):
                    </Typography>
                    <Box display="flex" alignItems="center" gap={2}>
                      <Rating
                        value={overallScore}
                        onChange={(_, newValue) => setOverallScore(newValue || 0)}
                        max={5}
                        size="large"
                      />
                      <Typography variant="body2" color="text.secondary">
                        {overallScore > 0 ? RATING_LABELS[overallScore] : 'Not rated'}
                      </Typography>
                    </Box>
                  </Box>
                  
                  <TextField
                    fullWidth
                    multiline
                    rows={4}
                    label="Overall Comments"
                    value={overallComments}
                    onChange={(e) => setOverallComments(e.target.value)}
                    placeholder="Provide an overall assessment of the agent's output quality, highlighting key strengths and areas for improvement..."
                  />
                </CardContent>
              </Card>
            </Grid>

            {/* Submit Button */}
            <Grid item xs={12}>
              <Box display="flex" justifyContent="center" mt={2}>
                <Button
                  variant="contained"
                  size="large"
                  onClick={handleSubmitEvaluation}
                  disabled={submitting}
                  startIcon={submitting ? <CircularProgress size={20} /> : <CheckCircleIcon />}
                >
                  {submitting ? 'Submitting...' : 'Submit Evaluation'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    );
  };

  return (
    <Container maxWidth="lg">
      <Box py={3}>
        <Typography variant="h4" gutterBottom>
          Evaluation Center
        </Typography>
        
        {/* Tab Navigation */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={currentTab} onChange={handleTabChange} aria-label="evaluation tabs">
            <Tab 
              icon={<AssessmentIcon />}
              label="Dashboard" 
              id="evaluation-tab-0"
              aria-controls="evaluation-tabpanel-0"
            />
            <Tab 
              icon={<AssignmentIcon />}
              label="Human Evaluations" 
              id="evaluation-tab-1"
              aria-controls="evaluation-tabpanel-1"
            />
            <Tab 
              icon={<BookIcon />}
              label="User Guide" 
              id="evaluation-tab-2"
              aria-controls="evaluation-tabpanel-2"
            />
          </Tabs>
        </Box>

        {/* Tab Content */}
        {currentTab === 0 && (
          <Box id="evaluation-tabpanel-0" role="tabpanel" aria-labelledby="evaluation-tab-0">
            <AutomatedEvalDashboardPage />
          </Box>
        )}

        {currentTab === 1 && (
          <Box id="evaluation-tabpanel-1" role="tabpanel" aria-labelledby="evaluation-tab-1">
            <Typography variant="body1" color="text.secondary" gutterBottom>
              Select an evaluation task and provide scores and feedback for the agent output.
            </Typography>

            {/* Status Messages */}
            {error && (
              <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
                <Box display="flex" alignItems="center">
                  <ErrorIcon sx={{ mr: 1 }} />
                  {error}
                </Box>
              </Alert>
            )}

            {success && (
              <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
                <Box display="flex" alignItems="center">
                  <CheckCircleIcon sx={{ mr: 1 }} />
                  {success}
                </Box>
              </Alert>
            )}

            {loading ? (
              <Box display="flex" justifyContent="center" py={4}>
                <CircularProgress />
              </Box>
            ) : (
              <Grid container spacing={3}>
                {/* Task List */}
                <Grid item xs={12} md={4}>
                  {renderTaskList()}
                </Grid>

                {/* Evaluation Form */}
                <Grid item xs={12} md={8}>
                  {selectedTask ? (
                    renderEvaluationForm()
                  ) : (
                    <Card>
                      <CardContent>
                        <Typography variant="h6" color="text.secondary" textAlign="center">
                          Select a task from the list to begin evaluation
                        </Typography>
                      </CardContent>
                    </Card>
                  )}
                </Grid>
              </Grid>
            )}
          </Box>
        )}

        {currentTab === 2 && (
          <Box id="evaluation-tabpanel-2" role="tabpanel" aria-labelledby="evaluation-tab-2">
            <EvaluationUserGuide />
          </Box>
        )}
      </Box>
    </Container>
  );
};

export default HumanEvaluationPage; 