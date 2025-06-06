import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Stack,
  Button,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Chip,
  Divider,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Cancel as RejectIcon,
  Send as SendIcon,
} from '@mui/icons-material';
import { useAgentContext } from '../../hooks/useAgentContext';
import { useAuth } from '../../hooks/useAuth';
import { BusinessCaseDetails } from '../../services/agent/AgentService';
import { toAppError } from '../../types/api';

interface FinalApprovalSectionProps {
  currentCaseDetails: BusinessCaseDetails;
  isLoading: boolean;
}

export const FinalApprovalSection: React.FC<FinalApprovalSectionProps> = ({
  currentCaseDetails,
  isLoading,
}) => {
  const { currentUser, systemRole } = useAuth();
  const {
    submitCaseForFinalApproval,
    approveFinalCase,
    rejectFinalCase,
  } = useAgentContext();

  // State management
  const [isFinalRejectDialogOpen, setIsFinalRejectDialogOpen] = useState(false);
  const [finalRejectionReason, setFinalRejectionReason] = useState('');
  const [statusUpdateSuccess, setStatusUpdateSuccess] = useState<string | null>(null);
  const [statusUpdateError, setStatusUpdateError] = useState<string | null>(null);
  const [approvalSuccess, setApprovalSuccess] = useState<string | null>(null);
  const [approvalError, setApprovalError] = useState<string | null>(null);

  // Permission helpers
  const canSubmitForFinalApproval = () => {
    if (!currentCaseDetails || !currentUser) return false;
    const isInitiator = currentCaseDetails.user_id === currentUser.uid;
    return isInitiator && currentCaseDetails.status === 'FINANCIAL_MODEL_COMPLETE';
  };

  const canApproveRejectFinalCase = () => {
    if (!currentCaseDetails || !currentUser) return false;
    const isFinalApprover = systemRole === 'FINAL_APPROVER';
    return isFinalApprover && currentCaseDetails.status === 'PENDING_FINAL_APPROVAL';
  };

  // Handlers
  const handleSubmitForFinalApproval = async () => {
    if (!currentCaseDetails?.case_id) return;

    try {
      const success = await submitCaseForFinalApproval(currentCaseDetails.case_id);
      if (success) {
        setStatusUpdateSuccess('Business case submitted for final approval successfully.');
        setStatusUpdateError(null);
      }
    } catch (error) {
      setStatusUpdateError(toAppError(error, 'api').message || 'Failed to submit for final approval.');
      setStatusUpdateSuccess(null);
    }
  };

  const handleApproveFinalCase = async () => {
    if (!currentCaseDetails?.case_id) return;

    try {
      const success = await approveFinalCase(currentCaseDetails.case_id);
      if (success) {
        setApprovalSuccess('Business case approved successfully.');
        setApprovalError(null);
      }
    } catch (error) {
      setApprovalError(toAppError(error, 'api').message || 'Failed to approve business case.');
      setApprovalSuccess(null);
    }
  };

  const handleRejectFinalCase = async () => {
    if (!currentCaseDetails?.case_id) return;

    try {
      const success = await rejectFinalCase(currentCaseDetails.case_id, finalRejectionReason);
      if (success) {
        setApprovalSuccess('Business case rejected successfully.');
        setApprovalError(null);
        setIsFinalRejectDialogOpen(false);
        setFinalRejectionReason('');
      }
    } catch (error) {
      setApprovalError(toAppError(error, 'api').message || 'Failed to reject business case.');
      setApprovalSuccess(null);
    }
  };

  const handleOpenFinalRejectDialog = () => {
    setIsFinalRejectDialogOpen(true);
    setFinalRejectionReason('');
  };

  const handleCloseFinalRejectDialog = () => {
    setIsFinalRejectDialogOpen(false);
    setFinalRejectionReason('');
  };

  // Show section if any final approval action is relevant
  const shouldShowSection = canSubmitForFinalApproval() || 
                          canApproveRejectFinalCase() || 
                          currentCaseDetails.status === 'PENDING_FINAL_APPROVAL' ||
                          currentCaseDetails.status === 'APPROVED' ||
                          currentCaseDetails.status === 'REJECTED';

  if (!shouldShowSection) {
    return null;
  }

  return (
    <>
      <Divider sx={{ my: 3 }} />
      <Box mb={3}>
        <Typography
          variant="h5"
          component="h2"
          gutterBottom
          sx={{ display: 'flex', alignItems: 'center', mb: 3 }}
        >
          <CheckCircleIcon
            sx={{
              mr: 1,
              color:
                currentCaseDetails.status === 'APPROVED'
                  ? 'success.main'
                  : currentCaseDetails.status === 'REJECTED'
                  ? 'error.main'
                  : 'primary.main',
            }}
          />
          Final Business Case Approval
        </Typography>

        {/* Alert Messages */}
        {statusUpdateSuccess && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setStatusUpdateSuccess(null)}>
            {statusUpdateSuccess}
          </Alert>
        )}
        {statusUpdateError && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setStatusUpdateError(null)}>
            {statusUpdateError}
          </Alert>
        )}
        {approvalSuccess && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setApprovalSuccess(null)}>
            {approvalSuccess}
          </Alert>
        )}
        {approvalError && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setApprovalError(null)}>
            {approvalError}
          </Alert>
        )}

        {/* Status Display */}
        {(currentCaseDetails.status === 'PENDING_FINAL_APPROVAL' ||
          currentCaseDetails.status === 'APPROVED' ||
          currentCaseDetails.status === 'REJECTED') && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Stack spacing={2}>
                <Box>
                  <Typography variant="h6" component="h3" gutterBottom>
                    Current Status:
                    <Chip
                      label={
                        currentCaseDetails.status === 'PENDING_FINAL_APPROVAL'
                          ? 'Pending Final Approval'
                          : currentCaseDetails.status === 'APPROVED'
                          ? 'Approved'
                          : currentCaseDetails.status === 'REJECTED'
                          ? 'Rejected'
                          : currentCaseDetails.status
                      }
                      color={
                        currentCaseDetails.status === 'APPROVED'
                          ? 'success'
                          : currentCaseDetails.status === 'REJECTED'
                          ? 'error'
                          : 'warning'
                      }
                      sx={{ ml: 1 }}
                    />
                  </Typography>
                </Box>

                {currentCaseDetails.status === 'APPROVED' && (
                  <Alert severity="success">
                    <Typography variant="body1">
                      🎉 <strong>Congratulations!</strong> This business case has been approved and is ready for implementation.
                    </Typography>
                  </Alert>
                )}

                {currentCaseDetails.status === 'REJECTED' && (
                  <Alert severity="error">
                    <Typography variant="body1">
                      ❌ This business case has been rejected. Please review the feedback and consider revisions.
                    </Typography>
                  </Alert>
                )}

                {currentCaseDetails.status === 'PENDING_FINAL_APPROVAL' && (
                  <Alert severity="info">
                    <Typography variant="body1">
                      ⏳ This business case is awaiting final approval from authorized reviewers.
                    </Typography>
                  </Alert>
                )}
              </Stack>
            </CardContent>
          </Card>
        )}

        {/* Submit for Final Approval */}
        {canSubmitForFinalApproval() && (
          <Box sx={{ mt: 3, pt: 2, borderTop: '1px solid #eee' }}>
            <Typography variant="h6" component="h3" gutterBottom>
              Ready for Final Approval
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              All prerequisite components (PRD, System Design, and Financial Model) have been completed. 
              You can now submit this business case for final approval.
            </Typography>
            <Stack direction="row" spacing={2} alignItems="center">
              <Button
                variant="contained"
                color="primary"
                onClick={handleSubmitForFinalApproval}
                disabled={isLoading}
                startIcon={<SendIcon />}
                size="large"
              >
                Submit for Final Approval
              </Button>
            </Stack>
          </Box>
        )}

        {/* Final Approval Actions (for FINAL_APPROVER role) */}
        {canApproveRejectFinalCase() && (
          <Box sx={{ mt: 3, pt: 2, borderTop: '1px solid #eee' }}>
            <Typography variant="h6" component="h3" gutterBottom>
              Final Approval Actions
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              As a final approver, you can approve or reject this complete business case.
            </Typography>
            <Stack direction="row" spacing={2} alignItems="center">
              <Button
                variant="contained"
                color="success"
                onClick={handleApproveFinalCase}
                disabled={isLoading}
                startIcon={<CheckCircleIcon />}
                size="large"
              >
                Approve Final Business Case
              </Button>
              <Button
                variant="outlined"
                color="error"
                onClick={handleOpenFinalRejectDialog}
                disabled={isLoading}
                startIcon={<RejectIcon />}
                size="large"
              >
                Reject Final Business Case
              </Button>
            </Stack>
          </Box>
        )}
      </Box>

      {/* Final Business Case Rejection Dialog */}
      <Dialog
        open={isFinalRejectDialogOpen}
        onClose={handleCloseFinalRejectDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Reject Final Business Case</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Please provide a reason for rejecting this business case (optional):
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={3}
            value={finalRejectionReason}
            onChange={(e) => setFinalRejectionReason(e.target.value)}
            placeholder="Enter reason for rejection..."
            variant="outlined"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseFinalRejectDialog} disabled={isLoading}>
            Cancel
          </Button>
          <Button
            onClick={handleRejectFinalCase}
            color="error"
            variant="contained"
            disabled={isLoading}
          >
            {isLoading ? 'Rejecting...' : 'Reject Business Case'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}; 