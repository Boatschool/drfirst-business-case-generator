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
5. [Environment Variable Reference](#environment-variable-reference)
6. [Security Best Practices](#security-best-practices)
7. [Troubleshooting](#troubleshooting)

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

#### Option 1: Environment-Specific Build
```bash
# Production build with specific .env file
cp .env.production .env
npm run build

# Staging build with specific .env file  
cp .env.staging .env
npm run build
```

#### Option 2: CI/CD Environment Variables
Use your CI/CD pipeline to set environment-specific values:
```bash
# In CI/CD pipeline
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
  --set-env-vars="LOG_LEVEL=INFO" \
  --set-env-vars="GOOGLE_CLOUD_PROJECT_ID=drfirst-business-case-gen" \
  --set-env-vars="VERTEX_AI_LOCATION=us-central1" \
  --set-env-vars="VERTEX_AI_MODEL_NAME=gemini-2.0-flash-lite" \
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

1. **Create a dedicated service account** for the Cloud Run service
2. **Grant necessary IAM roles**:
   - `Vertex AI User` (for AI model access)
   - `Firebase Rules System` (for Firestore access)
   - `Secret Manager Secret Accessor` (for secrets access)
3. **Use Application Default Credentials (ADC)**

The backend code automatically uses the Cloud Run service account identity when `GOOGLE_APPLICATION_CREDENTIALS` is not set.

---

## Environment Variable Reference

### Frontend Variables (VITE_*)

All frontend environment variables must be prefixed with `VITE_` to be included in the build:

- **Build-time**: Values are embedded into the JavaScript bundle during `npm run build`
- **Client-side**: Accessible via `import.meta.env.VITE_VARIABLE_NAME`
- **TypeScript**: Defined in `frontend/src/vite-env.d.ts`

### Backend Variables

Backend variables are loaded at runtime using Pydantic BaseSettings:

- **Runtime**: Values are read from environment or `.env` file when the application starts
- **Type-safe**: Automatically validated and type-converted by Pydantic
- **Hierarchical**: Environment variables override `.env` file values

### Special Variable Behaviors

#### BACKEND_CORS_ORIGINS
```bash
# Format: Comma-separated list of URLs
BACKEND_CORS_ORIGINS="http://localhost:4000,https://frontend.example.com,https://staging.example.com"

# Parsed automatically into a Python list
# ['http://localhost:4000', 'https://frontend.example.com', 'https://staging.example.com']
```

#### SECRET_KEY Security Requirements
- **Length**: Minimum 32 characters
- **Randomness**: Cryptographically secure random generation
- **Uniqueness**: Different value for each environment
- **Storage**: Google Secret Manager for production

---

## Security Best Practices

### ✅ Do's

- ✅ **Use Secret Manager** for production secrets
- ✅ **Generate unique SECRET_KEY** for each environment
- ✅ **Rotate secrets regularly** (quarterly recommended)
- ✅ **Use service account identity** for Cloud Run authentication
- ✅ **Validate required variables** at application startup
- ✅ **Use HTTPS** for all production origins in CORS

### ❌ Don'ts

- ❌ **Never commit `.env` files** to version control
- ❌ **Never use placeholder values** in production
- ❌ **Never hardcode secrets** in source code
- ❌ **Never use development secrets** in production
- ❌ **Never expose internal URLs** in frontend CORS origins

### Production Checklist

Before deploying to production:

- [ ] All secrets stored in Google Secret Manager
- [ ] Unique SECRET_KEY generated and stored securely
- [ ] CORS origins limited to actual frontend domains
- [ ] Debug logging disabled (`VITE_ENABLE_DEBUG_LOGGING=false`)
- [ ] Environment set to `production`
- [ ] Service account permissions minimized (principle of least privilege)
- [ ] All required environment variables configured
- [ ] Application starts successfully with production configuration

---

## Troubleshooting

### Common Issues

#### Frontend Not Connecting to Backend
```bash
# Check VITE_API_BASE_URL in frontend/.env
VITE_API_BASE_URL=http://localhost:8000  # Must match backend port

# Check CORS configuration in backend/.env
BACKEND_CORS_ORIGINS=http://localhost:4000,http://127.0.0.1:4000  # Must include frontend URL
```

#### Firebase Authentication Errors
```bash
# Verify Firebase credentials in frontend/.env
VITE_FIREBASE_API_KEY=AIzaSy...     # Must be actual API key, not placeholder
VITE_FIREBASE_PROJECT_ID=your-project  # Must match Firebase console project

# Check authorized domains in Firebase Console:
# Authentication → Settings → Authorized domains
# Must include: localhost, localhost:4000, your-domain.com
```

#### Backend SECRET_KEY Validation Error
```bash
# Error: Field required for secret_key
# Solution: Ensure SECRET_KEY is set in backend/.env
SECRET_KEY=generated-secure-key-here  # Not placeholder value
```

#### CORS Errors in Browser
```bash
# Error: CORS policy blocked request
# Solution: Update BACKEND_CORS_ORIGINS in backend/.env
BACKEND_CORS_ORIGINS=http://localhost:4000  # Add your frontend URL
```

#### Google Cloud Authentication Issues
```bash
# For local development, authenticate with:
gcloud auth application-default login

# For Cloud Run, ensure service account has proper IAM roles:
# - Vertex AI User
# - Firebase Rules System  
# - Secret Manager Secret Accessor (if using secrets)
```

### Validation Commands

#### Frontend Environment Check
```bash
cd frontend/
npm run dev
# Check browser console for Firebase config debug output
```

#### Backend Environment Check
```bash
cd backend/
source venv/bin/activate
python -c "from app.core.config import settings; print('✅ Configuration loaded successfully')"
```

#### CORS Configuration Test
```bash
cd backend/
source venv/bin/activate
python -c "from app.core.config import settings; print('CORS Origins:', settings.cors_origins_list)"
```

### Getting Help

If you encounter issues not covered here:

1. **Check application logs** for specific error messages
2. **Verify all required variables** are set correctly
3. **Test with minimal configuration** first
4. **Review Google Cloud IAM permissions** for Cloud Run service account
5. **Consult Firebase Console** for authentication and Firestore configuration

---

## Appendix

### Complete Local Development .env Examples

#### frontend/.env (Development)
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_API_VERSION=v1
VITE_FIREBASE_API_KEY=AIzaSyBSsGH6ihs8GINwee8fBRGI84P3LqbVQ4w
VITE_FIREBASE_AUTH_DOMAIN=drfirst-business-case-gen.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=drfirst-business-case-gen
VITE_ENVIRONMENT=development
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_DEBUG_LOGGING=true
```

#### backend/.env (Development)
```bash
# Application Settings
APP_NAME=DrFirst Business Case Generator
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# API Settings
API_V1_PREFIX=/api/v1

# Authentication Settings
SECRET_KEY=60MUPLLELegYZPxBGuVioMdAH2-GlqwAn0_UO91-BGs
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google Cloud Settings
GOOGLE_CLOUD_PROJECT_ID=drfirst-business-case-gen
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# Firebase Settings
FIREBASE_PROJECT_ID=drfirst-business-case-gen
FIREBASE_API_KEY=AIzaSyBSsGH6ihs8GINwee8fBRGI84P3LqbVQ4w

# Firestore Settings
FIRESTORE_COLLECTION_USERS=users
FIRESTORE_COLLECTION_BUSINESS_CASES=business_cases
FIRESTORE_COLLECTION_JOBS=jobs

# VertexAI Settings
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL_NAME=gemini-2.0-flash-lite
VERTEX_AI_TEMPERATURE=0.6
VERTEX_AI_MAX_TOKENS=4096
VERTEX_AI_TOP_P=0.9
VERTEX_AI_TOP_K=40

# CORS Settings
BACKEND_CORS_ORIGINS=http://localhost:4000,http://127.0.0.1:4000
```

---

**Last Updated:** January 2025  
**Version:** 1.0.0  
**Maintainer:** DevOps Configuration Team 