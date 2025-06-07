# Frontend Performance Optimization Guide

## 🚀 Performance Optimizations Implemented

### 1. **Vite Configuration Optimizations**

#### Build Optimizations
- **ES2020 Target**: Updated build target for modern browsers
- **CSS Code Splitting**: Enabled for better caching
- **esbuild Minification**: Faster build times
- **Manual Chunk Splitting**: Organized vendor libraries for better caching
- **Optimized Dependencies**: Pre-bundled common libraries

#### Development Optimizations
- **React Fast Refresh**: Enabled for instant hot reloading
- **Automatic JSX Runtime**: Reduced bundle size
- **Backend Proxy**: Fixed proxy target to port 8000

### 2. **Performance Utilities Created**

#### Hook-based Optimizations (`src/utils/performanceUtils.ts`)
- `useDebounce`: Debounce expensive operations (API calls, search)
- `useThrottle`: Throttle frequent events (scroll, resize)
- `useStableCallback`: Prevent unnecessary re-renders
- `useStableMemo`: Optimized memoization
- `useIntersectionObserver`: Lazy loading support
- `useVirtualScrolling`: Handle large lists efficiently
- `useImagePreloader`: Preload images for better UX
- `usePerformanceMonitor`: Development performance tracking

#### Lazy Loading Components (`src/components/common/LazyWrapper.tsx`)
- `withLazyLoading`: HOC for lazy component loading
- `ConditionalLazy`: Conditional rendering with suspense
- `IntersectionLazy`: Intersection-based lazy loading

### 3. **Package.json Enhancements**

Added performance-focused scripts:
- `npm run dev:perf`: Development with profiling
- `npm run build:analyze`: Build with bundle analysis
- `npm run analyze`: Bundle size analysis

## 🎯 Recommended Implementation Strategies

### Immediate Performance Wins

#### 1. **Optimize Heavy Components**
```typescript
// Before: Heavy component causing slow renders
const BusinessCaseDetailPage: React.FC = () => {
  // Multiple expensive calculations on every render
  const calculations = expensiveCalculation(data);
  
  return <div>{/* component content */}</div>;
};

// After: Optimized with memoization
const BusinessCaseDetailPage: React.FC = () => {
  const calculations = useStableMemo(
    () => expensiveCalculation(data),
    [data.id, data.lastModified]
  );
  
  return <div>{/* component content */}</div>;
};
```

#### 2. **Debounce API Calls**
```typescript
// In search components, replace direct API calls with debounced ones
const searchTerm = useDebounce(inputValue, 300);

useEffect(() => {
  if (searchTerm) {
    performSearch(searchTerm);
  }
}, [searchTerm]);
```

#### 3. **Lazy Load Heavy Components**
```typescript
// Replace direct imports with lazy loading for large components
const BusinessCaseDetailPage = withLazyLoading(
  () => import('../pages/BusinessCaseDetailPage'),
  { height: '500px' }
);
```

### Context Optimization

#### Current Issues Identified:
1. **AgentContext**: Large state object causing unnecessary re-renders
2. **AuthContext**: Complex dependency arrays in useMemo

#### Recommended Fixes:

```typescript
// Split large contexts into smaller, focused ones
const AgentStateContext = createContext(state);
const AgentActionsContext = createContext(actions);

// Use stable references for context values
const contextValue = useStableMemo(
  () => ({ currentUser, actions }),
  [currentUser.id, currentUser.role] // Only relevant changes
);
```

### Component-Level Optimizations

#### 1. **Memoize Expensive Components**
```typescript
const CaseCard = React.memo(({ case, onAction }) => {
  // Component implementation
}, (prevProps, nextProps) => {
  // Custom comparison for optimal re-rendering
  return prevProps.case.id === nextProps.case.id && 
         prevProps.case.lastModified === nextProps.case.lastModified;
});
```

