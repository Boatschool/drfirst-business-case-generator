import React, { useEffect, useContext } from 'react';
import {
  Typography,
  Container,
  Box,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Alert,
  Button,
  Paper,
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { useAgentContext } from '../contexts/AgentContext';
import { BusinessCaseSummary } from '../services/agent/AgentService';

const DashboardPage: React.FC = () => {
  const {
    cases,
    isLoadingCases,
    casesError,
    fetchUserCases,
  } = useAgentContext();

  useEffect(() => {
    fetchUserCases();
  }, [fetchUserCases]);

  return (
    <Container component="main" maxWidth="md">
      <Box sx={{ marginTop: 4, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Typography component="h1" variant="h4" gutterBottom>
          Business Cases Dashboard
        </Typography>

        <Button 
          variant="contained" 
          color="primary" 
          component={RouterLink} 
          to="/new-case"
          sx={{ mb: 3, alignSelf: 'flex-start' }}
        >
          Create New Business Case
        </Button>

        {isLoadingCases && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 3 }}>
            <CircularProgress />
          </Box>
        )}

        {casesError && (
          <Alert severity="error" sx={{ width: '100%', mb: 3 }}>
            {casesError.message || 'Failed to load business cases.'}
          </Alert>
        )}

        {!isLoadingCases && !casesError && cases.length === 0 && (
          <Typography sx={{ mt: 2 }}>
            No business cases found. Get started by creating a new one!
          </Typography>
        )}

        {!isLoadingCases && !casesError && cases.length > 0 && (
          <Paper elevation={2} sx={{ width: '100%' }}>
            <List>
              {cases.map((caseItem: BusinessCaseSummary) => (
                <ListItem 
                  key={caseItem.case_id} 
                  divider 
                  button 
                  component={RouterLink} 
                  to={`/cases/${caseItem.case_id}`}
                >
                  <ListItemText 
                    primary={caseItem.title}
                    secondary={`Status: ${caseItem.status} | Updated: ${new Date(caseItem.updated_at).toLocaleDateString()}`}
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        )}
      </Box>
    </Container>
  );
};

export default DashboardPage; 