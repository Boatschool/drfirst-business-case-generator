# HITL Financial Estimates Testing Guide

## Overview
This guide provides comprehensive testing procedures for the Human-in-the-Loop (HITL) Financial Estimates functionality.

## Testing Strategy

### 1. Automated Backend API Testing ✅

**Script**: `test_hitl_financial_estimates.py`

```bash
# Run the automated test suite
python test_hitl_financial_estimates.py --base-url http://localhost:8000

# With authentication (if required)
python test_hitl_financial_estimates.py --base-url http://localhost:8000 --auth-token YOUR_TOKEN
```

**What it tests**:
- ✅ API endpoint functionality (PUT and POST for all 3 financial sections)
- ✅ Status transitions (COMPLETE → PENDING_REVIEW)
- ✅ Data persistence in Firestore
- ✅ History logging
- ✅ Authorization (initiator-only access)
- ✅ Error handling

### 2. Manual Frontend Testing 🧪

#### Prerequisites
1. Start the backend server: `cd backend && uvicorn app.main:app --reload`
2. Start the frontend: `cd frontend && npm run dev`
3. Ensure you have a test user account

#### Test Case Setup
1. **Create a New Business Case**:
   - Navigate to the dashboard
   - Click "Start New Business Case"
   - Fill in problem statement: "Test HITL Financial Estimates"
   - Add a relevant link (optional)
   - Submit and wait for agents to generate estimates

2. **Wait for Initial Estimates**:
   - The case should progress through: INTAKE → PRD_DRAFTING → ... → PLANNING_COMPLETE/COSTING_COMPLETE/VALUE_ANALYSIS_COMPLETE
   - Verify all three financial sections appear with agent-generated data

#### Test Scenarios

##### **Scenario A: Effort Estimate HITL**

**Test Steps**:
1. Navigate to a case with `PLANNING_COMPLETE` status
2. Scroll to "Effort Estimate" section
3. Verify "Edit Effort Estimate" button is visible
4. Click "Edit Effort Estimate"

**Expected Results**:
- ✅ Form fields appear with current values
- ✅ Can edit: Total Hours, Duration, Complexity Assessment, Notes
- ✅ Save/Cancel buttons are present

**Test Data Updates**:
- Change Total Hours: `180`
- Change Duration: `6 weeks`
- Change Complexity: `"Medium-High (Updated via HITL)"`
- Add Notes: `"Updated through manual testing"`

**Test Actions**:
1. **Save Changes**: Click "Save Changes"
   - ✅ Success alert appears
   - ✅ Data persists after page refresh
   - ✅ Edit mode exits automatically

2. **Submit for Review**: Click "Submit for Review"
   - ✅ Success alert appears
   - ✅ Status changes to `EFFORT_PENDING_REVIEW`
   - ✅ Edit/Submit buttons disappear
   - ✅ Case history shows submission entry

##### **Scenario B: Cost Estimate HITL**

**Test Steps**:
1. Navigate to a case with `COSTING_COMPLETE` status
2. Scroll to "Cost Estimate" section
3. Click "Edit Cost Estimate"

**Test Data Updates**:
- Change Total Cost: `$45,000`
- Change Currency: `USD`
- Change Rate Card: `"Standard 2024 Rates (Updated)"`
- Update Calculation Method: `"Updated hourly rates based on market analysis"`
- Add Notes: `"Costs reviewed and updated via HITL"`

**Test Actions**:
1. **Save and Submit**: Follow same pattern as Effort Estimate
2. **Verify**: Status changes to `COSTING_PENDING_REVIEW`

##### **Scenario C: Value Projection HITL**

**Test Steps**:
1. Navigate to a case with `VALUE_ANALYSIS_COMPLETE` status
2. Scroll to "Value/Revenue Projection" section
3. Click "Edit Value Projection"

**Test Data Updates**:
- Change Currency: `USD`
- Update Template: `"Updated SaaS Revenue Template 2024"`
- Change Methodology: `"Updated DCF analysis with market research"`
- Update Assumptions (one per line):
  ```
  Market penetration rate: 15% in year 1
  Customer acquisition cost: $500
  Average revenue per user: $1,200/year
  Churn rate: 5% annually
  ```
- Add Notes: `"Value projection refined via HITL process"`

**Test Actions**:
1. **Save and Submit**: Follow same pattern
2. **Verify**: Status changes to `VALUE_PENDING_REVIEW`

#### **Scenario D: Authorization Testing**

**Test Steps**:
1. **Different User Access**:
   - Login as different user (not case initiator)
   - Navigate to the test case
   - Verify Edit/Submit buttons are hidden

