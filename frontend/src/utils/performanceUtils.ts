/* eslint-disable @typescript-eslint/no-explicit-any */
import { useCallback, useMemo, useRef, useEffect, useState } from 'react';

/**
 * Debounce hook for performance optimization
 * Useful for search inputs, API calls, etc.
 */
export const useDebounce = <T>(value: T, delay: number): T => {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

/**
 * Throttle hook for performance optimization
 * Useful for scroll events, resize events, etc.
 */
export const useThrottle = <T>(value: T, limit: number): T => {
  const [throttledValue, setThrottledValue] = useState<T>(value);
  const lastRan = useRef<number>(Date.now());

  useEffect(() => {
    const handler = setTimeout(() => {
      if (Date.now() - lastRan.current >= limit) {
        setThrottledValue(value);
        lastRan.current = Date.now();
      }
    }, limit - (Date.now() - lastRan.current));

    return () => {
      clearTimeout(handler);
    };
  }, [value, limit]);

  return throttledValue;
};

/**
 * Stable callback hook - prevents unnecessary re-renders
 * Use instead of useCallback when dependencies don't change often
 */
export const useStableCallback = <T extends (...args: any[]) => any>(
  callback: T
): T => {
  const callbackRef = useRef<T>(callback);
  callbackRef.current = callback;

  return useCallback((...args: any[]) => {
    return callbackRef.current(...args);
  }, []) as T;
};

/**
 * Memoized computation with stable dependencies
 */
export const useStableMemo = <T>(
  factory: () => T,
  deps: React.DependencyList
): T => {
  const depsRef = useRef<React.DependencyList>(deps);
  const valueRef = useRef<T>();

  // Check if dependencies have actually changed
  const depsChanged = deps.some((dep, index) => {
    return !Object.is(dep, depsRef.current[index]);
  });

  if (depsChanged || valueRef.current === undefined) {
    valueRef.current = factory();
    depsRef.current = deps;
  }

  return valueRef.current;
};

/**
 * Intersection Observer hook for lazy loading
 */
export const useIntersectionObserver = (
  options: IntersectionObserverInit = {}
) => {
  const [isVisible, setIsVisible] = useState(false);
  const [element, setElement] = useState<Element | null>(null);

  useEffect(() => {
    if (!element) return;

    const observer = new IntersectionObserver(([entry]) => {
      setIsVisible(entry.isIntersecting);
    }, options);

    observer.observe(element);

    return () => {
      observer.disconnect();
    };
  }, [element, options]);

  return [setElement, isVisible] as const;
};

/**
 * Virtual scrolling hook for large lists
 */
export const useVirtualScrolling = <T>(
  items: T[],
  itemHeight: number,
  containerHeight: number
) => {
  const [scrollTop, setScrollTop] = useState(0);

  const visibleStart = Math.floor(scrollTop / itemHeight);
  const visibleEnd = Math.min(
    visibleStart + Math.ceil(containerHeight / itemHeight) + 1,
    items.length
  );

  const visibleItems = useMemo(() => {
    return items.slice(visibleStart, visibleEnd).map((item, index) => ({
      item,
      index: visibleStart + index,
      offsetY: (visibleStart + index) * itemHeight,
    }));
  }, [items, visibleStart, visibleEnd, itemHeight]);

  const totalHeight = items.length * itemHeight;

  return {
    visibleItems,
    totalHeight,
    setScrollTop,
    visibleStart,
    visibleEnd,
  };
};

/**
 * Image preloader hook
 */
export const useImagePreloader = (imageUrls: string[]) => {
  const [loadedImages, setLoadedImages] = useState<Set<string>>(new Set());
  const [failedImages, setFailedImages] = useState<Set<string>>(new Set());

  useEffect(() => {
    imageUrls.forEach((url) => {
      if (loadedImages.has(url) || failedImages.has(url)) return;

      const img = new Image();
      img.onload = () => {
        setLoadedImages((prev) => new Set(prev).add(url));
      };
      img.onerror = () => {
        setFailedImages((prev) => new Set(prev).add(url));
      };
      img.src = url;
    });
  }, [imageUrls, loadedImages, failedImages]);

  return { loadedImages, failedImages };
};

/**
 * Performance monitoring hook
 */
export const usePerformanceMonitor = (componentName: string) => {
  const renderCount = useRef(0);
  const renderTimes = useRef<number[]>([]);

  useEffect(() => {
    const startTime = performance.now();
    renderCount.current += 1;

    return () => {
      const endTime = performance.now();
      const renderTime = endTime - startTime;
      renderTimes.current.push(renderTime);

      // Log performance data in development
      if (process.env.NODE_ENV === 'development') {
        console.log(`${componentName} render #${renderCount.current}: ${renderTime.toFixed(2)}ms`);
        
        if (renderTimes.current.length > 10) {
          const avgTime = renderTimes.current.reduce((a, b) => a + b, 0) / renderTimes.current.length;
          console.log(`${componentName} average render time: ${avgTime.toFixed(2)}ms`);
          renderTimes.current = renderTimes.current.slice(-5); // Keep last 5
        }
      }
    };
  });
};

 