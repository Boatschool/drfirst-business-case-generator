import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Box,
  Button,
  Divider,
  Stack,
  TextField,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Send as SendIcon,
  Refresh as RefreshIcon,
  ArrowBack as ArrowBackIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as RejectIcon,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import { useAgentContext } from '../contexts/AgentContext';
import { AgentUpdate } from '../services/agent/AgentService';
import { useAuth } from '../contexts/AuthContext';


// Helper function to improve text formatting for better readability
const formatPrdContent = (content: string): string => {
  if (!content) return content;
  
  // Ensure proper line breaks after headings and before new sections
  let formatted = content
    // Add line breaks after markdown headings
    .replace(/^(#{1,6}\s.+)$/gm, '$1\n')
    // Add line breaks before new headings if not already present
    .replace(/([^\n])\n(#{1,6}\s)/g, '$1\n\n$2')
    // Ensure bullet points have proper spacing
    .replace(/^(\s*[-*+]\s.+)$/gm, '$1')
    // Add spacing after bullet point groups
    .replace(/^(\s*[-*+]\s.+)(\n(?!\s*[-*+]))/gm, '$1\n$2')
    // Clean up multiple consecutive line breaks (max 2)
    .replace(/\n{3,}/g, '\n\n');
    
  return formatted;
};

// Enhanced markdown styles for better PRD formatting
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
  '& em': {
    fontStyle: 'italic',
    color: '#666',
  },
  '& blockquote': {
    borderLeft: '4px solid #1976d2',
    paddingLeft: '1rem',
    margin: '1rem 0',
    fontStyle: 'italic',
    backgroundColor: '#f8f9fa',
    padding: '0.5rem 1rem',
  },
  '& code': {
    backgroundColor: '#f5f5f5',
    padding: '0.2rem 0.4rem',
    borderRadius: '3px',
    fontSize: '0.9em',
    fontFamily: 'monospace',
  },
  '& pre': {
    backgroundColor: '#f5f5f5',
    padding: '1rem',
    borderRadius: '5px',
    overflow: 'auto',
    margin: '1rem 0',
  },
};

const BusinessCaseDetailPage: React.FC = () => {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();
  const {
    currentCaseDetails,
    isLoadingCaseDetails,
    caseDetailsError,
    fetchCaseDetails,
    sendFeedbackToAgent,
    updatePrdDraft,
    submitPrdForReview,
    approvePrd,
    rejectPrd,
    isLoading,
    error: agentContextError,
    clearCurrentCaseDetails,
    messages
  } = useAgentContext();
  const { currentUser } = useAuth();

  const [isEditingPrd, setIsEditingPrd] = useState(false);
  const [editablePrdContent, setEditablePrdContent] = useState('');
  const [feedbackMessage, setFeedbackMessage] = useState('');
  const [isSendingFeedback, setIsSendingFeedback] = useState(false);
  const [feedbackSendError, setFeedbackSendError] = useState<string | null>(null);
  const [prdUpdateError, setPrdUpdateError] = useState<string | null>(null);
  const [prdUpdateSuccess, setPrdUpdateSuccess] = useState<string | null>(null);
  const [statusUpdateSuccess, setStatusUpdateSuccess] = useState<string | null>(null);
  const [statusUpdateError, setStatusUpdateError] = useState<string | null>(null);
  const [approvalSuccess, setApprovalSuccess] = useState<string | null>(null);
  const [approvalError, setApprovalError] = useState<string | null>(null);
  const [isRejectDialogOpen, setIsRejectDialogOpen] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');

  const loadDetails = useCallback(() => {
    if (caseId) {
      fetchCaseDetails(caseId);
    }
  }, [caseId, fetchCaseDetails]);

  useEffect(() => {
    loadDetails();
    return () => {
      clearCurrentCaseDetails();
    };
  }, [loadDetails, clearCurrentCaseDetails]);

  useEffect(() => {
    if (currentCaseDetails?.prd_draft?.content_markdown && !isEditingPrd) {
      setEditablePrdContent(currentCaseDetails.prd_draft.content_markdown);
    }
  }, [currentCaseDetails, isEditingPrd]);

  const handleEditPrd = () => {
    setEditablePrdContent(currentCaseDetails?.prd_draft?.content_markdown || '');
    setIsEditingPrd(true);
    setPrdUpdateError(null);
    setPrdUpdateSuccess(null);
  };

  const handleCancelEditPrd = () => {
    setEditablePrdContent(currentCaseDetails?.prd_draft?.content_markdown || '');
    setIsEditingPrd(false);
    setPrdUpdateError(null);
    setPrdUpdateSuccess(null);
  };

  const handleSavePrd = async () => {
    if (!caseId || !currentCaseDetails) return;
    setPrdUpdateError(null);
    setPrdUpdateSuccess(null);

    const success = await updatePrdDraft({
      caseId,
      content_markdown: editablePrdContent,
    });

    if (success) {
      setIsEditingPrd(false);
      setPrdUpdateSuccess('PRD updated successfully!');
      // Clear success message after 5 seconds
      setTimeout(() => setPrdUpdateSuccess(null), 5000);
    } else {
      setPrdUpdateError(agentContextError?.message || 'Failed to save PRD. Please try again.');
    }
  };

  const handleSendFeedback = async () => {
    if (!caseId || !feedbackMessage.trim() || !currentUser?.uid) return;
    setIsSendingFeedback(true);
    setFeedbackSendError(null);
    try {
      await sendFeedbackToAgent({
        caseId,
        message: feedbackMessage,
      });
      setFeedbackMessage('');
    } catch (err: any) {
      setFeedbackSendError(err.message || 'Failed to send feedback. Please try again.');
    } finally {
      setIsSendingFeedback(false);
    }
  };

  const handleSubmitPrdForReview = async () => {
    if (!caseId || !currentCaseDetails) return;
    setStatusUpdateError(null);
    setStatusUpdateSuccess(null);

    const success = await submitPrdForReview(caseId);

    if (success) {
      setStatusUpdateSuccess('PRD submitted for review successfully!');
      // Clear success message after 5 seconds
      setTimeout(() => setStatusUpdateSuccess(null), 5000);
    } else {
      setStatusUpdateError(agentContextError?.message || 'Failed to submit PRD for review. Please try again.');
    }
  };

  const handleApprovePrd = async () => {
    if (!caseId || !currentCaseDetails) return;
    setApprovalError(null);
    setApprovalSuccess(null);

    const success = await approvePrd(caseId);

    if (success) {
      setApprovalSuccess('PRD approved successfully!');
      // Clear success message after 5 seconds
      setTimeout(() => setApprovalSuccess(null), 5000);
    } else {
      setApprovalError(agentContextError?.message || 'Failed to approve PRD. Please try again.');
    }
  };

  const handleRejectPrd = async () => {
    if (!caseId || !currentCaseDetails) return;
    setApprovalError(null);
    setApprovalSuccess(null);

    const success = await rejectPrd(caseId, rejectionReason.trim() || undefined);

    if (success) {
      setApprovalSuccess('PRD rejected successfully.');
      setIsRejectDialogOpen(false);
      setRejectionReason('');
      // Clear success message after 5 seconds
      setTimeout(() => setApprovalSuccess(null), 5000);
    } else {
      setApprovalError(agentContextError?.message || 'Failed to reject PRD. Please try again.');
    }
  };

  const handleOpenRejectDialog = () => {
    setIsRejectDialogOpen(true);
    setRejectionReason('');
    setApprovalError(null);
    setApprovalSuccess(null);
  };

  const handleCloseRejectDialog = () => {
    setIsRejectDialogOpen(false);
    setRejectionReason('');
  };

  if (isLoadingCaseDetails && !currentCaseDetails) {
    return <CircularProgress sx={{ display: 'block', margin: 'auto', mt: 5 }} />;
  }

  if (caseDetailsError) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="error">
          Error loading case details: {caseDetailsError.message}
        </Alert>
        <Button onClick={() => navigate('/dashboard')} sx={{ mt: 2 }}>Back to Dashboard</Button>
      </Container>
    );
  }

  if (!currentCaseDetails) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Typography variant="h6">Case not found or no details available.</Typography>
        <Button onClick={() => navigate('/dashboard')} sx={{ mt: 2 }}>Back to Dashboard</Button>
      </Container>
    );
  }

  const { title, status, problem_statement, relevant_links, prd_draft } = currentCaseDetails;

  const displayMessages = (messages || []).filter(msg => msg.messageType !== 'PRD_DRAFT');

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: { xs: 2, md: 4 } }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
          <Stack direction="row" alignItems="center" spacing={2}>
            <Tooltip title="Back to Dashboard">
              <IconButton onClick={() => navigate('/dashboard')} disabled={isLoading}>
                <ArrowBackIcon />
              </IconButton>
            </Tooltip>
            <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 0 }}>
              {title || 'Business Case Details'}
            </Typography>
          </Stack>
          <Stack direction="row" spacing={1}>
            <Tooltip title="Refresh Case Details">
              <IconButton onClick={loadDetails} disabled={isLoading || isLoadingCaseDetails}>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          </Stack>
        </Stack>

        <Typography variant="overline" display="block" gutterBottom>Status: {status}</Typography>
        
        <Box mb={3}>
          <Typography variant="h6" gutterBottom>Problem Statement</Typography>
          <Typography paragraph sx={{ whiteSpace: 'pre-wrap' }}>{problem_statement || 'Not provided'}</Typography>
        </Box>

        {relevant_links && relevant_links.length > 0 && (
          <Box mb={3}>
            <Typography variant="h6" gutterBottom>Relevant Links</Typography>
            <Stack spacing={1}>
              {relevant_links.map((link: { name: string; url: string }, index: number) => (
                <Typography key={index} component="a" href={link.url} target="_blank" rel="noopener noreferrer">
                  {link.name || link.url} 
                </Typography>
              ))}
            </Stack>
          </Box>
        )}

        <Divider sx={{ my: 3 }} />

        <Box mb={3}>
          <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1}>
            <Typography variant="h5" gutterBottom>PRD Draft</Typography>
            {!isEditingPrd && (
              <Button 
                startIcon={<EditIcon />} 
                onClick={handleEditPrd} 
                disabled={isLoading} 
              >
                Edit PRD
              </Button>
            )}
          </Stack>

          {isEditingPrd ? (
            <Box>
              <TextField
                fullWidth
                multiline
                rows={15}
                value={editablePrdContent}
                onChange={(e) => setEditablePrdContent(e.target.value)}
                variant="outlined"
                sx={{ mb: 1 }}
              />
              <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                <Button 
                  variant="contained" 
                  onClick={handleSavePrd} 
                  startIcon={<SaveIcon />} 
                  disabled={isLoading} 
                >
                  {isLoading && !isSendingFeedback ? 'Saving...' : 'Save Changes'} 
                </Button>
                <Button 
                  variant="outlined" 
                  onClick={handleCancelEditPrd} 
                  startIcon={<CancelIcon />} 
                  disabled={isLoading}
                >
                  Cancel
                </Button>
              </Stack>
            </Box>
          ) : (
            prd_draft?.content_markdown ? (
              <Paper elevation={0} sx={{ 
                p: 3, 
                mt: 1, 
                border: '1px solid #eee', 
                backgroundColor: '#ffffff',
                ...markdownStyles
              }}>
                <ReactMarkdown>{formatPrdContent(prd_draft.content_markdown)}</ReactMarkdown>
              </Paper>
            ) : (
              <Typography color="textSecondary" sx={{mt:1}}>PRD content not yet generated or available.</Typography>
            )
          )}
          {prdUpdateError && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {prdUpdateError}
            </Alert>
          )}
          {prdUpdateSuccess && (
            <Alert severity="success" sx={{ mt: 2 }}>
              {prdUpdateSuccess}
            </Alert>
          )}

          {/* Submit PRD for Review Section */}
          {!isEditingPrd && prd_draft?.content_markdown && (status === 'INTAKE' || status === 'PRD_DRAFTING' || status === 'PRD_REVIEW') && (
            <Box sx={{ mt: 3, pt: 2, borderTop: '1px solid #eee' }}>
              <Stack direction="row" spacing={2} alignItems="center">
                <Button 
                  variant="contained" 
                  color="primary"
                  onClick={handleSubmitPrdForReview} 
                  disabled={isLoading}
                  startIcon={<SendIcon />}
                                  >
                    {status === 'PRD_REVIEW' ? 'Resubmit PRD for Review' : 'Submit PRD for Review'}
                  </Button>
                  <Typography variant="body2" color="text.secondary">
                    {status === 'PRD_REVIEW' 
                      ? 'PRD is currently under review. You can resubmit if changes were made.'
                      : status === 'INTAKE' 
                        ? 'Submit your PRD content for review by stakeholders.'
                        : 'Submit your PRD draft for review by stakeholders.'
                    }
                </Typography>
              </Stack>
              {statusUpdateError && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {statusUpdateError}
                </Alert>
              )}
              {statusUpdateSuccess && (
                <Alert severity="success" sx={{ mt: 2 }}>
                  {statusUpdateSuccess}
                </Alert>
              )}
            </Box>
          )}

          {/* PRD Approval/Rejection Section */}
          {!isEditingPrd && status === 'PRD_REVIEW' && currentUser?.uid === currentCaseDetails.user_id && (
            <Box sx={{ mt: 3, pt: 2, borderTop: '1px solid #eee' }}>
              <Typography variant="h6" gutterBottom>
                PRD Review Actions
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                As the case initiator, you can approve or reject this PRD.
              </Typography>
              <Stack direction="row" spacing={2} alignItems="center">
                <Button 
                  variant="contained" 
                  color="success"
                  onClick={handleApprovePrd} 
                  disabled={isLoading}
                  startIcon={<CheckCircleIcon />}
                >
                  Approve PRD
                </Button>
                <Button 
                  variant="outlined" 
                  color="error"
                  onClick={handleOpenRejectDialog} 
                  disabled={isLoading}
                  startIcon={<RejectIcon />}
                >
                  Reject PRD
                </Button>
              </Stack>
              {approvalError && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {approvalError}
                </Alert>
              )}
              {approvalSuccess && (
                <Alert severity="success" sx={{ mt: 2 }}>
                  {approvalSuccess}
                </Alert>
              )}
            </Box>
          )}
        </Box>
        
        {(isLoading && !isSendingFeedback && !isLoadingCaseDetails && !isEditingPrd) && 
          <CircularProgress sx={{display: 'block', margin: '20px auto'}} />
        }



      </Paper>

      {/* Rejection Dialog */}
      <Dialog open={isRejectDialogOpen} onClose={handleCloseRejectDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Reject PRD</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Please provide a reason for rejecting this PRD (optional):
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={3}
            value={rejectionReason}
            onChange={(e) => setRejectionReason(e.target.value)}
            placeholder="Enter reason for rejection..."
            variant="outlined"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseRejectDialog} disabled={isLoading}>
            Cancel
          </Button>
          <Button 
            onClick={handleRejectPrd} 
            color="error" 
            variant="contained"
            disabled={isLoading}
          >
            {isLoading ? 'Rejecting...' : 'Reject PRD'}
          </Button>
        </DialogActions>
      </Dialog>


    </Container>
  );
};

export default BusinessCaseDetailPage; 