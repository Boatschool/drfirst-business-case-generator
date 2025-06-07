import React from 'react';
import { Alert, Container, Typography, Box, Paper } from '@mui/material';
import { ValueAnalysisSection } from '../../components/specific/ValueAnalysisSection';
import { useAgentContext } from '../../hooks/useAgentContext';
import { STANDARD_STYLES } from '../../styles/constants';

const ValueAnalysisPage: React.FC = () => {
  const { currentCaseDetails, isLoading, caseDetailsError } = useAgentContext();

  // Error state
  if (caseDetailsError) {
    return (
      <Container>
        <Alert severity="error">
          Failed to load value analysis details. Please try refreshing the page.
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
          Value Analysis
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Analyze potential business value, revenue opportunities, cost savings, and return on investment.
          Project financial benefits and strategic value to the organization.
        </Typography>
      </Paper>
      
      <ValueAnalysisSection
        currentCaseDetails={currentCaseDetails}
        isLoading={isLoading}
      />
    </Box>
  );
};

export default ValueAnalysisPage; 