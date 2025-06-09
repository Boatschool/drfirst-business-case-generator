import React, { useState, useEffect } from 'react';
import {
  Typography,
  Paper,
  Box,
  Button,
  Alert,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stack,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Send as SendIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as RejectIcon,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import { BusinessCaseDetails } from '../../services/agent/AgentService';
import { useAgentContext } from '../../hooks/useAgentContext';
import { useAuth } from '../../hooks/useAuth';
import { PAPER_ELEVATION, STANDARD_STYLES } from '../../styles/constants';


interface PRDSectionProps {
  currentCaseDetails: BusinessCaseDetails | null;
  isLoading: boolean;
}

// Enhanced markdown styles for better formatting and readability
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
  '& h4': {
    fontSize: '1.1rem',
    fontWeight: 500,
    color: '#555',
    marginTop: '1rem',
    marginBottom: '0.5rem',
  },
  '& p': {
    marginBottom: '1rem',
    lineHeight: 1.6,
    color: '#333',
    fontSize: '1rem',
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
    borderRadius: '4px',
  },
  '& code': {
    backgroundColor: '#f5f5f5',
    padding: '0.2rem 0.4rem',
    borderRadius: '3px',
    fontSize: '0.9em',
    fontFamily: 'monospace',
    color: '#d32f2f',
  },
  '& pre': {
    backgroundColor: '#f5f5f5',
    padding: '1rem',
    borderRadius: '5px',
    overflow: 'auto',
    margin: '1rem 0',
    border: '1px solid #e0e0e0',
  },
  '& table': {
    width: '100%',
    borderCollapse: 'collapse',
    margin: '1rem 0',
  },
  '& th, & td': {
    border: '1px solid #ddd',
    padding: '8px 12px',
    textAlign: 'left',
  },
  '& th': {
    backgroundColor: '#f5f5f5',
    fontWeight: 600,
  },
};

