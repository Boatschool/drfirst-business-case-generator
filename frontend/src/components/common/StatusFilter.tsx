import React from 'react';
import {
  FormControl,
  FormControlProps,
  Select,
  MenuItem,
  SelectChangeEvent,
  Box,
  Tooltip,
  IconButton,
  Menu
} from '@mui/material';
import { FilterList as FilterListIcon } from '@mui/icons-material';

interface StatusFilterProps {
  allStatuses: string[];
  selectedStatus: string;
  onStatusChange: (newStatus: string) => void;
  fullWidth?: boolean;
  size?: FormControlProps['size'];
}

/**
 * Formats a status string for display by replacing underscores with spaces
 * and converting to title case
 */
const formatStatusText = (status: string): string => {
  return status
    .replace(/_/g, ' ')
    .toLowerCase()
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

/**
 * StatusFilter component that provides a compact filter icon dropdown to filter business cases by status
 */
const StatusFilter: React.FC<StatusFilterProps> = ({
  allStatuses,
  selectedStatus,
  onStatusChange,
  size = 'small' as const
}) => {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleStatusSelect = (status: string) => {
    onStatusChange(status);
    handleClose();
  };

  // Get current status display text
  const currentStatusText = selectedStatus 
    ? formatStatusText(selectedStatus)
    : 'All Statuses';

  return (
    <Box>
      <Tooltip title={`Filter by Status (Current: ${currentStatusText})`}>
        <IconButton
          onClick={handleClick}
          size={size}
          sx={{
            color: selectedStatus ? 'primary.main' : 'text.secondary',
            backgroundColor: selectedStatus ? 'primary.50' : 'transparent',
            '&:hover': {
              backgroundColor: selectedStatus ? 'primary.100' : 'action.hover',
            },
          }}
        >
          <FilterListIcon />
        </IconButton>
      </Tooltip>
      
      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        PaperProps={{
          sx: {
            maxHeight: 300,
            minWidth: 200,
          },
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        {/* All Statuses option */}
        <MenuItem 
          onClick={() => handleStatusSelect('')}
          selected={selectedStatus === ''}
          sx={{ fontStyle: selectedStatus === '' ? 'normal' : 'italic' }}
        >
          All Statuses
        </MenuItem>
        
        {/* Individual status options */}
        {allStatuses.map((status) => (
          <MenuItem 
            key={status} 
            onClick={() => handleStatusSelect(status)}
            selected={selectedStatus === status}
          >
            {formatStatusText(status)}
          </MenuItem>
        ))}
      </Menu>
    </Box>
  );
};

export default StatusFilter; 