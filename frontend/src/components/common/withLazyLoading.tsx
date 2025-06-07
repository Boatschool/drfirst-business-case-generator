import React, { Suspense, lazy, ComponentType } from 'react';
import { CircularProgress, Box } from '@mui/material';

interface LazyWrapperProps {
  fallback?: React.ReactNode;
  height?: string | number;
}

/**
 * Higher-order component for lazy loading
 * Provides a consistent loading state across the app
 */
export const withLazyLoading = (
  importFunc: () => Promise<{ default: ComponentType<any> }>,
  options: LazyWrapperProps = {}
) => {
  const LazyComponent = lazy(importFunc);

  const WrappedComponent: React.FC<any> = (props) => {
    const { fallback, height = '200px' } = options;

    const defaultFallback = (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height,
          width: '100%',
        }}
      >
        <CircularProgress size={40} />
      </Box>
    );

    return (
      <Suspense fallback={fallback || defaultFallback}>
        <LazyComponent {...props} />
      </Suspense>
    );
  };

  // Set display name for debugging
  WrappedComponent.displayName = `LazyLoaded(Component)`;

  return WrappedComponent;
};
