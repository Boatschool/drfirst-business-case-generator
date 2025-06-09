import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  TablePagination,
  CircularProgress,
  Alert,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Container,
  Tooltip,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Close as CloseIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
  CheckCircle as CheckCircleIcon,
  DataUsage as DataUsageIcon,
  PlayArrow as PlayArrowIcon,
} from '@mui/icons-material';
import {
  evaluationService,
  DashboardSummaryData,
  PaginatedRunListData,
  RunDetailsData,
  RunListParams,
  FailedValidationEntry,
} from '../../../services/EvaluationService';
import HumanEvaluationInsights from '../../../components/specific/HumanEvaluationInsights';

interface SortState {
  field: string;
  direction: 'asc' | 'desc';
}

const AutomatedEvalDashboardPage: React.FC = () => {
  // State for summary data
  const [summaryData, setSummaryData] = useState<DashboardSummaryData | null>(null);
  const [summaryLoading, setSummaryLoading] = useState(true);
  const [summaryError, setSummaryError] = useState<string | null>(null);

  // State for runs list
  const [runsData, setRunsData] = useState<PaginatedRunListData | null>(null);
  const [runsLoading, setRunsLoading] = useState(true);
  const [runsError, setRunsError] = useState<string | null>(null);

  // State for detailed view
  const [selectedRunDetails, setSelectedRunDetails] = useState<RunDetailsData | null>(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [detailsError, setDetailsError] = useState<string | null>(null);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);

  // State for evaluation execution
  const [evaluationRunning, setEvaluationRunning] = useState(false);
  const [evaluationError, setEvaluationError] = useState<string | null>(null);

  // Pagination and sorting state
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [sortState, setSortState] = useState<SortState>({
    field: 'run_timestamp_start',
    direction: 'desc'
  });

  const loadSummaryData = useCallback(async () => {
    try {
      setSummaryLoading(true);
      setSummaryError(null);
      const data = await evaluationService.getDashboardSummary();
      setSummaryData(data);
    } catch (err) {
      setSummaryError(err instanceof Error ? err.message : 'Failed to load summary data');
    } finally {
      setSummaryLoading(false);
    }
  }, []);

  const loadRunsData = useCallback(async () => {
    try {
      setRunsLoading(true);
      setRunsError(null);
      
      const params: RunListParams = {
        page: page + 1, // Convert to 1-based
        limit: rowsPerPage,
        sortBy: sortState.field,
        order: sortState.direction
      };
      
      const data = await evaluationService.listEvaluationRuns(params);
      setRunsData(data);
    } catch (err) {
      setRunsError(err instanceof Error ? err.message : 'Failed to load runs data');
    } finally {
      setRunsLoading(false);
    }
  }, [page, rowsPerPage, sortState]);

  const loadDashboardData = useCallback(async () => {
    await Promise.all([
      loadSummaryData(),
      loadRunsData()
    ]);
  }, [loadSummaryData, loadRunsData]);

  // Load dashboard data on component mount
  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  // Load runs data when pagination/sorting changes
  useEffect(() => {
    loadRunsData();
  }, [loadRunsData]);

  const handleRunClick = async (evalRunId: string) => {
    try {
      setDetailsLoading(true);
      setDetailsError(null);
      setDetailsDialogOpen(true);
      
      const details = await evaluationService.getEvaluationRunDetails(evalRunId);
      setSelectedRunDetails(details);
    } catch (err) {
      setDetailsError(err instanceof Error ? err.message : 'Failed to load run details');
    } finally {
      setDetailsLoading(false);
    }
  };

  const handleSort = (field: string) => {
    setSortState(prev => ({
      field,
      direction: prev.field === field && prev.direction === 'desc' ? 'asc' : 'desc'
    }));
  };

  const handlePageChange = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleCloseDetailsDialog = () => {
    setDetailsDialogOpen(false);
    setSelectedRunDetails(null);
    setDetailsError(null);
  };

  const handleRunEvaluation = async () => {
    try {
      setEvaluationRunning(true);
      setEvaluationError(null);
      
      // Get Firebase auth token
      const auth = (await import('firebase/auth')).getAuth();
      const user = auth.currentUser;
      
      if (!user) {
        throw new Error('User not authenticated');
      }

      const token = await user.getIdToken();
      
      const response = await fetch('/api/v1/evaluations/dashboard/evaluations/runs/trigger', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to trigger evaluation: ${response.statusText}`);
      }

      const result = await response.json();
      
      // Start polling for updates (we'll implement this next)
      await pollEvaluationStatus(result.job_id);
      
      // Refresh dashboard data after completion
      await loadDashboardData();
      
    } catch (err) {
      setEvaluationError(err instanceof Error ? err.message : 'Failed to run evaluation');
    } finally {
      setEvaluationRunning(false);
    }
  };

  const pollEvaluationStatus = async (jobId: string) => {
    // Simple polling implementation - check every 5 seconds
    return new Promise((resolve) => {
      const pollInterval = setInterval(async () => {
        try {
          // Get Firebase auth token for status polling
          const auth = (await import('firebase/auth')).getAuth();
          const user = auth.currentUser;
          
          if (!user) {
            clearInterval(pollInterval);
            resolve({ completed: true, error: 'User not authenticated' });
            return;
          }

          const token = await user.getIdToken();
          
          const response = await fetch(`/api/v1/evaluations/dashboard/evaluations/runs/status/${jobId}`, {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });
          
          if (response.ok) {
            const status = await response.json();
            if (status.completed) {
              clearInterval(pollInterval);
              resolve(status);
            }
          }
        } catch (error) {
          console.error('Error polling evaluation status:', error);
        }
      }, 5000);

      // Set maximum polling time to 10 minutes
      setTimeout(() => {
        clearInterval(pollInterval);
        resolve({ completed: true, timeout: true });
      }, 600000);
    });
  };

  const formatTimestamp = (timestamp: string) => {
    if (!timestamp) return 'N/A';
    return new Date(timestamp).toLocaleString();
  };

  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const getStatusColor = (rate: number) => {
    if (rate >= 90) return 'success';
    if (rate >= 70) return 'warning';
    return 'error';
  };

  const renderSummaryCards = () => {
    if (summaryLoading) {
      return (
        <Grid container spacing={3}>
          {[1, 2, 3, 4].map((i) => (
            <Grid item xs={12} sm={6} md={3} key={i}>
              <Card>
                <CardContent>
                  <CircularProgress size={24} />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      );
    }

    if (summaryError) {
      return (
        <Alert severity="error" sx={{ mb: 3 }}>
          {summaryError}
        </Alert>
      );
    }

    if (!summaryData) return null;

    return (
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color="primary">
                    {summaryData.total_runs}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Evaluation Runs
                  </Typography>
                </Box>
                <AssessmentIcon color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color="primary">
                    {summaryData.total_examples_processed}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Examples Processed
                  </Typography>
                </Box>
                <DataUsageIcon color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color={getStatusColor(summaryData.overall_avg_success_rate)}>
                    {summaryData.overall_avg_success_rate.toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Avg Success Rate
                  </Typography>
                </Box>
                <TrendingUpIcon color={getStatusColor(summaryData.overall_avg_success_rate)} sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color={getStatusColor(summaryData.overall_avg_validation_pass_rate)}>
                    {summaryData.overall_avg_validation_pass_rate.toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Avg Validation Pass Rate
                  </Typography>
                </Box>
                <CheckCircleIcon color={getStatusColor(summaryData.overall_avg_validation_pass_rate)} sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  const renderRunsTable = () => {
    if (runsLoading) {
      return (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      );
    }

    if (runsError) {
      return (
        <Alert severity="error" sx={{ mb: 3 }}>
          {runsError}
        </Alert>
      );
    }

    if (!runsData || runsData.runs.length === 0) {
      return (
        <Alert severity="info" sx={{ mb: 3 }}>
          No evaluation runs found. Run some automated evaluations to see data here.
        </Alert>
      );
    }

    return (
      <Paper sx={{ width: '100%', mb: 2 }}>
        <TableContainer>
          <Table stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell>
                  <TableSortLabel
                    active={sortState.field === 'run_timestamp_start'}
                    direction={sortState.field === 'run_timestamp_start' ? sortState.direction : 'asc'}
                    onClick={() => handleSort('run_timestamp_start')}
                  >
                    Run Start Time
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={sortState.field === 'total_examples_processed'}
                    direction={sortState.field === 'total_examples_processed' ? sortState.direction : 'asc'}
                    onClick={() => handleSort('total_examples_processed')}
                  >
                    Examples
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={sortState.field === 'success_rate_percentage'}
                    direction={sortState.field === 'success_rate_percentage' ? sortState.direction : 'asc'}
                    onClick={() => handleSort('success_rate_percentage')}
                  >
                    Success Rate
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={sortState.field === 'validation_pass_rate_percentage'}
                    direction={sortState.field === 'validation_pass_rate_percentage' ? sortState.direction : 'asc'}
                    onClick={() => handleSort('validation_pass_rate_percentage')}
                  >
                    Validation Rate
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={sortState.field === 'total_evaluation_time_seconds'}
                    direction={sortState.field === 'total_evaluation_time_seconds' ? sortState.direction : 'asc'}
                    onClick={() => handleSort('total_evaluation_time_seconds')}
                  >
                    Duration
                  </TableSortLabel>
                </TableCell>
                <TableCell>Dataset</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {runsData.runs.map((run) => (
                <TableRow key={run.eval_run_id} hover>
                  <TableCell>{formatTimestamp(run.run_timestamp_start)}</TableCell>
                  <TableCell>{run.total_examples_processed}</TableCell>
                  <TableCell>
                    <Chip
                      label={`${run.success_rate_percentage.toFixed(1)}%`}
                      color={getStatusColor(run.success_rate_percentage)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={`${run.validation_pass_rate_percentage.toFixed(1)}%`}
                      color={getStatusColor(run.validation_pass_rate_percentage)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{formatDuration(run.total_evaluation_time_seconds)}</TableCell>
                  <TableCell>
                    <Tooltip title={run.dataset_file_used}>
                      <Typography variant="body2" noWrap sx={{ maxWidth: 150 }}>
                        {run.dataset_file_used}
                      </Typography>
                    </Tooltip>
                  </TableCell>
                  <TableCell>
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() => handleRunClick(run.eval_run_id)}
                    >
                      View Details
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={runsData.total_count}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handlePageChange}
          onRowsPerPageChange={handleRowsPerPageChange}
        />
      </Paper>
    );
  };

  const renderFailedValidationsTable = (failedValidations: FailedValidationEntry[]) => {
    if (failedValidations.length === 0) {
      return (
        <Alert severity="success">
          🎉 All validations passed in this run!
        </Alert>
      );
    }

    return (
      <TableContainer component={Paper} sx={{ mt: 2 }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Input ID</TableCell>
              <TableCell>Agent</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Failed Metrics</TableCell>
              <TableCell>Error Message</TableCell>
              <TableCell>Time (ms)</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {failedValidations.map((entry, index) => (
              <TableRow key={index}>
                <TableCell>{entry.golden_dataset_inputId}</TableCell>
                <TableCell>{entry.agent_name}</TableCell>
                <TableCell>
                  <Chip
                    label={entry.agent_run_status}
                    color={entry.agent_run_status === 'SUCCESS' ? 'success' : 'error'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Box>
                    {Object.entries(entry.validation_results).map(([metric, passed]) => (
                      !passed && (
                        <Chip
                          key={metric}
                          label={metric}
                          color="error"
                          size="small"
                          sx={{ mr: 0.5, mb: 0.5 }}
                        />
                      )
                    ))}
                  </Box>
                </TableCell>
                <TableCell>
                  <Typography variant="body2" sx={{ maxWidth: 200, wordBreak: 'break-word' }}>
                    {entry.agent_error_message || 'No error message'}
                  </Typography>
                </TableCell>
                <TableCell>{entry.execution_time_ms}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  const renderDetailsDialog = () => {
    return (
      <Dialog
        open={detailsDialogOpen}
        onClose={handleCloseDetailsDialog}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">
              Evaluation Run Details
            </Typography>
            <IconButton onClick={handleCloseDetailsDialog}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          {detailsLoading && (
            <Box display="flex" justifyContent="center" p={4}>
              <CircularProgress />
            </Box>
          )}

          {detailsError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {detailsError}
            </Alert>
          )}

          {selectedRunDetails && (
            <Box>
              {/* Run Summary */}
              <Typography variant="h6" gutterBottom>
                Run Summary
              </Typography>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Basic Information
                    </Typography>
                    <Typography variant="body2">
                      <strong>Run ID:</strong> {selectedRunDetails.run_summary.eval_run_id}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Start Time:</strong> {formatTimestamp(selectedRunDetails.run_summary.run_timestamp_start)}
                    </Typography>
                    <Typography variant="body2">
                      <strong>End Time:</strong> {formatTimestamp(selectedRunDetails.run_summary.run_timestamp_end)}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Duration:</strong> {formatDuration(selectedRunDetails.run_summary.total_evaluation_time_seconds)}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Dataset:</strong> {selectedRunDetails.run_summary.dataset_file_used}
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Results
                    </Typography>
                    <Typography variant="body2">
                      <strong>Total Examples:</strong> {selectedRunDetails.run_summary.total_examples_processed}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Successful Runs:</strong> {selectedRunDetails.run_summary.successful_agent_runs}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Failed Runs:</strong> {selectedRunDetails.run_summary.failed_agent_runs}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Validation Passed:</strong> {selectedRunDetails.run_summary.overall_validation_passed_count}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Success Rate:</strong> {selectedRunDetails.run_summary.success_rate_percentage.toFixed(1)}%
                    </Typography>
                    <Typography variant="body2">
                      <strong>Validation Rate:</strong> {selectedRunDetails.run_summary.validation_pass_rate_percentage.toFixed(1)}%
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>

              {/* Agent-Specific Statistics */}
              <Typography variant="h6" gutterBottom>
                Agent-Specific Statistics
              </Typography>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
                {Object.entries(selectedRunDetails.agent_specific_statistics).map(([agentName, stats]: [string, any]) => (
                  <Grid item xs={12} md={6} lg={4} key={agentName}>
                    <Paper sx={{ p: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        {agentName}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Total:</strong> {stats.total}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Successful:</strong> {stats.successful_runs}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Validation Passed:</strong> {stats.validation_passed}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Avg Time:</strong> {stats.avg_execution_time_ms}ms
                      </Typography>
                      <Box sx={{ mt: 1 }}>
                        <Chip
                          label={`${((stats.successful_runs / stats.total) * 100).toFixed(1)}% Success`}
                          color={getStatusColor((stats.successful_runs / stats.total) * 100)}
                          size="small"
                        />
                      </Box>
                    </Paper>
                  </Grid>
                ))}
              </Grid>

              {/* Failed Validations */}
              <Typography variant="h6" gutterBottom>
                Failed Validations ({selectedRunDetails.failed_validations_count})
              </Typography>
              {renderFailedValidationsTable(selectedRunDetails.failed_validations)}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDetailsDialog}>Close</Button>
        </DialogActions>
      </Dialog>
    );
  };

  return (
    <Container maxWidth="lg">
      <Box py={3}>
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4" gutterBottom>
            Evaluation Dashboard
          </Typography>
          <Box display="flex" gap={2}>
            <Button
              variant="contained"
              color="primary"
              startIcon={<PlayArrowIcon />}
              onClick={handleRunEvaluation}
              disabled={evaluationRunning || summaryLoading || runsLoading}
            >
              {evaluationRunning ? 'Running Evaluation...' : 'Run New Evaluation'}
            </Button>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={loadDashboardData}
              disabled={summaryLoading || runsLoading || evaluationRunning}
            >
              Refresh
            </Button>
          </Box>
        </Box>

        {/* Evaluation Error Display */}
        {evaluationError && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setEvaluationError(null)}>
            {evaluationError}
          </Alert>
        )}

        {/* Automated Evaluation Section */}
        <Typography variant="h5" gutterBottom sx={{ mt: 2, mb: 3 }}>
          Automated Evaluation Metrics
        </Typography>
        
        {/* Summary Cards */}
        {renderSummaryCards()}

        {/* Runs Table */}
        <Paper sx={{ p: 2, mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            Evaluation Runs
          </Typography>
          {renderRunsTable()}
        </Paper>

        {/* Human Evaluation Section */}
        <HumanEvaluationInsights />

        {/* Details Dialog */}
        {renderDetailsDialog()}
      </Box>
    </Container>
  );
};

export default AutomatedEvalDashboardPage; 