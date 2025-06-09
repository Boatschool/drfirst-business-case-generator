# Accessibility Testing Guide

This guide provides instructions for testing the accessibility improvements implemented in the DrFirst Agentic Business Case Generator web application.

## Quick Manual Testing Checklist

### 1. Keyboard Navigation Testing

**Test Steps:**
1. Open the application in your browser
2. Use only the keyboard to navigate (Tab, Shift+Tab, Enter, Spacebar, Arrow keys)
3. Test all major pages: Login, Dashboard, New Case, Business Case Detail, Admin

**What to Check:**
- [ ] All interactive elements can be reached with Tab key
- [ ] Focus indicators are clearly visible (blue outline)
- [ ] Tab order follows logical page flow
- [ ] Skip link appears when Tab is pressed on any page
- [ ] Modal dialogs trap focus properly
- [ ] Menus can be navigated with arrow keys

**Key Improvements:**
- Skip to main content link added
- Improved focus indicators
- Better ARIA labeling for interactive elements

### 2. Screen Reader Testing

**Basic Testing with Built-in Screen Readers:**
- **macOS**: Use VoiceOver (Cmd+F5)
- **Windows**: Use Narrator (Windows+Ctrl+Enter) or NVDA (free download)
- **Mobile**: Use TalkBack (Android) or VoiceOver (iOS)

**Test Areas:**
- [ ] Page titles are announced correctly
- [ ] Headings provide good page structure
- [ ] Form labels are read with inputs
- [ ] Button purposes are clear
- [ ] Error messages are announced
- [ ] Status updates are announced

**Key Improvements:**
- Added proper ARIA labels to icon-only buttons
- Improved form structure with fieldsets and legends
- Added live regions for status updates
- Better heading hierarchy

### 3. Color Contrast Testing

**Tools to Use:**
- Chrome DevTools Lighthouse accessibility audit
- WebAIM Contrast Checker (online)
- Colour Contrast Analyser (desktop app)

**Test Areas:**
- [ ] Primary text meets WCAG AA contrast (4.5:1)
- [ ] Secondary text meets WCAG AA contrast
- [ ] Button text against button backgrounds
- [ ] Link text against backgrounds
- [ ] Status indicators and badges

### 4. Form Accessibility Testing

**Test Forms:**
- Login form
- Sign up form  
- New business case form
- Admin forms (rate cards, pricing templates)

**What to Check:**
- [ ] All inputs have proper labels
- [ ] Required fields are indicated clearly
- [ ] Error messages are associated with fields
- [ ] Form validation works without JavaScript
- [ ] Fieldsets group related fields logically

**Key Improvements:**
- Added fieldset/legend structure
- Better error message associations
- Improved ARIA descriptions

### 5. Modal and Interactive Component Testing

**Components to Test:**
- FloatingChat component
- Status filter dropdown
- Sort menu
- Admin modals
- Confirmation dialogs

**What to Check:**
- [ ] Modals have proper ARIA attributes (role="dialog", aria-modal="true")
- [ ] Focus is trapped within modals
- [ ] Modal headers are properly labeled
- [ ] Dropdowns have expanded/collapsed states
- [ ] Close buttons are properly labeled

**Key Improvements:**
- Added dialog roles and ARIA labeling
- Improved focus management
- Better button labeling

## Automated Testing

### Lighthouse Accessibility Audit

1. Open Chrome DevTools (F12)
2. Go to Lighthouse tab
3. Select "Accessibility" category
4. Run audit
5. Review results and recommendations

**Target Score:** 90+ (current baseline improved from ~75)

### Axe DevTools Extension

1. Install Axe DevTools browser extension
2. Navigate to any page
3. Click Axe icon and run scan
4. Review violations and recommendations

## Specific Page Testing

### AppLayout (Navigation)
- [ ] Skip link works (Tab from any page)
- [ ] Navigation has proper ARIA labels
- [ ] Current page indicated with aria-current
- [ ] Sign out button clearly labeled

### Dashboard Page
- [ ] Page heading structure is logical
- [ ] List of business cases is properly labeled
- [ ] Sort and filter controls are accessible
- [ ] Empty states have proper announcements

### New Case Page
- [ ] Form structure uses fieldsets appropriately
- [ ] All inputs have labels and descriptions
- [ ] Dynamic link addition/removal is accessible
- [ ] Validation errors are clearly associated

### Login/Signup Pages
- [ ] Form roles and labels are correct
- [ ] Error states are announced
- [ ] Google login button is properly labeled
- [ ] Loading states are communicated

### FloatingChat
- [ ] Chat dialog has proper ARIA attributes
- [ ] Message history is accessible
- [ ] Input field is properly labeled
- [ ] Send button is clearly identified

## Common Issues Fixed

1. **Missing ARIA Labels**: Added to icon-only buttons throughout the app
2. **Poor Focus Management**: Improved focus indicators and skip links
3. **Form Structure**: Added fieldsets, legends, and better associations
4. **Modal Accessibility**: Added proper dialog roles and labeling
5. **Screen Reader Support**: Added live regions and better announcements

## Testing in Different Conditions

### High Contrast Mode
Test on Windows with High Contrast mode enabled to ensure visibility.

### Reduced Motion
Test with `prefers-reduced-motion` setting to ensure animations respect user preferences.

### Zoom Testing
Test at 200% and 400% zoom levels to ensure content remains accessible.

## Regression Testing

After any UI changes, re-run:
1. Keyboard navigation test
2. Lighthouse accessibility audit
3. Basic screen reader test
4. Form submission tests

## Getting Help

For accessibility questions or issues:
1. Refer to WCAG 2.1 AA guidelines
2. Use WebAIM resources and tools
3. Test with actual assistive technology users when possible
4. Consider accessibility from the design phase

## Next Steps

Future accessibility improvements to consider:
1. More comprehensive color contrast review
2. Advanced screen reader testing
3. Voice navigation support
4. More robust focus management
5. Progressive enhancement patterns 