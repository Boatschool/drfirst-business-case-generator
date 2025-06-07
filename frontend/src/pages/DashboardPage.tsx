import React, { useEffect, useState } from 'react';
import {
  Typography,
  Container,
  Box,
  List,
  ListItem,
  Button,
  Paper,
  IconButton,
  Stack,
  Tooltip,
  Menu,
  MenuItem,
} from '@mui/material';
import { 
  ArrowBack as ArrowBackIcon,
  Sort as SortIcon,
  Check as CheckIcon,
} from '@mui/icons-material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useAgentContext } from '../hooks/useAgentContext';
import { AuthContext } from '../contexts/AuthContext';
import { BusinessCaseSummary } from '../services/agent/AgentService';
import StatusBadge from '../components/common/StatusBadge';
import StatusFilter from '../components/common/StatusFilter';
import { ListSkeleton } from '../components/common/LoadingIndicators';
import { ALL_BUSINESS_CASE_STATUSES } from '../constants/businessCaseStatuses';
import useDocumentTitle from '../hooks/useDocumentTitle';
import { PAPER_ELEVATION, STANDARD_STYLES } from '../styles/constants';
import { LoadingErrorDisplay } from '../components/common/ErrorDisplay';
import Logger from '../utils/logger';

type SortOption = 'title-asc' | 'title-desc' | 'date-newest' | 'date-oldest' | 'status-asc' | 'status-desc';

const logger = Logger.create('DashboardPage');

const SORT_OPTIONS: { value: SortOption; label: string }[] = [
  { value: 'date-newest', label: 'Newest First' },
  { value: 'date-oldest', label: 'Oldest First' },
  { value: 'title-asc', label: 'Title A-Z' },
  { value: 'title-desc', label: 'Title Z-A' },
  { value: 'status-asc', label: 'Status A-Z' },
  { value: 'status-desc', label: 'Status Z-A' },
];

