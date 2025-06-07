import React, { useState } from 'react';
import { 
  Alert, 
  Typography, 
  Box, 
  Paper, 
  Button,
  Stack,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';
import {
  MonetizationOn as CostIcon,
  PlayArrow as GenerateIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as RejectIcon,
  Send as SendIcon,
} from '@mui/icons-material';
import { useAgentContext } from '../../hooks/useAgentContext';
import { useAuth } from '../../hooks/useAuth';
import { STANDARD_STYLES, PAPER_ELEVATION } from '../../styles/constants';
import { toAppError } from '../../types/api';

const CostAnalysisPage: React.FC = () => {
  const { currentCaseDetails, isLoading, caseDetailsError } = useAgentContext();
  const { currentUser, systemRole } = useAuth();
  const {
    approveCostEstimate,
    rejectCostEstimate,
    submitCostEstimateForReview,
    triggerCostAnalysisGeneration,
  } = useAgentContext();

  // Local state
  const [approvalSuccess, setApprovalSuccess] = useState<string | null>(null);
  const [approvalError, setApprovalError] = useState<string | null>(null);
  const [isRejectDialogOpen, setIsRejectDialogOpen] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');

  // Error state
  if (caseDetailsError) {
    return (
      <Alert severity="error">
        Failed to load cost analysis details. Please try refreshing the page.
      </Alert>
    );
  }

  // No case details available
  if (!currentCaseDetails) {
    return (
      <Alert severity="warning">
        Case details not available. Please ensure you have permission to view this case.
      </Alert>
    );
  }

  // Permission helpers
  const canGenerateCostAnalysis = () => {
    if (!currentCaseDetails || !currentUser) return false;
    const isInitiator = currentCaseDetails.user_id === currentUser.uid;
    const hasApprovedEffortEstimate = currentCaseDetails.status.includes('EFFORT_APPROVED') || 
                                     currentCaseDetails.status.includes('COSTING');
    return isInitiator && hasApprovedEffortEstimate && !currentCaseDetails.cost_estimate_v1;
  };

  const canSubmitCostEstimate = () => {
    if (!currentCaseDetails || !currentUser) return false;
    const isInitiator = currentCaseDetails.user_id === currentUser.uid;
    const allowedStatuses = ['COSTING_COMPLETE', 'COSTING_REJECTED'];
    return (
      isInitiator &&
      allowedStatuses.includes(currentCaseDetails.status) &&
      currentCaseDetails.cost_estimate_v1
    );
  };

  const canApproveRejectCostEstimate = () => {
    if (!currentCaseDetails || !currentUser) return false;
    const isInitiator = currentCaseDetails.user_id === currentUser.uid;
    const isFinanceManager = systemRole === 'FINANCE_MANAGER';
    return (
      (isInitiator || isFinanceManager) &&
      currentCaseDetails.status === 'COSTING_PENDING_REVIEW'
    );
  };

  // Handlers
  const handleGenerateCostAnalysis = async () => {
    if (!currentCaseDetails.case_id) return;
    try {
      setApprovalError(null);
      setApprovalSuccess(null);
      
      const success = await triggerCostAnalysisGeneration(currentCaseDetails.case_id);
      if (success) {
        setApprovalSuccess('Cost analysis generation triggered successfully! The analysis will be generated based on the approved effort estimate.');
      } else {
        setApprovalError('Failed to trigger cost analysis generation. Please try again.');
      }
    } catch (error) {
      const appError = toAppError(error, 'api');
      
      // Provide more specific error message for missing backend endpoints
      if (appError.status === 404) {
        setApprovalError(
          'Backend endpoint not implemented yet. The cost analysis generation feature requires backend development. ' +
          'Please contact the development team to implement the /cost-analysis/generate endpoint.'
        );
      } else if (appError.message?.includes('fetch')) {
        setApprovalError(
          'Network error: Unable to connect to the backend. Please ensure the backend server is running and try again.'
        );
      } else {
        setApprovalError(appError.message || 'Failed to generate cost analysis. Please try again.');
      }
    }
  };

  const handleSubmitCostEstimate = async () => {
    if (!currentCaseDetails.case_id) return;
    try {
      const success = await submitCostEstimateForReview(currentCaseDetails.case_id);
      if (success) {
        setApprovalSuccess('Cost Estimate submitted for review successfully!');
        setApprovalError(null);
      }
    } catch (error) {
      setApprovalError(toAppError(error, 'api').message || 'Failed to submit cost estimate for review.');
    }
  };

  const handleApproveCostEstimate = async () => {
    if (!currentCaseDetails.case_id) return;
    try {
      const success = await approveCostEstimate(currentCaseDetails.case_id);
      if (success) {
        setApprovalSuccess('Cost Estimate approved successfully!');
        setApprovalError(null);
      }
    } catch (error) {
      setApprovalError(toAppError(error, 'api').message || 'Failed to approve cost estimate.');
    }
  };

  const handleRejectCostEstimate = async () => {
    if (!currentCaseDetails.case_id) return;
    try {
      const success = await rejectCostEstimate(
        currentCaseDetails.case_id,
        rejectionReason || undefined
      );
      if (success) {
        setApprovalSuccess('Cost Estimate rejected successfully!');
        setIsRejectDialogOpen(false);
        setRejectionReason('');
        setApprovalError(null);
      }
    } catch (error) {
      setApprovalError(toAppError(error, 'api').message || 'Failed to reject cost estimate.');
    }
  };

  const { cost_estimate_v1 } = currentCaseDetails;

  return (
    <Box>
      <Paper sx={{ ...STANDARD_STYLES.mainContentPaper, mb: 3 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Cost Analysis
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Analyze development and operational costs including personnel, infrastructure, licensing, and ongoing maintenance.
          Calculate total cost of ownership and budget requirements.
        </Typography>
      </Paper>

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

      {/* No Cost Estimate - Generation UI */}
      {!cost_estimate_v1 && (
        <Paper elevation={PAPER_ELEVATION.MAIN_CONTENT} sx={{ p: 3, mb: 3 }}>
          <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
            <CostIcon color="primary" />
            <Typography variant="h6">Generate Cost Analysis</Typography>
          </Stack>
          
          {canGenerateCostAnalysis() ? (
            <Box>
              <Typography variant="body1" paragraph>
                The effort estimate has been approved. You can now generate cost analysis for this project.
              </Typography>
              <Button
                variant="contained"
                color="primary"
                startIcon={<GenerateIcon />}
                onClick={handleGenerateCostAnalysis}
                disabled={isLoading}
                size="large"
              >
                Generate Cost Analysis
              </Button>
            </Box>
          ) : (
            <Alert severity="info">
              Cost analysis will be available once the effort estimate is approved.
              Current status: {currentCaseDetails.status.replace(/_/g, ' ')}
            </Alert>
          )}
        </Paper>
      )}

      {/* Cost Estimate Display */}
      {cost_estimate_v1 && (
        <Card elevation={PAPER_ELEVATION.MAIN_CONTENT}>
          <CardContent>
            <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
              <Stack direction="row" alignItems="center" spacing={1}>
                <CostIcon color="primary" />
                <Typography variant="h6" component="h3">Cost Analysis</Typography>
              </Stack>
              <Stack direction="row" spacing={1}>
                {canSubmitCostEstimate() && (
                  <Button
                    variant="contained"
                    size="small"
                    color="primary"
                    startIcon={<SendIcon />}
                    onClick={handleSubmitCostEstimate}
                    disabled={isLoading}
                  >
                    Submit for Review
                  </Button>
                )}
                {canApproveRejectCostEstimate() && (
                  <>
                    <Button
                      variant="contained"
                      size="small"
                      color="success"
                      startIcon={<CheckCircleIcon />}
                      onClick={handleApproveCostEstimate}
                      disabled={isLoading}
                    >
                      Approve
                    </Button>
                    <Button
                      variant="outlined"
                      size="small"
                      color="error"
                      startIcon={<RejectIcon />}
                      onClick={() => setIsRejectDialogOpen(true)}
                      disabled={isLoading}
                    >
                      Reject
                    </Button>
                  </>
                )}
              </Stack>
            </Stack>

            {/* Summary Metrics */}
            <Stack direction="row" spacing={3} sx={{ mb: 3 }}>
              <Box>
                <Typography variant="h4" color="primary.main" fontWeight="bold">
                  ${cost_estimate_v1.estimated_cost.toLocaleString()}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Cost ({cost_estimate_v1.currency})
                </Typography>
              </Box>
              <Box>
                <Typography variant="h4" color="primary.main" fontWeight="bold">
                  {cost_estimate_v1.breakdown_by_role.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Role Categories
                </Typography>
              </Box>
              <Box>
                <Chip 
                  label={cost_estimate_v1.rate_card_used || 'Standard Rates'} 
                  color="default"
                  size="medium"
                />
                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                  Rate Card Used
                </Typography>
              </Box>
            </Stack>

            {/* Cost Breakdown Table */}
            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell><strong>Role</strong></TableCell>
                    <TableCell align="right"><strong>Hours</strong></TableCell>
                    <TableCell align="right"><strong>Rate/Hour</strong></TableCell>
                    <TableCell align="right"><strong>Total Cost</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {cost_estimate_v1.breakdown_by_role.map((roleData, index) => (
                    <TableRow key={index}>
                      <TableCell>{roleData.role}</TableCell>
                      <TableCell align="right">{roleData.hours}</TableCell>
                      <TableCell align="right">${roleData.hourly_rate}</TableCell>
                      <TableCell align="right">${roleData.total_cost.toLocaleString()}</TableCell>
                    </TableRow>
                  ))}
                  <TableRow>
                    <TableCell colSpan={3}><strong>Total</strong></TableCell>
                    <TableCell align="right"><strong>${cost_estimate_v1.estimated_cost.toLocaleString()}</strong></TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>

            {/* Additional Notes */}
            {cost_estimate_v1.notes && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Additional Notes:
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {cost_estimate_v1.notes}
                </Typography>
              </Box>
            )}

            {/* Warnings */}
            {cost_estimate_v1.warnings && cost_estimate_v1.warnings.length > 0 && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Warnings:
                </Typography>
                {cost_estimate_v1.warnings.map((warning, index) => (
                  <Alert key={index} severity="warning" sx={{ mt: 1 }}>
                    {warning}
                  </Alert>
                ))}
              </Box>
            )}
          </CardContent>
        </Card>
      )}

      {/* Rejection Dialog */}
      <Dialog
        open={isRejectDialogOpen}
        onClose={() => setIsRejectDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Reject Cost Estimate</DialogTitle>
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
            placeholder="Please provide a reason for rejecting this cost estimate..."
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsRejectDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleRejectCostEstimate} color="error" variant="contained">
            Reject Estimate
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CostAnalysisPage; 