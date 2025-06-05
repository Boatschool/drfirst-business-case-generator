import React from 'react';
import { Chip, ChipProps } from '@mui/material';

// Define color mapping for all BusinessCaseStatus enum values
const STATUS_COLORS: { [key: string]: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' } = {
  // Initial stages
  INTAKE: 'info',
  PRD_DRAFTING: 'warning',
  PRD_REVIEW: 'secondary',
  PRD_APPROVED: 'success',
  PRD_REJECTED: 'error',
  
  // System Design stages
  SYSTEM_DESIGN_DRAFTING: 'warning',
  SYSTEM_DESIGN_DRAFTED: 'info',
  SYSTEM_DESIGN_PENDING_REVIEW: 'secondary',
  SYSTEM_DESIGN_APPROVED: 'success',
  SYSTEM_DESIGN_REJECTED: 'error',
  
  // Planning stages
  PLANNING_IN_PROGRESS: 'warning',
  PLANNING_COMPLETE: 'primary',
  
  // Effort estimation stages
  EFFORT_PENDING_REVIEW: 'secondary',
  EFFORT_APPROVED: 'success',
  EFFORT_REJECTED: 'error',
  
  // Cost estimation stages
  COSTING_IN_PROGRESS: 'warning',
  COSTING_COMPLETE: 'primary',
  COSTING_PENDING_REVIEW: 'secondary',
  COSTING_APPROVED: 'success',
  COSTING_REJECTED: 'error',
  
  // Value analysis stages
  VALUE_ANALYSIS_IN_PROGRESS: 'warning',
  VALUE_ANALYSIS_COMPLETE: 'primary',
  VALUE_PENDING_REVIEW: 'secondary',
  VALUE_APPROVED: 'success',
  VALUE_REJECTED: 'error',
  
  // Financial model stages
  FINANCIAL_MODEL_IN_PROGRESS: 'warning',
  FINANCIAL_MODEL_COMPLETE: 'primary',
  FINANCIAL_ANALYSIS: 'primary',
  
  // Final approval stages
  FINAL_REVIEW: 'secondary',
  PENDING_FINAL_APPROVAL: 'warning',
  APPROVED: 'success',
  REJECTED: 'error',
};

interface StatusBadgeProps {
  status: string;
  size?: ChipProps['size'];
  variant?: ChipProps['variant'];
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
 * StatusBadge component that displays business case status as a colored Material-UI Chip
 */
const StatusBadge: React.FC<StatusBadgeProps> = ({ 
  status, 
  size = 'small' as const,
  variant = 'filled' as const
}) => {
  // Get the color for this status, fallback to 'default' if not found
  const chipColor = STATUS_COLORS[status] || 'default';
  
  // Format the status text for display
  const displayText = formatStatusText(status);

  return (
    <Chip
      label={displayText}
      color={chipColor}
      size={size}
      variant={variant}
      sx={{
        fontWeight: 'medium',
        // Add some spacing for better readability
        minWidth: 'fit-content',
      }}
    />
  );
};

export default StatusBadge; 