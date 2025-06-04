import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  CircularProgress,
  Alert,
  Box,
  IconButton,
  Button,
  Stack,
  Tooltip,
} from '@mui/material';
import { 
  ArrowBack as ArrowBackIcon,
  PictureAsPdf as PdfIcon,
  Refresh as RefreshIcon,
  Share as ShareIcon
} from '@mui/icons-material';
import { useAgentContext } from '../contexts/AgentContext';

import { PRDSection } from '../components/specific/PRDSection';
import { SystemDesignSection } from '../components/specific/SystemDesignSection';
import { FinancialEstimatesSection } from '../components/specific/FinancialEstimatesSection';
import { FinancialSummarySection } from '../components/specific/FinancialSummarySection';
import { FinalApprovalSection } from '../components/specific/FinalApprovalSection';

const BusinessCaseDetailPageSimplified: React.FC = () => {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();
  const {
    currentCaseDetails,
    isLoadingCaseDetails,
    caseDetailsError,
    fetchCaseDetails,
    isLoading,
    clearCurrentCaseDetails,
    exportCaseToPdf,
  } = useAgentContext();

  const [isExportingPdf, setIsExportingPdf] = useState(false);

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
      console.error('Failed to copy link:', err);
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
      console.error('Error exporting PDF:', error);
    } finally {
      setIsExportingPdf(false);
    }
  };

  // SIMPLIFIED: Direct useEffect with caseId dependency only - no complex chains
  useEffect(() => {
    if (caseId) {
      fetchCaseDetails(caseId);
    }

    // Cleanup when component unmounts or caseId changes
    return () => {
      clearCurrentCaseDetails();
    };
  }, [caseId]); // SIMPLIFIED: Only caseId dependency, no function dependencies

  // Loading state
  if (isLoadingCaseDetails && !currentCaseDetails) {
    return (
      <CircularProgress sx={{ display: 'block', margin: 'auto', mt: 5 }} />
    );
  }

  // Error state
  if (caseDetailsError) {
    return (
      <Container component="main" maxWidth="lg">
        <Alert severity="error" sx={{ mt: 3 }}>
          {caseDetailsError.message || 'Failed to load business case details.'}
        </Alert>
      </Container>
    );
  }

  // Not found state
  if (!currentCaseDetails) {
    return (
      <Container component="main" maxWidth="lg">
        <Alert severity="warning" sx={{ mt: 3 }}>
          Business case not found.
        </Alert>
      </Container>
    );
  }

  return (
    <Container component="main" maxWidth="lg">
      <Box sx={{ marginTop: 2, marginBottom: 2 }}>
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

        {/* PRD Section */}
        <PRDSection
          currentCaseDetails={currentCaseDetails}
          isLoading={isLoading}
        />

        {/* System Design Section */}
        <SystemDesignSection
          currentCaseDetails={currentCaseDetails}
          isLoading={isLoading}
        />

        {/* Financial Estimates Section */}
        <FinancialEstimatesSection
          currentCaseDetails={currentCaseDetails}
          isLoading={isLoading}
        />

        {/* Financial Summary Section */}
        <FinancialSummarySection
          currentCaseDetails={currentCaseDetails}
        />

        {/* Final Approval Section */}
        <FinalApprovalSection
          currentCaseDetails={currentCaseDetails}
          isLoading={isLoading}
        />
      </Box>
    </Container>
  );
};

export default BusinessCaseDetailPageSimplified;
