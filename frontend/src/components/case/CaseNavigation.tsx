import React from 'react';
import { useLocation, Link as RouterLink } from 'react-router-dom';
import { Tabs, Tab, Box, Typography } from '@mui/material';
import {
  Description as PRDIcon,
  RateReview as ReviewIcon,
  Architecture as DesignIcon,
  Schedule as EffortIcon,
  MonetizationOn as CostIcon,
  TrendingUp as ValueIcon,
  Assessment as ModelIcon,
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
    if (path.endsWith('/summary')) return 'prd'; // Default to PRD for summary route
    if (path.endsWith('/prd')) return 'prd';
    if (path.endsWith('/prd-review')) return 'prd-review';
    if (path.endsWith('/design')) return 'design';
    if (path.endsWith('/effort-estimation')) return 'effort-estimation';
    if (path.endsWith('/cost-analysis')) return 'cost-analysis';
    if (path.endsWith('/value-analysis')) return 'value-analysis';
    if (path.endsWith('/financial-model')) return 'financial-model';
    if (path.endsWith('/financials')) return 'financials';
    return 'prd'; // Default to PRD for base route
  };

  const currentTab = getCurrentTab();

  const navigationTabs = [
    {
      label: 'PRD Creation',
      value: 'prd',
      icon: <PRDIcon />,
      path: `/cases/${caseId}/prd`,
    },
    {
      label: 'PRD Review',
      value: 'prd-review',
      icon: <ReviewIcon />,
      path: `/cases/${caseId}/prd-review`,
    },
    {
      label: 'System Design',
      value: 'design',
      icon: <DesignIcon />,
      path: `/cases/${caseId}/design`,
    },
    {
      label: 'Effort Estimation',
      value: 'effort-estimation',
      icon: <EffortIcon />,
      path: `/cases/${caseId}/effort-estimation`,
    },
    {
      label: 'Cost Analysis',
      value: 'cost-analysis',
      icon: <CostIcon />,
      path: `/cases/${caseId}/cost-analysis`,
    },
    {
      label: 'Value Analysis',
      value: 'value-analysis',
      icon: <ValueIcon />,
      path: `/cases/${caseId}/value-analysis`,
    },
    {
      label: 'Financial Model',
      value: 'financial-model',
      icon: <ModelIcon />,
      path: `/cases/${caseId}/financial-model`,
    },
    {
      label: 'All Financials',
      value: 'financials',
      icon: <FinancialIcon />,
      path: `/cases/${caseId}/financials`,
    },
  ];

  return (
    <Box sx={{ 
      mb: 3,
      p: 2,
      backgroundColor: 'background.paper',
      borderRadius: 1,
      border: '1px solid',
      borderColor: 'divider',
    }}>
      <Typography 
        variant="h6" 
        component="h2" 
        gutterBottom 
        sx={{ 
          mb: 2,
          fontSize: '1.25rem',
          fontWeight: 600,
        }}
      >
        Stage Review
      </Typography>
      
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs 
          value={currentTab} 
          aria-label="case navigation tabs"
          variant="standard"
          sx={{
            '& .MuiTabs-flexContainer': {
              justifyContent: 'space-between',
            },
          }}
        >
          {navigationTabs.map((tab) => (
            <Tab
              key={tab.value}
              label={tab.label}
              value={tab.value}
              icon={tab.icon}
              iconPosition="start"
              component={RouterLink}
              to={tab.path}
              sx={{
                textDecoration: 'none',
                minWidth: 'auto',
                fontSize: '0.875rem',
                fontWeight: 400,
                flex: 1,
                '& .MuiTab-wrapper': {
                  fontSize: '0.875rem',
                },
                '&.Mui-selected': {
                  color: 'primary.main',
                  fontWeight: 600,
                },
                '&:hover': {
                  backgroundColor: 'action.hover',
                },
              }}
            />
          ))}
        </Tabs>
      </Box>
    </Box>
  );
};

export default CaseNavigation; 