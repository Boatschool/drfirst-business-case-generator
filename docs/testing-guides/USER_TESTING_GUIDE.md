# 🧪 User Testing Guide: Global Final Approver Role Configuration

**Feature:** Task 9.1.4 - Admin UI to Designate Global Final Approver Role  
**Date:** June 4, 2025  
**Testing Status:** Ready for User Testing

---

## 🚀 **Quick Start Testing**

### **Step 1: Start the Servers**

**Backend Server:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend Server (in new terminal):**
```bash
cd frontend
npm start
```

Wait for both servers to start (frontend usually opens browser automatically at `http://localhost:3000`).

### **Step 2: Basic API Test**

Run this to verify the backend is working:
```bash
python test_api_simple.py
```

You should see:
- ✅ Backend is running and healthy
- ✅ API endpoints exist and require authentication

---

## 🎯 **Testing Scenarios**

### **Test 1: Frontend Admin UI Testing**

#### **Prerequisites:**
- You need an ADMIN user account
- If you don't have one, create one or assign ADMIN role to your test user

#### **Steps:**

1. **Login as ADMIN:**
   - Go to `http://localhost:3000`
   - Log in with a user that has `systemRole: "ADMIN"`

2. **Navigate to Admin Page:**
   - Go to `http://localhost:3000/admin`
   - You should see the admin dashboard

3. **Find Global Approval Settings:**
   - Look for a section titled **"Global Approval Settings"**
   - It should have a ⚙️ settings icon
   - This section should appear near the top, before Rate Cards

4. **Verify Current Display:**
   - You should see "Current Final Approver Role: FINAL_APPROVER" (blue chip)
   - Below that, a dropdown labeled "Final Approver Role"
   - A "Save Setting" button

5. **Test Role Change:**
   - Change dropdown from "FINAL_APPROVER" to "ADMIN"
   - Click "Save Setting"
   - You should see a green success notification
   - The current role chip should update to show "ADMIN"

6. **Test Persistence:**
   - Refresh the page (`Ctrl+R` or `Cmd+R`)
   - Verify the role is still set to "ADMIN"
   - The dropdown should show "ADMIN" selected

7. **Test Reset:**
   - Change back to "FINAL_APPROVER"
   - Save and verify it works

---

### **Test 2: Backend API Testing with Authentication**

#### **Get Authentication Token:**

1. **Login to Frontend:**
   - Log in as an ADMIN user at `http://localhost:3000`

2. **Get Firebase Token:**
   - Press `F12` to open developer tools
   - Go to "Application" or "Storage" tab
   - Find "Local Storage" → `http://localhost:3000`
   - Look for a key containing "firebase" or "auth"
   - Copy the token value (long string starting with "eyJ...")

3. **Run Authenticated Tests:**
   - Edit `test_global_approver_config.py`
   - Find line: `ADMIN_TOKEN = None`
   - Change to: `ADMIN_TOKEN = "your_token_here"`
   - Save and run: `python test_global_approver_config.py`

#### **Expected Results:**
- ✅ GET request successful
- ✅ PUT request successful
- ✅ Configuration change verified
- ✅ Successfully reset to FINAL_APPROVER

---

### **Test 3: End-to-End Approval Workflow Testing**

This tests that the role change actually affects who can approve business cases.

#### **Setup:**
1. **Create Test Business Case:**
   - Go to `/new-case` and create a simple test case
   - Complete all stages: PRD → System Design → Financial Model
   - Submit for final approval

2. **Prepare Test Users:**
   - One user with `systemRole: "ADMIN"`
   - One user with `systemRole: "FINAL_APPROVER"`
   - One user with different role (e.g., `systemRole: "DEVELOPER"`)

#### **Test Scenario A: Default Configuration (FINAL_APPROVER)**

1. **Set Configuration:**
   - As ADMIN, go to `/admin`
   - Set final approver role to "FINAL_APPROVER"

2. **Test Access:**
   - **FINAL_APPROVER user:** Should see approve/reject buttons on the case
   - **ADMIN user:** Should also see buttons (fallback rule)
   - **DEVELOPER user:** Should NOT see buttons

3. **Test Approval:**
   - Use FINAL_APPROVER user to approve or reject the case
   - Verify it works

#### **Test Scenario B: Changed Configuration (ADMIN)**

