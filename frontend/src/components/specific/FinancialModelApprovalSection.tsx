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
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Cancel as RejectIcon,
  Send as SendIcon,
} from '@mui/icons-material';
import { useAgentContext } from '../../hooks/useAgentContext';
import { useAuth } from '../../hooks/useAuth';
import { useStageApproverConfig } from '../../hooks/useStageApproverConfig';
import { BusinessCaseDetails } from '../../services/agent/AgentService';
import { toAppError } from '../../types/api';

interface FinancialModelApprovalSectionProps {
  currentCaseDetails: BusinessCaseDetails;
  isLoading: boolean;
}

export const FinancialModelApprovalSection: React.FC<FinancialModelApprovalSectionProps> = ({
  currentCaseDetails,
  isLoading,
}) => {
  const { currentUser, systemRole } = useAuth();
  const { canApproveStage } = useStageApproverConfig();
  const {
    submitFinancialModelForReview,
    approveFinancialModel,
    rejectFinancialModel,
  } = useAgentContext();

  // State management
  const [isRejectDialogOpen, setIsRejectDialogOpen] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');
  const [approvalSuccess, setApprovalSuccess] = useState<string | null>(null);
  const [approvalError, setApprovalError] = useState<string | null>(null);

  // Permission helpers
  const canSubmitForReview = () => {
    if (!currentCaseDetails || !currentUser) return false;
    const isInitiator = currentCaseDetails.user_id === currentUser.uid;
    const allowedStatuses = ['FINANCIAL_MODEL_COMPLETE', 'FINANCIAL_MODEL_REJECTED'];
    return (
      isInitiator &&
      allowedStatuses.includes(currentCaseDetails.status) &&
      currentCaseDetails.financial_summary_v1
    );
  };

  const canApproveRejectFinancialModel = () => {
    if (!currentCaseDetails || !currentUser) return false;
    const isInitiator = currentCaseDetails.user_id === currentUser.uid;
    const isApprover = canApproveStage('FinancialModel', systemRole);
    return (
      (isInitiator || isApprover) && 
      currentCaseDetails.status === 'FINANCIAL_MODEL_PENDING_REVIEW'
    );
  };

  // Handlers
  const handleSubmitForReview = async () => {
    if (!currentCaseDetails?.case_id) return;

    try {
      const success = await submitFinancialModelForReview(currentCaseDetails.case_id);
      if (success) {
        setApprovalSuccess('Financial model submitted for review successfully.');
        setApprovalError(null);
      }
    } catch (error) {
      setApprovalError(toAppError(error, 'api').message || 'Failed to submit financial model for review.');
      setApprovalSuccess(null);
    }
  };

  const handleApprove = async () => {
    if (!currentCaseDetails?.case_id) return;

    try {
      const success = await approveFinancialModel(currentCaseDetails.case_id);
      if (success) {
        setApprovalSuccess('Financial model approved successfully.');
        setApprovalError(null);
      }
    } catch (error) {
      setApprovalError(toAppError(error, 'api').message || 'Failed to approve financial model.');
      setApprovalSuccess(null);
    }
  };

  const handleReject = async () => {
    if (!currentCaseDetails?.case_id) return;

    try {
      const success = await rejectFinancialModel(
        currentCaseDetails.case_id,
        rejectionReason || undefined
      );
      if (success) {
        setApprovalSuccess('Financial model rejected successfully.');
        setIsRejectDialogOpen(false);
        setRejectionReason('');
        setApprovalError(null);
      }
    } catch (error) {
      setApprovalError(toAppError(error, 'api').message || 'Failed to reject financial model.');
      setApprovalSuccess(null);
    }
  };

  // Don't show if no financial summary exists
  if (!currentCaseDetails.financial_summary_v1) {
    return null;
  }

  return (
    <Box sx={{ mb: 4 }}>
      {/* Alert Messages */}
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

      <Card>
        <CardContent>
          <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
            <Typography variant="h6" component="h3">
              📊 Financial Model Approval
            </Typography>
            <Stack direction="row" spacing={1}>
              {canSubmitForReview() && (
                <Button
                  variant="contained"
                  size="small"
                  color="primary"
                  startIcon={<SendIcon />}
                  onClick={handleSubmitForReview}
                  disabled={isLoading}
                >
                  Submit for Review
                </Button>
              )}
              {canApproveRejectFinancialModel() && (
                <>
                  <Button
                    variant="contained"
                    size="small"
                    color="success"
                    startIcon={<CheckCircleIcon />}
                    onClick={handleApprove}
                    disabled={isLoading}
                  >
                    Approve Financial Model
                  </Button>
                  <Button
                    variant="outlined"
                    size="small"
                    color="error"
                    startIcon={<RejectIcon />}
                    onClick={() => setIsRejectDialogOpen(true)}
                    disabled={isLoading}
                  >
                    Reject Financial Model
                  </Button>
                </>
              )}
            </Stack>
          </Stack>

          {/* Status Information */}
          {currentCaseDetails.status === 'FINANCIAL_MODEL_COMPLETE' && (
            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="body2">
                💡 The financial model has been generated and is ready for review. 
                Submit it for approval to proceed to final business case approval.
              </Typography>
            </Alert>
          )}

          {currentCaseDetails.status === 'FINANCIAL_MODEL_PENDING_REVIEW' && (
            <Alert severity="warning" sx={{ mb: 2 }}>
              <Typography variant="body2">
                ⏳ The financial model is currently under review. 
                Waiting for approval from authorized reviewers.
              </Typography>
            </Alert>
          )}

          {currentCaseDetails.status === 'FINANCIAL_MODEL_APPROVED' && (
            <Alert severity="success" sx={{ mb: 2 }}>
              <Typography variant="body2">
                ✅ The financial model has been approved. 
                You can now submit the business case for final approval.
              </Typography>
            </Alert>
          )}

          {currentCaseDetails.status === 'FINANCIAL_MODEL_REJECTED' && (
            <Alert severity="error" sx={{ mb: 2 }}>
              <Typography variant="body2">
                ❌ The financial model has been rejected. 
                Please review the feedback and resubmit for review.
              </Typography>
            </Alert>
          )}

          {/* Financial Summary Preview */}
          <Typography variant="body2" color="text.secondary">
            Financial model includes cost analysis, value projections, ROI calculations, 
            and scenario analysis. Review the complete financial summary before approval.
          </Typography>
        </CardContent>
      </Card>

      {/* Rejection Dialog */}
      <Dialog open={isRejectDialogOpen} onClose={() => setIsRejectDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Reject Financial Model</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Please provide a reason for rejecting this financial model (optional):
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
          <Button onClick={() => setIsRejectDialogOpen(false)} disabled={isLoading}>
            Cancel
          </Button>
          <Button onClick={handleReject} color="error" variant="contained" disabled={isLoading}>
            {isLoading ? 'Rejecting...' : 'Reject Financial Model'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}; 