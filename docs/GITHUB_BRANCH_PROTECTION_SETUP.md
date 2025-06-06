# GitHub Branch Protection Rules Configuration Guide

## Overview

This guide provides step-by-step instructions for configuring GitHub branch protection rules for the **DrFirst Agentic Business Case Generator** project. These rules will enforce CI checks, code reviews, and maintain code quality as defined in our Git Branching Strategy.

## Required CI Job Names for Status Checks

Based on the existing CI workflows, the following jobs must be configured as required status checks:

### Backend CI Jobs (from `.github/workflows/backend-ci.yml`)
- **Job Name**: `build-and-test`
  - **Includes**: Python linting (flake8), unit tests with coverage, Docker image build
  - **Triggers**: On pull requests to `main` and `develop` branches

### Frontend CI Jobs (from `.github/workflows/frontend-ci-cd.yml`)
- **Job Name**: `build-test-deploy`
  - **Includes**: ESLint linting, unit tests, React build verification
  - **Triggers**: On pull requests to `main` and `develop` branches

## Step-by-Step Configuration Instructions

### Prerequisites
- Admin access to the `df-bus-case-generator` GitHub repository
- Existing CI workflows are functional and running on pull requests

### Part 1: Configure Protection for `main` Branch

1. **Navigate to Branch Protection Settings**
   - Go to your GitHub repository: `https://github.com/[your-org]/df-bus-case-generator`
   - Click on **Settings** tab (you need admin access)
   - In the left sidebar, click **Branches**

2. **Create New Branch Protection Rule**
   - Under "Branch protection rules," click **Add rule**

3. **Configure Branch Pattern**
   - In "Branch name pattern" field, enter: `main`

4. **Enable Core Protection Settings**
   - ✅ **Require a pull request before merging**
     - ✅ **Require approvals**: Set to `1` (minimum recommended)
     - ✅ **Dismiss stale reviews when new commits are pushed** (recommended)
     - ✅ **Require review from code owners** (if you have CODEOWNERS file)

5. **Configure Status Check Requirements**
   - ✅ **Require status checks to pass before merging**
   - ✅ **Require branches to be up to date before merging**
   - In the status checks search box, add the following required checks:
     - `build-and-test` (from Backend CI workflow)
     - `build-test-deploy` (from Frontend CI workflow)

6. **Additional Protection Options (Recommended)**
   - ✅ **Include administrators** (enforces rules for all users)
   - ✅ **Restrict pushes that create files with a large file size** (helps prevent accidental large commits)
   - ✅ **Allow force pushes**: ❌ **Disabled** (prevents force pushes to main)
   - ✅ **Allow deletions**: ❌ **Disabled** (prevents accidental branch deletion)

7. **Save Configuration**
   - Click **Create** to save the branch protection rule

### Part 2: Configure Protection for `develop` Branch

1. **Create Second Branch Protection Rule**
   - Click **Add rule** again

2. **Configure Branch Pattern**
   - In "Branch name pattern" field, enter: `develop`

3. **Apply Same Protection Settings**
   - ✅ **Require a pull request before merging**
     - ✅ **Require approvals**: Set to `1`
     - ✅ **Dismiss stale reviews when new commits are pushed**
     - ✅ **Require review from code owners** (if applicable)

4. **Configure Status Check Requirements**
   - ✅ **Require status checks to pass before merging**
   - ✅ **Require branches to be up to date before merging**
   - Add the same required status checks:
     - `build-and-test` (Backend CI)
     - `build-test-deploy` (Frontend CI)

5. **Additional Protection Options**
   - ✅ **Include administrators**
   - ✅ **Restrict pushes that create files with a large file size**
   - ✅ **Allow force pushes**: ❌ **Disabled**
   - ✅ **Allow deletions**: ❌ **Disabled**

6. **Save Configuration**
   - Click **Create** to save the branch protection rule

## Alternative: GitHub API Configuration

If you prefer to configure branch protection via API, use the following commands:

### API Setup
```bash
# Set your GitHub token and repository variables
export GITHUB_TOKEN="your_personal_access_token"
export REPO_OWNER="your-organization"
export REPO_NAME="df-bus-case-generator"
```

