import React from 'react';
import { Alert, Container, Box } from '@mui/material';
import { FinancialEstimatesSection } from '../../components/specific/FinancialEstimatesSection';
import { FinancialSummarySection } from '../../components/specific/FinancialSummarySection';
import { useAgentContext } from '../../hooks/useAgentContext';

const FinancialPage: React.FC = () => {
  const { currentCaseDetails, isLoading, caseDetailsError } = useAgentContext();

  // Error state - case details error is handled by CaseLayout, but we can show additional context
  if (caseDetailsError) {
    return (
      <Container>
        <Alert severity="error">
          Failed to load Financial details. Please try refreshing the page.
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
      <FinancialEstimatesSection
        currentCaseDetails={currentCaseDetails}
        isLoading={isLoading}
      />
      <FinancialSummarySection
        currentCaseDetails={currentCaseDetails}
      />
    </Box>
  );
};

export default FinancialPage; 