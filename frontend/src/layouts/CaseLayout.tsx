import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Outlet } from 'react-router-dom';
import {
  Container,
  Typography,
  CircularProgress,
  Alert,
  Box,
  Stack,
  IconButton,
  Button,
  Tooltip,
  Paper,
  Grid,
  Chip,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  PictureAsPdf as PdfIcon,
  Refresh as RefreshIcon,
  Share as ShareIcon,
} from '@mui/icons-material';
import { useAgentContext } from '../hooks/useAgentContext';
import useDocumentTitle from '../hooks/useDocumentTitle';
import CaseNavigation from '../components/case/CaseNavigation';
import ProgressStepper from '../components/common/ProgressStepper';
import { PAPER_ELEVATION, STANDARD_STYLES } from '../styles/constants';
import Logger from '../utils/logger';

const logger = Logger.create('CaseLayout');

const CaseLayout: React.FC = () => {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();
  const {
    currentCaseDetails,
    isLoadingCaseDetails,
    caseDetailsError,
    fetchCaseDetails,
    clearCurrentCaseDetails,
    exportCaseToPdf,
  } = useAgentContext();

  const [isExportingPdf, setIsExportingPdf] = useState(false);

  // Get status color for the chip
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

  // Set document title dynamically based on case title
  useDocumentTitle(
    currentCaseDetails?.title || `Case ${caseId?.substring(0, 8)}...` || 'Business Case',
    currentCaseDetails?.title
  );

  // Helper function to determine if case is shareable
  const isShareable = (status: string) => {
    return status === 'APPROVED' || status === 'PENDING_FINAL_APPROVAL';
  };

  const handleGenerateShareableLink = () => {
    if (!caseId) return;
    
    // Generate the shareable link URL
    const shareableUrl = `${window.location.origin}/cases/${caseId}/view`;
    
    // Copy to clipboard
    navigator.clipboard.writeText(shareableUrl).then(() => {
      // You could add a toast notification here
      alert('Shareable link copied to clipboard!');
    }).catch((err) => {
      logger.error('Failed to copy link:', err);
      // Fallback: show the link in a prompt
      prompt('Copy this shareable link:', shareableUrl);
    });
  };

  const handleExportToPdf = async () => {
    if (!currentCaseDetails || !caseId) return;
    
    setIsExportingPdf(true);
    try {
      await exportCaseToPdf(caseId);
    } catch (error) {
      logger.error('Error exporting PDF:', error);
    } finally {
      setIsExportingPdf(false);
    }
  };

  // Fetch case details when component mounts or caseId changes
  useEffect(() => {
    if (caseId) {
      fetchCaseDetails(caseId);
    }

    // Cleanup when component unmounts or caseId changes
    return () => {
      clearCurrentCaseDetails();
    };
  }, [caseId, fetchCaseDetails, clearCurrentCaseDetails]);

  // Loading state
  if (isLoadingCaseDetails && !currentCaseDetails) {
    return (
      <Container component="main" maxWidth="lg" sx={STANDARD_STYLES.pageContainer}>
        <CircularProgress sx={{ display: 'block', margin: 'auto', mt: 5 }} />
      </Container>
    );
  }

  // Error state
  if (caseDetailsError) {
    return (
      <Container component="main" maxWidth="lg" sx={STANDARD_STYLES.pageContainer}>
        <Alert severity="error" sx={{ mt: 3 }}>
          {caseDetailsError.message || 'Failed to load business case details.'}
        </Alert>
      </Container>
    );
  }

  // Not found state
  if (!currentCaseDetails) {
    return (
      <Container component="main" maxWidth="lg" sx={STANDARD_STYLES.pageContainer}>
        <Alert severity="warning" sx={{ mt: 3 }}>
          Business case not found.
        </Alert>
      </Container>
    );
  }

  return (
    <Container component="main" maxWidth="lg" sx={STANDARD_STYLES.pageContainer}>
      <Box>
        {/* Header */}
        <Stack
          direction="row"
          justifyContent="space-between"
          alignItems="center"
          mb={3}
        >
          <Stack direction="row" alignItems="center" spacing={2}>
            <IconButton onClick={() => navigate('/dashboard')}>
              <ArrowBackIcon />
            </IconButton>
            <Box>
              <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 0 }}>
                {currentCaseDetails.title}
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Status: {currentCaseDetails.status} | Updated:{' '}
                {new Date(currentCaseDetails.updated_at).toLocaleDateString()}
              </Typography>
            </Box>
          </Stack>
          <Stack direction="row" spacing={1}>
            {isShareable(currentCaseDetails.status) && (
              <Tooltip title="Generate Shareable Link">
                <Button
                  variant="outlined"
                  startIcon={<ShareIcon />}
                  onClick={handleGenerateShareableLink}
                  sx={{ minWidth: 140 }}
                >
                  Share Link
                </Button>
              </Tooltip>
            )}
            <Tooltip title="Export to PDF">
              <Button
                variant="contained"
                startIcon={<PdfIcon />}
                onClick={handleExportToPdf}
                disabled={isExportingPdf}
                sx={{ minWidth: 120 }}
              >
                {isExportingPdf ? 'Exporting...' : 'Export PDF'}
              </Button>
            </Tooltip>
            <Tooltip title="Refresh">
              <IconButton 
                onClick={() => caseId && fetchCaseDetails(caseId)}
                disabled={isLoadingCaseDetails}
              >
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          </Stack>
        </Stack>

        {/* Executive Summary */}
        <Paper elevation={PAPER_ELEVATION.MAIN_CONTENT} sx={{ ...STANDARD_STYLES.mainContentPaper, mb: 3 }}>
          <Typography variant="h5" component="h2" gutterBottom>
            Executive Summary
          </Typography>

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

        {/* Progress Stepper */}
        <ProgressStepper currentCaseStatus={currentCaseDetails.status} />

        {/* Navigation */}
        {caseId && <CaseNavigation caseId={caseId} />}

        {/* Content outlet for sub-pages */}
        <Outlet />
      </Box>
    </Container>
  );
};

export default CaseLayout; 