#!/bin/bash

echo "🔐 Getting GitHub Secrets Values for DrFirst Business Case Generator"
echo "======================================================================="
echo ""

# Set project details
PROJECT_ID="drfirst-business-case-gen"
SERVICE_ACCOUNT_NAME="github-actions-cicd"
POOL_NAME="github-actions-pool"
PROVIDER_NAME="github-provider"

echo "📊 Project Configuration:"
echo "  Project ID: $PROJECT_ID"
echo "  Service Account: $SERVICE_ACCOUNT_NAME"
echo "  Pool Name: $POOL_NAME"
echo "  Provider Name: $PROVIDER_NAME"
echo ""

# Get project number
echo "🔍 Getting project number..."
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

if [ -z "$PROJECT_NUMBER" ]; then
    echo "❌ Error: Could not get project number. Make sure you're authenticated with gcloud and the project exists."
    exit 1
fi

echo "✅ Project Number: $PROJECT_NUMBER"
echo ""

echo "🎯 GitHub Secrets Configuration:"
echo "=================================="
echo ""

echo "Copy these values to your GitHub repository secrets:"
echo "Go to: Settings → Secrets and variables → Actions → New repository secret"
echo ""

echo "1️⃣ GCP_WORKLOAD_IDENTITY_PROVIDER:"
echo "   projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$POOL_NAME/providers/$PROVIDER_NAME"
echo ""

echo "2️⃣ GCP_SERVICE_ACCOUNT_EMAIL:"
echo "   $SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"
echo ""

echo "3️⃣ CLOUD_RUN_SERVICE_DEV:"
echo "   drfirst-backend-dev"
echo ""

echo "4️⃣ GCP_REGION:"
echo "   us-central1"
echo ""

echo "5️⃣ DEV_BACKEND_CORS_ORIGINS:"
echo "   http://localhost:4000,https://drfirst-business-case-gen.web.app"
echo ""

echo "📋 Summary Table:"
echo "+--------------------------------+------------------------------------------------------------------------------------+"
echo "| Secret Name                    | Value                                                                              |"
echo "+--------------------------------+------------------------------------------------------------------------------------+"
echo "| GCP_WORKLOAD_IDENTITY_PROVIDER | projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$POOL_NAME/providers/$PROVIDER_NAME |"
echo "| GCP_SERVICE_ACCOUNT_EMAIL      | $SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com                        |"
echo "| CLOUD_RUN_SERVICE_DEV          | drfirst-backend-dev                                                                |"
echo "| GCP_REGION                     | us-central1                                                                        |"
echo "| DEV_BACKEND_CORS_ORIGINS       | http://localhost:4000,https://drfirst-business-case-gen.web.app                   |"
echo "+--------------------------------+------------------------------------------------------------------------------------+"
echo ""

echo "🔍 Verification Commands:"
echo "=========================="
echo ""

echo "Verify Workload Identity Pool exists:"
echo "gcloud iam workload-identity-pools describe $POOL_NAME --location=global --project=$PROJECT_ID"
echo ""

echo "Verify Workload Identity Provider exists:"
echo "gcloud iam workload-identity-pools providers describe $PROVIDER_NAME --location=global --workload-identity-pool=$POOL_NAME --project=$PROJECT_ID"
echo ""

echo "Verify Service Account exists:"
echo "gcloud iam service-accounts describe $SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com --project=$PROJECT_ID"
echo ""

echo "⚠️  IMPORTANT NOTES:"
echo "==================="
echo ""
echo "1. Make sure you've completed the Workload Identity Federation setup first"
echo "   See: docs/workload-identity-setup.md"
echo ""
echo "2. Replace 'YOUR_GITHUB_ORG/YOUR_REPO_NAME' in the Workload Identity setup"
echo "   with your actual GitHub repository path (e.g., 'ronwince/drfirst-business-case-generator')"
echo ""
echo "3. The service account needs these IAM roles:"
echo "   - roles/artifactregistry.writer"
echo "   - roles/run.developer" 
echo "   - roles/iam.serviceAccountUser"
echo "   - roles/secretmanager.secretAccessor"
echo ""
echo "4. After adding secrets, test by pushing to the 'develop' branch"
echo ""

echo "✅ Script completed! Use the values above to configure your GitHub secrets." 