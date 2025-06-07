import React from 'react';
import { Alert, Container, Typography, Box, Paper } from '@mui/material';
import { PRDSection } from '../../components/specific/PRDSection';
import { useAgentContext } from '../../hooks/useAgentContext';
import { STANDARD_STYLES } from '../../styles/constants';

const PRDReviewPage: React.FC = () => {
  const { currentCaseDetails, isLoading, caseDetailsError } = useAgentContext();

  // Error state - case details error is handled by CaseLayout, but we can show additional context
  if (caseDetailsError) {
    return (
      <Container>
        <Alert severity="error">
          Failed to load PRD review details. Please try refreshing the page.
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
          PRD Review & Approval
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Review the Product Requirements Document for accuracy, completeness, and alignment with business objectives.
          Provide feedback and approval to proceed to system design.
        </Typography>
      </Paper>
      
      <PRDSection
        currentCaseDetails={currentCaseDetails}
        isLoading={isLoading}
      />
    </Box>
  );
};

export default PRDReviewPage; 