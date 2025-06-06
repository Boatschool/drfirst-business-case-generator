import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  Alert,
  Chip,
  Stack,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Cancel as RejectIcon,
  PictureAsPdf as PdfIcon,
  Share as ShareIcon,
  TrendingUp as TrendingUpIcon,
  AttachMoney as MoneyIcon,
  Schedule as ScheduleIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { useAgentContext } from '../../hooks/useAgentContext';
import { useAuth } from '../../hooks/useAuth';
import { PAPER_ELEVATION, STANDARD_STYLES } from '../../styles/constants';

const SummaryPage: React.FC = () => {
  const { 
    currentCaseDetails, 
    isLoading,
    submitCaseForFinalApproval,
    approveFinalCase,
    rejectFinalCase,
    exportCaseToPdf
  } = useAgentContext();
  const { currentUser, systemRole } = useAuth();

  // State for final approval/rejection
  const [isRejectDialogOpen, setIsRejectDialogOpen] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');
  const [isExporting, setIsExporting] = useState(false);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  if (!currentCaseDetails) {
    return (
      <Alert severity="warning">
        Case details not available.
      </Alert>
    );
  }

  // Permission helpers
  const canSubmitForFinalApproval = () => {
    if (!currentUser) return false;
    const isInitiator = currentCaseDetails.user_id === currentUser.uid;
    return isInitiator && currentCaseDetails.status === 'FINANCIAL_MODEL_COMPLETE';
  };

  const canApproveFinalCase = () => {
    if (!currentUser) return false;
    const isFinalApprover = systemRole === 'FINAL_APPROVER' || systemRole === 'ADMIN';
    return isFinalApprover && currentCaseDetails.status === 'PENDING_FINAL_APPROVAL';
  };

  // Get status color
  const getStatusColor = (status: string) => {
    const statusColors: Record<string, 'success' | 'warning' | 'info' | 'error' | 'default'> = {
      'APPROVED': 'success',
      'PENDING_FINAL_APPROVAL': 'warning',
      'REJECTED': 'error',
      'FINANCIAL_MODEL_COMPLETE': 'info',
      'PRD_APPROVED': 'success',
      'SYSTEM_DESIGN_APPROVED': 'success',
    };
    return statusColors[status] || 'default';
  };

  // Format currency
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  // Handle actions
  const handleSubmitForFinalApproval = async () => {
    if (!currentCaseDetails.case_id) return;
    try {
      const success = await submitCaseForFinalApproval(currentCaseDetails.case_id);
      if (success) {
        setActionSuccess('Case submitted for final approval successfully!');
        setActionError(null);
      }
    } catch (err) {
      setActionError('Failed to submit case for final approval.');
      setActionSuccess(null);
    }
  };

  const handleApproveFinalCase = async () => {
    if (!currentCaseDetails.case_id) return;
    try {
      const success = await approveFinalCase(currentCaseDetails.case_id);
      if (success) {
        setActionSuccess('Business case approved successfully!');
        setActionError(null);
      }
    } catch (err) {
      setActionError('Failed to approve business case.');
      setActionSuccess(null);
    }
  };

  const handleRejectFinalCase = async () => {
    if (!currentCaseDetails.case_id) return;
    try {
      const success = await rejectFinalCase(
        currentCaseDetails.case_id,
        rejectionReason || undefined
      );
      if (success) {
        setActionSuccess('Business case rejected.');
        setIsRejectDialogOpen(false);
        setRejectionReason('');
        setActionError(null);
      }
    } catch (err) {
      setActionError('Failed to reject business case.');
      setActionSuccess(null);
    }
  };

  const handleExportToPdf = async () => {
    if (!currentCaseDetails.case_id) return;
    setIsExporting(true);
    try {
      await exportCaseToPdf(currentCaseDetails.case_id);
    } catch (err) {
      setActionError('Failed to export PDF.');
    } finally {
      setIsExporting(false);
    }
  };

  const handleGenerateShareableLink = () => {
    const shareableUrl = `${window.location.origin}/cases/${currentCaseDetails.case_id}/view`;
    navigator.clipboard.writeText(shareableUrl).then(() => {
      setActionSuccess('Shareable link copied to clipboard!');
    }).catch(() => {
      setActionError('Failed to copy shareable link.');
    });
  };

  return (
    <Box>
      {/* Success/Error Messages */}
      {actionSuccess && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setActionSuccess(null)}>
          {actionSuccess}
        </Alert>
      )}
      {actionError && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setActionError(null)}>
          {actionError}
        </Alert>
      )}

      {/* Header with Actions */}
      <Paper elevation={PAPER_ELEVATION.MAIN_CONTENT} sx={{ ...STANDARD_STYLES.mainContentPaper, mb: 3 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h5" component="h1">
            Executive Summary
          </Typography>
          <Stack direction="row" spacing={1}>
            <Button
              variant="outlined"
              startIcon={<PdfIcon />}
              onClick={handleExportToPdf}
              disabled={isExporting}
            >
              {isExporting ? 'Exporting...' : 'Export PDF'}
            </Button>
            {(currentCaseDetails.status === 'APPROVED' || currentCaseDetails.status === 'PENDING_FINAL_APPROVAL') && (
              <Button
                variant="outlined"
                startIcon={<ShareIcon />}
                onClick={handleGenerateShareableLink}
              >
                Share Link
              </Button>
            )}
          </Stack>
        </Stack>

        {/* Case Overview */}
        <Grid container spacing={2} mb={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
              Case Status
            </Typography>
            <Chip 
              label={currentCaseDetails.status.replace(/_/g, ' ')} 
              color={getStatusColor(currentCaseDetails.status)}
              size="medium"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
              Last Updated
            </Typography>
            <Typography variant="body1">
              {new Date(currentCaseDetails.updated_at).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </Typography>
          </Grid>
        </Grid>

        {/* Problem Statement */}
        <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
          Problem Statement
        </Typography>
        <Typography variant="body1" paragraph>
          {currentCaseDetails.problem_statement}
        </Typography>
      </Paper>

      {/* Key Metrics */}
      <Grid container spacing={3} mb={3}>
        {/* Financial Summary */}
        {currentCaseDetails.financial_summary_v1 && (
          <Grid item xs={12} md={6}>
            <Card elevation={PAPER_ELEVATION.MAIN_CONTENT}>
              <CardContent>
                <Stack direction="row" alignItems="center" spacing={1} mb={2}>
                  <MoneyIcon color="primary" />
                  <Typography variant="h6">Financial Summary</Typography>
                </Stack>
                <TableContainer>
                  <Table size="small">
                    <TableBody>
                      <TableRow>
                        <TableCell><strong>Total Cost</strong></TableCell>
                        <TableCell align="right">
                          {formatCurrency(currentCaseDetails.financial_summary_v1.total_estimated_cost)}
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>Expected Value (Base)</strong></TableCell>
                        <TableCell align="right">
                          {currentCaseDetails.financial_summary_v1.value_scenarios?.Base ? 
                            formatCurrency(currentCaseDetails.financial_summary_v1.value_scenarios.Base) : 'N/A'}
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>Net Value</strong></TableCell>
                        <TableCell align="right">
                          {formatCurrency(currentCaseDetails.financial_summary_v1.financial_metrics.primary_net_value)}
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>ROI</strong></TableCell>
                        <TableCell align="right">
                          {currentCaseDetails.financial_summary_v1.financial_metrics.primary_roi_percentage}
                          {typeof currentCaseDetails.financial_summary_v1.financial_metrics.primary_roi_percentage === 'number' ? '%' : ''}
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Effort Summary */}
        {currentCaseDetails.effort_estimate_v1 && (
          <Grid item xs={12} md={6}>
            <Card elevation={PAPER_ELEVATION.MAIN_CONTENT}>
              <CardContent>
                <Stack direction="row" alignItems="center" spacing={1} mb={2}>
                  <ScheduleIcon color="primary" />
                  <Typography variant="h6">Effort Summary</Typography>
                </Stack>
                <TableContainer>
                  <Table size="small">
                    <TableBody>
                      <TableRow>
                        <TableCell><strong>Total Hours</strong></TableCell>
                        <TableCell align="right">{currentCaseDetails.effort_estimate_v1.total_hours}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>Duration</strong></TableCell>
                        <TableCell align="right">{currentCaseDetails.effort_estimate_v1.estimated_duration_weeks} weeks</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>Complexity</strong></TableCell>
                        <TableCell align="right">
                          <Chip 
                            label={currentCaseDetails.effort_estimate_v1.complexity_assessment} 
                            size="small"
                            color={currentCaseDetails.effort_estimate_v1.complexity_assessment === 'High' ? 'warning' : 'default'}
                          />
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>Team Roles</strong></TableCell>
                        <TableCell align="right">{currentCaseDetails.effort_estimate_v1.roles.length}</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>

      {/* Progress Overview */}
      <Paper elevation={PAPER_ELEVATION.MAIN_CONTENT} sx={{ ...STANDARD_STYLES.mainContentPaper, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Project Progress
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Stack alignItems="center" spacing={1}>
              <AssessmentIcon color={currentCaseDetails.prd_draft ? 'success' : 'disabled'} />
              <Typography variant="body2" align="center">
                PRD {currentCaseDetails.prd_draft ? 'Complete' : 'Pending'}
              </Typography>
            </Stack>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Stack alignItems="center" spacing={1}>
              <AssessmentIcon color={currentCaseDetails.system_design_v1_draft ? 'success' : 'disabled'} />
              <Typography variant="body2" align="center">
                System Design {currentCaseDetails.system_design_v1_draft ? 'Complete' : 'Pending'}
              </Typography>
            </Stack>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Stack alignItems="center" spacing={1}>
              <TrendingUpIcon color={currentCaseDetails.effort_estimate_v1 ? 'success' : 'disabled'} />
              <Typography variant="body2" align="center">
                Effort Estimate {currentCaseDetails.effort_estimate_v1 ? 'Complete' : 'Pending'}
              </Typography>
            </Stack>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Stack alignItems="center" spacing={1}>
              <MoneyIcon color={currentCaseDetails.financial_summary_v1 ? 'success' : 'disabled'} />
              <Typography variant="body2" align="center">
                Financial Model {currentCaseDetails.financial_summary_v1 ? 'Complete' : 'Pending'}
              </Typography>
            </Stack>
          </Grid>
        </Grid>
      </Paper>

      {/* Action Buttons */}
      <Paper elevation={PAPER_ELEVATION.MAIN_CONTENT} sx={STANDARD_STYLES.mainContentPaper}>
        <Typography variant="h6" gutterBottom>
          Actions
        </Typography>
        <Divider sx={{ mb: 2 }} />
        
        <Stack direction="row" spacing={2} flexWrap="wrap">
          {canSubmitForFinalApproval() && (
            <Button
              variant="contained"
              color="primary"
              startIcon={<CheckCircleIcon />}
              onClick={handleSubmitForFinalApproval}
              disabled={isLoading}
            >
              Submit for Final Approval
            </Button>
          )}
          
          {canApproveFinalCase() && (
            <>
              <Button
                variant="contained"
                color="success"
                startIcon={<CheckCircleIcon />}
                onClick={handleApproveFinalCase}
                disabled={isLoading}
              >
                Approve Business Case
              </Button>
              <Button
                variant="outlined"
                color="error"
                startIcon={<RejectIcon />}
                onClick={() => setIsRejectDialogOpen(true)}
                disabled={isLoading}
              >
                Reject Business Case
              </Button>
            </>
          )}
        </Stack>
      </Paper>

      {/* Rejection Dialog */}
      <Dialog
        open={isRejectDialogOpen}
        onClose={() => setIsRejectDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Reject Business Case</DialogTitle>
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
            placeholder="Please provide a reason for rejecting this business case..."
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsRejectDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleRejectFinalCase} color="error" variant="contained">
            Reject Business Case
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SummaryPage; 