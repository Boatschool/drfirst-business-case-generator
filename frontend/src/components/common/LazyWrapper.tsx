import React, { Suspense } from 'react';
import { CircularProgress, Box } from '@mui/material';

interface LazyWrapperProps {
  fallback?: React.ReactNode;
  height?: string | number;
}

/**
 * Lazy loading component for conditional rendering
 */
interface ConditionalLazyProps extends LazyWrapperProps {
  condition: boolean;
  children: React.ReactNode;
}

export const ConditionalLazy: React.FC<ConditionalLazyProps> = ({
  condition,
  children,
  fallback,
  height = '200px',
}) => {
  if (!condition) {
    return null;
  }

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
      {children}
    </Suspense>
  );
};

/**
 * Intersection observer based lazy loading
 */
interface IntersectionLazyProps extends LazyWrapperProps {
  children: React.ReactNode;
  rootMargin?: string;
  threshold?: number;
}

export const IntersectionLazy: React.FC<IntersectionLazyProps> = ({
  children,
  fallback,
  height = '200px',
  rootMargin = '50px',
  threshold = 0.1,
}) => {
  const [isVisible, setIsVisible] = React.useState(false);
  const [element, setElement] = React.useState<Element | null>(null);

  React.useEffect(() => {
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect(); // Only load once
        }
      },
      { rootMargin, threshold }
    );

    observer.observe(element);

    return () => {
      observer.disconnect();
    };
  }, [element, rootMargin, threshold]);

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
    <div ref={setElement as any} style={{ minHeight: typeof height === 'number' ? `${height}px` : height }}>
      {isVisible ? (
        <Suspense fallback={fallback || defaultFallback}>
          {children}
        </Suspense>
      ) : (
        fallback || defaultFallback
      )}
    </div>
  );
}; 