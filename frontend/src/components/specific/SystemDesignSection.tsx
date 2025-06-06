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
  Divider,
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
import { toAppError } from '../../types/api';

interface SystemDesignSectionProps {
  currentCaseDetails: BusinessCaseDetails | null;
  isLoading: boolean;
}

export const SystemDesignSection: React.FC<SystemDesignSectionProps> = ({
  currentCaseDetails,
  isLoading,
}) => {
  const {
    updateSystemDesign,
    submitSystemDesignForReview,
    approveSystemDesign,
    rejectSystemDesign,
  } = useAgentContext();
  const { currentUser, systemRole } = useAuth();

  // Local state for system design editing
  const [isEditingSystemDesign, setIsEditingSystemDesign] = useState(false);
  const [editableSystemDesignContent, setEditableSystemDesignContent] =
    useState('');
  const [systemDesignUpdateError, setSystemDesignUpdateError] = useState<
    string | null
  >(null);
  const [systemDesignUpdateSuccess, setSystemDesignUpdateSuccess] = useState<
    string | null
  >(null);
  const [statusUpdateSuccess, setStatusUpdateSuccess] = useState<string | null>(
    null
  );
  const [statusUpdateError, setStatusUpdateError] = useState<string | null>(
    null
  );
  const [approvalSuccess, setApprovalSuccess] = useState<string | null>(null);
  const [approvalError, setApprovalError] = useState<string | null>(null);
  const [isSystemDesignRejectDialogOpen, setIsSystemDesignRejectDialogOpen] =
    useState(false);
  const [systemDesignRejectionReason, setSystemDesignRejectionReason] =
    useState('');

  // Update editable content when currentCaseDetails changes
  useEffect(() => {
    if (
      currentCaseDetails?.system_design_v1_draft?.content_markdown &&
      !isEditingSystemDesign
    ) {
      setEditableSystemDesignContent(
        currentCaseDetails.system_design_v1_draft.content_markdown
      );
    }
  }, [currentCaseDetails, isEditingSystemDesign]);

  // System Design editing handlers
  const handleEditSystemDesign = () => {
    setEditableSystemDesignContent(
      currentCaseDetails?.system_design_v1_draft?.content_markdown || ''
    );
    setIsEditingSystemDesign(true);
    setSystemDesignUpdateError(null);
    setSystemDesignUpdateSuccess(null);
  };

  const handleCancelEditSystemDesign = () => {
    setIsEditingSystemDesign(false);
    setEditableSystemDesignContent(
      currentCaseDetails?.system_design_v1_draft?.content_markdown || ''
    );
    setSystemDesignUpdateError(null);
    setSystemDesignUpdateSuccess(null);
  };

  const handleSaveSystemDesign = async () => {
    if (!currentCaseDetails?.case_id) return;

    try {
      const success = await updateSystemDesign(
        currentCaseDetails.case_id,
        editableSystemDesignContent
      );
      if (success) {
        setIsEditingSystemDesign(false);
        setSystemDesignUpdateSuccess('System Design saved successfully.');
        setSystemDesignUpdateError(null);
        setTimeout(() => setSystemDesignUpdateSuccess(null), 5000);
      }
    } catch (error) {
      setSystemDesignUpdateError(
        toAppError(error, 'api').message || 'Failed to save System Design.'
      );
      setSystemDesignUpdateSuccess(null);
    }
  };

  const handleSubmitSystemDesignForReview = async () => {
    if (!currentCaseDetails?.case_id) return;

    try {
      const success = await submitSystemDesignForReview(
        currentCaseDetails.case_id
      );
      if (success) {
        setStatusUpdateSuccess(
          'System Design submitted for review successfully.'
        );
        setStatusUpdateError(null);
        setTimeout(() => setStatusUpdateSuccess(null), 5000);
      }
    } catch (error) {
      setStatusUpdateError(
        toAppError(error, 'api').message || 'Failed to submit System Design for review.'
      );
      setStatusUpdateSuccess(null);
    }
  };

  const handleApproveSystemDesign = async () => {
    if (!currentCaseDetails?.case_id) return;

    try {
      const success = await approveSystemDesign(currentCaseDetails.case_id);
      if (success) {
        setApprovalSuccess('System Design approved successfully.');
        setApprovalError(null);
        setTimeout(() => setApprovalSuccess(null), 5000);
      }
    } catch (error) {
      setApprovalError(toAppError(error, 'api').message || 'Failed to approve System Design.');
      setApprovalSuccess(null);
    }
  };

  const handleRejectSystemDesign = async () => {
    if (!currentCaseDetails?.case_id) return;

    try {
      const success = await rejectSystemDesign(
        currentCaseDetails.case_id,
        systemDesignRejectionReason
      );
      if (success) {
        setApprovalSuccess('System Design rejected successfully.');
        setIsSystemDesignRejectDialogOpen(false);
        setSystemDesignRejectionReason('');
        setApprovalError(null);
        setTimeout(() => setApprovalSuccess(null), 5000);
      }
    } catch (error) {
      setApprovalError(toAppError(error, 'api').message || 'Failed to reject System Design.');
      setApprovalSuccess(null);
    }
  };

  const handleOpenSystemDesignRejectDialog = () => {
    setIsSystemDesignRejectDialogOpen(true);
    setSystemDesignRejectionReason('');
    setApprovalError(null);
    setApprovalSuccess(null);
  };

  const handleCloseSystemDesignRejectDialog = () => {
    setIsSystemDesignRejectDialogOpen(false);
    setSystemDesignRejectionReason('');
  };

  // Permission helpers
  const canEditSystemDesign = () => {
    if (!currentCaseDetails || !currentUser) return false;
    const isInitiator = currentCaseDetails.user_id === currentUser.uid;
    const allowedStatuses = ['SYSTEM_DESIGN_DRAFTED', 'SYSTEM_DESIGN_REJECTED'];
    return isInitiator && allowedStatuses.includes(currentCaseDetails.status);
  };

  const canSubmitSystemDesign = () => {
    if (!currentCaseDetails || !currentUser) return false;
    const isInitiator = currentCaseDetails.user_id === currentUser.uid;
    const allowedStatuses = ['SYSTEM_DESIGN_DRAFTED', 'SYSTEM_DESIGN_REJECTED'];
    return (
      isInitiator &&
      allowedStatuses.includes(currentCaseDetails.status) &&
      currentCaseDetails.system_design_v1_draft
    );
  };

  const canApproveRejectSystemDesign = () => {
    if (!currentCaseDetails || !currentUser) return false;
    const isDeveloper = systemRole === 'DEVELOPER';
    return (
      isDeveloper &&
      currentCaseDetails.status === 'SYSTEM_DESIGN_PENDING_REVIEW'
    );
  };

  if (!currentCaseDetails?.system_design_v1_draft) {
    // Check if PRD is approved but system design hasn't been generated
    const isPrdApproved = currentCaseDetails?.status === 'PRD_APPROVED';
    const isSystemDesignInProgress = currentCaseDetails?.status === 'SYSTEM_DESIGN_DRAFTING';
    
    return (
      <Box mb={4}>
        <Divider sx={{ my: 3 }} />
        <Paper elevation={PAPER_ELEVATION.MAIN_CONTENT} sx={STANDARD_STYLES.mainContentPaper}>
          <Typography variant="h5" component="h2" gutterBottom>
            System Design
          </Typography>
          {isPrdApproved ? (
            <Box>
              <Alert severity="warning" sx={{ mt: 2 }}>
                The PRD has been approved, but the system design generation appears to be incomplete. 
                The system design should have been automatically generated.
              </Alert>
              <Stack direction="row" spacing={2} sx={{ mt: 2 }}>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() => window.location.reload()}
                  disabled={isLoading}
                >
                  Refresh Page
                </Button>
                <Button
                  variant="outlined"
                  color="secondary"
                  onClick={() => {
                    // For now, suggest refresh - we could add a manual trigger API later
                    alert('Please try refreshing the page. If the issue persists, the system design generation may have encountered an error during the PRD approval process.');
                  }}
                  disabled={isLoading}
                >
                  Get Help
                </Button>
              </Stack>
            </Box>
          ) : isSystemDesignInProgress ? (
            <Alert severity="info" sx={{ mt: 2 }}>
              System design generation is in progress. Please wait while the Architect Agent creates the system design based on your approved PRD.
            </Alert>
          ) : (
            <Alert severity="info" sx={{ mt: 2 }}>
              The system design has not been generated yet. Once the PRD is approved, the system design will be automatically generated.
            </Alert>
          )}
        </Paper>
      </Box>
    );
  }

  return (
    <Box mb={4}>
      <Divider sx={{ my: 3 }} />
      <Paper elevation={PAPER_ELEVATION.MAIN_CONTENT} sx={STANDARD_STYLES.mainContentPaper}>
        <Stack
          direction="row"
          alignItems="center"
          justifyContent="space-between"
          mb={2}
        >
          <Typography variant="h5" component="h2" gutterBottom sx={{ mb: 0 }}>
            System Design
          </Typography>
          <Stack direction="row" spacing={1}>
            {canEditSystemDesign() && !isEditingSystemDesign && (
              <Tooltip title="Edit System Design">
                <IconButton
                  color="primary"
                  onClick={handleEditSystemDesign}
                  disabled={isLoading}
                >
                  <EditIcon />
                </IconButton>
              </Tooltip>
            )}
            {canSubmitSystemDesign() && !isEditingSystemDesign && (
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
            {canApproveRejectSystemDesign() && !isEditingSystemDesign && (
              <>
                <Button
                  variant="contained"
                  color="success"
                  size="small"
                  startIcon={<CheckCircleIcon />}
                  onClick={handleApproveSystemDesign}
                  disabled={isLoading}
                >
                  Approve
                </Button>
                <Button
                  variant="outlined"
                  color="error"
                  size="small"
                  startIcon={<RejectIcon />}
                  onClick={handleOpenSystemDesignRejectDialog}
                  disabled={isLoading}
                >
                  Reject
                </Button>
              </>
            )}
          </Stack>
        </Stack>

        {/* Success/Error Messages */}
        {systemDesignUpdateSuccess && (
          <Alert
            severity="success"
            sx={{ mb: 2 }}
            onClose={() => setSystemDesignUpdateSuccess(null)}
          >
            {systemDesignUpdateSuccess}
          </Alert>
        )}
        {systemDesignUpdateError && (
          <Alert
            severity="error"
            sx={{ mb: 2 }}
            onClose={() => setSystemDesignUpdateError(null)}
          >
            {systemDesignUpdateError}
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

        {/* System Design Content */}
        {!isEditingSystemDesign ? (
          <Box>
            {currentCaseDetails.system_design_v1_draft.generated_by && (
              <Typography
                variant="caption"
                color="text.secondary"
                sx={{ mb: 2, display: 'block' }}
              >
                Generated by:{' '}
                {currentCaseDetails.system_design_v1_draft.generated_by} |
                Version: {currentCaseDetails.system_design_v1_draft.version}
              </Typography>
            )}
            <ReactMarkdown>
              {currentCaseDetails.system_design_v1_draft.content_markdown}
            </ReactMarkdown>
          </Box>
        ) : (
          <Box>
            <TextField
              multiline
              fullWidth
              rows={20}
              value={editableSystemDesignContent}
              onChange={(e) => setEditableSystemDesignContent(e.target.value)}
              variant="outlined"
              placeholder="Enter system design content here..."
              sx={{ mb: 2 }}
            />
            <Stack direction="row" spacing={2} justifyContent="flex-end">
              <Button
                variant="outlined"
                startIcon={<CancelIcon />}
                onClick={handleCancelEditSystemDesign}
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={handleSaveSystemDesign}
                disabled={isLoading}
              >
                {isLoading ? 'Saving...' : 'Save Changes'}
              </Button>
            </Stack>
          </Box>
        )}
      </Paper>

      {/* System Design Rejection Dialog */}
      <Dialog
        open={isSystemDesignRejectDialogOpen}
        onClose={handleCloseSystemDesignRejectDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Reject System Design</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Rejection Reason (Optional)"
            fullWidth
            multiline
            rows={4}
            value={systemDesignRejectionReason}
            onChange={(e) => setSystemDesignRejectionReason(e.target.value)}
            placeholder="Please provide a reason for rejecting this System Design..."
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseSystemDesignRejectDialog}>Cancel</Button>
          <Button
            onClick={handleRejectSystemDesign}
            color="error"
            variant="contained"
          >
            Reject System Design
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
