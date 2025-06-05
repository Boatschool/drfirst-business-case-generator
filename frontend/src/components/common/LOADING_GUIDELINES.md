# Loading State Guidelines

This document outlines the standardized loading state patterns implemented in the DrFirst Agentic Business Case Generator to ensure consistent user experience across the application.

## Available Loading Components

All loading components are available from `@/components/common/LoadingIndicators`:

```typescript
import {
  PageLoading,
  LoadingButton,
  InlineLoading,
  LoadingOverlay,
  ListSkeleton,
  TableSkeleton,
  CardSkeleton,
} from '@/components/common/LoadingIndicators';
```

## Loading Component Usage Guidelines

### 1. PageLoading
**When to use:** Initial page loads, full-page data fetching
**Variants:** 
- `spinner`: Simple centered spinner with message
- `skeleton`: Skeleton placeholder that mimics page structure

```typescript
// For initial page loads
<PageLoading 
  message="Loading business case details..." 
  variant="skeleton" 
  skeletonLines={8} 
/>

// Simple spinner for quick loads
<PageLoading message="Loading..." />
```

**Used in:**
- `ReadOnlyCaseViewPage.tsx` - Case details loading
- `BusinessCaseDetailPage.tsx` - Case details loading

### 2. LoadingButton
**When to use:** Form submissions, action buttons with async operations
**Features:** 
- Automatically disables button
- Shows spinner and custom loading text
- Maintains button styling and icons

```typescript
<LoadingButton
  variant="contained"
  onClick={handleSubmit}
  loading={isSubmitting}
  loadingText="Saving..."
  startIcon={<SaveIcon />}
>
  Save Changes
</LoadingButton>
```

**Used in:**
- `NewCasePage.tsx` - Case initiation
- `AdminPage.tsx` - All CRUD operations
- `LoginPage.tsx` & `SignUpPage.tsx` - Authentication
- `BusinessCaseDetailPage.tsx` - Save/submit actions

### 3. ListSkeleton
**When to use:** Dashboard-style lists, case listings
**Configuration:** Number of rows, optional avatar placeholders

```typescript
<ListSkeleton rows={5} showAvatar={false} />
```

**Used in:**
- `DashboardPage.tsx` - Business case list loading

### 4. TableSkeleton
**When to use:** Admin tables, data grids
**Configuration:** Number of rows and columns

```typescript
<TableSkeleton rows={5} columns={7} />
```

**Used in:**
- `AdminPage.tsx` - Rate cards and user tables

### 5. CardSkeleton
**When to use:** Dashboard cards, summary widgets
**Configuration:** Number of content rows

```typescript
<CardSkeleton rows={2} />
```

**Used in:**
- `MainPage.tsx` - Statistics cards

### 6. InlineLoading
**When to use:** Small content areas, settings panels
**Configuration:** Custom message and spinner size

```typescript
<InlineLoading message="Loading configuration..." size={24} />
```

**Used in:**
- `AdminPage.tsx` - Approver configuration loading

### 7. LoadingOverlay
**When to use:** Overlay loading for specific content areas
**Features:** Semi-transparent overlay with spinner

```typescript
<LoadingOverlay loading={isProcessing} message="Processing...">
  <ContentComponent />
</LoadingOverlay>
```

## Implementation Standards

### Context-Level Loading States
The application uses context-level loading states from `AgentContext` and `AuthContext`:

```typescript
// AgentContext loading states
isLoading: boolean;           // General operations
isLoadingCases: boolean;      // Case list fetching
isLoadingCaseDetails: boolean; // Case detail fetching

// AuthContext loading state
loading: boolean;             // Authentication state
```

### Button Loading Patterns
**Before (Inconsistent):**
```typescript
<Button disabled={isLoading}>
  {isLoading ? <CircularProgress size={24} /> : 'Save'}
</Button>
```

**After (Standardized):**
```typescript
<LoadingButton loading={isLoading} loadingText="Saving...">
  Save
</LoadingButton>
```

### Page Loading Patterns
**Before:**
```typescript
{isLoading && <CircularProgress />}
```

**After:**
```typescript
{isLoading && (
  <PageLoading
    message="Loading data..."
    variant="skeleton"
    skeletonLines={6}
  />
)}
```

## Benefits of Standardization

1. **Consistency** - Uniform loading experience across all pages
2. **Better UX** - Skeleton loading provides visual context
3. **Accessibility** - Consistent loading messages for screen readers
4. **Maintainability** - Centralized loading logic in reusable components
5. **Performance** - Optimized loading states prevent UI flicker

## Best Practices

### Loading State Timing
- Show loading immediately when operation starts
- Hide loading when operation completes (success or error)
- For very quick operations (<200ms), consider debouncing to avoid flicker

### Loading Messages
- Be specific: "Loading business cases..." vs "Loading..."
- Use action-specific text: "Saving changes..." vs "Loading..."
- Keep messages concise but informative

### Skeleton Loading
- Use skeleton loading for initial page loads
- Match skeleton structure to actual content layout
- Prefer skeleton over spinners for data that has known structure

### Button Loading
- Always disable buttons during async operations
- Use meaningful loading text that indicates the action
- Maintain visual hierarchy and styling during loading

### Error Handling
- Always pair loading states with proper error handling
- Clear loading states when errors occur
- Provide clear error messages and recovery options

## Migration Notes

All major async operations have been updated to use the new loading components:

- ✅ Dashboard case list loading - now uses `ListSkeleton`
- ✅ New case creation - now uses `LoadingButton`
- ✅ Admin operations - now uses `TableSkeleton` and `LoadingButton`
- ✅ Authentication - now uses `LoadingButton`
- ✅ Case details loading - now uses `PageLoading` with skeleton
- ✅ Main page stats - now uses `CardSkeleton`

The standardized loading states provide a more professional and consistent user experience while maintaining the application's existing functionality. 