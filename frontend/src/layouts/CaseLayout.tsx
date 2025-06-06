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
import { STANDARD_STYLES } from '../styles/constants';
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

        {/* Navigation */}
        {caseId && <CaseNavigation caseId={caseId} />}

        {/* Content outlet for sub-pages */}
        <Outlet />
      </Box>
    </Container>
  );
};

export default CaseLayout; 