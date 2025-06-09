import React, { useContext } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Button,
  Stack,
  Chip,
  List,
  ListItem,
  ListItemText,
  Divider,
  Paper,
} from '@mui/material';
import {
  Add as AddIcon,
  Dashboard as DashboardIcon,
  Assignment as AssignmentIcon,
  TrendingUp as TrendingUpIcon,
  Speed as SpeedIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { Link as RouterLink } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';
import { useAgentContext } from '../hooks/useAgentContext';
import { CardSkeleton } from '../components/common/LoadingIndicators';
import { PAPER_ELEVATION, STANDARD_STYLES } from '../styles/constants';

const MainPage: React.FC = () => {
  const authContext = useContext(AuthContext);
  const { cases, isLoadingCases, fetchUserCases } = useAgentContext();

  // Fetch user cases when component mounts and authentication is ready
  React.useEffect(() => {
    // Only fetch cases when authentication is ready
    if (authContext && !authContext.loading && authContext.currentUser) {
      fetchUserCases();
    }
  }, [fetchUserCases, authContext]);

  // Calculate some quick stats
  const totalCases = cases.length;
  const draftCases = cases.filter(
    (c) => c.status === 'INTAKE' || c.status === 'PRD_DRAFTING'
  ).length;
  const reviewCases = cases.filter((c) => c.status === 'PRD_REVIEW').length;
  const approvedCases = cases.filter((c) => c.status === 'PRD_APPROVED').length;

  return (
    <Container maxWidth="lg" sx={STANDARD_STYLES.pageContainer}>
      {/* Welcome Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Welcome back,{' '}
          {authContext?.currentUser?.displayName ||
            authContext?.currentUser?.email}
          !
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Generate comprehensive business cases with AI-powered analysis and
          collaboration
        </Typography>
      </Box>

      {/* Quick Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            {isLoadingCases ? (
              <CardSkeleton rows={2} />
            ) : (
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <AssignmentIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6" component="h3">Total Cases</Typography>
                </Box>
                <Typography variant="h4" color="primary">
                  {totalCases}
                </Typography>
              </CardContent>
            )}
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            {isLoadingCases ? (
              <CardSkeleton rows={2} />
            ) : (
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <SpeedIcon color="warning" sx={{ mr: 1 }} />
                  <Typography variant="h6" component="h3">In Progress</Typography>
                </Box>
                <Typography variant="h4" color="warning.main">
                  {draftCases}
                </Typography>
              </CardContent>
            )}
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            {isLoadingCases ? (
              <CardSkeleton rows={2} />
            ) : (
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <TrendingUpIcon color="info" sx={{ mr: 1 }} />
                  <Typography variant="h6" component="h3">Under Review</Typography>
                </Box>
                <Typography variant="h4" color="info.main">
                  {reviewCases}
                </Typography>
              </CardContent>
            )}
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            {isLoadingCases ? (
              <CardSkeleton rows={2} />
            ) : (
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                  <Typography variant="h6" component="h3">Approved</Typography>
                </Box>
                <Typography variant="h4" color="success.main">
                  {approvedCases}
                </Typography>
              </CardContent>
            )}
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Quick Actions */}
        <Grid item xs={12}>
          <Paper elevation={PAPER_ELEVATION.MAIN_CONTENT} sx={STANDARD_STYLES.mainContentPaper}>
            <Typography variant="h5" component="h2" gutterBottom>
              Quick Actions
            </Typography>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} justifyContent="center">
              <Button
                component={RouterLink}
                to="/new-case"
                variant="contained"
                size="large"
                startIcon={<AddIcon />}
                sx={{ minWidth: '200px' }}
              >
                Create New Business Case
              </Button>
              <Button
                component={RouterLink}
                to="/dashboard"
                variant="outlined"
                size="large"
                startIcon={<DashboardIcon />}
                sx={{ minWidth: '200px' }}
              >
                View All Cases
              </Button>
            </Stack>
          </Paper>
        </Grid>


      </Grid>

      {/* Recent Cases Preview */}
      {cases.length > 0 && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="h5" component="h2" gutterBottom>
            Recent Business Cases
          </Typography>
          <Paper elevation={PAPER_ELEVATION.SUB_SECTION} sx={STANDARD_STYLES.subSectionPaper}>
            <List>
              {cases.slice(0, 3).map((businessCase, index) => (
                <React.Fragment key={businessCase.case_id}>
                  <ListItem
                    component={RouterLink}
                    to={`/cases/${businessCase.case_id}`}
                    sx={{
                      textDecoration: 'none',
                      color: 'inherit',
                      '&:hover': { backgroundColor: 'action.hover' },
                    }}
                  >
                    <ListItemText
                      primary={businessCase.title}
                      secondary={
                        <>
                          <Chip
                            label={businessCase.status.replace('_', ' ')}
                            size="small"
                            color={
                              businessCase.status === 'PRD_APPROVED'
                                ? 'success'
                                : businessCase.status === 'PRD_REVIEW'
                                ? 'warning'
                                : 'default'
                            }
                            sx={{ mr: 1, mt: 0.5 }}
                          />
                          <Typography variant="caption" color="text.secondary" component="span">
                            Updated:{' '}
                            {new Date(
                              businessCase.updated_at
                            ).toLocaleDateString()}
                          </Typography>
                        </>
                      }
                    />
                  </ListItem>
                  {index < Math.min(cases.length - 1, 2) && <Divider />}
                </React.Fragment>
              ))}
            </List>
            {cases.length > 3 && (
              <Box sx={{ textAlign: 'center', mt: 2 }}>
                <Button component={RouterLink} to="/dashboard" variant="text">
                  View All Cases ({cases.length})
                </Button>
              </Box>
            )}
          </Paper>
        </Box>
      )}
    </Container>
  );
};

export default MainPage;
