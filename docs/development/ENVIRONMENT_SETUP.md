# Environment Setup Guide

**Project:** DrFirst Agentic Business Case Generator  
**Version:** 1.0.0  
**Last Updated:** January 2025

---

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Local Development Setup](#local-development-setup)
4. [Deployed Environments (Cloud Run)](#deployed-environments-cloud-run)
5. [Key Variable Explanations](#key-variable-explanations)
6. [Security Best Practices](#security-best-practices)
7. [Verification Steps](#verification-steps)
8. [Troubleshooting Common Issues](#troubleshooting-common-issues)

---

## Introduction

The DrFirst Agentic Business Case Generator uses environment variables to manage configuration across different environments (development, staging, production). This approach ensures:

- **Security**: Sensitive information like API keys and secrets are not hardcoded in source code
- **Flexibility**: Different configurations for different environments
- **Maintainability**: Centralized configuration management

The application consists of two main components that require separate configuration:
- **Frontend (React/Vite)**: Build-time environment variables with `VITE_` prefix
- **Backend (FastAPI/Python)**: Runtime environment variables managed via Pydantic BaseSettings

---

## Prerequisites

Ensure you have the following tools installed for local development:

- **Node.js** (v18 or higher) and npm
- **Python** (v3.11 or higher)
- **Google Cloud CLI** (`gcloud`) - for production deployment
- **Docker** and **Docker Compose** - for containerized development (optional)
- **Git** - for version control

### Firebase Project Setup

Before configuring environment variables, ensure you have:

1. **Firebase Project**: Created in [Firebase Console](https://console.firebase.google.com/)
2. **Authentication Enabled**: Google sign-in provider enabled
3. **Firestore Database**: Created in native mode
4. **Authorized Domains**: Added `localhost` and your deployment domains

---

## Local Development Setup

### Frontend Configuration (`frontend/`)

#### Step 1: Copy Template
```bash
cd frontend/
cp .env.template .env
```

#### Step 2: Configure Frontend Variables

Edit `frontend/.env` with your actual values:

| Variable | Required | Description | Example Value |
|----------|----------|-------------|---------------|
| `VITE_API_BASE_URL` | ✅ Yes | Backend API base URL | `http://localhost:8000` |
| `VITE_API_VERSION` | ✅ Yes | API version for endpoint paths | `v1` |
| `VITE_FIREBASE_API_KEY` | ✅ Yes | Firebase Web API key | `AIzaSyC1234567890abcdefg...` |
| `VITE_FIREBASE_AUTH_DOMAIN` | ✅ Yes | Firebase auth domain | `your-project.firebaseapp.com` |
| `VITE_FIREBASE_PROJECT_ID` | ✅ Yes | Firebase project identifier | `your-project-id` |
| `VITE_ENVIRONMENT` | ✅ Yes | Environment mode | `development` |
| `VITE_ENABLE_ANALYTICS` | ❌ Optional | Enable analytics tracking | `false` |
| `VITE_ENABLE_DEBUG_LOGGING` | ❌ Optional | Enable debug console logs | `true` |

#### Getting Firebase Credentials:
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project → ⚙️ **Project Settings**
3. Scroll to **"Your apps"** → Click **Web app** (`</>`)
4. Copy values from the `firebaseConfig` object

### Backend Configuration (`backend/`)

#### Step 1: Copy Template
```bash
cd backend/
cp .env.template .env
```

#### Step 2: Configure Backend Variables

Edit `backend/.env` with your actual values:

| Variable | Required | Description | Example Value |
|----------|----------|-------------|---------------|
| **Application Settings** |
| `APP_NAME` | ❌ Optional | Application display name | `DrFirst Business Case Generator` |
| `APP_VERSION` | ❌ Optional | Application version | `1.0.0` |
| `ENVIRONMENT` | ✅ Yes | Environment mode | `development` |
| `DEBUG` | ❌ Optional | Enable debug mode | `true` |
| `LOG_LEVEL` | ❌ Optional | Logging verbosity | `INFO` |
| **API Settings** |
| `API_V1_PREFIX` | ❌ Optional | API route prefix | `/api/v1` |
| **Authentication** |
| `SECRET_KEY` | ✅ **CRITICAL** | JWT signing secret | Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ❌ Optional | Token expiration time | `30` |
| **Google Cloud** |
| `GOOGLE_CLOUD_PROJECT_ID` | ✅ Yes | GCP project ID | `drfirst-business-case-gen` |
| `GOOGLE_APPLICATION_CREDENTIALS` | ❌ Optional* | Service account key path | `path/to/service-account-key.json` |
| **Firebase** |
| `FIREBASE_PROJECT_ID` | ✅ Yes | Firebase project ID (same as GCP) | `drfirst-business-case-gen` |
| `FIREBASE_API_KEY` | ✅ Yes | Firebase server API key | `AIzaSyBSsGH6ihs8GINwee8f...` |
| **Firestore Collections** |
| `FIRESTORE_COLLECTION_USERS` | ❌ Optional | Users collection name | `users` |
| `FIRESTORE_COLLECTION_BUSINESS_CASES` | ❌ Optional | Business cases collection | `business_cases` |
| `FIRESTORE_COLLECTION_JOBS` | ❌ Optional | Jobs collection name | `jobs` |
| **Vertex AI** |
| `VERTEX_AI_LOCATION` | ❌ Optional | GCP region for Vertex AI | `us-central1` |
| `VERTEX_AI_MODEL_NAME` | ❌ Optional | AI model identifier | `gemini-2.0-flash-lite` |
| `VERTEX_AI_TEMPERATURE` | ❌ Optional | AI response randomness (0.0-1.0) | `0.6` |
| `VERTEX_AI_MAX_TOKENS` | ❌ Optional | Maximum response length | `4096` |
| `VERTEX_AI_TOP_P` | ❌ Optional | Nucleus sampling parameter | `0.9` |
| `VERTEX_AI_TOP_K` | ❌ Optional | Top-k sampling parameter | `40` |
| **CORS** |
| `BACKEND_CORS_ORIGINS` | ✅ Yes | Allowed frontend origins (comma-separated) | `http://localhost:4000,http://127.0.0.1:4000` |
| **Rate Limiting** |
| `DEFAULT_RATE_LIMIT` | ❌ Optional | Default API rate limit | `100/minute` |
| `BURST_RATE_LIMIT` | ❌ Optional | Burst rate limit | `20/second` |
| `REDIS_URL` | ❌ Optional | Redis URL for distributed rate limiting | `redis://localhost:6379` |

**\* Note**: `GOOGLE_APPLICATION_CREDENTIALS` is optional for local development if you use `gcloud auth application-default login`

#### Critical Security Note for SECRET_KEY:
```bash
# Generate a secure SECRET_KEY:
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
```

⚠️ **Never use the placeholder value in production!**

---

## Deployed Environments (Cloud Run)

### Frontend Deployment Strategy

Frontend environment variables are **build-time** variables. For different environments:

#### Option 1: Environment-Specific Build Files
Create environment-specific `.env` files:

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8000
VITE_ENVIRONMENT=development
VITE_ENABLE_DEBUG_LOGGING=true

# .env.staging  
VITE_API_BASE_URL=https://api-staging.drfirst-business-case.com
VITE_ENVIRONMENT=staging
VITE_ENABLE_DEBUG_LOGGING=false

# .env.production
VITE_API_BASE_URL=https://api.drfirst-business-case.com
VITE_ENVIRONMENT=production
VITE_ENABLE_DEBUG_LOGGING=false
```

Build with specific environment:
```bash
# Production build
cp .env.production .env
npm run build

# Staging build
cp .env.staging .env
npm run build
```

#### Option 2: CI/CD Environment Variables
Use your CI/CD pipeline to inject environment-specific values:
```bash
# In CI/CD pipeline for production
export VITE_API_BASE_URL="https://api.drfirst-business-case.com"
export VITE_ENVIRONMENT="production"
export VITE_ENABLE_DEBUG_LOGGING="false"
npm run build
```

### Backend Deployment (Google Cloud Run)

#### Non-Sensitive Variables
Set directly in Cloud Run environment variables:

```bash
gcloud run services update drfirst-backend \
  --set-env-vars="ENVIRONMENT=production" \
  --set-env-vars="DEBUG=false" \
  --set-env-vars="LOG_LEVEL=INFO" \
  --set-env-vars="GOOGLE_CLOUD_PROJECT_ID=drfirst-business-case-gen" \
  --set-env-vars="VERTEX_AI_LOCATION=us-central1" \
  --set-env-vars="VERTEX_AI_MODEL_NAME=gemini-2.0-flash-lite" \
  --set-env-vars="VERTEX_AI_TEMPERATURE=0.6" \
  --set-env-vars="VERTEX_AI_MAX_TOKENS=4096" \
  --set-env-vars="VERTEX_AI_TOP_P=0.9" \
  --set-env-vars="VERTEX_AI_TOP_K=40" \
  --set-env-vars="FIRESTORE_COLLECTION_USERS=users" \
  --set-env-vars="FIRESTORE_COLLECTION_BUSINESS_CASES=business_cases" \
  --set-env-vars="FIRESTORE_COLLECTION_JOBS=jobs" \
  --set-env-vars="DEFAULT_RATE_LIMIT=100/minute" \
  --set-env-vars="BURST_RATE_LIMIT=20/second" \
  --set-env-vars="BACKEND_CORS_ORIGINS=https://drfirst-business-case.com,https://staging.drfirst-business-case.com"
```

#### Sensitive Variables (Google Secret Manager)

**Step 1: Create Secrets**
```bash
# Create SECRET_KEY
echo -n "$(python -c 'import secrets; print(secrets.token_urlsafe(32))')" | \
  gcloud secrets create app-secret-key --data-file=-

# Create Firebase API Key
echo -n "AIzaSyBSsGH6ihs8GINwee8f..." | \
  gcloud secrets create firebase-api-key --data-file=-
```

**Step 2: Grant Cloud Run Access**
```bash
# Get the Cloud Run service account
PROJECT_ID="drfirst-business-case-gen"
SERVICE_ACCOUNT="$(gcloud run services describe drfirst-backend --format='value(spec.template.spec.serviceAccountName)')"

# If no custom service account is set, use the default compute service account
if [ -z "$SERVICE_ACCOUNT" ]; then
  PROJECT_NUMBER="$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')"
  SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
fi

# Grant Secret Manager access
gcloud secrets add-iam-policy-binding app-secret-key \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding firebase-api-key \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"
```

**Step 3: Configure Cloud Run with Secret References**
```bash
gcloud run services update drfirst-backend \
  --set-env-vars="SECRET_KEY=projects/drfirst-business-case-gen/secrets/app-secret-key/versions/latest" \
  --set-env-vars="FIREBASE_API_KEY=projects/drfirst-business-case-gen/secrets/firebase-api-key/versions/latest"
```

#### Service Account Authentication (Recommended)

For Cloud Run, **avoid** using `GOOGLE_APPLICATION_CREDENTIALS` file. Instead:

1. **Create a custom service account** for the Cloud Run service:
```bash
gcloud iam service-accounts create drfirst-backend-service \
  --display-name="DrFirst Backend Service Account"
```

2. **Grant necessary IAM roles**:
```bash
PROJECT_ID="drfirst-business-case-gen"
SERVICE_ACCOUNT_EMAIL="drfirst-backend-service@${PROJECT_ID}.iam.gserviceaccount.com"

# Grant required roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/datastore.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/firebase.admin"
```

3. **Deploy Cloud Run with the custom service account**:
```bash
gcloud run deploy drfirst-backend \
  --service-account="${SERVICE_ACCOUNT_EMAIL}" \
  --other-deployment-flags...
```

The backend code automatically uses the Cloud Run service account identity when `GOOGLE_APPLICATION_CREDENTIALS` is not set, leveraging Application Default Credentials (ADC).

---

## Key Variable Explanations

### BACKEND_CORS_ORIGINS
**Critical for frontend-backend communication.** This variable must contain all URLs from which your frontend will make API requests.

**Format**: Comma-separated list of URLs (no spaces)
```bash
# Development
BACKEND_CORS_ORIGINS=http://localhost:4000,http://127.0.0.1:4000

# Production
BACKEND_CORS_ORIGINS=https://drfirst-business-case.com,https://staging.drfirst-business-case.com
```

**Common Issues**:
- Missing `https://` prefix for production URLs
- Including trailing slashes
- Wrong port numbers for development

### SECRET_KEY (Backend)
**Critical for security.** Used for JWT token signing and other cryptographic operations.

**Requirements**:
- Must be unique per environment
- Minimum 32 characters
- Should be cryptographically random
- Never reuse between environments

**Generation**:
```bash
# Python method (recommended)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL method (alternative)
openssl rand -hex 32
```

### GOOGLE_APPLICATION_CREDENTIALS Best Practices

**Local Development**: 
- Use service account key file OR `gcloud auth application-default login`
- If using key file, never commit to version control
- Store in secure location outside project directory

**Cloud Run Production**:
- **DO NOT** use this variable
- Use service account identity with appropriate IAM roles
- Rely on Application Default Credentials (ADC)

---

## Security Best Practices

### Secrets Management

1. **Local Development**:
   - Copy `.env.template` to `.env` and configure
   - Add `.env` to `.gitignore` (already done)
   - Use strong, unique values for `SECRET_KEY`

2. **Production**:
   - Store sensitive variables in Google Secret Manager
   - Use Cloud Run service account with minimal required permissions
   - Rotate secrets regularly

3. **Never commit**:
   - Actual `.env` files
   - Service account key files
   - Any files containing real credentials

### Environment Separation

- Use different Firebase projects for dev/staging/production
- Use different GCP projects or clear resource separation
- Generate unique `SECRET_KEY` values for each environment
- Configure environment-specific CORS origins

---

## Verification Steps

### Frontend Verification

1. **Environment loaded correctly**:
```bash
cd frontend/
npm run dev
# Check browser console for environment variables
console.log(import.meta.env.VITE_API_BASE_URL)
```

2. **API connection working**:
   - Visit http://localhost:4000 (or your configured port)
   - Check Network tab for successful API calls to backend
   - Verify no CORS errors in console

### Backend Verification

1. **Server starts without errors**:
```bash
cd backend/
python -m uvicorn app.main:app --reload --port 8000
# Should start without configuration errors
```

2. **Environment variables loaded**:
```bash
# Add to a test endpoint temporarily:
from app.core.config import settings
print(f"Environment: {settings.environment}")
print(f"CORS Origins: {settings.cors_origins_list}")
```

3. **Firebase connection working**:
   - Attempt Google authentication from frontend
   - Check backend logs for successful Firebase token verification

4. **Vertex AI working**:
   - Create a test business case
   - Verify AI agent responses are generated

---

## Troubleshooting Common Issues

### Frontend Issues

**"VITE_* variable is undefined"**
- Ensure variable is prefixed with `VITE_`
- Restart development server after changing `.env`
- Check variable name spelling in both `.env` and code

**"Firebase configuration invalid"**
- Verify all Firebase variables are correct
- Check Firebase project settings match your `.env`
- Ensure authorized domains include your development URLs

### Backend Issues

**"SECRET_KEY not found"**
- Ensure `SECRET_KEY` is set in `.env` file
- Verify `.env` file is in the correct directory (`backend/`)
- Check for typos in variable name

**"Google Cloud authentication failed"**
- For local development: `gcloud auth application-default login`
- Verify `GOOGLE_CLOUD_PROJECT_ID` matches your actual GCP project
- Check service account has required permissions

**"CORS error from frontend"**
- Verify `BACKEND_CORS_ORIGINS` includes your frontend URL
- Check for exact URL match (including port, protocol)
- Restart backend server after changing CORS settings

**"Vertex AI permission denied"**
- Ensure service account has `roles/aiplatform.user` role
- Verify `VERTEX_AI_LOCATION` matches your GCP project's region
- Check Vertex AI API is enabled in GCP

### Production Deployment Issues

**"Secret not found in Cloud Run"**
- Verify secrets exist in Google Secret Manager
- Check IAM permissions for Cloud Run service account
- Ensure secret references use correct format

**"Environment variables not loading"**
- Use `gcloud run services describe` to verify variables are set
- Check variable names match exactly (case-sensitive)
- Verify no extra spaces in variable values

---

## Environment Variable Reference

### Frontend Variables (VITE_*)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `VITE_API_BASE_URL` | string | - | Backend API base URL |
| `VITE_API_VERSION` | string | `v1` | API version |
| `VITE_FIREBASE_API_KEY` | string | - | Firebase Web API key |
| `VITE_FIREBASE_AUTH_DOMAIN` | string | - | Firebase auth domain |
| `VITE_FIREBASE_PROJECT_ID` | string | - | Firebase project ID |
| `VITE_ENVIRONMENT` | string | `development` | Environment mode |
| `VITE_ENABLE_ANALYTICS` | boolean | `false` | Enable analytics |
| `VITE_ENABLE_DEBUG_LOGGING` | boolean | `true` | Debug logging |

### Backend Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `APP_NAME` | string | `DrFirst Business Case Generator` | App name |
| `APP_VERSION` | string | `1.0.0` | App version |
| `ENVIRONMENT` | string | `development` | Environment mode |
| `DEBUG` | boolean | `true` | Debug mode |
| `LOG_LEVEL` | string | `INFO` | Log level |
| `API_V1_PREFIX` | string | `/api/v1` | API prefix |
| `SECRET_KEY` | string | **REQUIRED** | JWT secret |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | integer | `30` | Token expiry |
| `GOOGLE_CLOUD_PROJECT_ID` | string | `drfirst-business-case-gen` | GCP project |
| `GOOGLE_APPLICATION_CREDENTIALS` | string | `None` | Service account path |
| `FIREBASE_PROJECT_ID` | string | `drfirst-business-case-gen` | Firebase project |
| `FIREBASE_API_KEY` | string | `None` | Firebase API key |
| `FIRESTORE_COLLECTION_USERS` | string | `users` | Users collection |
| `FIRESTORE_COLLECTION_BUSINESS_CASES` | string | `business_cases` | Cases collection |
| `FIRESTORE_COLLECTION_JOBS` | string | `jobs` | Jobs collection |
| `VERTEX_AI_LOCATION` | string | `us-central1` | AI region |
| `VERTEX_AI_MODEL_NAME` | string | `gemini-2.0-flash-lite` | AI model |
| `VERTEX_AI_TEMPERATURE` | float | `0.6` | AI temperature |
| `VERTEX_AI_MAX_TOKENS` | integer | `4096` | Max tokens |
| `VERTEX_AI_TOP_P` | float | `0.9` | Top-p sampling |
| `VERTEX_AI_TOP_K` | integer | `40` | Top-k sampling |
| `BACKEND_CORS_ORIGINS` | string | **REQUIRED** | CORS origins |
| `DEFAULT_RATE_LIMIT` | string | `100/minute` | Rate limit |
| `BURST_RATE_LIMIT` | string | `20/second` | Burst limit |
| `REDIS_URL` | string | `None` | Redis URL |

---

**Last Updated:** January 2025  
**Next Review:** After production deployment 