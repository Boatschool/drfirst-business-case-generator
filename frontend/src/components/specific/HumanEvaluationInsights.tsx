import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TableSortLabel,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Chip,
  Rating,
  CircularProgress,
  Alert,
  TextField,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Visibility as VisibilityIcon,
  Person as PersonIcon,
  Assessment as AssessmentIcon,
  TrendingUp as TrendingUpIcon,
  DateRange as DateRangeIcon,
} from '@mui/icons-material';
import {
  evaluationService,
  HumanEvalSummaryData,
  HumanEvalResultDetail,
  HumanEvalListParams,
  PaginatedHumanEvalData,
} from '../../services/EvaluationService';

const HumanEvaluationInsights: React.FC = () => {
  // State for summary data
  const [summaryData, setSummaryData] = useState<HumanEvalSummaryData | null>(null);
  const [summaryLoading, setSummaryLoading] = useState(true);
  const [summaryError, setSummaryError] = useState<string | null>(null);

  // State for results table
  const [resultsData, setResultsData] = useState<PaginatedHumanEvalData | null>(null);
  const [resultsLoading, setResultsLoading] = useState(true);
  const [resultsError, setResultsError] = useState<string | null>(null);

  // State for detailed view modal
  const [selectedResult, setSelectedResult] = useState<HumanEvalResultDetail | null>(null);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);

  // Table/pagination state
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [sortBy, setSortBy] = useState('evaluation_date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // Filter state
  const [agentNameFilter, setAgentNameFilter] = useState('');
  const [evaluatorIdFilter, setEvaluatorIdFilter] = useState('');

  // Load data on mount and when filters/pagination change
  const loadSummaryData = useCallback(async () => {
    try {
      setSummaryLoading(true);
      setSummaryError(null);
      const data = await evaluationService.getHumanEvalDashboardSummary();
      setSummaryData(data);
    } catch (error) {
      setSummaryError(error instanceof Error ? error.message : 'Failed to load summary data');
    } finally {
      setSummaryLoading(false);
    }
  }, []);

  const loadResultsData = useCallback(async () => {
    try {
      setResultsLoading(true);
      setResultsError(null);
      const params: HumanEvalListParams = {
        page: page + 1, // API expects 1-based page
        limit: rowsPerPage,
        sortBy,
        order: sortOrder,
        agent_name: agentNameFilter || undefined,
        evaluator_id: evaluatorIdFilter || undefined,
      };
      const data = await evaluationService.listHumanEvaluationResults(params);
      setResultsData(data);
    } catch (error) {
      setResultsError(error instanceof Error ? error.message : 'Failed to load results data');
    } finally {
      setResultsLoading(false);
    }
  }, [page, rowsPerPage, sortBy, sortOrder, agentNameFilter, evaluatorIdFilter]);

  useEffect(() => {
    loadSummaryData();
  }, [loadSummaryData]);

  useEffect(() => {
    loadResultsData();
  }, [loadResultsData]);

  const handleSort = (property: string) => {
    const isAsc = sortBy === property && sortOrder === 'asc';
    setSortOrder(isAsc ? 'desc' : 'asc');
    setSortBy(property);
  };

  const handlePageChange = (_: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleViewDetails = async (submissionId: string) => {
    try {
      setDetailLoading(true);
      setDetailModalOpen(true);
      const details = await evaluationService.getHumanEvaluationResultDetails(submissionId);
      setSelectedResult(details);
    } catch (error) {
      console.error('Error loading result details:', error);
      setDetailModalOpen(false);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleCloseDetailModal = () => {
    setDetailModalOpen(false);
    setSelectedResult(null);
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return dateString;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 4) return 'success';
    if (score >= 3) return 'warning';
    return 'error';
  };

  const renderSummaryCards = () => {
    if (summaryLoading) {
      return (
        <Box display="flex" justifyContent="center" py={4}>
          <CircularProgress />
        </Box>
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
              <Box display="flex" alignItems="center" mb={1}>
                <AssessmentIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6" color="primary">
                  Total Evaluations
                </Typography>
              </Box>
              <Typography variant="h3" fontWeight="bold">
                {summaryData.total_evaluations}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <PersonIcon color="secondary" sx={{ mr: 1 }} />
                <Typography variant="h6" color="secondary">
                  Unique Evaluators
                </Typography>
              </Box>
              <Typography variant="h3" fontWeight="bold">
                {summaryData.unique_evaluators}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <TrendingUpIcon color="success" sx={{ mr: 1 }} />
                <Typography variant="h6" color="success.main">
                  Average Score
                </Typography>
              </Box>
              <Box display="flex" alignItems="center">
                <Typography variant="h3" fontWeight="bold" sx={{ mr: 1 }}>
                  {summaryData.average_overall_score.toFixed(1)}
                </Typography>
                <Rating value={summaryData.average_overall_score} precision={0.1} readOnly />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <DateRangeIcon color="info" sx={{ mr: 1 }} />
                <Typography variant="h6" color="info.main">
                  Latest Evaluation
                </Typography>
              </Box>
              <Typography variant="h6" fontWeight="bold">
                {summaryData.latest_evaluation_date 
                  ? formatDate(summaryData.latest_evaluation_date)
                  : 'N/A'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Score Distribution */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Score Distribution
              </Typography>
              <Grid container spacing={1}>
                {Object.entries(summaryData.score_distribution).map(([score, count]) => (
                  <Grid item key={score}>
                    <Chip 
                      label={`${score}: ${count}`} 
                      color={getScoreColor(parseInt(score))}
                      variant="outlined"
                    />
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Evaluations by Agent */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Evaluations by Agent
              </Typography>
              <Grid container spacing={1}>
                {Object.entries(summaryData.evaluations_by_agent).map(([agent, count]) => (
                  <Grid item key={agent}>
                    <Chip 
                      label={`${agent}: ${count}`} 
                      color="primary"
                      variant="outlined"
                    />
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  const renderResultsTable = () => {
    if (resultsLoading) {
      return (
        <Box display="flex" justifyContent="center" py={4}>
          <CircularProgress />
        </Box>
      );
    }

    if (resultsError) {
      return (
        <Alert severity="error" sx={{ mb: 3 }}>
          {resultsError}
        </Alert>
      );
    }

    if (!resultsData) return null;

    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Human Evaluation Results
          </Typography>

          {/* Filters */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={4}>
              <TextField
                fullWidth
                label="Filter by Agent"
                value={agentNameFilter}
                onChange={(e) => setAgentNameFilter(e.target.value)}
                placeholder="Enter agent name..."
              />
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <TextField
                fullWidth
                label="Filter by Evaluator ID"
                value={evaluatorIdFilter}
                onChange={(e) => setEvaluatorIdFilter(e.target.value)}
                placeholder="Enter evaluator ID..."
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <Button 
                variant="outlined" 
                onClick={() => {
                  setAgentNameFilter('');
                  setEvaluatorIdFilter('');
                }}
                fullWidth
              >
                Clear Filters
              </Button>
            </Grid>
          </Grid>

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>
                    <TableSortLabel
                      active={sortBy === 'submission_id'}
                      direction={sortBy === 'submission_id' ? sortOrder : 'asc'}
                      onClick={() => handleSort('submission_id')}
                    >
                      Submission ID
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={sortBy === 'evaluation_date'}
                      direction={sortBy === 'evaluation_date' ? sortOrder : 'asc'}
                      onClick={() => handleSort('evaluation_date')}
                    >
                      Date
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={sortBy === 'agent_name'}
                      direction={sortBy === 'agent_name' ? sortOrder : 'asc'}
                      onClick={() => handleSort('agent_name')}
                    >
                      Agent
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>Evaluator</TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={sortBy === 'overall_quality_score'}
                      direction={sortBy === 'overall_quality_score' ? sortOrder : 'asc'}
                      onClick={() => handleSort('overall_quality_score')}
                    >
                      Score
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>Golden Dataset ID</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {resultsData.evaluations.map((result) => (
                  <TableRow key={result.submission_id}>
                    <TableCell>
                      <Typography variant="body2" fontFamily="monospace">
                        {result.submission_id.substring(0, 20)}...
                      </Typography>
                    </TableCell>
                    <TableCell>{formatDate(result.evaluation_date)}</TableCell>
                    <TableCell>
                      <Chip label={result.agent_name} size="small" />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {result.evaluator_email}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center">
                        <Typography variant="body2" sx={{ mr: 1 }}>
                          {result.overall_quality_score}
                        </Typography>
                        <Rating value={result.overall_quality_score} size="small" readOnly />
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontFamily="monospace">
                        {result.golden_dataset_inputId}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Button
                        size="small"
                        startIcon={<VisibilityIcon />}
                        onClick={() => handleViewDetails(result.submission_id)}
                      >
                        View
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
            count={resultsData.total_count}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handlePageChange}
            onRowsPerPageChange={handleRowsPerPageChange}
          />
        </CardContent>
      </Card>
    );
  };

  const renderDetailModal = () => {
    return (
      <Dialog 
        open={detailModalOpen} 
        onClose={handleCloseDetailModal} 
        maxWidth="md" 
        fullWidth
      >
        <DialogTitle>
          Human Evaluation Details
        </DialogTitle>
        <DialogContent>
          {detailLoading ? (
            <Box display="flex" justifyContent="center" py={4}>
              <CircularProgress />
            </Box>
          ) : selectedResult ? (
            <Box>
              {/* Basic Info */}
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Submission ID
                  </Typography>
                  <Typography variant="body2" fontFamily="monospace">
                    {selectedResult.submission_id}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Evaluation Date
                  </Typography>
                  <Typography variant="body2">
                    {formatDate(selectedResult.evaluation_date)}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Agent
                  </Typography>
                  <Chip label={selectedResult.agent_name} size="small" />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Evaluator
                  </Typography>
                  <Typography variant="body2">
                    {selectedResult.evaluator_email}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Golden Dataset ID
                  </Typography>
                  <Typography variant="body2" fontFamily="monospace">
                    {selectedResult.golden_dataset_inputId}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Overall Score
                  </Typography>
                  <Box display="flex" alignItems="center">
                    <Typography variant="h6" sx={{ mr: 1 }}>
                      {selectedResult.overall_quality_score}
                    </Typography>
                    <Rating value={selectedResult.overall_quality_score} readOnly />
                  </Box>
                </Grid>
              </Grid>

              <Divider sx={{ my: 2 }} />

              {/* Overall Comments */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Overall Comments
                </Typography>
                <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                  <Typography variant="body2">
                    {selectedResult.overall_comments || 'No overall comments provided.'}
                  </Typography>
                </Paper>
              </Box>

              {/* Metric Scores and Comments */}
              <Typography variant="subtitle1" gutterBottom>
                Metric Evaluations
              </Typography>
              {Object.entries(selectedResult.metric_scores_and_comments).map(([metric, data]) => (
                <Accordion key={metric} sx={{ mb: 1 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Box display="flex" alignItems="center" width="100%">
                      <Typography variant="subtitle2" sx={{ flexGrow: 1 }}>
                        {metric.replace(/_/g, ' ')}
                      </Typography>
                      <Box display="flex" alignItems="center" mr={2}>
                        <Typography variant="body2" sx={{ mr: 1 }}>
                          Score: {data.score}
                        </Typography>
                        <Rating value={data.score} size="small" readOnly />
                      </Box>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography variant="body2">
                      {data.comment || 'No comments provided for this metric.'}
                    </Typography>
                  </AccordionDetails>
                </Accordion>
              ))}
            </Box>
          ) : (
            <Typography>No details available</Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDetailModal}>Close</Button>
        </DialogActions>
      </Dialog>
    );
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Human Evaluation Insights
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        View summary metrics and detailed results from human evaluations.
      </Typography>

      {renderSummaryCards()}
      {renderResultsTable()}
      {renderDetailModal()}
    </Box>
  );
};

export default HumanEvaluationInsights; 