#### 2. **Optimize List Rendering**
```typescript
// For large case lists, implement virtual scrolling
const CaseList: React.FC = ({ cases }) => {
  const { visibleItems, totalHeight, setScrollTop } = useVirtualScrolling(
    cases, 
    80, // item height
    600  // container height
  );

  return (
    <div style={{ height: 600, overflow: 'auto' }}>
      <div style={{ height: totalHeight }}>
        {visibleItems.map(({ item, offsetY }) => (
          <div key={item.id} style={{ transform: `translateY(${offsetY}px)` }}>
            <CaseCard case={item} />
          </div>
        ))}
      </div>
    </div>
  );
};
```

### Bundle Size Optimization

#### 1. **Tree Shaking Material-UI**
```typescript
// Instead of importing entire library
import { Button, TextField } from '@mui/material';

// Import specific components
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
```

#### 2. **Code Splitting Routes**
```typescript
// In App.tsx, lazy load page components
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const BusinessCaseDetailPage = lazy(() => import('./pages/BusinessCaseDetailPage'));

// Use in routes
<Route path="/dashboard" element={
  <Suspense fallback={<PageLoading />}>
    <DashboardPage />
  </Suspense>
} />
```

### Network Performance

#### 1. **API Response Caching**
```typescript
// Implement proper caching in React Query
const { data: cases, isLoading } = useQuery({
  queryKey: ['cases', userId],
  queryFn: () => agentService.listCases(),
  staleTime: 5 * 60 * 1000, // 5 minutes
  cacheTime: 10 * 60 * 1000, // 10 minutes
});
```

#### 2. **Optimize Image Loading**
```typescript
// For images in the app
const imageUrls = useMemo(() => 
  cases.map(c => c.thumbnailUrl).filter(Boolean), 
  [cases]
);

const { loadedImages } = useImagePreloader(imageUrls);
```

## 📊 Performance Monitoring

### Development Monitoring
```typescript
// Add to heavy components
const BusinessCaseDetailPage: React.FC = () => {
  usePerformanceMonitor('BusinessCaseDetailPage');
  
  // Component implementation
};
```

### Production Monitoring
1. Enable React DevTools Profiler
2. Use Chrome DevTools Performance tab
3. Monitor Core Web Vitals:
   - **LCP (Largest Contentful Paint)**: < 2.5s
   - **FID (First Input Delay)**: < 100ms
   - **CLS (Cumulative Layout Shift)**: < 0.1

## 🛠 Tools for Analysis

### Bundle Analysis
```bash
npm run analyze  # Analyze bundle size
```

### Performance Testing
```bash
npm run dev:perf  # Development with profiling
```

### Runtime Performance
- React DevTools Profiler
- Chrome DevTools Performance
- Web Vitals Extension

## 🎯 Next Steps

### Priority 1 (Immediate)
1. ✅ **Vite Configuration**: Optimized
2. ✅ **Performance Utilities**: Created
3. ✅ **Lazy Loading**: Components created
4. 🔄 **Apply to Heavy Components**: In progress

### Priority 2 (This Week)
1. **Context Optimization**: Split AgentContext
2. **List Virtualization**: Implement for case lists
3. **Image Optimization**: Add lazy loading for images
4. **API Debouncing**: Add to search components

### Priority 3 (Next Week)
1. **Bundle Analysis**: Run and optimize
2. **Component Memoization**: Add to expensive components
3. **Performance Monitoring**: Add to production
4. **Service Worker**: Add for caching

## 📝 Performance Checklist

### Development
- [ ] Use React.memo for pure components
- [ ] Implement useCallback for expensive functions
- [ ] Add useMemo for expensive calculations
- [ ] Use lazy loading for routes and heavy components
- [ ] Debounce user inputs and API calls
- [ ] Implement virtual scrolling for long lists

### Build
- [ ] Analyze bundle size regularly
- [ ] Optimize chunk splitting
- [ ] Enable compression (gzip/brotli)
- [ ] Use CDN for static assets
- [ ] Implement proper caching headers

### Runtime
- [ ] Monitor Core Web Vitals
- [ ] Use React DevTools Profiler
- [ ] Implement error boundaries
- [ ] Add performance logging
- [ ] Use intersection observer for lazy loading

---

**Note**: The optimizations have been implemented and are ready for testing. Restart the development server to see improvements in rendering performance. 