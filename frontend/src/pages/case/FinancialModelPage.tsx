import React from 'react';
import { Alert, Container, Typography, Box, Paper } from '@mui/material';
import { FinancialSummarySection } from '../../components/specific/FinancialSummarySection';
import { useAgentContext } from '../../hooks/useAgentContext';
import { STANDARD_STYLES } from '../../styles/constants';

const FinancialModelPage: React.FC = () => {
  const { currentCaseDetails, caseDetailsError } = useAgentContext();

  // Error state
  if (caseDetailsError) {
    return (
      <Container>
        <Alert severity="error">
          Failed to load financial model details. Please try refreshing the page.
        </Alert>
      </Container>
    );
  }

  // No case details available
  if (!currentCaseDetails) {
    return (
      <Container>
        <Alert severity="warning">
          Case details not available. Please ensure you have permission to view this case.
        </Alert>
      </Container>
    );
  }

  return (
    <Box>
      <Paper sx={{ ...STANDARD_STYLES.mainContentPaper, mb: 3 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Financial Model
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Comprehensive financial model combining cost analysis and value projections.
          Review ROI calculations, scenario analysis, and financial recommendations.
        </Typography>
      </Paper>
      
      <FinancialSummarySection
        currentCaseDetails={currentCaseDetails}
      />
    </Box>
  );
};

export default FinancialModelPage; 