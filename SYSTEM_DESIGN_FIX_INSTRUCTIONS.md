# System Design Generation Fix Instructions

## Problem Summary
Your business case "TEST" is in PRD_APPROVED status but the system design was not automatically generated due to a Firestore permissions issue that has now been resolved.

## Solution
I've created a script that will retrigger the PRD approval workflow to generate the missing system design.

## Steps to Fix

### Option 1: Use the Retrigger Script (Recommended)

1. **Get your Firebase Auth Token:**
   - Open your browser and go to your business case: https://drfirst-business-case-gen.web.app/cases/TEST
   - Open Developer Tools (F12 or right-click → Inspect)
   - Go to the **Network** tab
   - Click any button on the page (like "Refresh Page") to make an API request
   - Find a request to `drfirst-backend-782346002710.us-central1.run.app`
   - Click on it and look for the **Authorization** header
   - Copy the value after "Bearer " (it will be a long string starting with "eyJ...")

2. **Run the retrigger script:**
   ```bash
   python3 scripts/debug/retrigger_prd_approval.py TEST <your_auth_token>
   ```
   
   Replace `<your_auth_token>` with the token you copied in step 1.

3. **Wait and check:**
   - The script will reset your case to PRD_REJECTED, then resubmit and approve it
   - This should trigger the system design generation
   - Wait 2-3 minutes, then refresh your browser
   - Check the System Design tab - it should now have content!

### Option 2: Manual UI Steps

If the script doesn't work, you can do this manually through the UI:

1. Go to your case: https://drfirst-business-case-gen.web.app/cases/TEST
2. Go to the PRD tab
3. Use the browser's developer console to make API calls (this is more complex)

## Expected Result

After running the script successfully, you should see:
- ✅ System design generation initiated
- The case status will show system design content
- The System Design tab will no longer show the warning message
- Instead, it will display the generated system architecture

## If It Still Doesn't Work

The root cause was a Firestore permissions issue that I've now fixed by granting the Cloud Run service account proper database access. If the retrigger script doesn't work, it may indicate:

1. **Auth token expired** - Get a fresh token from the browser
2. **Backend deployment issue** - The updated backend with proper permissions may need to be redeployed
3. **Different permissions issue** - There might be another service account or permission that needs updating

## Technical Details

**Root Cause:** The Cloud Run service account (`782346002710-compute@developer.gserviceaccount.com`) was missing Firestore database permissions. When the PRD was approved, the system design generation workflow failed with "403 Missing or insufficient permissions" when trying to access Firestore.

**Fix Applied:** Granted `roles/datastore.user` role to the Cloud Run service account using:
```bash
gcloud projects add-iam-policy-binding drfirst-business-case-gen \
    --member="serviceAccount:782346002710-compute@developer.gserviceaccount.com" \
    --role="roles/datastore.user"
```

**Script Logic:** The retrigger script uses the existing API endpoints to:
1. Reject the PRD (resets the workflow)
2. Resubmit the PRD for review  
3. Approve the PRD again (triggers system design generation with fixed permissions)

## Files Created/Modified

- `scripts/debug/retrigger_prd_approval.py` - New retrigger script
- `scripts/debug/trigger_system_design_manual.py` - Direct trigger script (requires local setup)
- `backend/app/api/v1/cases/prd_routes.py` - Added new trigger-system-design endpoint
- `frontend/src/components/specific/SystemDesignSection.tsx` - Added "Trigger System Design" button

The retrigger script is the most reliable option since it doesn't require local backend setup or complex authentication. 