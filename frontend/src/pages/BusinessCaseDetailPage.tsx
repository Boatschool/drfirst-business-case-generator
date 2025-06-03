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
} from '@mui/material';
import {
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Send as SendIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import { useAgentContext } from '../contexts/AgentContext';
import { AgentUpdate } from '../services/agent/AgentService';
import { useAuth } from '../contexts/AuthContext';

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
          <Typography variant="h4" component="h1" gutterBottom>
            {title || 'Business Case Details'}
          </Typography>
          <Tooltip title="Refresh Case Details">
            <IconButton onClick={loadDetails} disabled={isLoading || isLoadingCaseDetails}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
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
              <Paper elevation={0} sx={{ p: 2, mt: 1, border: '1px solid #eee', backgroundColor: '#f9f9f9' }}>
                <ReactMarkdown>{prd_draft.content_markdown}</ReactMarkdown>
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
        </Box>
        
        {(isLoading && !isSendingFeedback && !isLoadingCaseDetails && !isEditingPrd) && 
          <CircularProgress sx={{display: 'block', margin: '20px auto'}} />
        }

        <Divider sx={{ my: 3 }} />

        <Box>
          <Typography variant="h5" gutterBottom>Interaction History / Messages</Typography>
          <Stack spacing={2} sx={{ maxHeight: '400px', overflowY: 'auto', p: 1, border: '1px solid #ddd', borderRadius: 1}}>
            {displayMessages.length > 0 ? (
              displayMessages.map((msg: AgentUpdate, index: number) => (
                <Paper 
                  key={`${msg.timestamp}-${index}`} 
                  elevation={1} 
                  sx={{
                    p: 1.5, 
                    alignSelf: msg.source === 'USER' ? 'flex-end' : 'flex-start',
                    backgroundColor: msg.source === 'USER' ? 'primary.light' : 'grey.200',
                    color: msg.source === 'USER' ? 'primary.contrastText' : 'inherit',
                    maxWidth: '75%',
                    minWidth: '20%',
                    wordBreak: 'break-word'
                  }}
                >
                  <Typography variant="caption" display="block" sx={{ mb: 0.5, opacity: 0.8}}>
                    {msg.source} - {new Date(msg.timestamp).toLocaleString()}
                  </Typography>
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>{msg.content}</Typography>
                </Paper>
              ))
            ) : (
              <Typography color="textSecondary" sx={{p:1}}>No messages yet.</Typography>
            )}
          </Stack>

          <Box component="form" noValidate autoComplete="off" sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Send a message to the agent"
              variant="outlined"
              value={feedbackMessage}
              onChange={(e) => setFeedbackMessage(e.target.value)}
              multiline
              rows={3}
              disabled={isSendingFeedback || isLoading}
              sx={{mb:1}}
            />
            <Button 
              variant="contained" 
              onClick={handleSendFeedback} 
              startIcon={<SendIcon />} 
              disabled={!feedbackMessage.trim() || isSendingFeedback || isLoading}
            >
              {isSendingFeedback ? 'Sending...' : 'Send Message'}
            </Button>
            {feedbackSendError && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {feedbackSendError}
              </Alert>
            )}
          </Box>
        </Box>

      </Paper>
    </Container>
  );
};

export default BusinessCaseDetailPage; 