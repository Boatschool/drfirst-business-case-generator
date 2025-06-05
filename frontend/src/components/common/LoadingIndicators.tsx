import React from 'react';
import {
  CircularProgress,
  Skeleton,
  Box,
  Typography,
  Button,
  ButtonProps,
} from '@mui/material';

// Page-level loading indicator with optional message and skeleton support
interface PageLoadingProps {
  message?: string;
  variant?: 'spinner' | 'skeleton';
  skeletonLines?: number;
}

export const PageLoading: React.FC<PageLoadingProps> = ({
  message = 'Loading...',
  variant = 'spinner',
  skeletonLines = 5,
}) => {
  if (variant === 'skeleton') {
    return (
      <Box sx={{ width: '100%', p: 3 }}>
        {Array.from({ length: skeletonLines }).map((_, index) => (
          <Skeleton
            key={index}
            variant="text"
            height={index === 0 ? 40 : 20}
            sx={{ mb: index === 0 ? 2 : 1 }}
            width={index === 0 ? '60%' : `${Math.random() * 40 + 60}%`}
          />
        ))}
        <Box sx={{ mt: 3 }}>
          <Skeleton variant="rectangular" height={120} />
        </Box>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        py: 4,
      }}
    >
      <CircularProgress size={40} />
      <Typography
        variant="body1"
        color="text.secondary"
        sx={{ mt: 2 }}
      >
        {message}
      </Typography>
    </Box>
  );
};

// Loading button with consistent styling and spinner
interface LoadingButtonProps extends ButtonProps {
  loading?: boolean;
  loadingText?: string;
  children: React.ReactNode;
}

export const LoadingButton: React.FC<LoadingButtonProps> = ({
  loading = false,
  loadingText,
  children,
  disabled,
  startIcon,
  ...buttonProps
}) => {
  return (
    <Button
      {...buttonProps}
      disabled={disabled || loading}
      startIcon={loading ? <CircularProgress size={20} /> : startIcon}
    >
      {loading ? (loadingText || 'Loading...') : children}
    </Button>
  );
};

// Inline loading indicator for content areas
interface InlineLoadingProps {
  message?: string;
  size?: number;
}

export const InlineLoading: React.FC<InlineLoadingProps> = ({
  message = 'Loading...',
  size = 24,
}) => (
  <Box
    sx={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 1,
      py: 2,
    }}
  >
    <CircularProgress size={size} />
    <Typography variant="body2" color="text.secondary">
      {message}
    </Typography>
  </Box>
);

// Overlay loading for specific content areas
interface LoadingOverlayProps {
  loading: boolean;
  children: React.ReactNode;
  message?: string;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  loading,
  children,
  message = 'Loading...',
}) => (
  <Box sx={{ position: 'relative' }}>
    {children}
    {loading && (
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          bgcolor: 'rgba(255, 255, 255, 0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexDirection: 'column',
          zIndex: 1000,
        }}
      >
        <CircularProgress />
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ mt: 1 }}
        >
          {message}
        </Typography>
      </Box>
    )}
  </Box>
);

// List skeleton for dashboard-style lists
interface ListSkeletonProps {
  rows?: number;
  showAvatar?: boolean;
}

export const ListSkeleton: React.FC<ListSkeletonProps> = ({
  rows = 5,
  showAvatar = false,
}) => (
  <Box sx={{ width: '100%' }}>
    {Array.from({ length: rows }).map((_, index) => (
      <Box
        key={index}
        sx={{
          display: 'flex',
          alignItems: 'center',
          py: 2,
          px: 2,
          borderBottom: '1px solid #e0e0e0',
        }}
      >
        {showAvatar && (
          <Skeleton
            variant="circular"
            width={40}
            height={40}
            sx={{ mr: 2 }}
          />
        )}
        <Box sx={{ flex: 1 }}>
          <Skeleton variant="text" width="70%" height={24} />
          <Skeleton variant="text" width="40%" height={16} sx={{ mt: 0.5 }} />
        </Box>
        <Skeleton variant="rectangular" width={80} height={24} />
      </Box>
    ))}
  </Box>
);

// Table skeleton for admin-style tables
interface TableSkeletonProps {
  rows?: number;
  columns?: number;
}

export const TableSkeleton: React.FC<TableSkeletonProps> = ({
  rows = 5,
  columns = 4,
}) => (
  <Box sx={{ width: '100%' }}>
    {/* Table header */}
    <Box
      sx={{
        display: 'flex',
        p: 2,
        bgcolor: '#f5f5f5',
        borderBottom: '1px solid #e0e0e0',
      }}
    >
      {Array.from({ length: columns }).map((_, index) => (
        <Box key={index} sx={{ flex: 1, mr: index < columns - 1 ? 2 : 0 }}>
          <Skeleton variant="text" width="60%" height={20} />
        </Box>
      ))}
    </Box>
    
    {/* Table rows */}
    {Array.from({ length: rows }).map((_, rowIndex) => (
      <Box
        key={rowIndex}
        sx={{
          display: 'flex',
          p: 2,
          borderBottom: '1px solid #e0e0e0',
        }}
      >
        {Array.from({ length: columns }).map((_, colIndex) => (
          <Box key={colIndex} sx={{ flex: 1, mr: colIndex < columns - 1 ? 2 : 0 }}>
            <Skeleton
              variant="text"
              width={colIndex === columns - 1 ? '40%' : '80%'}
              height={16}
            />
          </Box>
        ))}
      </Box>
    ))}
  </Box>
);

// Card skeleton for dashboard cards
interface CardSkeletonProps {
  rows?: number;
}

export const CardSkeleton: React.FC<CardSkeletonProps> = ({ rows = 3 }) => (
  <Box sx={{ p: 2 }}>
    <Skeleton variant="text" width="70%" height={32} sx={{ mb: 2 }} />
    {Array.from({ length: rows }).map((_, index) => (
      <Skeleton
        key={index}
        variant="text"
        width={`${Math.random() * 30 + 60}%`}
        height={20}
        sx={{ mb: 1 }}
      />
    ))}
    <Skeleton variant="rectangular" height={100} sx={{ mt: 2 }} />
  </Box>
); 