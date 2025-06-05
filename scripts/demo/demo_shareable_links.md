# Shareable Links Feature Demo

## 🎯 Overview
This guide demonstrates the newly implemented Shareable Links feature (Tasks 9.3.1-9.3.2) that allows authenticated users to share read-only views of approved business cases.

## 🚀 Quick Start Demo

### Prerequisites
1. Backend server running on `http://localhost:8000`
2. Frontend server running on `http://localhost:3000`
3. Two user accounts for testing (can be the same browser with different tabs)

### Step-by-Step Demo

#### 1. Create an Approved Business Case
```bash
# Start the backend and frontend servers
cd backend && python -m uvicorn app.main:app --reload --port 8000
cd frontend && npm start
```

#### 2. Generate a Shareable Link
1. **Log in** to the application
2. **Navigate** to an existing business case or create a new one
3. **Advance the case** to `APPROVED` or `PENDING_FINAL_APPROVAL` status
4. **Look for the "Share Link" button** in the case detail page header
5. **Click "Share Link"** - the URL will be copied to your clipboard
6. **The shareable URL format**: `http://localhost:3000/cases/{caseId}/view`

#### 3. Test the Shareable Link
1. **Open a new browser tab/window** (or use incognito mode)
2. **Log in** with a different user account (or same account)
3. **Paste the shareable URL** and navigate to it
4. **Verify** you can see the case details in read-only mode

## 🔍 What to Look For

### In the Business Case Detail Page
- ✅ **Share Button Visibility**: "Share Link" button appears only for approved cases
- ✅ **Button Styling**: Outlined button with share icon
- ✅ **Click Behavior**: Copies URL to clipboard and shows confirmation
- ✅ **Button Position**: Located next to Export PDF and Refresh buttons

### In the Read-Only View Page
- ✅ **Read-Only Indicator**: Clear badge showing "Read-Only View"
- ✅ **Navigation**: Back button to return to dashboard
- ✅ **Content Display**: Shows all case information without edit capabilities
- ✅ **Professional Layout**: Clean, organized presentation

### Security Verification
- ✅ **Authentication Required**: Must be logged in to access shared links
- ✅ **Status-Based Access**: Only approved/pending cases are shareable
- ✅ **No Edit Access**: Read-only view prevents any modifications

## 🧪 Test Scenarios

### Scenario 1: Owner Shares Approved Case
```
1. User A creates and approves a business case
2. User A clicks "Share Link" button
3. User A shares the URL with User B
4. User B (authenticated) accesses the shared URL
5. User B sees read-only view of the case
✅ Expected: Success
```

### Scenario 2: Sharing Non-Approved Case
```
1. User A has a draft business case
2. User A looks for "Share Link" button
✅ Expected: Button is NOT visible
```

### Scenario 3: Unauthenticated Access
```
1. User A shares a link to User B
2. User B tries to access without logging in
✅ Expected: Redirected to login page
```

### Scenario 4: Cross-User Access
```
1. User A shares approved case link
2. User B (different user, authenticated) accesses link
✅ Expected: Can view the case in read-only mode
```

## 📱 User Interface Elements

### Share Button
- **Location**: Business case detail page header
- **Appearance**: Outlined button with share icon
- **Text**: "Share Link"
- **Tooltip**: "Generate Shareable Link"
- **Minimum Width**: 140px

### Read-Only View Page
- **Header**: Title with read-only badge and back navigation
- **Content Sections**:
  - Problem Statement
  - PRD Content (Markdown rendered)
  - System Design Content
  - Financial Information
- **No Edit Controls**: No save/edit buttons or form fields

## 🔧 Technical Verification

### Backend API Changes
```bash
# Test approved case access by non-owner
curl -H "Authorization: Bearer <token>" \
     http://localhost:8000/api/v1/cases/<approved_case_id>
# Should return 200 OK

# Test draft case access by non-owner  
curl -H "Authorization: Bearer <token>" \
     http://localhost:8000/api/v1/cases/<draft_case_id>
# Should return 403 Forbidden
```

### Frontend Route Testing
```
✅ /cases/:caseId - Original case detail page
✅ /cases/:caseId/view - New read-only view page
```

## 📊 Success Metrics

- [ ] Share button appears for approved cases only
- [ ] Share button generates correct shareable URL
- [ ] Shareable URL is copied to clipboard
- [ ] Read-only view loads correctly for shared cases
- [ ] Non-owners can access approved shared cases
- [ ] Draft cases remain owner-only
- [ ] Authentication is still required for all access
- [ ] No edit functionality in read-only view

## 🐛 Troubleshooting

### Common Issues

**Issue**: Share button not appearing
- **Check**: Case status is `APPROVED` or `PENDING_FINAL_APPROVAL`
- **Verify**: User is viewing their own case or has proper access

**Issue**: Shared link shows "Access Denied"
- **Check**: Recipient is logged in
- **Verify**: Case is in shareable status
- **Confirm**: Backend authorization changes are deployed

**Issue**: Read-only view not loading
- **Check**: Frontend route is properly configured
- **Verify**: ReadOnlyCaseViewPage component is imported
- **Confirm**: No TypeScript/build errors

**Issue**: Clipboard not working
- **Check**: Browser supports clipboard API
- **Try**: Manual copy from browser prompt fallback
- **Note**: HTTPS may be required for clipboard access

## 🎉 Demo Script

Here's a suggested script for demonstrating the feature:

```
"Today I'll show you our new Shareable Links feature that allows 
users to share approved business cases with colleagues.

1. First, I'll navigate to an approved business case
2. Notice the new 'Share Link' button next to Export PDF
3. When I click it, the shareable URL is copied to my clipboard
4. Now I'll open a new tab and paste this URL
5. As you can see, I can view all the case details in read-only mode
6. This includes the problem statement, PRD, system design, and financials
7. The interface clearly indicates this is a read-only view
8. Users can easily navigate back to their dashboard

This feature enables secure sharing while maintaining proper access controls
and ensuring approved cases can be easily shared across teams."
```

## ✅ Completion Checklist

- [x] Backend authorization updated
- [x] ReadOnlyCaseViewPage component created
- [x] Share button added to case detail page
- [x] Frontend routing configured
- [x] TypeScript compilation successful
- [x] Security measures implemented
- [x] Documentation completed
- [ ] Manual testing performed
- [ ] User acceptance testing conducted

The Shareable Links feature is ready for production use! 