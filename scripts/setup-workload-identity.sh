#!/bin/bash

echo "🚀 Setting up Workload Identity Federation for DrFirst Business Case Generator"
echo "==============================================================================="
echo ""

# Configuration
PROJECT_ID="drfirst-business-case-gen"
SERVICE_ACCOUNT_NAME="github-actions-cicd"
POOL_NAME="github-actions-pool"
PROVIDER_NAME="github-provider"
GITHUB_REPO="Boatschool/drfirst-business-case-generator"

echo "📊 Configuration:"
echo "  Project ID: $PROJECT_ID"
echo "  Service Account: $SERVICE_ACCOUNT_NAME"
echo "  GitHub Repository: $GITHUB_REPO"
echo "  Pool Name: $POOL_NAME"
echo "  Provider Name: $PROVIDER_NAME"
echo ""

# Verify gcloud authentication
echo "🔍 Verifying gcloud authentication..."
CURRENT_USER=$(gcloud config get-value account)
if [ -z "$CURRENT_USER" ]; then
    echo "❌ Error: Not authenticated with gcloud. Run 'gcloud auth login' first."
    exit 1
fi
echo "✅ Authenticated as: $CURRENT_USER"
echo ""

# Get project number
echo "🔍 Getting project number..."
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
if [ -z "$PROJECT_NUMBER" ]; then
    echo "❌ Error: Could not get project number. Make sure the project exists and you have access."
    exit 1
fi
echo "✅ Project Number: $PROJECT_NUMBER"
echo ""

# Step 1: Create Service Account
echo "👤 Step 1: Creating service account..."
if gcloud iam service-accounts describe $SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com --project=$PROJECT_ID >/dev/null 2>&1; then
    echo "✅ Service account already exists: $SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"
else
    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
        --display-name="GitHub Actions CI/CD Service Account" \
        --description="Service account for GitHub Actions to push to Artifact Registry and deploy to Cloud Run" \
        --project=$PROJECT_ID
    
    if [ $? -eq 0 ]; then
        echo "✅ Service account created: $SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"
    else
        echo "❌ Failed to create service account"
        exit 1
    fi
fi
echo ""

# Step 2: Grant IAM permissions
echo "🔐 Step 2: Granting IAM permissions..."

IAM_ROLES=(
    "roles/artifactregistry.writer"
    "roles/run.developer"
    "roles/iam.serviceAccountUser"
    "roles/secretmanager.secretAccessor"
)

for role in "${IAM_ROLES[@]}"; do
    echo "  Granting $role..."
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="$role" \
        --quiet
    
    if [ $? -eq 0 ]; then
        echo "  ✅ Granted: $role"
    else
        echo "  ❌ Failed to grant: $role"
        exit 1
    fi
done
echo ""

# Step 3: Create Workload Identity Pool
echo "🏊 Step 3: Creating Workload Identity Pool..."
if gcloud iam workload-identity-pools describe $POOL_NAME --location=global --project=$PROJECT_ID >/dev/null 2>&1; then
    echo "✅ Workload Identity Pool already exists: $POOL_NAME"
else
    gcloud iam workload-identity-pools create $POOL_NAME \
        --project=$PROJECT_ID \
        --location=global \
        --display-name="GitHub Actions Pool" \
        --description="Pool for GitHub Actions authentication"
    
    if [ $? -eq 0 ]; then
        echo "✅ Workload Identity Pool created: $POOL_NAME"
    else
        echo "❌ Failed to create Workload Identity Pool"
        exit 1
    fi
fi
echo ""

# Step 4: Create Workload Identity Provider
echo "🎫 Step 4: Creating Workload Identity Provider..."
if gcloud iam workload-identity-pools providers describe $PROVIDER_NAME --location=global --workload-identity-pool=$POOL_NAME --project=$PROJECT_ID >/dev/null 2>&1; then
    echo "✅ Workload Identity Provider already exists: $PROVIDER_NAME"
