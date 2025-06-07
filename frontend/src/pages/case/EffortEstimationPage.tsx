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
  Schedule as EffortIcon,
  PlayArrow as GenerateIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as RejectIcon,
  Send as SendIcon,
} from '@mui/icons-material';
import { useAgentContext } from '../../hooks/useAgentContext';
import { useAuth } from '../../hooks/useAuth';
import { STANDARD_STYLES, PAPER_ELEVATION } from '../../styles/constants';
import { toAppError } from '../../types/api';

const EffortEstimationPage: React.FC = () => {
  const { currentCaseDetails, isLoading, caseDetailsError } = useAgentContext();
  const { currentUser, systemRole } = useAuth();
  const {
    approveEffortEstimate,
    rejectEffortEstimate,
    submitEffortEstimateForReview,
    triggerEffortEstimateGeneration,
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
        Failed to load effort estimation details. Please try refreshing the page.
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
  const canGenerateEffortEstimate = () => {
    if (!currentCaseDetails || !currentUser) return false;
    const isInitiator = currentCaseDetails.user_id === currentUser.uid;
    const hasApprovedSystemDesign = currentCaseDetails.status.includes('SYSTEM_DESIGN_APPROVED') || 
                                   currentCaseDetails.status.includes('PLANNING');
    return isInitiator && hasApprovedSystemDesign && !currentCaseDetails.effort_estimate_v1;
  };

  const canSubmitEffortEstimate = () => {
    if (!currentCaseDetails || !currentUser) return false;
    const isInitiator = currentCaseDetails.user_id === currentUser.uid;
    const allowedStatuses = ['PLANNING_COMPLETE', 'EFFORT_REJECTED'];
    return (
      isInitiator &&
      allowedStatuses.includes(currentCaseDetails.status) &&
      currentCaseDetails.effort_estimate_v1
    );
  };

  const canApproveRejectEffortEstimate = () => {
    if (!currentCaseDetails || !currentUser) return false;
    const isInitiator = currentCaseDetails.user_id === currentUser.uid;
    const isProjectManager = systemRole === 'PROJECT_MANAGER';
    return (
      (isInitiator || isProjectManager) &&
      currentCaseDetails.status === 'EFFORT_PENDING_REVIEW'
    );
  };

  // Handlers
  const handleGenerateEffortEstimate = async () => {
    if (!currentCaseDetails.case_id) return;
    try {
      setApprovalError(null);
      setApprovalSuccess(null);
      
      const success = await triggerEffortEstimateGeneration(currentCaseDetails.case_id);
      if (success) {
        setApprovalSuccess('Effort estimate generation triggered successfully! The estimate will be generated based on the approved system design.');
      } else {
        setApprovalError('Failed to trigger effort estimate generation. Please try again.');
      }
    } catch (error) {
      const appError = toAppError(error, 'api');
      
      // Provide more specific error message for missing backend endpoints
      if (appError.status === 404) {
        setApprovalError(
          'Backend endpoint not implemented yet. The effort estimate generation feature requires backend development. ' +
          'Please contact the development team to implement the /effort-estimate/generate endpoint.'
        );
      } else if (appError.message?.includes('fetch')) {
        setApprovalError(
          'Network error: Unable to connect to the backend. Please ensure the backend server is running and try again.'
        );
      } else {
        setApprovalError(appError.message || 'Failed to generate effort estimate. Please try again.');
      }
    }
  };

  const handleSubmitEffortEstimate = async () => {
    if (!currentCaseDetails.case_id) return;
    try {
      const success = await submitEffortEstimateForReview(currentCaseDetails.case_id);
      if (success) {
        setApprovalSuccess('Effort Estimate submitted for review successfully!');
        setApprovalError(null);
      }
    } catch (error) {
      setApprovalError(toAppError(error, 'api').message || 'Failed to submit effort estimate for review.');
    }
  };

  const handleApproveEffortEstimate = async () => {
    if (!currentCaseDetails.case_id) return;
    try {
      const success = await approveEffortEstimate(currentCaseDetails.case_id);
      if (success) {
        setApprovalSuccess('Effort Estimate approved successfully!');
        setApprovalError(null);
      }
    } catch (error) {
      setApprovalError(toAppError(error, 'api').message || 'Failed to approve effort estimate.');
    }
  };

  const handleRejectEffortEstimate = async () => {
    if (!currentCaseDetails.case_id) return;
    try {
      const success = await rejectEffortEstimate(
        currentCaseDetails.case_id,
        rejectionReason || undefined
      );
      if (success) {
        setApprovalSuccess('Effort Estimate rejected successfully!');
        setIsRejectDialogOpen(false);
        setRejectionReason('');
        setApprovalError(null);
      }
    } catch (error) {
      setApprovalError(toAppError(error, 'api').message || 'Failed to reject effort estimate.');
    }
  };

  const { effort_estimate_v1 } = currentCaseDetails;

  return (
    <Box>
      <Paper sx={{ ...STANDARD_STYLES.mainContentPaper, mb: 3 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Effort Estimation
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Estimate development effort, timeline, and resource requirements based on the approved system design.
          Define project scope, complexity assessment, and team composition.
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

      {/* No Effort Estimate - Generation UI */}
      {!effort_estimate_v1 && (
        <Paper elevation={PAPER_ELEVATION.MAIN_CONTENT} sx={{ p: 3, mb: 3 }}>
          <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
            <EffortIcon color="primary" />
            <Typography variant="h6">Generate Effort Estimate</Typography>
          </Stack>
          
          {canGenerateEffortEstimate() ? (
            <Box>
              <Typography variant="body1" paragraph>
                The system design has been approved. You can now generate effort estimates for this project.
              </Typography>
              <Button
                variant="contained"
                color="primary"
                startIcon={<GenerateIcon />}
                onClick={handleGenerateEffortEstimate}
                disabled={isLoading}
                size="large"
              >
                Generate Effort Estimate
              </Button>
            </Box>
          ) : (
            <Alert severity="info">
              Effort estimation will be available once the system design is approved.
              Current status: {currentCaseDetails.status.replace(/_/g, ' ')}
            </Alert>
          )}
        </Paper>
      )}

      {/* Effort Estimate Display */}
      {effort_estimate_v1 && (
        <Card elevation={PAPER_ELEVATION.MAIN_CONTENT}>
          <CardContent>
            <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
              <Stack direction="row" alignItems="center" spacing={1}>
                <EffortIcon color="primary" />
                <Typography variant="h6" component="h3">Effort Estimate</Typography>
              </Stack>
              <Stack direction="row" spacing={1}>
                {canSubmitEffortEstimate() && (
                  <Button
                    variant="contained"
                    size="small"
                    color="primary"
                    startIcon={<SendIcon />}
                    onClick={handleSubmitEffortEstimate}
                    disabled={isLoading}
                  >
                    Submit for Review
                  </Button>
                )}
                {canApproveRejectEffortEstimate() && (
                  <>
                    <Button
                      variant="contained"
                      size="small"
                      color="success"
                      startIcon={<CheckCircleIcon />}
                      onClick={handleApproveEffortEstimate}
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
                  {effort_estimate_v1.total_hours}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Hours
                </Typography>
              </Box>
              <Box>
                <Typography variant="h4" color="primary.main" fontWeight="bold">
                  {effort_estimate_v1.estimated_duration_weeks}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Weeks Duration
                </Typography>
              </Box>
              <Box>
                <Chip 
                  label={effort_estimate_v1.complexity_assessment} 
                  color={effort_estimate_v1.complexity_assessment === 'High' ? 'warning' : 'default'}
                  size="medium"
                />
                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                  Complexity
                </Typography>
              </Box>
            </Stack>

            {/* Role Breakdown Table */}
            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell><strong>Role</strong></TableCell>
                    <TableCell align="right"><strong>Hours</strong></TableCell>
                    <TableCell align="right"><strong>Percentage</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {effort_estimate_v1.roles.map((roleData, index) => (
                    <TableRow key={index}>
                      <TableCell>{roleData.role}</TableCell>
                      <TableCell align="right">{roleData.hours}</TableCell>
                      <TableCell align="right">
                        {((roleData.hours / effort_estimate_v1.total_hours) * 100).toFixed(1)}%
                      </TableCell>
                    </TableRow>
                  ))}
                  <TableRow>
                    <TableCell><strong>Total</strong></TableCell>
                    <TableCell align="right"><strong>{effort_estimate_v1.total_hours}</strong></TableCell>
                    <TableCell align="right"><strong>100%</strong></TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>

            {/* Additional Notes */}
            {effort_estimate_v1.notes && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Additional Notes:
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {effort_estimate_v1.notes}
                </Typography>
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
        <DialogTitle>Reject Effort Estimate</DialogTitle>
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
            placeholder="Please provide a reason for rejecting this effort estimate..."
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsRejectDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleRejectEffortEstimate} color="error" variant="contained">
            Reject Estimate
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default EffortEstimationPage; 