2. **Status-Based Access**:
   - Try editing when status is not appropriate (e.g., `EFFORT_PENDING_REVIEW`)
   - Verify buttons are hidden/disabled

3. **API Direct Testing**:
   - Use browser dev tools or Postman
   - Try API calls without proper authorization
   - Verify 401/403 responses

### 3. Integration Testing 🔄

#### **End-to-End Workflow Test**
1. **Create Complete Case**: Start → PRD → System Design → Financial Estimates
2. **Edit All Sections**: Update effort, cost, and value estimates
3. **Submit All Sections**: Submit all three for review
4. **Verify Final State**: Check case history and status transitions

#### **Error Handling Test**
1. **Network Errors**: Disconnect internet during save
2. **Invalid Data**: Try saving with negative values
3. **Concurrent Editing**: Open same case in multiple tabs

### 4. Performance Testing ⚡

#### **Load Testing**
- Test with multiple users editing simultaneously
- Verify response times under load
- Check for memory leaks during extended editing sessions

#### **Data Volume Testing**
- Test with large financial datasets
- Verify UI responsiveness with many role breakdown entries
- Test with very long notes/assumptions

### 5. UI/UX Testing 🎨

#### **Responsive Design**
- Test on mobile devices
- Verify form layouts on different screen sizes
- Check button accessibility

#### **User Experience**
- Test keyboard navigation
- Verify screen reader compatibility
- Check loading states and feedback messages

### 6. Browser Compatibility 🌐

**Test Browsers**:
- ✅ Chrome (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Edge (latest)

**Test Features**:
- Form editing functionality
- Alert messages
- Button interactions
- Loading states

## Test Data Templates

### **Effort Estimate Test Data**
```json
{
  "roles": [
    {"role": "Senior Developer", "hours": 120},
    {"role": "QA Engineer", "hours": 40},
    {"role": "DevOps Engineer", "hours": 20}
  ],
  "total_hours": 180,
  "estimated_duration_weeks": 6,
  "complexity_assessment": "Medium-High (Updated)",
  "notes": "Updated via HITL testing"
}
```

### **Cost Estimate Test Data**
```json
{
  "estimated_cost": 45000.00,
  "currency": "USD",
  "rate_card_used": "Standard 2024 Rates",
  "calculation_method": "Market-based hourly rates",
  "notes": "Costs updated via HITL process"
}
```

### **Value Projection Test Data**
```json
{
  "currency": "USD",
  "template_used": "SaaS Revenue Template 2024",
  "methodology": "DCF analysis with market research",
  "assumptions": [
    "Market penetration: 15% year 1",
    "CAC: $500",
    "ARPU: $1,200/year"
  ],
  "notes": "Value projection refined via HITL"
}
```

## Expected Results Summary

### **Successful Test Indicators**
- ✅ All financial sections can be edited by case initiators
- ✅ Save/Cancel functionality works correctly
- ✅ Submit for review transitions status appropriately
- ✅ Success/error messages display correctly
- ✅ Data persists across page refreshes
- ✅ History logging captures all changes
- ✅ Authorization properly restricts access
- ✅ UI remains responsive and accessible

### **Performance Benchmarks**
- ⚡ Save operations complete within 2 seconds
- ⚡ Page loads complete within 3 seconds
- ⚡ Form interactions are instantaneous
- ⚡ No memory leaks during extended use

## Bug Reporting Template

When reporting issues, include:

```
**Bug Title**: Brief description

**Environment**:
- Browser: [Chrome/Firefox/Safari/Edge]
- Version: [Browser version]
- OS: [Windows/Mac/Linux]

**Steps to Reproduce**:
1. Step 1
2. Step 2
3. Step 3

**Expected Result**: What should happen

**Actual Result**: What actually happened

**Test Case ID**: [If using automated tests]

**Screenshots/Logs**: [Attach if applicable]

**Severity**: [Critical/High/Medium/Low]
```

## Smoke Test Checklist

Quick verification checklist (5-10 minutes):

- [ ] Can create new business case
- [ ] Financial estimates appear after agent processing
- [ ] Can edit effort estimate and save
- [ ] Can submit effort estimate for review
- [ ] Can edit cost estimate and save
- [ ] Can submit cost estimate for review
- [ ] Can edit value projection and save
- [ ] Can submit value projection for review
- [ ] Status transitions work correctly
- [ ] Success/error messages appear
- [ ] Page refreshes maintain data
- [ ] Authorization blocks unauthorized users

## Automated CI/CD Integration

For continuous testing, integrate into your CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
name: Test HITL Financial Estimates
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install requests
      - name: Run HITL tests
        run: python test_hitl_financial_estimates.py
```

This comprehensive testing approach ensures the HITL Financial Estimates functionality is robust, user-friendly, and production-ready. 