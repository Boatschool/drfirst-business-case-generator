import React, { useEffect, useState } from 'react';
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
  Menu,
  MenuItem,
} from '@mui/material';
import { 
  ArrowBack as ArrowBackIcon,
  Sort as SortIcon,
  Check as CheckIcon,
} from '@mui/icons-material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useAgentContext } from '../contexts/AgentContext';
import { BusinessCaseSummary } from '../services/agent/AgentService';
import StatusBadge from '../components/common/StatusBadge';
import StatusFilter from '../components/common/StatusFilter';
import { ALL_BUSINESS_CASE_STATUSES } from '../constants/businessCaseStatuses';

type SortOption = 'title-asc' | 'title-desc' | 'date-newest' | 'date-oldest' | 'status-asc' | 'status-desc';

const SORT_OPTIONS: { value: SortOption; label: string }[] = [
  { value: 'date-newest', label: 'Newest First' },
  { value: 'date-oldest', label: 'Oldest First' },
  { value: 'title-asc', label: 'Title A-Z' },
  { value: 'title-desc', label: 'Title Z-A' },
  { value: 'status-asc', label: 'Status A-Z' },
  { value: 'status-desc', label: 'Status Z-A' },
];

const DashboardPage: React.FC = () => {
  console.log('🟢 DashboardPage: Component rendering');

  const navigate = useNavigate();
  const { cases, isLoadingCases, casesError, fetchUserCases } =
    useAgentContext();

  // State for status filtering and sorting
  const [selectedStatusFilter, setSelectedStatusFilter] = useState<string>('');
  const [currentSort, setCurrentSort] = useState<SortOption>('date-newest');
  const [sortAnchorEl, setSortAnchorEl] = useState<null | HTMLElement>(null);

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
            <Stack direction="row" spacing={1}>
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
            >
              <span>{option.label}</span>
              {currentSort === option.value && (
                <CheckIcon sx={{ ml: 1, fontSize: 16, color: 'primary.main' }} />
              )}
            </MenuItem>
          ))}
        </Menu>

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
          <>
            {/* Show filtering/sorting info */}
            {(selectedStatusFilter || currentSort !== 'date-newest') && (
              <Box sx={{ width: '100%', mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Showing {processedCases.length} of {cases.length} cases
                  {selectedStatusFilter && (
                    <>
                      {' '}with status: <StatusBadge status={selectedStatusFilter} size="small" />
                    </>
                  )}
                  {currentSort !== 'date-newest' && (
                    <> • Sorted by: {getCurrentSortLabel()}</>
                  )}
                </Typography>
              </Box>
            )}

            {processedCases.length === 0 && selectedStatusFilter ? (
              <Typography sx={{ mt: 2 }}>
                No business cases found with the selected status. Try a different filter or select "All Statuses".
              </Typography>
            ) : (
              <Paper elevation={2} sx={{ width: '100%' }}>
                <List>
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