// Helper function to improve text formatting for better readability
const formatPrdContent = (content: string): string => {
  if (!content) return content;

  // Ensure proper line breaks after headings and before new sections
  const formatted = content
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

export const PRDSection: React.FC<PRDSectionProps> = ({
  currentCaseDetails,
  isLoading,
}) => {
  const {
    updatePrdDraft,
    submitPrdForReview,
    approvePrd,
    rejectPrd,
    error: agentContextError,
  } = useAgentContext();
  const { currentUser } = useAuth();

  // Local state for PRD editing
  const [isEditingPrd, setIsEditingPrd] = useState(false);
  const [editablePrdContent, setEditablePrdContent] = useState('');
  const [prdUpdateError, setPrdUpdateError] = useState<string | null>(null);
  const [prdUpdateSuccess, setPrdUpdateSuccess] = useState<string | null>(null);
  const [statusUpdateSuccess, setStatusUpdateSuccess] = useState<string | null>(
    null
  );
  const [statusUpdateError, setStatusUpdateError] = useState<string | null>(
    null
  );
  const [approvalSuccess, setApprovalSuccess] = useState<string | null>(null);
  const [approvalError, setApprovalError] = useState<string | null>(null);
  const [isRejectDialogOpen, setIsRejectDialogOpen] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');

  // Update editable content when currentCaseDetails changes
  useEffect(() => {
    if (currentCaseDetails?.prd_draft?.content_markdown && !isEditingPrd) {
      setEditablePrdContent(currentCaseDetails.prd_draft.content_markdown);
    }
  }, [currentCaseDetails, isEditingPrd]);

  // PRD editing handlers
  const handleEditPrd = () => {
    setEditablePrdContent(
      currentCaseDetails?.prd_draft?.content_markdown || ''
    );
    setIsEditingPrd(true);
    setPrdUpdateError(null);
    setPrdUpdateSuccess(null);
  };

  const handleCancelEditPrd = () => {
    setEditablePrdContent(
      currentCaseDetails?.prd_draft?.content_markdown || ''
    );
    setIsEditingPrd(false);
    setPrdUpdateError(null);
    setPrdUpdateSuccess(null);
  };

  const handleSavePrd = async () => {
    if (!currentCaseDetails?.case_id) return;
    setPrdUpdateError(null);
    setPrdUpdateSuccess(null);

    const success = await updatePrdDraft({
      caseId: currentCaseDetails.case_id,
      content_markdown: editablePrdContent,
    });

    if (success) {
      setIsEditingPrd(false);
      setPrdUpdateSuccess('PRD updated successfully!');
      setTimeout(() => setPrdUpdateSuccess(null), 5000);
    } else {
      setPrdUpdateError(
        agentContextError?.message || 'Failed to save PRD. Please try again.'
      );
    }
  };

  // PRD submission and approval handlers
  const handleSubmitPrdForReview = async () => {
    if (!currentCaseDetails?.case_id) return;
    setStatusUpdateError(null);
    setStatusUpdateSuccess(null);

    const success = await submitPrdForReview(currentCaseDetails.case_id);

    if (success) {
      setStatusUpdateSuccess('PRD submitted for review successfully!');
      setTimeout(() => setStatusUpdateSuccess(null), 5000);
    } else {
      setStatusUpdateError(
        agentContextError?.message ||
          'Failed to submit PRD for review. Please try again.'
      );
    }
  };

  const handleApprovePrd = async () => {
    if (!currentCaseDetails?.case_id) return;
    setApprovalError(null);
    setApprovalSuccess(null);

    const success = await approvePrd(currentCaseDetails.case_id);

    if (success) {
      setApprovalSuccess('PRD approved successfully!');
      setTimeout(() => setApprovalSuccess(null), 5000);
    } else {
      setApprovalError(
        agentContextError?.message || 'Failed to approve PRD. Please try again.'
      );
    }
  };

  const handleRejectPrd = async () => {
    if (!currentCaseDetails?.case_id) return;
    setApprovalError(null);
    setApprovalSuccess(null);

    const success = await rejectPrd(
      currentCaseDetails.case_id,
      rejectionReason.trim() || undefined
    );

    if (success) {
      setApprovalSuccess('PRD rejected successfully.');
      setIsRejectDialogOpen(false);
      setRejectionReason('');
      setTimeout(() => setApprovalSuccess(null), 5000);
    } else {
      setApprovalError(
        agentContextError?.message || 'Failed to reject PRD. Please try again.'
      );
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

  // Permission helpers
  const canEditPrd = () => {
    if (!currentCaseDetails || !currentUser) return false;
    const isInitiator = currentCaseDetails.user_id === currentUser.uid;
    const allowedStatuses = ['PRD_DRAFTING', 'PRD_REJECTED'];
    return isInitiator && allowedStatuses.includes(currentCaseDetails.status);
  };

  const canSubmitPrd = () => {
    if (!currentCaseDetails || !currentUser) return false;
    const isInitiator = currentCaseDetails.user_id === currentUser.uid;
    const allowedStatuses = ['PRD_DRAFTING', 'PRD_REJECTED'];
    return (
      isInitiator &&
      allowedStatuses.includes(currentCaseDetails.status) &&
      currentCaseDetails.prd_draft
    );
  };

  const canApproveRejectPrd = () => {
    if (!currentCaseDetails || !currentUser) return false;
    const isInitiator = currentCaseDetails.user_id === currentUser.uid;
    return isInitiator && currentCaseDetails.status === 'PRD_REVIEW';
  };

  if (!currentCaseDetails?.prd_draft) {
    return null;
  }

  return (
    <Box mb={4}>
      <Paper elevation={PAPER_ELEVATION.MAIN_CONTENT} sx={STANDARD_STYLES.mainContentPaper}>
        <Stack
          direction="row"
          alignItems="center"
          justifyContent="space-between"
          mb={2}
        >
          <Typography variant="h5" component="h2" gutterBottom sx={{ mb: 0 }}>
            Product Requirements Document (PRD)
          </Typography>
          <Stack direction="row" spacing={1}>
            {canEditPrd() && !isEditingPrd && (
              <Tooltip title="Edit PRD">
                <IconButton
                  color="primary"
                  onClick={handleEditPrd}
                  disabled={isLoading}
                >
                  <EditIcon />
                </IconButton>
              </Tooltip>
            )}
            {canSubmitPrd() && !isEditingPrd && (
              <Button
                variant="contained"
                size="small"
                startIcon={<SendIcon />}
                onClick={handleSubmitPrdForReview}
                disabled={isLoading}
              >
                Submit for Review
              </Button>
            )}
            {canApproveRejectPrd() && !isEditingPrd && (
              <>
                <Button
                  variant="contained"
                  color="success"
                  size="small"
                  startIcon={<CheckCircleIcon />}
                  onClick={handleApprovePrd}
                  disabled={isLoading}
                >
                  Approve
                </Button>
                <Button
                  variant="outlined"
                  color="error"
                  size="small"
                  startIcon={<RejectIcon />}
                  onClick={handleOpenRejectDialog}
                  disabled={isLoading}
                >
                  Reject
                </Button>
              </>
            )}
          </Stack>
        </Stack>

        {/* Success/Error Messages */}
        {prdUpdateSuccess && (
          <Alert
            severity="success"
            sx={{ mb: 2 }}
            onClose={() => setPrdUpdateSuccess(null)}
          >
            {prdUpdateSuccess}
          </Alert>
        )}
        {prdUpdateError && (
          <Alert
            severity="error"
            sx={{ mb: 2 }}
            onClose={() => setPrdUpdateError(null)}
          >
            {prdUpdateError}
          </Alert>
        )}
        {statusUpdateSuccess && (
          <Alert
            severity="success"
            sx={{ mb: 2 }}
            onClose={() => setStatusUpdateSuccess(null)}
          >
            {statusUpdateSuccess}
          </Alert>
        )}
        {statusUpdateError && (
          <Alert
            severity="error"
            sx={{ mb: 2 }}
            onClose={() => setStatusUpdateError(null)}
          >
            {statusUpdateError}
          </Alert>
        )}
        {approvalSuccess && (
          <Alert
            severity="success"
            sx={{ mb: 2 }}
            onClose={() => setApprovalSuccess(null)}
          >
            {approvalSuccess}
          </Alert>
        )}
        {approvalError && (
          <Alert
            severity="error"
            sx={{ mb: 2 }}
            onClose={() => setApprovalError(null)}
          >
            {approvalError}
          </Alert>
        )}

        {/* PRD Content */}
        {!isEditingPrd ? (
          <Box sx={markdownStyles}>
            <ReactMarkdown>
              {formatPrdContent(currentCaseDetails.prd_draft.content_markdown)}
            </ReactMarkdown>
          </Box>
        ) : (
          <Box>
            <TextField
              multiline
              fullWidth
              rows={20}
              value={editablePrdContent}
              onChange={(e) => setEditablePrdContent(e.target.value)}
              variant="outlined"
              placeholder="Enter PRD content here..."
              sx={{ mb: 2 }}
            />
            <Stack direction="row" spacing={2} justifyContent="flex-end">
              <Button
                variant="outlined"
                startIcon={<CancelIcon />}
                onClick={handleCancelEditPrd}
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={handleSavePrd}
                disabled={isLoading}
              >
                {isLoading ? 'Saving...' : 'Save Changes'}
              </Button>
            </Stack>
          </Box>
        )}
      </Paper>

      {/* Rejection Dialog */}
      <Dialog
        open={isRejectDialogOpen}
        onClose={handleCloseRejectDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Reject PRD</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Rejection Reason (Optional)"
            fullWidth
            multiline
            rows={4}
            value={rejectionReason}
            onChange={(e) => setRejectionReason(e.target.value)}
            placeholder="Please provide a reason for rejecting this PRD..."
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseRejectDialog}>Cancel</Button>
          <Button onClick={handleRejectPrd} color="error" variant="contained">
            Reject PRD
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
