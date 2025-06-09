# GitHub Secrets Configuration for DrFirst Business Case Generator

## Required Secrets

After completing the Workload Identity Federation setup, you need to configure the following secrets in your GitHub repository.

### How to Add Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each of the following secrets:

### Required Secret Values

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | The full resource name of your Workload Identity Provider | `projects/123456789/locations/global/workloadIdentityPools/github-actions-pool/providers/github-provider` |
| `GCP_SERVICE_ACCOUNT_EMAIL` | The email address of your GCP Service Account | `github-actions-cicd@drfirst-business-case-gen.iam.gserviceaccount.com` |

### Getting the Actual Values

After running the Workload Identity Federation setup commands, get the exact values:

```bash
# Get your project number
PROJECT_NUMBER=$(gcloud projects describe drfirst-business-case-gen --format="value(projectNumber)")

# Get the Workload Identity Provider resource name
echo "GCP_WORKLOAD_IDENTITY_PROVIDER:"
echo "projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-actions-pool/providers/github-provider"

# Get the Service Account email
echo "GCP_SERVICE_ACCOUNT_EMAIL:"
echo "github-actions-cicd@drfirst-business-case-gen.iam.gserviceaccount.com"
```

### Notes

- **Project ID and Repository Name**: These are configured directly in the workflow file as environment variables, so they don't need to be secrets.
- **Security**: These values are not sensitive authentication keys, but they should still be kept as secrets for security best practices.
- **Branch Restrictions**: The Workload Identity Federation is configured to only work from `main` and `develop` branches.

### Verification

After adding the secrets, you can verify they're configured correctly by:

1. Push a commit to the `develop` branch
2. Check the GitHub Actions run
3. Look for successful authentication in the "Authenticate to Google Cloud" step
4. Verify the image appears in Google Artifact Registry

### Troubleshooting

If authentication fails:

1. **Check Secret Names**: Ensure the secret names match exactly (case-sensitive)
2. **Verify WIF Setup**: Run the verification commands from the Workload Identity setup guide
3. **Check Repository Path**: Ensure you replaced `YOUR_GITHUB_ORG/YOUR_REPO_NAME` in the WIF setup with your actual repository path
4. **Branch Restrictions**: Ensure you're pushing to `main` or `develop` branch

### Future Secrets

As the project grows, you may need additional secrets for:
- Production deployments
- Database connections
- API keys for external services
- Monitoring and alerting integrations 