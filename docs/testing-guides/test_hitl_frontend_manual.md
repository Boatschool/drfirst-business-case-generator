# HITL Financial Estimates - Frontend Manual Test Script

## 🎯 Quick Start Guide (15-minute test)

### Prerequisites
1. Backend running: `cd backend && uvicorn app.main:app --reload`
2. Frontend running: `cd frontend && npm run dev`
3. Browser open to: `http://localhost:3000` (or your frontend URL)

### Test Execution

#### Step 1: Create Test Case
```
✅ Action: Create new business case
📝 Problem Statement: "HITL Financial Estimates Test - [Your Name] [Timestamp]"
⏰ Wait: ~30 seconds for agents to process
🎯 Goal: Get to status with financial estimates
```

#### Step 2: Locate Test Case
```
✅ Action: Navigate to case details page
👀 Look for: Three financial sections:
   - 📊 Effort Estimate (with TimeIcon)
   - 💰 Cost Estimate (with MoneyIcon) 
   - 📈 Value/Revenue Projection (with ValueIcon)
```

#### Step 3: Test Effort Estimate
```
🔍 Find: "Effort Estimate" section
👀 Check: "Edit Effort Estimate" button visible
🖱️ Click: "Edit Effort Estimate"

📝 Edit Fields:
   - Total Hours: 180
   - Duration: 6
   - Complexity: "Medium-High (HITL Test)"
   - Notes: "Updated via manual testing [timestamp]"

💾 Click: "Save Changes"
✅ Verify: Success alert appears
✅ Verify: Edit mode exits

🚀 Click: "Submit for Review"
✅ Verify: Success alert appears
✅ Verify: Buttons disappear/change
```

#### Step 4: Test Cost Estimate
```
🔍 Find: "Cost Estimate" section
🖱️ Click: "Edit Cost Estimate"

📝 Edit Fields:
   - Total Cost: 45000
   - Currency: USD
   - Rate Card: "2024 Standard Rates (Updated)"
   - Calculation Method: "Market analysis based"
   - Notes: "HITL updated costs [timestamp]"

💾 Click: "Save Changes"
🚀 Click: "Submit for Review"
✅ Verify: Status transitions correctly
```

#### Step 5: Test Value Projection
```
🔍 Find: "Value/Revenue Projection" section
🖱️ Click: "Edit Value Projection"

📝 Edit Fields:
   - Currency: USD
   - Template: "SaaS Template 2024"
   - Methodology: "DCF with market research"
   - Assumptions: 
     Market penetration: 15%
     Customer acquisition cost: $500
     Average revenue per user: $1200
   - Notes: "HITL refined projections [timestamp]"

💾 Click: "Save Changes"
🚀 Click: "Submit for Review"
✅ Verify: Final status transition
```

#### Step 6: Verification
```
🔄 Refresh page
✅ Verify: All changes persisted
👀 Check: Case history shows HITL entries
📊 Verify: Status reflects pending reviews
```

### Quick Validation Checklist

**UI/UX Tests** (2 minutes):
- [ ] Edit buttons appear for case initiator
- [ ] Form fields populate with current values
- [ ] Save/Cancel buttons work
- [ ] Loading states show during operations
- [ ] Success/error alerts display properly
- [ ] Edit mode exits after save

**Data Persistence** (1 minute):
- [ ] Changes persist after page refresh
- [ ] History entries appear in case timeline
- [ ] Status transitions are logged

**Authorization** (2 minutes):
- [ ] Different user cannot see edit buttons
- [ ] API calls fail without proper auth
- [ ] Status-inappropriate edits are blocked

## 🐛 Common Issues to Check

### Frontend Issues
- Edit buttons not appearing → Check user permissions & case status
- Form fields not populating → Check data structure in API response
- Save not working → Check network tab for API errors
- Loading states stuck → Check for JavaScript errors in console

### Backend Issues
- 401/403 errors → Check authentication token & user permissions
- 400 errors → Check request payload structure
- 500 errors → Check backend logs for validation errors

### Data Issues
- Changes not persisting → Check Firestore connection
- Status not updating → Check enum values match
- History not logging → Check history entry format

## 🚀 Performance Quick Check

**Response Times** (should be):
- Save operations: < 2 seconds
- Page loads: < 3 seconds
- Form interactions: Instant

**Memory Usage**:
- Open dev tools → Performance tab
- Start recording → Perform all edit operations → Stop
- Check for memory leaks

## 📊 Test Results Template

```
HITL Financial Estimates Manual Test Results
==========================================

Date: [Date]
Tester: [Your Name]
Case ID: [Test Case ID]
Environment: [Local/Dev/Staging]

Test Results:
✅/❌ Effort Estimate Edit: 
✅/❌ Effort Estimate Submit: 
✅/❌ Cost Estimate Edit: 
✅/❌ Cost Estimate Submit: 
✅/❌ Value Projection Edit: 
✅/❌ Value Projection Submit: 
✅/❌ Data Persistence: 
✅/❌ Authorization: 
✅/❌ UI/UX Quality: 

Issues Found:
- [List any issues discovered]

Performance Notes:
- Save time: [X] seconds
- Load time: [X] seconds
- Memory usage: Normal/High

Overall Status: PASS/FAIL
```

## 🎉 Success Criteria

Test is successful if:
- ✅ All three financial sections can be edited
- ✅ All submissions change status correctly
- ✅ Data persists across refreshes
- ✅ Only authorized users can edit
- ✅ UI is responsive and intuitive
- ✅ No console errors during operations
- ✅ Performance is acceptable

**Time to complete**: 15-20 minutes for full manual test
**Frequency**: Run before each deployment or after UI changes 