1. **Change Configuration:**
   - As ADMIN, go to `/admin`
   - Change final approver role to "ADMIN"

2. **Test Access:**
   - **ADMIN user:** Should see approve/reject buttons
   - **FINAL_APPROVER user:** Should NOT see buttons anymore
   - **DEVELOPER user:** Should NOT see buttons

3. **Test Approval:**
   - Use ADMIN user to approve or reject the case
   - Verify it works

#### **Test Scenario C: Changed Configuration (DEVELOPER)**

1. **Change Configuration:**
   - As ADMIN, change final approver role to "DEVELOPER"

2. **Test Access:**
   - **DEVELOPER user:** Should now see approve/reject buttons
   - **FINAL_APPROVER user:** Should NOT see buttons
   - **ADMIN user:** Should still see buttons (fallback)

---

### **Test 4: Security Testing**

#### **Test Non-Admin Access:**

1. **Login as Non-Admin:**
   - Log in with a user that has `systemRole: "DEVELOPER"` or `"CASE_INITIATOR"`

2. **Try to Access Admin Page:**
   - Go to `http://localhost:3000/admin`
   - You should see an "Access Denied" message
   - Should not be able to change global settings

#### **Test API Security:**
- Try to call the API endpoints with a non-ADMIN token
- Should receive 403 Forbidden errors

---

### **Test 5: Error Handling**

#### **Test Invalid Roles:**
1. **Using API directly:**
   - Try to set `finalApproverRoleName` to invalid value like "INVALID_ROLE"
   - Should receive error: "Invalid role name. Must be one of: ..."

#### **Test Offline/Error Scenarios:**
1. **Stop Backend:**
   - Stop the backend server
   - Try to use the admin UI
   - Should show error messages, not crash

2. **Network Issues:**
   - Test with slow network
   - Should show loading states appropriately

---

## 📋 **Expected Test Results**

### **✅ Success Criteria:**

1. **UI Works:**
   - Global Approval Settings section appears for ADMIN users
   - Dropdown shows correct roles
   - Save button works and shows feedback
   - Changes persist across page reloads

2. **API Works:**
   - GET endpoint returns current configuration
   - PUT endpoint updates configuration
   - Proper authentication required
   - Invalid roles rejected

3. **Approval Logic Works:**
   - Role changes immediately affect who can approve cases
   - ADMIN users always have access (fallback)
   - Non-configured roles cannot approve

4. **Security Works:**
   - Only ADMIN users can access admin interface
   - Only ADMIN users can change global settings
   - API properly validates authentication

### **❌ Failure Scenarios:**

If you see these, something needs to be fixed:

- Global Approval Settings section not appearing
- Role changes not saving or persisting
- Approval buttons not updating based on role configuration
- Non-ADMIN users able to change settings
- API returning 500 errors instead of proper responses

---

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **"Section not appearing":**
   - Make sure you're logged in as ADMIN user
   - Check browser console for JavaScript errors
   - Verify frontend is latest version

2. **"Save button not working":**
   - Check browser network tab for API errors
   - Verify backend is running on port 8000
   - Check authentication token is valid

3. **"Changes not taking effect":**
   - Wait 5 minutes for cache to expire, or restart backend
   - Verify Firestore configuration document was updated
   - Check backend logs for errors

4. **"API returns 401":**
   - Your authentication token may have expired
   - Get a fresh token from browser dev tools
   - Make sure you're using ADMIN user token

### **Debug Commands:**

```bash
# Check if backend is running
curl http://localhost:8000/health

# Check Firestore configuration
python -c "
import firebase_admin
from firebase_admin import firestore
firebase_admin.initialize_app()
db = firestore.client()
doc = db.collection('systemConfiguration').document('approvalSettings').get()
print(doc.to_dict() if doc.exists else 'Not found')
"

# Reset configuration to default
python setup_global_approver_config.py
```

---

## 🎉 **Success!**

If all tests pass, you've successfully implemented and verified the Global Final Approver Role Configuration feature! 

The system now allows administrators to dynamically configure which role acts as the final approver for business cases, with immediate effect and proper security controls.

**Next Steps:**
- Deploy to staging environment for broader testing
- Train admin users on the new functionality
- Monitor usage and gather feedback for improvements 