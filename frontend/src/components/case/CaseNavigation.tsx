import React from 'react';
import { useLocation, Link as RouterLink } from 'react-router-dom';
import { Tabs, Tab, Box } from '@mui/material';
import {
  Summarize as SummaryIcon,
  Description as PRDIcon,
  Architecture as DesignIcon,
  AccountBalance as FinancialIcon,
} from '@mui/icons-material';

interface CaseNavigationProps {
  caseId: string;
}

const CaseNavigation: React.FC<CaseNavigationProps> = ({ caseId }) => {
  const location = useLocation();
  
  // Determine the current tab based on the URL
  const getCurrentTab = (): string => {
    const path = location.pathname;
    if (path.endsWith('/prd')) return 'prd';
    if (path.endsWith('/design')) return 'design';
    if (path.endsWith('/financials')) return 'financials';
    return 'summary'; // Default to summary for base route
  };

  const currentTab = getCurrentTab();

  return (
    <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
      <Tabs value={currentTab} aria-label="case navigation tabs">
        <Tab
          label="Summary"
          value="summary"
          icon={<SummaryIcon />}
          iconPosition="start"
          component={RouterLink}
          to={`/cases/${caseId}`}
          sx={{
            textDecoration: 'none',
            '&.Mui-selected': {
              color: 'primary.main',
            },
          }}
        />
        <Tab
          label="PRD"
          value="prd"
          icon={<PRDIcon />}
          iconPosition="start"
          component={RouterLink}
          to={`/cases/${caseId}/prd`}
          sx={{
            textDecoration: 'none',
            '&.Mui-selected': {
              color: 'primary.main',
            },
          }}
        />
        <Tab
          label="System Design"
          value="design"
          icon={<DesignIcon />}
          iconPosition="start"
          component={RouterLink}
          to={`/cases/${caseId}/design`}
          sx={{
            textDecoration: 'none',
            '&.Mui-selected': {
              color: 'primary.main',
            },
          }}
        />
        <Tab
          label="Financials"
          value="financials"
          icon={<FinancialIcon />}
          iconPosition="start"
          component={RouterLink}
          to={`/cases/${caseId}/financials`}
          sx={{
            textDecoration: 'none',
            '&.Mui-selected': {
              color: 'primary.main',
            },
          }}
        />
      </Tabs>
    </Box>
  );
};

export default CaseNavigation; 