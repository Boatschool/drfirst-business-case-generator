# Workload Identity Federation Setup for DrFirst Business Case Generator

## Prerequisites
- gcloud CLI installed and authenticated with admin privileges
- Project: `drfirst-business-case-gen`
- Repository: Your GitHub repository (e.g., `your-org/drfirst-business-case-generator`)

## Step 1: Create Service Account for GitHub Actions

```bash
# Create a dedicated service account for GitHub Actions CI/CD
gcloud iam service-accounts create github-actions-cicd \
    --display-name="GitHub Actions CI/CD Service Account" \
    --description="Service account for GitHub Actions to push to Artifact Registry and deploy to Cloud Run" \
    --project=drfirst-business-case-gen
```

## Step 2: Grant Required IAM Permissions

```bash
# Grant Artifact Registry Writer role for pushing images
gcloud projects add-iam-policy-binding drfirst-business-case-gen \
    --member="serviceAccount:github-actions-cicd@drfirst-business-case-gen.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.writer"

# Grant Cloud Run Developer role for deployments (optional for future tasks)
gcloud projects add-iam-policy-binding drfirst-business-case-gen \
    --member="serviceAccount:github-actions-cicd@drfirst-business-case-gen.iam.gserviceaccount.com" \
    --role="roles/run.developer"

# Grant Service Account User role for Cloud Run deployments (optional for future tasks)
gcloud projects add-iam-policy-binding drfirst-business-case-gen \
    --member="serviceAccount:github-actions-cicd@drfirst-business-case-gen.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"
```

## Step 3: Create Workload Identity Pool

```bash
# Create the workload identity pool
gcloud iam workload-identity-pools create "github-actions-pool" \
    --project="drfirst-business-case-gen" \
    --location="global" \
    --display-name="GitHub Actions Pool" \
    --description="Pool for GitHub Actions authentication"
```

## Step 4: Create Workload Identity Provider

```bash
# Create the provider for GitHub
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
    --project="drfirst-business-case-gen" \
    --location="global" \
    --workload-identity-pool="github-actions-pool" \
    --display-name="GitHub Provider" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner,attribute.ref=assertion.ref" \
    --issuer-uri="https://token.actions.githubusercontent.com"
```

## Step 5: Allow GitHub Repository to Impersonate Service Account

**IMPORTANT:** Replace `YOUR_GITHUB_ORG/YOUR_REPO_NAME` with your actual GitHub organization and repository name.

```bash
# Get the project number (needed for the principal)
PROJECT_NUMBER=$(gcloud projects describe drfirst-business-case-gen --format="value(projectNumber)")

# Allow the GitHub repository to impersonate the service account
# Replace YOUR_GITHUB_ORG/YOUR_REPO_NAME with your actual repository
gcloud iam service-accounts add-iam-policy-binding \
    --project="drfirst-business-case-gen" \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-actions-pool/attribute.repository/YOUR_GITHUB_ORG/YOUR_REPO_NAME" \
    github-actions-cicd@drfirst-business-case-gen.iam.gserviceaccount.com

# Additional constraint to only allow specific branches (main and develop)
gcloud iam service-accounts add-iam-policy-binding \
    --project="drfirst-business-case-gen" \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-actions-pool/attribute.repository/YOUR_GITHUB_ORG/YOUR_REPO_NAME" \
    --condition='expression=assertion.ref in ["refs/heads/main", "refs/heads/develop"],title=Limit to main and develop branches,description=Only allow authentication from main and develop branches' \
    github-actions-cicd@drfirst-business-case-gen.iam.gserviceaccount.com
```

## Step 6: Get Required Values for GitHub Secrets

```bash
# Get the Workload Identity Provider resource name
echo "GCP_WORKLOAD_IDENTITY_PROVIDER:"
echo "projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-actions-pool/providers/github-provider"

# Service account email
echo "GCP_SERVICE_ACCOUNT_EMAIL:"
echo "github-actions-cicd@drfirst-business-case-gen.iam.gserviceaccount.com"

# Project ID
echo "GCP_PROJECT_ID:"
echo "drfirst-business-case-gen"

# GAR Repository Name
echo "GAR_REPOSITORY_NAME:"
echo "drfirst-backend"
```

## Verification Commands

```bash
# Verify the service account exists
gcloud iam service-accounts describe github-actions-cicd@drfirst-business-case-gen.iam.gserviceaccount.com --project=drfirst-business-case-gen

# Verify the workload identity pool
gcloud iam workload-identity-pools describe github-actions-pool --location=global --project=drfirst-business-case-gen

# Verify the provider
gcloud iam workload-identity-pools providers describe github-provider --location=global --workload-identity-pool=github-actions-pool --project=drfirst-business-case-gen

# Check IAM bindings on the service account
gcloud iam service-accounts get-iam-policy github-actions-cicd@drfirst-business-case-gen.iam.gserviceaccount.com --project=drfirst-business-case-gen
```

## Important Notes

1. **Replace Repository Path**: Make sure to replace `YOUR_GITHUB_ORG/YOUR_REPO_NAME` with your actual GitHub organization and repository name in the commands above.

2. **Branch Restrictions**: The setup includes conditions to only allow authentication from `main` and `develop` branches for security.

3. **Project Number vs Project ID**: The Workload Identity Provider resource name uses the project number, not the project ID.

4. **Security**: This setup provides secure authentication without storing service account keys in GitHub. 