const DashboardPage: React.FC = () => {
  logger.debug('🟢 DashboardPage: Component rendering');

  // Set document title
  useDocumentTitle('Dashboard');

  const navigate = useNavigate();
  const authContext = React.useContext(AuthContext);
  const { cases, isLoadingCases, casesError, fetchUserCases } =
    useAgentContext();

  // State for status filtering and sorting
  const [selectedStatusFilter, setSelectedStatusFilter] = useState<string>('');
  const [currentSort, setCurrentSort] = useState<SortOption>('date-newest');
  const [sortAnchorEl, setSortAnchorEl] = useState<null | HTMLElement>(null);

  // Debug: Log component mount/unmount
  useEffect(() => {
    logger.debug('🟢 DashboardPage: Mounted');
    return () => {
      logger.debug('🔴 DashboardPage: Unmounted');
    };
  }, []);

  useEffect(() => {
    // Only fetch cases when authentication is ready
    if (authContext && !authContext.loading && authContext.currentUser) {
      logger.debug('DashboardPage: Authentication ready, calling fetchUserCases');
      fetchUserCases();
    } else {
      logger.debug('DashboardPage: Waiting for authentication to be ready');
    }
  }, [fetchUserCases, authContext]);

  // Sort function
  const sortCases = (cases: BusinessCaseSummary[], sortOption: SortOption): BusinessCaseSummary[] => {
    const sorted = [...cases];
    
    switch (sortOption) {
      case 'title-asc':
        return sorted.sort((a, b) => a.title.localeCompare(b.title));
      case 'title-desc':
        return sorted.sort((a, b) => b.title.localeCompare(a.title));
      case 'date-newest':
        return sorted.sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime());
      case 'date-oldest':
        return sorted.sort((a, b) => new Date(a.updated_at).getTime() - new Date(b.updated_at).getTime());
      case 'status-asc':
        return sorted.sort((a, b) => a.status.localeCompare(b.status));
      case 'status-desc':
        return sorted.sort((a, b) => b.status.localeCompare(a.status));
      default:
        return sorted;
    }
  };

  // Filter and sort cases
  const processedCases = React.useMemo(() => {
    // First filter by status
    const filtered = cases.filter((caseItem: BusinessCaseSummary) => {
      if (!selectedStatusFilter) {
        return true; // Show all cases when no filter is selected
      }
      return caseItem.status === selectedStatusFilter;
    });

    // Then sort the filtered results
    return sortCases(filtered, currentSort);
  }, [cases, selectedStatusFilter, currentSort]);

  const handleStatusFilterChange = (newStatus: string) => {
    setSelectedStatusFilter(newStatus);
  };

  const handleSortClick = (event: React.MouseEvent<HTMLElement>) => {
    setSortAnchorEl(event.currentTarget);
  };

  const handleSortClose = () => {
    setSortAnchorEl(null);
  };

  const handleSortSelect = (sortOption: SortOption) => {
    setCurrentSort(sortOption);
    handleSortClose();
  };

  const getCurrentSortLabel = () => {
    const option = SORT_OPTIONS.find(opt => opt.value === currentSort);
    return option ? option.label : 'Date (Newest)';
  };

  return (
    <Container component="main" maxWidth="md" sx={STANDARD_STYLES.pageContainer}>
      <Box
        sx={{
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
              <IconButton 
                onClick={() => navigate('/main')}
                aria-label="Back to home page"
              >
                <ArrowBackIcon />
              </IconButton>
            </Tooltip>
            <Typography component="h1" variant="h4" gutterBottom sx={{ mb: 0 }}>
              Business Cases Dashboard
            </Typography>
          </Stack>
        </Stack>

        {/* Action Row with Create Button, Sort, and Status Filter */}
        <Stack
          direction={{ xs: 'column', sm: 'row' }}
          alignItems={{ xs: 'flex-start', sm: 'center' }}
          justifyContent="space-between"
          spacing={2}
          sx={{ width: '100%', mb: 3 }}
        >
          <Button
            variant="contained"
            color="primary"
            component={RouterLink}
            to="/new-case"
          >
            Create New Business Case
          </Button>

          {/* Sort and Filter Controls - only show if there are cases */}
          {!isLoadingCases && cases.length > 0 && (
            <Stack direction="row" spacing={1} role="toolbar" aria-label="Dashboard controls">
              {/* Sort Button */}
              <Tooltip title={`Sort by: ${getCurrentSortLabel()}`}>
                <IconButton
                  onClick={handleSortClick}
                  size="small"
                  sx={{
                    color: 'text.secondary',
                    '&:hover': {
                      backgroundColor: 'action.hover',
                    },
                  }}
                  aria-label={`Sort business cases. Current sort: ${getCurrentSortLabel()}`}
                  aria-expanded={Boolean(sortAnchorEl)}
                  aria-haspopup="menu"
                  aria-controls={sortAnchorEl ? 'sort-menu' : undefined}
                >
                  <SortIcon />
                </IconButton>
              </Tooltip>

              {/* Status Filter */}
              <StatusFilter
                allStatuses={[...ALL_BUSINESS_CASE_STATUSES]}
                selectedStatus={selectedStatusFilter}
                onStatusChange={handleStatusFilterChange}
              />
            </Stack>
          )}
        </Stack>

        {/* Sort Menu */}
        <Menu
          id="sort-menu"
          anchorEl={sortAnchorEl}
          open={Boolean(sortAnchorEl)}
          onClose={handleSortClose}
          PaperProps={{
            sx: {
              minWidth: 180,
            },
          }}
          transformOrigin={{ horizontal: 'right', vertical: 'top' }}
          anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
          MenuListProps={{
            'aria-labelledby': 'sort-button',
            role: 'menu',
          }}
        >
          {SORT_OPTIONS.map((option) => (
            <MenuItem
              key={option.value}
              onClick={() => handleSortSelect(option.value)}
              selected={currentSort === option.value}
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
              role="menuitem"
              aria-label={`Sort by ${option.label}`}
            >
              <span>{option.label}</span>
              {currentSort === option.value && (
                <CheckIcon 
                  sx={{ ml: 1, fontSize: 16, color: 'primary.main' }} 
                  aria-hidden="true"
                />
              )}
            </MenuItem>
          ))}
        </Menu>

        {isLoadingCases && (
          <Paper elevation={PAPER_ELEVATION.MAIN_CONTENT} sx={{ width: '100%' }}>
            <ListSkeleton rows={5} />
          </Paper>
        )}

        <LoadingErrorDisplay 
          error={casesError}
          context="load_cases"
          onRetry={fetchUserCases}
        />

        {!isLoadingCases && !casesError && cases.length === 0 && (
          <Typography sx={{ mt: 2 }}>
            No business cases found. Get started by creating a new one!
          </Typography>
        )}

        {!isLoadingCases && !casesError && cases.length > 0 && (
          <>
            {/* Show filtering/sorting info */}
            {(selectedStatusFilter || currentSort !== 'date-newest') && (
              <Box sx={{ width: '100%', mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Showing {processedCases.length} of {cases.length} cases
                  {selectedStatusFilter && (
                    <>
                      {' '}with status: <StatusBadge status={selectedStatusFilter} />
                    </>
                  )}
                  {currentSort !== 'date-newest' && (
                    <> • Sorted by: {getCurrentSortLabel()}</>
                  )}
                </Typography>
              </Box>
            )}

            {processedCases.length === 0 && selectedStatusFilter ? (
              <Typography sx={{ mt: 2 }} role="status" aria-live="polite">
                No business cases found with the selected status. Try a different filter or select "All Statuses".
              </Typography>
            ) : (
              <Paper elevation={PAPER_ELEVATION.MAIN_CONTENT} sx={{ width: '100%' }}>
                <List 
                  role="list"
                  aria-label={`Business cases list (${processedCases.length} items)`}
                >
                  {processedCases.map((caseItem: BusinessCaseSummary) => (
                    <ListItem
                      key={caseItem.case_id}
                      divider
                      button
                      component={RouterLink}
                      to={`/cases/${caseItem.case_id}`}
                      sx={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        py: 2,
                      }}
                      role="listitem"
                      aria-label={`Business case: ${caseItem.title}, Status: ${caseItem.status}, Updated: ${new Date(caseItem.updated_at).toLocaleDateString()}`}
                    >
                      <Box sx={{ flex: 1, minWidth: 0 }}>
                        <Typography variant="h6" component="div" sx={{ mb: 0.5 }}>
                          {caseItem.title}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Updated: {new Date(caseItem.updated_at).toLocaleDateString()}
                        </Typography>
                      </Box>
                      <Box sx={{ ml: 2, flexShrink: 0 }}>
                        <StatusBadge status={caseItem.status} />
                      </Box>
                    </ListItem>
                  ))}
                </List>
              </Paper>
            )}
          </>
        )}
      </Box>
    </Container>
  );
};

export default DashboardPage;