else
    gcloud iam workload-identity-pools providers create-oidc $PROVIDER_NAME \
        --project=$PROJECT_ID \
        --location=global \
        --workload-identity-pool=$POOL_NAME \
        --display-name="GitHub Provider" \
        --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner,attribute.ref=assertion.ref" \
        --issuer-uri="https://token.actions.githubusercontent.com"
    
    if [ $? -eq 0 ]; then
        echo "✅ Workload Identity Provider created: $PROVIDER_NAME"
    else
        echo "❌ Failed to create Workload Identity Provider"
        exit 1
    fi
fi
echo ""

# Step 5: Allow GitHub repository to impersonate service account
echo "🔗 Step 5: Configuring repository access..."

# Principal for the specific repository
PRINCIPAL="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$POOL_NAME/attribute.repository/$GITHUB_REPO"

echo "  Granting workloadIdentityUser role to repository: $GITHUB_REPO"
gcloud iam service-accounts add-iam-policy-binding \
    --project=$PROJECT_ID \
    --role="roles/iam.workloadIdentityUser" \
    --member="$PRINCIPAL" \
    $SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com

if [ $? -eq 0 ]; then
    echo "✅ Repository access granted"
else
    echo "❌ Failed to grant repository access"
    exit 1
fi
echo ""

# Step 6: Add branch restrictions
echo "🌿 Step 6: Adding branch restrictions..."
echo "  Adding condition to limit access to main and develop branches..."

CONDITION='expression=assertion.ref in ["refs/heads/main", "refs/heads/develop"],title=Limit to main and develop branches,description=Only allow authentication from main and develop branches'

gcloud iam service-accounts add-iam-policy-binding \
    --project=$PROJECT_ID \
    --role="roles/iam.workloadIdentityUser" \
    --member="$PRINCIPAL" \
    --condition="$CONDITION" \
    $SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com

if [ $? -eq 0 ]; then
    echo "✅ Branch restrictions added (main and develop branches only)"
else
    echo "⚠️  Warning: Failed to add branch restrictions, but basic access is configured"
fi
echo ""

# Display GitHub secrets configuration
echo "🎯 SUCCESS! Workload Identity Federation configured!"
echo "=================================================="
echo ""
echo "🔐 GitHub Secrets to Configure:"
echo "--------------------------------"
echo ""
echo "Go to: https://github.com/$GITHUB_REPO/settings/secrets/actions"
echo "Add these repository secrets:"
echo ""
echo "1️⃣ Name: GCP_WORKLOAD_IDENTITY_PROVIDER"
echo "   Value: projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$POOL_NAME/providers/$PROVIDER_NAME"
echo ""
echo "2️⃣ Name: GCP_SERVICE_ACCOUNT_EMAIL"
echo "   Value: $SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"
echo ""
echo "3️⃣ Name: CLOUD_RUN_SERVICE_DEV"
echo "   Value: drfirst-backend-dev"
echo ""
echo "4️⃣ Name: GCP_REGION"
echo "   Value: us-central1"
echo ""
echo "5️⃣ Name: DEV_BACKEND_CORS_ORIGINS"
echo "   Value: http://localhost:4000,https://drfirst-business-case-gen.web.app"
echo ""

# Verification instructions
echo "🧪 Verification:"
echo "=================="
echo ""
echo "After adding the GitHub secrets:"
echo "1. Push a commit to the 'develop' branch"
echo "2. Check GitHub Actions: https://github.com/$GITHUB_REPO/actions"
echo "3. The workflow should authenticate successfully and deploy to Cloud Run"
echo ""

echo "🔍 Manual verification commands:"
echo "gcloud iam workload-identity-pools describe $POOL_NAME --location=global --project=$PROJECT_ID"
echo "gcloud iam service-accounts get-iam-policy $SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com --project=$PROJECT_ID"
echo ""

echo "✅ Setup completed successfully!" 