import React, { useEffect } from 'react';
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
  IconButton,
  Stack,
  Tooltip,
} from '@mui/material';
import { ArrowBack as ArrowBackIcon } from '@mui/icons-material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useAgentContext } from '../contexts/AgentContext';
import { BusinessCaseSummary } from '../services/agent/AgentService';

const DashboardPage: React.FC = () => {
  console.log('🟢 DashboardPage: Component rendering');

  const navigate = useNavigate();
  const { cases, isLoadingCases, casesError, fetchUserCases } =
    useAgentContext();

  // Debug: Log component mount/unmount
  useEffect(() => {
    console.log('🟢 DashboardPage: Mounted');
    return () => {
      console.log('🔴 DashboardPage: Unmounted');
    };
  }, []);

  useEffect(() => {
    console.log('🔄 DashboardPage: Calling fetchUserCases');
    fetchUserCases();
  }, []);

  return (
    <Container component="main" maxWidth="md">
      <Box
        sx={{
          marginTop: 4,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        {/* Header with Back Button */}
        <Stack
          direction="row"
          alignItems="center"
          justifyContent="space-between"
          sx={{ width: '100%', mb: 3 }}
        >
          <Stack direction="row" alignItems="center" spacing={2}>
            <Tooltip title="Back to Home">
              <IconButton onClick={() => navigate('/main')}>
                <ArrowBackIcon />
              </IconButton>
            </Tooltip>
            <Typography component="h1" variant="h4" gutterBottom sx={{ mb: 0 }}>
              Business Cases Dashboard
            </Typography>
          </Stack>
        </Stack>

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
                    secondary={`Status: ${
                      caseItem.status
                    } | Updated: ${new Date(
                      caseItem.updated_at
                    ).toLocaleDateString()}`}
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
