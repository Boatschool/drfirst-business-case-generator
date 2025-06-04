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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
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
  AccessTime as TimeIcon,
  AttachMoney as MoneyIcon,
  TrendingUp as ValueIcon,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import { useAgentContext } from '../contexts/AgentContext';

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
    updateSystemDesign,
    submitSystemDesignForReview,
    approveSystemDesign,
    rejectSystemDesign,
    isLoading,
    error: agentContextError,
    clearCurrentCaseDetails,
    messages
  } = useAgentContext();
  const { currentUser, systemRole } = useAuth();

  const [isEditingPrd, setIsEditingPrd] = useState(false);
  const [editablePrdContent, setEditablePrdContent] = useState('');
  const [isEditingSystemDesign, setIsEditingSystemDesign] = useState(false);
  const [editableSystemDesignContent, setEditableSystemDesignContent] = useState('');
  const [feedbackMessage, setFeedbackMessage] = useState('');
  const [isSendingFeedback, setIsSendingFeedback] = useState(false);
  const [feedbackSendError, setFeedbackSendError] = useState<string | null>(null);
  const [prdUpdateError, setPrdUpdateError] = useState<string | null>(null);
  const [prdUpdateSuccess, setPrdUpdateSuccess] = useState<string | null>(null);
  const [systemDesignUpdateError, setSystemDesignUpdateError] = useState<string | null>(null);
  const [systemDesignUpdateSuccess, setSystemDesignUpdateSuccess] = useState<string | null>(null);
  const [statusUpdateSuccess, setStatusUpdateSuccess] = useState<string | null>(null);
  const [statusUpdateError, setStatusUpdateError] = useState<string | null>(null);
  const [approvalSuccess, setApprovalSuccess] = useState<string | null>(null);
  const [approvalError, setApprovalError] = useState<string | null>(null);
  const [isRejectDialogOpen, setIsRejectDialogOpen] = useState(false);
  const [isSystemDesignRejectDialogOpen, setIsSystemDesignRejectDialogOpen] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');
  const [systemDesignRejectionReason, setSystemDesignRejectionReason] = useState('');

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

  useEffect(() => {
    if (currentCaseDetails?.system_design_v1_draft?.content_markdown && !isEditingSystemDesign) {
      setEditableSystemDesignContent(currentCaseDetails.system_design_v1_draft.content_markdown);
    }
  }, [currentCaseDetails, isEditingSystemDesign]);

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

  // System Design Handlers
  const handleEditSystemDesign = () => {
    setEditableSystemDesignContent(currentCaseDetails?.system_design_v1_draft?.content_markdown || '');
    setIsEditingSystemDesign(true);
    setSystemDesignUpdateError(null);
    setSystemDesignUpdateSuccess(null);
  };

  const handleCancelEditSystemDesign = () => {
    setIsEditingSystemDesign(false);
    setEditableSystemDesignContent(currentCaseDetails?.system_design_v1_draft?.content_markdown || '');
    setSystemDesignUpdateError(null);
    setSystemDesignUpdateSuccess(null);
  };

  const handleSaveSystemDesign = async () => {
    if (!caseId) return;
    
    try {
      const success = await updateSystemDesign(caseId, editableSystemDesignContent);
      if (success) {
        setIsEditingSystemDesign(false);
        setSystemDesignUpdateSuccess('System Design saved successfully.');
        setSystemDesignUpdateError(null);
      }
    } catch (error: any) {
      setSystemDesignUpdateError(error.message || 'Failed to save System Design.');
      setSystemDesignUpdateSuccess(null);
    }
  };

  const handleSubmitSystemDesignForReview = async () => {
    if (!caseId) return;
    
    try {
      const success = await submitSystemDesignForReview(caseId);
      if (success) {
        setStatusUpdateSuccess('System Design submitted for review successfully.');
        setStatusUpdateError(null);
      }
    } catch (error: any) {
      setStatusUpdateError(error.message || 'Failed to submit System Design for review.');
      setStatusUpdateSuccess(null);
    }
  };

  const handleApproveSystemDesign = async () => {
    if (!caseId) return;
    
    try {
      const success = await approveSystemDesign(caseId);
      if (success) {
        setApprovalSuccess('System Design approved successfully.');
        setApprovalError(null);
      }
    } catch (error: any) {
      setApprovalError(error.message || 'Failed to approve System Design.');
      setApprovalSuccess(null);
    }
  };

  const handleRejectSystemDesign = async () => {
    if (!caseId) return;
    
    try {
      const success = await rejectSystemDesign(caseId, systemDesignRejectionReason);
      if (success) {
        setApprovalSuccess('System Design rejected successfully.');
        setApprovalError(null);
        setIsSystemDesignRejectDialogOpen(false);
        setSystemDesignRejectionReason('');
      }
    } catch (error: any) {
      setApprovalError(error.message || 'Failed to reject System Design.');
      setApprovalSuccess(null);
    }
  };

  const handleOpenSystemDesignRejectDialog = () => {
    setIsSystemDesignRejectDialogOpen(true);
    setSystemDesignRejectionReason('');
  };

  const handleCloseSystemDesignRejectDialog = () => {
    setIsSystemDesignRejectDialogOpen(false);
    setSystemDesignRejectionReason('');
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

  const { title, status, problem_statement, relevant_links, prd_draft, system_design_v1_draft, effort_estimate_v1, cost_estimate_v1, value_projection_v1 } = currentCaseDetails;

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

        {/* System Design Section */}
        {system_design_v1_draft?.content_markdown && (
          <>
            <Divider sx={{ my: 3 }} />
            <Box mb={3}>
              <Stack direction="row" alignItems="center" justifyContent="space-between" mb={2}>
                <Typography variant="h5">System Design (v1)</Typography>
                <Stack direction="row" spacing={1}>
                  {/* Edit System Design Button - Show for owner or DEVELOPER role in appropriate statuses */}
                  {!isEditingSystemDesign && 
                   (status === 'SYSTEM_DESIGN_DRAFTED' || status === 'SYSTEM_DESIGN_PENDING_REVIEW') &&
                   (currentCaseDetails?.user_id === currentUser?.uid || systemRole === 'DEVELOPER') && (
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<EditIcon />}
                      onClick={handleEditSystemDesign}
                      disabled={isLoading}
                    >
                      Edit System Design
                    </Button>
                  )}
                  
                  {/* Submit for Review Button - Show for owner or DEVELOPER role when status is SYSTEM_DESIGN_DRAFTED */}
                  {!isEditingSystemDesign && 
                   status === 'SYSTEM_DESIGN_DRAFTED' &&
                   (currentCaseDetails?.user_id === currentUser?.uid || systemRole === 'DEVELOPER') && (
                    <Button
                      variant="contained"
                      size="small"
                      startIcon={<SendIcon />}
                      onClick={handleSubmitSystemDesignForReview}
                      disabled={isLoading}
                    >
                      Submit for Review
                    </Button>
                  )}
                  
                  {/* Approve System Design Button - Show only for DEVELOPER role when status is SYSTEM_DESIGN_PENDING_REVIEW */}
                  {!isEditingSystemDesign && 
                   status === 'SYSTEM_DESIGN_PENDING_REVIEW' &&
                   systemRole === 'DEVELOPER' && (
                    <Button
                      variant="contained"
                      size="small"
                      color="success"
                      startIcon={<CheckCircleIcon />}
                      onClick={handleApproveSystemDesign}
                      disabled={isLoading}
                    >
                      Approve System Design
                    </Button>
                  )}
                  
                  {/* Reject System Design Button - Show only for DEVELOPER role when status is SYSTEM_DESIGN_PENDING_REVIEW */}
                  {!isEditingSystemDesign && 
                   status === 'SYSTEM_DESIGN_PENDING_REVIEW' &&
                   systemRole === 'DEVELOPER' && (
                    <Button
                      variant="outlined"
                      size="small"
                      color="error"
                      startIcon={<RejectIcon />}
                      onClick={handleOpenSystemDesignRejectDialog}
                      disabled={isLoading}
                    >
                      Reject System Design
                    </Button>
                  )}
                </Stack>
              </Stack>
              
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Generated by: {system_design_v1_draft.generated_by} • Version: {system_design_v1_draft.version}
                {system_design_v1_draft.last_edited_by && (
                  <> • Last edited by: {system_design_v1_draft.last_edited_by}</>
                )}
              </Typography>
              
              {/* System Design Update Success/Error Messages */}
              {systemDesignUpdateSuccess && (
                <Alert severity="success" sx={{ mb: 2 }}>
                  {systemDesignUpdateSuccess}
                </Alert>
              )}
              {systemDesignUpdateError && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {systemDesignUpdateError}
                </Alert>
              )}
              
              {/* System Design Content - Editable or Read-only */}
              {isEditingSystemDesign ? (
                <Box>
                  <TextField
                    multiline
                    fullWidth
                    rows={20}
                    value={editableSystemDesignContent}
                    onChange={(e) => setEditableSystemDesignContent(e.target.value)}
                    variant="outlined"
                    placeholder="Edit the system design content..."
                    sx={{ mb: 2, fontFamily: 'monospace' }}
                  />
                  <Stack direction="row" spacing={1}>
                    <Button
                      variant="contained"
                      startIcon={<SaveIcon />}
                      onClick={handleSaveSystemDesign}
                      disabled={isLoading}
                    >
                      Save Changes
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<CancelIcon />}
                      onClick={handleCancelEditSystemDesign}
                      disabled={isLoading}
                    >
                      Cancel
                    </Button>
                  </Stack>
                </Box>
              ) : (
                <Paper elevation={0} sx={{ 
                  p: 3, 
                  mt: 1, 
                  border: '1px solid #eee', 
                  backgroundColor: '#fafafa',
                  ...markdownStyles
                }}>
                  <ReactMarkdown>{formatPrdContent(system_design_v1_draft.content_markdown)}</ReactMarkdown>
                </Paper>
              )}
            </Box>
          </>
        )}

        {/* Effort Estimate Section */}
        {effort_estimate_v1 && (
          <>
            <Divider sx={{ my: 3 }} />
            <Box mb={3}>
              <Stack direction="row" alignItems="center" spacing={1} mb={2}>
                <TimeIcon color="primary" />
                <Typography variant="h5" gutterBottom sx={{ mb: 0 }}>Effort Estimate</Typography>
              </Stack>
              <Card variant="outlined" sx={{ mb: 2 }}>
                <CardContent>
                  <Stack direction="row" spacing={4} mb={3}>
                    <Box>
                      <Typography variant="h6" color="primary">
                        {effort_estimate_v1.total_hours}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total Hours
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="h6" color="primary">
                        {effort_estimate_v1.estimated_duration_weeks}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Weeks Duration
                      </Typography>
                    </Box>
                    <Box>
                      <Chip 
                        label={effort_estimate_v1.complexity_assessment} 
                        color="info" 
                        variant="outlined" 
                      />
                    </Box>
                  </Stack>
                  
                  <Typography variant="h6" gutterBottom>Role Breakdown</Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell><strong>Role</strong></TableCell>
                          <TableCell align="right"><strong>Hours</strong></TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {effort_estimate_v1.roles?.map((role, index) => (
                          <TableRow key={index}>
                            <TableCell>{role.role}</TableCell>
                            <TableCell align="right">{role.hours}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                  
                  {effort_estimate_v1.notes && (
                    <Box mt={2}>
                      <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                        {effort_estimate_v1.notes}
                      </Typography>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Box>
          </>
        )}

        {/* Cost Estimate Section */}
        {cost_estimate_v1 && (
          <>
            <Divider sx={{ my: 3 }} />
            <Box mb={3}>
              <Stack direction="row" alignItems="center" spacing={1} mb={2}>
                <MoneyIcon color="primary" />
                <Typography variant="h5" gutterBottom sx={{ mb: 0 }}>Cost Estimate</Typography>
              </Stack>
              <Card variant="outlined" sx={{ mb: 2 }}>
                <CardContent>
                  <Stack direction="row" spacing={4} mb={3}>
                    <Box>
                      <Typography variant="h4" color="primary">
                        ${cost_estimate_v1.estimated_cost.toLocaleString()}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total Cost ({cost_estimate_v1.currency})
                      </Typography>
                    </Box>
                    {cost_estimate_v1.rate_card_used && (
                      <Box>
                        <Typography variant="body1" fontWeight="medium">
                          {cost_estimate_v1.rate_card_used}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Rate Card Used
                        </Typography>
                      </Box>
                    )}
                  </Stack>
                  
                  <Typography variant="h6" gutterBottom>Cost Breakdown by Role</Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell><strong>Role</strong></TableCell>
                          <TableCell align="right"><strong>Hours</strong></TableCell>
                          <TableCell align="right"><strong>Rate</strong></TableCell>
                          <TableCell align="right"><strong>Total Cost</strong></TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {cost_estimate_v1.role_breakdown?.map((role, index) => (
                          <TableRow key={index}>
                            <TableCell>{role.role}</TableCell>
                            <TableCell align="right">{role.hours}</TableCell>
                            <TableCell align="right">${role.hourly_rate}/hr</TableCell>
                            <TableCell align="right">${role.total_cost.toLocaleString()}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                  
                  {cost_estimate_v1.notes && (
                    <Box mt={2}>
                      <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                        {cost_estimate_v1.notes}
                      </Typography>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Box>
          </>
        )}

                {/* Value Projection Section */}
        {value_projection_v1 && (
          <>
            <Divider sx={{ my: 3 }} />
            <Box mb={3}>
              <Stack direction="row" alignItems="center" spacing={1} mb={2}>
                <ValueIcon color="primary" />
                <Typography variant="h5" gutterBottom sx={{ mb: 0 }}>Value/Revenue Projection</Typography>
              </Stack>
              <Card variant="outlined" sx={{ mb: 2 }}>
                <CardContent>
                  <Stack direction="row" spacing={4} mb={3}>
                    {value_projection_v1.template_used && (
                      <Box>
                        <Typography variant="body1" fontWeight="medium">
                          {value_projection_v1.template_used}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Template Used
                        </Typography>
                      </Box>
                    )}
                    {value_projection_v1.methodology && (
                      <Box>
                        <Typography variant="body1" fontWeight="medium">
                          {value_projection_v1.methodology}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Methodology
                        </Typography>
                      </Box>
                    )}
                  </Stack>
                  
                  <Typography variant="h6" gutterBottom>Value Scenarios</Typography>
                  <Stack spacing={2} mb={3}>
                    {value_projection_v1.scenarios?.map((scenario, index) => (
                      <Card key={index} variant="outlined" sx={{ backgroundColor: '#f8f9fa' }}>
                        <CardContent sx={{ py: 2 }}>
                          <Stack direction="row" justifyContent="space-between" alignItems="center">
                            <Box>
                              <Typography variant="h6" color="primary">
                                {scenario.case} Scenario
                              </Typography>
                              {scenario.description && (
                                <Typography variant="body2" color="text.secondary">
                                  {scenario.description}
                                </Typography>
                              )}
                            </Box>
                            <Typography variant="h5" fontWeight="bold" color="success.main">
                              ${scenario.value.toLocaleString()} {value_projection_v1.currency}
                            </Typography>
                          </Stack>
                        </CardContent>
                      </Card>
                    ))}
                  </Stack>
                  
                  {value_projection_v1.assumptions && value_projection_v1.assumptions.length > 0 && (
                    <Box mb={2}>
                      <Typography variant="h6" gutterBottom>Key Assumptions</Typography>
                      <List dense>
                        {value_projection_v1.assumptions.map((assumption, index) => (
                          <ListItem key={index} sx={{ py: 0.5 }}>
                            <ListItemText 
                              primary={assumption}
                              primaryTypographyProps={{ variant: 'body2' }}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}
                  
                  {value_projection_v1.notes && (
                    <Box mt={2}>
                      <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                        {value_projection_v1.notes}
                      </Typography>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Box>
          </>
        )}
        
        {(isLoading && !isSendingFeedback && !isLoadingCaseDetails && !isEditingPrd) && 
          <CircularProgress sx={{display: 'block', margin: '20px auto'}} />
        }

        

      </Paper>

      {/* PRD Rejection Dialog */}
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

      {/* System Design Rejection Dialog */}
      <Dialog open={isSystemDesignRejectDialogOpen} onClose={handleCloseSystemDesignRejectDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Reject System Design</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Please provide a reason for rejecting this System Design (optional):
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={3}
            value={systemDesignRejectionReason}
            onChange={(e) => setSystemDesignRejectionReason(e.target.value)}
            placeholder="Enter reason for rejection..."
            variant="outlined"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseSystemDesignRejectDialog} disabled={isLoading}>
            Cancel
          </Button>
          <Button 
            onClick={handleRejectSystemDesign} 
            color="error" 
            variant="contained"
            disabled={isLoading}
          >
            {isLoading ? 'Rejecting...' : 'Reject System Design'}
          </Button>
        </DialogActions>
      </Dialog>

    </Container>
  );
};

export default BusinessCaseDetailPage; 