/**
 * UI Style Constants for consistent spacing and elevation
 * Based on Material-UI theme spacing and elevation system
 * 
 * Addresses UI Consistency Review Report findings:
 * - Standardizes container padding/margin values
 * - Defines consistent Paper elevation patterns
 * - Provides reusable sx prop objects for common patterns
 */

// Container spacing constants (based on theme.spacing() values)
export const CONTAINER_SPACING = {
  // Page container vertical padding - applies to main page wrappers
  PAGE_CONTAINER_PADDING_Y: 4, // py: 4 = theme.spacing(4) = 32px
  
  // Section content padding - applies to Paper components containing main content
  SECTION_CONTENT_PADDING: 3, // p: 3 = theme.spacing(3) = 24px
  
  // Auth page specific - slightly larger for auth forms
  AUTH_CONTAINER_MARGIN_TOP: 8, // mt: 8 = theme.spacing(8) = 64px
  AUTH_CONTAINER_PADDING: 4, // p: 4 = theme.spacing(4) = 32px
} as const;

// Paper elevation constants
export const PAPER_ELEVATION = {
  // Main content Paper components (primary content areas on a page)
  MAIN_CONTENT: 2,
  
  // Sub-section Paper components (distinct sections within a main content area)
  SUB_SECTION: 1,
  
  // Auth forms - slightly elevated for emphasis
  AUTH_FORM: 3,
} as const;

// Standard sx prop objects for common patterns
export const STANDARD_STYLES = {
  // Page container with standard vertical padding
  pageContainer: {
    py: CONTAINER_SPACING.PAGE_CONTAINER_PADDING_Y,
  },
  
  // Main content Paper with standard elevation and padding
  mainContentPaper: {
    p: CONTAINER_SPACING.SECTION_CONTENT_PADDING,
  },
  
  // Sub-section Paper with standard elevation and padding
  subSectionPaper: {
    p: CONTAINER_SPACING.SECTION_CONTENT_PADDING,
  },
  
  // Auth form Paper with larger padding and elevation
  authFormPaper: {
    padding: CONTAINER_SPACING.AUTH_CONTAINER_PADDING,
  },
  
  // Auth page container with larger top margin
  authPageContainer: {
    marginTop: CONTAINER_SPACING.AUTH_CONTAINER_MARGIN_TOP,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
} as const; 