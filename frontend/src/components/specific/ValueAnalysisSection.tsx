import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Stack,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Divider,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as RejectIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { BusinessCaseDetails } from '../../services/agent/AgentService';
import { STANDARD_STYLES } from '../../styles/constants';

interface ValueAnalysisSectionProps {
  currentCaseDetails: BusinessCaseDetails;
  isLoading?: boolean;
}

export const ValueAnalysisSection: React.FC<ValueAnalysisSectionProps> = ({
  currentCaseDetails,
  isLoading = false,
}) => {
  const [isApproving, setIsApproving] = useState(false);
  const [isRejecting, setIsRejecting] = useState(false);
  const [isRejectDialogOpen, setIsRejectDialogOpen] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');
  const [apiError, setApiError] = useState<string | null>(null);

  const { value_projection_v1, status } = currentCaseDetails;

  const formatCurrency = (value: number | undefined) => {
    if (value === undefined || value === null || isNaN(value)) {
      return '$0';
    }
    return `$${value.toLocaleString()}`;
  };

  const canSubmitValueProjection = () => {
    return status === 'VALUE_ANALYSIS_COMPLETE' && value_projection_v1;
  };

  const canApproveRejectValueProjection = () => {
    return status === 'VALUE_ANALYSIS_COMPLETE' && value_projection_v1;
  };

  const handleApproveValueProjection = async () => {
    setIsApproving(true);
    setApiError(null);

    try {
      const response = await fetch(`/api/v1/cases/${currentCaseDetails.case_id}/value-projection/approve`, {
        method: 'POST',
        credentials: 'include',
      });

      if (response.ok) {
        const result = await response.json();
        // Refresh the page to show updated status
        window.location.reload();
      } else {
        const errorData = await response.json();
        setApiError(errorData.detail || 'Failed to approve value projection');
      }
    } catch (error) {
      console.error('Error approving value projection:', error);
      setApiError('Network error occurred while approving value projection');
    } finally {
      setIsApproving(false);
    }
  };

  const handleRejectValueProjection = async () => {
    setIsRejecting(true);
    setApiError(null);

    try {
      const response = await fetch(`/api/v1/cases/${currentCaseDetails.case_id}/value-projection/reject`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          reason: rejectionReason || undefined,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setIsRejectDialogOpen(false);
        setRejectionReason('');
        // Refresh the page to show updated status
        window.location.reload();
      } else {
        const errorData = await response.json();
        setApiError(errorData.detail || 'Failed to reject value projection');
      }
    } catch (error) {
      console.error('Error rejecting value projection:', error);
      setApiError('Network error occurred while rejecting value projection');
    } finally {
      setIsRejecting(false);
    }
  };

  const getStatusChip = () => {
    switch (status) {
      case 'VALUE_ANALYSIS_IN_PROGRESS':
        return <Chip label="In Progress" color="warning" size="small" />;
      case 'VALUE_ANALYSIS_COMPLETE':
        return <Chip label="Complete - Pending Review" color="info" size="small" />;
      case 'VALUE_APPROVED':
        return <Chip label="Approved" color="success" size="small" />;
      case 'VALUE_REJECTED':
        return <Chip label="Rejected" color="error" size="small" />;
      default:
        return <Chip label="Not Started" color="default" size="small" />;
    }
  };

  if (!value_projection_v1) {
    return (
      <Box sx={{ mb: 4 }}>
        <Divider sx={{ my: 3 }} />
        
        <Typography
          variant="h5"
          component="h2"
          gutterBottom
          sx={{ display: 'flex', alignItems: 'center', mb: 3 }}
        >
          <TrendingUpIcon sx={{ mr: 1, color: 'primary.main' }} />
          📈 Value Analysis
        </Typography>

        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
              <Typography variant="h6">Value Projection Status</Typography>
              {getStatusChip()}
            </Stack>
            
            <Alert severity="info">
              Value analysis has not been generated yet. This will be available after cost estimation is complete.
            </Alert>
          </CardContent>
        </Card>
      </Box>
    );
  }

  return (
    <Box sx={{ mb: 4 }}>
      <Divider sx={{ my: 3 }} />
      
      <Typography
        variant="h5"
        component="h2"
        gutterBottom
        sx={{ display: 'flex', alignItems: 'center', mb: 3 }}
      >
        <TrendingUpIcon sx={{ mr: 1, color: 'primary.main' }} />
        📈 Value Analysis
      </Typography>

      {apiError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {apiError}
        </Alert>
      )}

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
            <Stack direction="row" alignItems="center" spacing={1}>
              <AssessmentIcon color="primary" />
              <Typography variant="h6" component="h3">Value Projection</Typography>
              {getStatusChip()}
            </Stack>
            
            {canApproveRejectValueProjection() && (
              <Stack direction="row" spacing={1}>
                <Button
                  variant="contained"
                  size="small"
                  color="success"
                  startIcon={<CheckCircleIcon />}
                  onClick={handleApproveValueProjection}
                  disabled={isApproving || isLoading}
                >
                  {isApproving ? <CircularProgress size={16} /> : 'Approve Value'}
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  color="error"
                  startIcon={<RejectIcon />}
                  onClick={() => setIsRejectDialogOpen(true)}
                  disabled={isRejecting || isLoading}
                >
                  Reject Value
                </Button>
              </Stack>
            )}
          </Stack>

          {/* Value Scenarios */}
          <Typography variant="subtitle1" gutterBottom sx={{ mt: 2, fontWeight: 'bold' }}>
            Value Scenarios
          </Typography>
          
          <TableContainer component={Paper} variant="outlined" sx={{ mb: 2 }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell><strong>Scenario</strong></TableCell>
                  <TableCell align="right"><strong>Value</strong></TableCell>
                  <TableCell><strong>Description</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {value_projection_v1.scenarios?.map((scenario, index) => (
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
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" fontWeight="bold">
                        {formatCurrency(scenario.value)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {scenario.description || scenario.case}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Methodology and Assumptions */}
          <Grid container spacing={3} sx={{ mt: 2 }}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom>
                <strong>Methodology:</strong>
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {value_projection_v1.methodology || 'Standard value projection methodology'}
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom>
                <strong>Template Used:</strong>
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {value_projection_v1.template_used || 'Default template'}
              </Typography>
            </Grid>
          </Grid>

          {/* Assumptions */}
          {value_projection_v1.assumptions && value_projection_v1.assumptions.length > 0 && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle2" gutterBottom>
                <strong>Key Assumptions:</strong>
              </Typography>
              <Stack spacing={1}>
                {value_projection_v1.assumptions.map((assumption, index) => (
                  <Typography key={index} variant="body2" color="text.secondary">
                    • {assumption}
                  </Typography>
                ))}
              </Stack>
            </Box>
          )}

          {/* Notes */}
          {value_projection_v1.notes && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle2" gutterBottom>
                <strong>Notes:</strong>
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {value_projection_v1.notes}
              </Typography>
            </Box>
          )}

          {/* Generated by info */}
          <Typography variant="caption" display="block" sx={{ mt: 3, fontStyle: 'italic', color: 'text.secondary' }}>
            Generated by: Sales Value Analyst Agent • 
            Currency: {value_projection_v1.currency || 'USD'}
          </Typography>
        </CardContent>
      </Card>

      {/* Rejection Dialog */}
      <Dialog open={isRejectDialogOpen} onClose={() => setIsRejectDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Reject Value Projection</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" paragraph>
            Please provide a reason for rejecting this value projection (optional):
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={4}
            placeholder="Enter rejection reason..."
            value={rejectionReason}
            onChange={(e) => setRejectionReason(e.target.value)}
            disabled={isRejecting}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsRejectDialogOpen(false)} disabled={isRejecting}>
            Cancel
          </Button>
          <Button
            onClick={handleRejectValueProjection}
            color="error"
            variant="contained"
            disabled={isRejecting}
          >
            {isRejecting ? <CircularProgress size={20} /> : 'Reject'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}; 