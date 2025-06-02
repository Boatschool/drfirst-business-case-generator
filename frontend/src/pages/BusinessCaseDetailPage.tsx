import React, { useEffect, useState } from 'react';
import { useParams, Link as RouterLink } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  CircularProgress,
  Alert,
  Grid,
  List,
  ListItem,
  ListItemText,
  Divider,
  Link,
  Chip,
  TextField,
  Button,
  Stack,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import EditIcon from '@mui/icons-material/Edit';
import SaveIcon from '@mui/icons-material/Save';
import CancelIcon from '@mui/icons-material/Cancel';
import { useAgentContext } from '../contexts/AgentContext';
import { AgentUpdate, ProvideFeedbackPayload } from '../services/agent/AgentService';
import ReactMarkdown from 'react-markdown';

const BusinessCaseDetailPage: React.FC = () => {
  const { caseId } = useParams<{ caseId: string }>();
  const {
    currentCaseDetails,
    isLoadingCaseDetails,
    caseDetailsError,
    fetchCaseDetails,
    clearCurrentCaseDetails,
    sendFeedbackToAgent,
    isLoading,
    error,
  } = useAgentContext();

  const [feedbackMessage, setFeedbackMessage] = useState('');
  const [isEditingPrd, setIsEditingPrd] = useState(false);
  const [editedPrdContent, setEditedPrdContent] = useState('');

  useEffect(() => {
    if (caseId) {
      fetchCaseDetails(caseId);
    }
    return () => {
      clearCurrentCaseDetails();
    };
  }, [caseId, fetchCaseDetails, clearCurrentCaseDetails]);

  useEffect(() => {
    if (currentCaseDetails?.prd_draft?.content_markdown && !isEditingPrd) {
      setEditedPrdContent(currentCaseDetails.prd_draft.content_markdown);
    }
  }, [currentCaseDetails?.prd_draft?.content_markdown, isEditingPrd]);

  const handleSendFeedback = async () => {
    if (!caseId || !feedbackMessage.trim()) return;
    const payload: ProvideFeedbackPayload = {
      caseId,
      message: feedbackMessage,
    };
    try {
      await sendFeedbackToAgent(payload);
      setFeedbackMessage('');
    } catch (e) {
      console.error("Failed to send feedback directly in page:", e);
    }
  };

  const handleEditPrd = () => {
    setEditedPrdContent(currentCaseDetails?.prd_draft?.content_markdown || '');
    setIsEditingPrd(true);
  };

  const handleSavePrd = async () => {
    console.log("Saving PRD Content:", editedPrdContent);
    if (currentCaseDetails && currentCaseDetails.prd_draft) {
        // This is a mock update, actual update will come from backend
        // currentCaseDetails.prd_draft.content_markdown = editedPrdContent;
    }
    setIsEditingPrd(false);
  };

  const handleCancelPrdEdit = () => {
    setEditedPrdContent(currentCaseDetails?.prd_draft?.content_markdown || '');
    setIsEditingPrd(false);
  };

  if (isLoadingCaseDetails) {
    return (
      <Container sx={{display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh'}}>
        <CircularProgress />
        <Typography sx={{ml: 2}}>Loading case details...</Typography>
      </Container>
    );
  }

  if (caseDetailsError) {
    return (
      <Container sx={{mt: 4}}>
        <Alert severity="error">{caseDetailsError.message || 'Failed to load case details.'}</Alert>
      </Container>
    );
  }

  if (!currentCaseDetails) {
    return (
      <Container sx={{mt: 4}}>
        <Alert severity="info">No case details to display. Ensure the case ID is correct or try reloading.</Alert>
      </Container>
    );
  }

  const { title, problem_statement, relevant_links, status, prd_draft, history } = currentCaseDetails;

  return (
    <Container component="main" maxWidth="lg" sx={{mb: 4}}>
      <Paper elevation={3} sx={{ mt: 4, p: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={10}>
            <Typography component="h1" variant="h4" gutterBottom>
              {title || 'Business Case Details'}
            </Typography>
          </Grid>
          <Grid item xs={2} sx={{textAlign: 'right'}}>
            {status && <Chip label={status} color="primary" />}
          </Grid>
        </Grid>
        
        <Divider sx={{ my: 2 }} />

        <Box sx={{ mt: 3 }}>
          <Typography variant="h6" gutterBottom>Problem Statement</Typography>
          <Typography paragraph sx={{whiteSpace: 'pre-wrap'}}>
            {problem_statement || 'Not available.'}
          </Typography>

          {relevant_links && relevant_links.length > 0 && (
            <Box sx={{mb: 3}}>
              <Typography variant="h6" gutterBottom>Relevant Links</Typography>
              <List dense>
                {relevant_links.map((link, index) => (
                  <ListItem key={index} disableGutters>
                    <Link href={link.url} target="_blank" rel="noopener noreferrer">
                      {link.name || link.url}
                    </Link>
                  </ListItem>
                ))}
              </List>
            </Box>
          )}

          {prd_draft && (
            <Box sx={{mb: 3}}>
              <Grid container justifyContent="space-between" alignItems="center">
                <Grid item>
                  <Typography variant="h6" gutterBottom>PRD Draft</Typography>
                </Grid>
                <Grid item>
                  {!isEditingPrd && (
                    <Button startIcon={<EditIcon />} onClick={handleEditPrd} size="small">
                      Edit PRD
                    </Button>
                  )}
                </Grid>
              </Grid>
              {isEditingPrd ? (
                <Box component="div" sx={{mt:1}}>
                  <TextField
                    fullWidth
                    multiline
                    rows={15}
                    value={editedPrdContent}
                    onChange={(e) => setEditedPrdContent(e.target.value)}
                    variant="outlined"
                    sx={{mb:1}}
                  />
                  <Stack direction="row" spacing={2}>
                    <Button variant="contained" startIcon={<SaveIcon />} onClick={handleSavePrd}>
                      Save Changes
                    </Button>
                    <Button variant="outlined" startIcon={<CancelIcon />} onClick={handleCancelPrdEdit}>
                      Cancel
                    </Button>
                  </Stack>
                </Box>
              ) : (
                <Paper variant="outlined" sx={{ p: 2, maxHeight: '400px', overflowY: 'auto', whiteSpace: 'pre-wrap', backgroundColor: 'grey.50', mt:1 }}>
                  {prd_draft.content_markdown ? 
                    <ReactMarkdown>{prd_draft.content_markdown}</ReactMarkdown> : 
                    <Typography color="textSecondary">PRD content not available.</Typography>
                  }
                </Paper>
              )}
            </Box>
          )}

          {history && history.length > 0 && (
             <Box sx={{mb: 3}}>
                <Typography variant="h6" gutterBottom>Interaction History</Typography>
                <List sx={{maxHeight: '300px', overflowY: 'auto', border: '1px solid', borderColor: 'divider', borderRadius: 1}}>
                  {history.map((item: AgentUpdate, index: number) => (
                    <ListItem key={`${item.timestamp}-${index}`} divider={index < history.length -1}>
                      <ListItemText 
                        primaryTypographyProps={{fontWeight: item.source === 'USER' ? 'bold' : 'normal'}}
                        primary={`${item.source} (${new Date(item.timestamp).toLocaleString()}):`}
                        secondary={item.messageType === 'TEXT' || item.messageType === 'STATUS_UPDATE' || item.messageType === 'ERROR' ? (
                            <Typography component="span" variant="body2" sx={{whiteSpace: 'pre-wrap'}}>
                                {typeof item.content === 'string' ? item.content : JSON.stringify(item.content, null, 2)}
                            </Typography>
                        ) : item.messageType === 'PRD_DRAFT' ? (
                            <Typography component="span" variant="body2" color="text.secondary">
                                PRD Draft was generated/updated.
                            </Typography>
                        ) : (
                            <Typography component="span" variant="body2" color="text.secondary">
                                Complex content ({item.messageType}). See details above.
                            </Typography>
                        )}
                      />
                    </ListItem>
                  ))}
                </List>
            </Box>
          )}
        </Box>
        
        <Divider sx={{ my: 3 }} />

        <Box sx={{ mt: 2 }}>
          <Typography variant="h6" gutterBottom>Provide Feedback / Next Steps</Typography>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error.message || 'An error occurred while sending your message.'}
            </Alert>
          )}
          <TextField
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            label="Your message to the agent..."
            value={feedbackMessage}
            onChange={(e) => setFeedbackMessage(e.target.value)}
            disabled={isLoading}
            sx={{ mb: 1 }}
          />
          <Button
            variant="contained"
            color="primary"
            endIcon={<SendIcon />}
            onClick={handleSendFeedback}
            disabled={isLoading || !feedbackMessage.trim()}
          >
            Send Message
          </Button>
        </Box>

      </Paper>
    </Container>
  );
};

export default BusinessCaseDetailPage; 