### Configure `main` Branch Protection
```bash
curl -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/branches/main/protection \
  -d '{
    "required_status_checks": {
      "strict": true,
      "contexts": ["build-and-test", "build-test-deploy"]
    },
    "enforce_admins": true,
    "required_pull_request_reviews": {
      "required_approving_review_count": 1,
      "dismiss_stale_reviews": true,
      "require_code_owner_reviews": false
    },
    "restrictions": null,
    "allow_force_pushes": false,
    "allow_deletions": false
  }'
```

### Configure `develop` Branch Protection
```bash
curl -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/branches/develop/protection \
  -d '{
    "required_status_checks": {
      "strict": true,
      "contexts": ["build-and-test", "build-test-deploy"]
    },
    "enforce_admins": true,
    "required_pull_request_reviews": {
      "required_approving_review_count": 1,
      "dismiss_stale_reviews": true,
      "require_code_owner_reviews": false
    },
    "restrictions": null,
    "allow_force_pushes": false,
    "allow_deletions": false
  }'
```

## Verification Steps

### 1. Test Branch Protection with a Sample PR

1. **Create a test feature branch**:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/test-branch-protection
   ```

2. **Make a small change**:
   ```bash
   # Edit any file (e.g., add a comment to README.md)
   echo "# Test branch protection" >> README.md
   git add README.md
   git commit -m "Test: Verify branch protection rules"
   git push origin feature/test-branch-protection
   ```

3. **Create Pull Request**:
   - Go to GitHub and create a PR from `feature/test-branch-protection` to `develop`
   - Observe the following behaviors:

### 2. Expected Behaviors

✅ **CI Checks Start Automatically**
- You should see "Checks pending" status
- Both `build-and-test` and `build-test-deploy` jobs should start running

✅ **Merge Button Disabled Initially**
- "Merge pull request" button should be disabled
- Message should indicate: "Required status checks have not passed" or "Review required"

✅ **Merge Enabled After Success**
- Once CI passes and reviews are approved, merge button becomes enabled

### 3. Test Failure Scenario

1. **Introduce a linting error**:
   ```bash
   # In backend/app, add a file with intentional linting errors
   echo "import unused_module" > backend/app/test_lint_error.py
   git add .
   git commit -m "Test: Intentional lint error"
   git push origin feature/test-branch-protection
   ```

2. **Verify Protection**:
   - CI should fail on the linting step
   - Merge button should remain disabled
   - PR should show "Some checks were not successful"

3. **Clean up**:
   ```bash
   git rm backend/app/test_lint_error.py
   git commit -m "Fix: Remove test lint error"
   git push origin feature/test-branch-protection
   ```

## Troubleshooting

### Common Issues

1. **Status Checks Not Appearing**
   - Ensure CI workflows have run at least once on a PR to the protected branch
   - Check that job names in the workflows match exactly what you entered in protection rules

2. **Admin Override Not Working**
   - Verify "Include administrators" is checked if you want rules to apply to admins
   - Note that some organizations may have policies that prevent admin override

3. **Workflow Permissions**
   - Ensure the workflows have necessary permissions for status reporting
   - Check that `GITHUB_TOKEN` has appropriate scopes

### Status Check Names Reference

| Workflow File | Job Name | Purpose |
|--------------|----------|---------|
| `backend-ci.yml` | `build-and-test` | Python linting, testing, Docker build |
| `frontend-ci-cd.yml` | `build-test-deploy` | ESLint, React tests, build verification |

## Conclusion

With these branch protection rules in place, your repository will enforce:

- ✅ All changes to `main` and `develop` require pull requests
- ✅ Pull requests require at least 1 approval
- ✅ All CI checks must pass before merging
- ✅ Branches must be up-to-date before merging
- ✅ Protection applies to all users, including administrators

This configuration aligns with the Git Branching Strategy defined in `docs/BRANCHING_STRATEGY.md` and ensures code quality and review processes are enforced automatically.

## Next Steps

1. Configure the branch protection rules following this guide
2. Test with a sample pull request
3. Communicate the new requirements to all team members
4. Consider setting up additional status checks for security scanning or deployment verification as needed 