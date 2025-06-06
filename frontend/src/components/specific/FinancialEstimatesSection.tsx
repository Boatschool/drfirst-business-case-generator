import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
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
  Business as BusinessIcon,
  AttachMoney as MoneyIcon,
  TrendingUp as TrendingUpIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as RejectIcon,
} from '@mui/icons-material';
import { useAgentContext } from '../../hooks/useAgentContext';
import { useAuth } from '../../hooks/useAuth';
import { BusinessCaseDetails } from '../../services/agent/AgentService';
import { toAppError } from '../../types/api';

interface FinancialEstimatesSectionProps {
  currentCaseDetails: BusinessCaseDetails;
  isLoading: boolean;
}

export const FinancialEstimatesSection: React.FC<FinancialEstimatesSectionProps> = ({
  currentCaseDetails,
  isLoading,
}) => {
  const { currentUser, systemRole } = useAuth();
  const {
    approveEffortEstimate,
    rejectEffortEstimate,
    approveCostEstimate,
    rejectCostEstimate,
    approveValueProjection,
    rejectValueProjection,
    submitEffortEstimateForReview,
    submitCostEstimateForReview,
    submitValueProjectionForReview,
  } = useAgentContext();

  // Rejection dialog states
  const [isEffortRejectDialogOpen, setIsEffortRejectDialogOpen] = useState(false);
  const [isCostRejectDialogOpen, setIsCostRejectDialogOpen] = useState(false);
  const [isValueRejectDialogOpen, setIsValueRejectDialogOpen] = useState(false);
  const [effortRejectionReason, setEffortRejectionReason] = useState('');
  const [costRejectionReason, setCostRejectionReason] = useState('');
  const [valueRejectionReason, setValueRejectionReason] = useState('');

  // Alert states
  const [approvalSuccess, setApprovalSuccess] = useState<string | null>(null);
  const [approvalError, setApprovalError] = useState<string | null>(null);

  // Permission helpers
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
    return isInitiator && currentCaseDetails.status === 'EFFORT_PENDING_REVIEW';
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
    return isInitiator && currentCaseDetails.status === 'COSTING_PENDING_REVIEW';
  };

  const canSubmitValueProjection = () => {
    if (!currentCaseDetails || !currentUser) return false;
    const isInitiator = currentCaseDetails.user_id === currentUser.uid;
    const allowedStatuses = ['VALUE_ANALYSIS_COMPLETE', 'VALUE_REJECTED'];
    return (
      isInitiator &&
      allowedStatuses.includes(currentCaseDetails.status) &&
      currentCaseDetails.value_projection_v1
    );
  };

  const canApproveRejectValueProjection = () => {
    if (!currentCaseDetails || !currentUser) return false;
    const isInitiator = currentCaseDetails.user_id === currentUser.uid;
    const isSalesManagerApprover = systemRole === 'SALES_MANAGER_APPROVER';
    return (
      (isInitiator || isSalesManagerApprover) &&
      currentCaseDetails.status === 'VALUE_PENDING_REVIEW'
    );
  };

  // Handlers
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
        effortRejectionReason || undefined
      );
      if (success) {
        setApprovalSuccess('Effort Estimate rejected successfully!');
        setIsEffortRejectDialogOpen(false);
        setEffortRejectionReason('');
      }
    } catch (error) {
      setApprovalError(toAppError(error, 'api').message || 'Failed to reject effort estimate.');
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
        costRejectionReason || undefined
      );
      if (success) {
        setApprovalSuccess('Cost Estimate rejected successfully!');
        setIsCostRejectDialogOpen(false);
        setCostRejectionReason('');
      }
    } catch (error) {
      setApprovalError(toAppError(error, 'api').message || 'Failed to reject cost estimate.');
    }
  };

  const handleSubmitValueProjection = async () => {
    if (!currentCaseDetails.case_id) return;
    try {
      const success = await submitValueProjectionForReview(currentCaseDetails.case_id);
      if (success) {
        setApprovalSuccess('Value Projection submitted for review successfully!');
        setApprovalError(null);
      }
    } catch (error) {
      setApprovalError(toAppError(error, 'api').message || 'Failed to submit value projection for review.');
    }
  };

  const handleApproveValueProjection = async () => {
    if (!currentCaseDetails.case_id) return;
    try {
      const success = await approveValueProjection(currentCaseDetails.case_id);
      if (success) {
        setApprovalSuccess('Value Projection approved successfully!');
        setApprovalError(null);
      }
    } catch (error) {
      setApprovalError(toAppError(error, 'api').message || 'Failed to approve value projection.');
    }
  };

  const handleRejectValueProjection = async () => {
    if (!currentCaseDetails.case_id) return;
    try {
      const success = await rejectValueProjection(
        currentCaseDetails.case_id,
        valueRejectionReason || undefined
      );
      if (success) {
        setApprovalSuccess('Value Projection rejected successfully!');
        setIsValueRejectDialogOpen(false);
        setValueRejectionReason('');
      }
    } catch (error) {
      setApprovalError(toAppError(error, 'api').message || 'Failed to reject value projection.');
    }
  };

  const { effort_estimate_v1, cost_estimate_v1, value_projection_v1 } = currentCaseDetails;

  if (!effort_estimate_v1 && !cost_estimate_v1 && !value_projection_v1) {
    return (
      <Box sx={{ mb: 4 }}>
        <Paper elevation={2} sx={{ p: 3 }}>
          <Typography variant="h5" component="h2" gutterBottom>
            Financial Estimates
          </Typography>
          <Alert severity="info" sx={{ mt: 2 }}>
            Financial estimates have not been generated yet. Once the system design is approved, effort and cost estimates will be automatically generated.
          </Alert>
        </Paper>
      </Box>
    );
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

      {/* Effort Estimate Section */}
      {effort_estimate_v1 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
              <Stack direction="row" alignItems="center" spacing={1}>
                <BusinessIcon color="primary" />
                <Typography variant="h6" component="h3">💼 Effort Estimate</Typography>
              </Stack>
              <Stack direction="row" spacing={1}>
                {canSubmitEffortEstimate() && (
                  <Button
                    variant="contained"
                    size="small"
                    color="primary"
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
                      Approve Effort
                    </Button>
                    <Button
                      variant="outlined"
                      size="small"
                      color="error"
                      startIcon={<RejectIcon />}
                      onClick={() => setIsEffortRejectDialogOpen(true)}
                      disabled={isLoading}
                    >
                      Reject Effort
                    </Button>
                  </>
                )}
              </Stack>
            </Stack>

            <TableContainer component={Paper} variant="outlined" sx={{ mb: 2 }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell><strong>Role</strong></TableCell>
                    <TableCell align="right"><strong>Hours</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {effort_estimate_v1.roles.map((roleData, index) => (
                    <TableRow key={index}>
                      <TableCell>{roleData.role}</TableCell>
                      <TableCell align="right">{roleData.hours}</TableCell>
                    </TableRow>
                  ))}
                  <TableRow>
                    <TableCell><strong>Total</strong></TableCell>
                    <TableCell align="right"><strong>{effort_estimate_v1.total_hours}</strong></TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>

            <Typography variant="body2" color="text.secondary">
              Duration: {effort_estimate_v1.estimated_duration_weeks} weeks • 
              Complexity: {effort_estimate_v1.complexity_assessment}
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Cost Estimate Section */}
      {cost_estimate_v1 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
              <Stack direction="row" alignItems="center" spacing={1}>
                <MoneyIcon color="primary" />
                <Typography variant="h6" component="h3">💰 Cost Estimate</Typography>
              </Stack>
              <Stack direction="row" spacing={1}>
                {canSubmitCostEstimate() && (
                  <Button
                    variant="contained"
                    size="small"
                    color="primary"
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
                      Approve Cost
                    </Button>
                    <Button
                      variant="outlined"
                      size="small"
                      color="error"
                      startIcon={<RejectIcon />}
                      onClick={() => setIsCostRejectDialogOpen(true)}
                      disabled={isLoading}
                    >
                      Reject Cost
                    </Button>
                  </>
                )}
              </Stack>
            </Stack>

            <TableContainer component={Paper} variant="outlined" sx={{ mb: 2 }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell><strong>Role</strong></TableCell>
                    <TableCell align="right"><strong>Rate/Hour</strong></TableCell>
                    <TableCell align="right"><strong>Hours</strong></TableCell>
                    <TableCell align="right"><strong>Cost</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {cost_estimate_v1.breakdown_by_role.map((roleData, index) => (
                    <TableRow key={index}>
                      <TableCell>{roleData.role}</TableCell>
                      <TableCell align="right">${roleData.hourly_rate}</TableCell>
                      <TableCell align="right">{roleData.hours}</TableCell>
                      <TableCell align="right">${roleData.total_cost.toLocaleString()}</TableCell>
                    </TableRow>
                  ))}
                  <TableRow>
                    <TableCell colSpan={3}><strong>Total Cost</strong></TableCell>
                    <TableCell align="right"><strong>${cost_estimate_v1.estimated_cost.toLocaleString()}</strong></TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>

            <Typography variant="body2" color="text.secondary">
              Rate Card: {cost_estimate_v1.rate_card_used}
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Value Projection Section */}
      {value_projection_v1 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
              <Stack direction="row" alignItems="center" spacing={1}>
                <TrendingUpIcon color="primary" />
                <Typography variant="h6" component="h3">📈 Value Projection</Typography>
              </Stack>
              <Stack direction="row" spacing={1}>
                {canSubmitValueProjection() && (
                  <Button
                    variant="contained"
                    size="small"
                    color="primary"
                    onClick={handleSubmitValueProjection}
                    disabled={isLoading}
                  >
                    Submit for Review
                  </Button>
                )}
                {canApproveRejectValueProjection() && (
                  <>
                    <Button
                      variant="contained"
                      size="small"
                      color="success"
                      startIcon={<CheckCircleIcon />}
                      onClick={handleApproveValueProjection}
                      disabled={isLoading}
                    >
                      Approve Value
                    </Button>
                    <Button
                      variant="outlined"
                      size="small"
                      color="error"
                      startIcon={<RejectIcon />}
                      onClick={() => setIsValueRejectDialogOpen(true)}
                      disabled={isLoading}
                    >
                      Reject Value
                    </Button>
                  </>
                )}
              </Stack>
            </Stack>

            <TableContainer component={Paper} variant="outlined" sx={{ mb: 2 }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell><strong>Scenario</strong></TableCell>
                    <TableCell align="right"><strong>Value</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {value_projection_v1.scenarios.map((scenario, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        <Chip 
                          label={scenario.case} 
                          color={
                            scenario.case === 'Low' ? 'warning' :
                            scenario.case === 'Base' ? 'primary' :
                            scenario.case === 'High' ? 'success' : 'default'
                          } 
                          size="small" 
                          sx={{ mr: 1 }} 
                        />
                        {scenario.description || scenario.case}
                      </TableCell>
                      <TableCell align="right">${scenario.value.toLocaleString()}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

            <Typography variant="body2" color="text.secondary">
              Template: {value_projection_v1.template_used || 'Not specified'}
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Rejection Dialogs */}
      <Dialog open={isEffortRejectDialogOpen} onClose={() => setIsEffortRejectDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Reject Effort Estimate</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Please provide a reason for rejecting this Effort Estimate (optional):
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={3}
            value={effortRejectionReason}
            onChange={(e) => setEffortRejectionReason(e.target.value)}
            placeholder="Enter reason for rejection..."
            variant="outlined"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsEffortRejectDialogOpen(false)} disabled={isLoading}>Cancel</Button>
          <Button onClick={handleRejectEffortEstimate} color="error" variant="contained" disabled={isLoading}>
            {isLoading ? 'Rejecting...' : 'Reject Effort Estimate'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={isCostRejectDialogOpen} onClose={() => setIsCostRejectDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Reject Cost Estimate</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Please provide a reason for rejecting this Cost Estimate (optional):
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={3}
            value={costRejectionReason}
            onChange={(e) => setCostRejectionReason(e.target.value)}
            placeholder="Enter reason for rejection..."
            variant="outlined"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsCostRejectDialogOpen(false)} disabled={isLoading}>Cancel</Button>
          <Button onClick={handleRejectCostEstimate} color="error" variant="contained" disabled={isLoading}>
            {isLoading ? 'Rejecting...' : 'Reject Cost Estimate'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={isValueRejectDialogOpen} onClose={() => setIsValueRejectDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Reject Value Projection</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Please provide a reason for rejecting this Value Projection (optional):
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={3}
            value={valueRejectionReason}
            onChange={(e) => setValueRejectionReason(e.target.value)}
            placeholder="Enter reason for rejection..."
            variant="outlined"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsValueRejectDialogOpen(false)} disabled={isLoading}>Cancel</Button>
          <Button onClick={handleRejectValueProjection} color="error" variant="contained" disabled={isLoading}>
            {isLoading ? 'Rejecting...' : 'Reject Value Projection'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}; 