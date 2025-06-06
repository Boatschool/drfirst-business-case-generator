# Firebase Service Account Setup for GitHub Actions CI/CD

## Overview
This guide provides step-by-step instructions for creating a Firebase Service Account with appropriate permissions for automated deployment to Firebase Hosting from GitHub Actions.

## Prerequisites
- Admin access to the `drfirst-business-case-gen` GCP/Firebase project
- Admin access to the GitHub repository (`df-bus-case-generator`)
- Google Cloud Console access

## Step 1: Create Firebase Service Account

### 1.1 Navigate to Service Accounts
1. Open the [Google Cloud Console](https://console.cloud.google.com/)
2. Ensure you're working in the correct project: `drfirst-business-case-gen`
3. Navigate to **IAM & Admin** > **Service Accounts**
   - URL: `https://console.cloud.google.com/iam-admin/serviceaccounts?project=drfirst-business-case-gen`

### 1.2 Create New Service Account
1. Click **"CREATE SERVICE ACCOUNT"** button
2. Fill in the service account details:
   - **Service account name**: `firebase-hosting-deployer`
   - **Service account ID**: Will auto-generate as `firebase-hosting-deployer@drfirst-business-case-gen.iam.gserviceaccount.com`
   - **Service account description**: `Service account for GitHub Actions to deploy to Firebase Hosting`
3. Click **"CREATE AND CONTINUE"**

### 1.3 Grant Permissions
1. In the **"Grant this service account access to project"** section:
   - Search for and select the role: **"Firebase Hosting Admin"** (`roles/firebasehosting.admin`)
   - This role provides necessary permissions to deploy to Firebase Hosting
2. Click **"CONTINUE"**
3. Skip the **"Grant users access to this service account"** step by clicking **"DONE"**

## Step 2: Generate JSON Key

### 2.1 Access Service Account
1. From the Service Accounts list, find the newly created service account
2. Click on the service account email: `firebase-hosting-deployer@drfirst-business-case-gen.iam.gserviceaccount.com`

### 2.2 Create JSON Key
1. Navigate to the **"KEYS"** tab
2. Click **"ADD KEY"** → **"Create new key"**
3. Select **"JSON"** as the key type
4. Click **"CREATE"**
5. A JSON file will be automatically downloaded to your computer
   - **⚠️ CRITICAL**: This file contains sensitive credentials - handle with extreme care

## Step 3: Store Key as GitHub Secret

### 3.1 Navigate to GitHub Repository
1. Go to your GitHub repository: `df-bus-case-generator`
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
   - URL: `https://github.com/[your-username]/df-bus-case-generator/settings/secrets/actions`

### 3.2 Create Repository Secret
1. Click **"New repository secret"**
2. Configure the secret:
   - **Name**: `FIREBASE_SERVICE_ACCOUNT_KEY_JSON`
   - **Value**: 
     - Open the downloaded JSON key file in a text editor
     - Copy the **entire content** of the file (including curly braces)
     - Paste it into the "Value" field
3. Click **"Add secret"**

## Step 4: Secure Cleanup

### 4.1 Handle Downloaded JSON File
After successfully adding the secret to GitHub:
1. **Option 1 (Recommended)**: Delete the downloaded JSON file from your local machine
2. **Option 2**: Store the file in a secure location (encrypted storage, password manager)
3. **Never**: Commit this file to version control or store it in plain text

## Verification Steps

### 4.1 Verify Service Account in GCP
1. In Google Cloud Console, go to **IAM & Admin** > **Service Accounts**
2. Confirm the service account exists: `firebase-hosting-deployer@drfirst-business-case-gen.iam.gserviceaccount.com`
3. Verify the role assignment by clicking on the service account and checking the **"PERMISSIONS"** tab

### 4.2 Verify GitHub Secret
1. In GitHub repository settings, go to **Secrets and variables** > **Actions**
2. Confirm `FIREBASE_SERVICE_ACCOUNT_KEY_JSON` appears in the repository secrets list
3. Note: The actual value will be hidden for security

## Usage in GitHub Actions

The secret can now be used in your `.github/workflows/frontend-ci-cd.yml` file like this:

```yaml
- name: Deploy to Firebase Hosting
  uses: FirebaseExtended/action-hosting-deploy@v0
  with:
    repoToken: ${{ secrets.GITHUB_TOKEN }}
    firebaseServiceAccount: ${{ secrets.FIREBASE_SERVICE_ACCOUNT_KEY_JSON }}
    projectId: drfirst-business-case-gen
```

## Security Considerations

1. **Principle of Least Privilege**: The service account only has Firebase Hosting Admin permissions
2. **Secret Rotation**: Consider rotating the service account key periodically
3. **Access Monitoring**: Monitor service account usage in GCP audit logs
4. **Repository Access**: Ensure only trusted collaborators have access to repository secrets

## Troubleshooting

### Common Issues
1. **Permission Denied**: Ensure the service account has the correct role assigned
2. **Invalid JSON**: Ensure the entire JSON content was copied correctly to the GitHub secret
3. **Project Mismatch**: Verify the service account belongs to the correct GCP project

### Support Resources
- [Firebase Service Account Documentation](https://firebase.google.com/docs/admin/setup#initialize-sdk)
- [GitHub Encrypted Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Firebase Hosting Deploy Action](https://github.com/FirebaseExtended/action-hosting-deploy)

---

**Status**: Ready for implementation  
**Service Account Email**: `firebase-hosting-deployer@drfirst-business-case-gen.iam.gserviceaccount.com`  
**GitHub Secret Name**: `FIREBASE_SERVICE_ACCOUNT_KEY_JSON`  
**Required Role**: `Firebase Hosting Admin` (`roles/firebasehosting.admin`) 