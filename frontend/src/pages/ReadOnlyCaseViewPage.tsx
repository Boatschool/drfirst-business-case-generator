import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Box,
  Button,
  Stack,
  Chip,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Visibility as VisibilityIcon,
  Business as BusinessIcon,
  Architecture as ArchitectureIcon,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import { useAgentContext } from '../contexts/AgentContext';

// Helper function to improve text formatting for better readability
const formatMarkdownContent = (content: string): string => {
  if (!content) return content;

  let formatted = content
    .replace(/^(#{1,6}\s.+)$/gm, '$1\n')
    .replace(/([^\n])\n(#{1,6}\s)/g, '$1\n\n$2')
    .replace(/^(\s*[-*+]\s.+)$/gm, '$1')
    .replace(/^(\s*[-*+]\s.+)(\n(?!\s*[-*+]))/gm, '$1\n$2')
    .replace(/\n{3,}/g, '\n\n');

  return formatted;
};

// Enhanced markdown styles for better formatting
const markdownStyles = {
  '& h1': {
    fontSize: '1.8rem',
    fontWeight: 600,
    color: '#1976d2',
    marginTop: '2rem',
    marginBottom: '1rem',
    borderBottom: '2px solid #e3f2fd',
    paddingBottom: '0.5rem',
  },
  '& h2': {
    fontSize: '1.5rem',
    fontWeight: 600,
    color: '#333',
    marginTop: '1.5rem',
    marginBottom: '0.8rem',
  },
  '& h3': {
    fontSize: '1.3rem',
    fontWeight: 500,
    color: '#444',
    marginTop: '1.2rem',
    marginBottom: '0.6rem',
  },
  '& p': {
    marginBottom: '1rem',
    lineHeight: 1.6,
    color: '#333',
  },
  '& ul, & ol': {
    marginBottom: '1rem',
    paddingLeft: '1.5rem',
  },
  '& li': {
    marginBottom: '0.5rem',
    lineHeight: 1.5,
  },
  '& strong': {
    fontWeight: 600,
    color: '#1976d2',
  },
  '& code': {
    backgroundColor: '#f5f5f5',
    padding: '0.2rem 0.4rem',
    borderRadius: '3px',
    fontSize: '0.9em',
    fontFamily: 'monospace',
  },
};

const ReadOnlyCaseViewPage: React.FC = () => {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();
  const { 
    fetchCaseDetails, 
    currentCaseDetails, 
    isLoadingCaseDetails, 
    caseDetailsError 
  } = useAgentContext();

  useEffect(() => {
    if (caseId) {
      fetchCaseDetails(caseId);
    }
  }, [caseId, fetchCaseDetails]);

  if (isLoadingCaseDetails) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Container>
    );
  }

  if (caseDetailsError) {
    return (
      <Container sx={{ mt: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {caseDetailsError.message || 'Failed to load business case details'}
        </Alert>
        <Button
          variant="contained"
          onClick={() => navigate('/dashboard')}
          startIcon={<ArrowBackIcon />}
        >
          Back to Dashboard
        </Button>
      </Container>
    );
  }

  if (!currentCaseDetails) {
    return (
      <Container sx={{ mt: 4 }}>
        <Alert severity="warning" sx={{ mb: 2 }}>
          Business case not found
        </Alert>
        <Button
          variant="contained"
          onClick={() => navigate('/dashboard')}
          startIcon={<ArrowBackIcon />}
        >
          Back to Dashboard
        </Button>
      </Container>
    );
  }

  const status = currentCaseDetails.status;

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header Section */}
      <Paper elevation={2} sx={{ p: 3, mb: 3, backgroundColor: '#f8f9fa' }}>
        <Stack spacing={2}>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Typography
              variant="h4"
              component="h1"
              sx={{ display: 'flex', alignItems: 'center' }}
            >
              <VisibilityIcon sx={{ mr: 2, color: 'primary.main' }} />
              Read-Only Business Case View
            </Typography>
            <Button
              variant="outlined"
              onClick={() => navigate('/dashboard')}
              startIcon={<ArrowBackIcon />}
            >
              Back to Dashboard
            </Button>
          </Box>
          
          <Alert severity="info">
            <Typography variant="body1">
              You are viewing a shared business case in read-only mode. 
              This view is for informational purposes only and cannot be edited.
            </Typography>
          </Alert>

          <Box>
            <Typography variant="h5" gutterBottom>
              {currentCaseDetails.title}
            </Typography>
            <Box display="flex" alignItems="center" gap={2}>
              <Chip
                label={status}
                color={
                  status === 'APPROVED'
                    ? 'success'
                    : status === 'REJECTED'
                    ? 'error'
                    : status === 'PENDING_FINAL_APPROVAL'
                    ? 'warning'
                    : 'default'
                }
              />
              <Typography variant="body2" color="text.secondary">
                Created: {new Date(currentCaseDetails.created_at).toLocaleDateString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Updated: {new Date(currentCaseDetails.updated_at).toLocaleDateString()}
              </Typography>
            </Box>
          </Box>
        </Stack>
      </Paper>

      {/* Problem Statement */}
      <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
        <Typography
          variant="h5"
          gutterBottom
          sx={{ display: 'flex', alignItems: 'center', mb: 2 }}
        >
          <BusinessIcon sx={{ mr: 1, color: 'primary.main' }} />
          Problem Statement
        </Typography>
        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
          {currentCaseDetails.problem_statement}
        </Typography>
      </Paper>

      {/* PRD Section */}
      {currentCaseDetails.prd_draft && (
        <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
          <Typography
            variant="h5"
            gutterBottom
            sx={{ display: 'flex', alignItems: 'center', mb: 2 }}
          >
            <BusinessIcon sx={{ mr: 1, color: 'primary.main' }} />
            Product Requirements Document (PRD)
          </Typography>
          <Box sx={markdownStyles}>
            <ReactMarkdown>
              {formatMarkdownContent(currentCaseDetails.prd_draft.content_markdown || '')}
            </ReactMarkdown>
          </Box>
        </Paper>
      )}

      {/* System Design Section */}
      {currentCaseDetails.system_design_v1_draft && (
        <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
          <Typography
            variant="h5"
            gutterBottom
            sx={{ display: 'flex', alignItems: 'center', mb: 2 }}
          >
            <ArchitectureIcon sx={{ mr: 1, color: 'primary.main' }} />
            System Design
          </Typography>
          <Box sx={markdownStyles}>
            <ReactMarkdown>
              {formatMarkdownContent(
                currentCaseDetails.system_design_v1_draft.content_markdown || ''
              )}
            </ReactMarkdown>
          </Box>
        </Paper>
      )}

      {/* Basic financial information display without complex structures */}
      {currentCaseDetails.effort_estimate_v1 && (
        <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
          <Typography variant="h5" gutterBottom>
            Effort Estimate Available
          </Typography>
          <Typography variant="body1">
            Total Hours: {currentCaseDetails.effort_estimate_v1.total_hours}
          </Typography>
          <Typography variant="body1">
            Duration: {currentCaseDetails.effort_estimate_v1.estimated_duration_weeks} weeks
          </Typography>
        </Paper>
      )}

      {currentCaseDetails.cost_estimate_v1 && (
        <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
          <Typography variant="h5" gutterBottom>
            Cost Estimate Available
          </Typography>
          <Typography variant="body1">
            Estimated Cost: {currentCaseDetails.cost_estimate_v1.currency} {currentCaseDetails.cost_estimate_v1.estimated_cost.toLocaleString()}
          </Typography>
        </Paper>
      )}

      {currentCaseDetails.value_projection_v1 && (
        <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
          <Typography variant="h5" gutterBottom>
            Value Projection Available
          </Typography>
          <Typography variant="body1">
            Currency: {currentCaseDetails.value_projection_v1.currency}
          </Typography>
        </Paper>
      )}

      {/* Footer */}
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          This is a read-only view of a shared business case. 
          For questions or feedback, please contact the case owner.
        </Typography>
      </Box>
    </Container>
  );
};

export default ReadOnlyCaseViewPage; 