import React from 'react';
import { Alert, Container } from '@mui/material';
import { PRDSection } from '../../components/specific/PRDSection';
import { useAgentContext } from '../../hooks/useAgentContext';

const PRDPage: React.FC = () => {
  const { currentCaseDetails, isLoading, caseDetailsError } = useAgentContext();

  // Error state - case details error is handled by CaseLayout, but we can show additional context
  if (caseDetailsError) {
    return (
      <Container>
        <Alert severity="error">
          Failed to load PRD details. Please try refreshing the page.
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
    <PRDSection
      currentCaseDetails={currentCaseDetails}
      isLoading={isLoading}
    />
  );
};

export default PRDPage; 