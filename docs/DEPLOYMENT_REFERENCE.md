# DrFirst Business Case Generator - Deployment Reference

**Project:** DrFirst Agentic Business Case Generator  
**Environment:** Development/Staging  
**Deployment Date:** January 2025  
**Status:** ✅ **SUCCESSFULLY DEPLOYED**

---

## 🚀 Quick Access

| Service | URL | Status |
|---------|-----|--------|
| **Frontend** | https://drfirst-business-case-gen.web.app | ✅ Active |
| **Backend API** | https://drfirst-backend-dev-782346002710.us-central1.run.app | ✅ Active |
| **Firebase Console** | https://console.firebase.google.com/project/drfirst-business-case-gen/overview | ✅ Active |
| **Cloud Console** | https://console.cloud.google.com/run?project=drfirst-business-case-gen | ✅ Active |

---

## 📋 Deployment Overview

### Infrastructure
- **GCP Project:** `drfirst-business-case-gen`
- **Region:** `us-central1`
- **Backend:** Google Cloud Run
- **Frontend:** Firebase Hosting
- **Database:** Firestore with security rules
- **Secrets:** Google Secret Manager

### Deployed Components
1. ✅ **Firestore Security Rules** - Production-ready RBAC
2. ✅ **Backend API** - Docker container on Cloud Run
3. ✅ **Frontend SPA** - React/Vite build on Firebase Hosting
4. ✅ **Environment Configuration** - All variables configured
5. ✅ **CORS Configuration** - Cross-origin requests enabled

---

## 🔧 Service Details

### Backend (Cloud Run)
- **Service Name:** `drfirst-backend-dev`
- **Image:** `us-central1-docker.pkg.dev/drfirst-business-case-gen/drfirst-backend/drfirst-backend:dev`
- **Port:** 8000
- **Memory:** 1Gi
- **CPU:** 1
- **Concurrency:** Default
- **Authentication:** Allow unauthenticated (for initial testing)

#### Environment Variables
| Variable | Source | Description |
|----------|--------|-------------|
| `ENVIRONMENT` | Direct | `development` |
| `GOOGLE_CLOUD_PROJECT_ID` | Direct | `drfirst-business-case-gen` |
| `FIREBASE_PROJECT_ID` | Direct | `drfirst-business-case-gen` |
| `VERTEX_AI_LOCATION` | Direct | `us-central1` |
| `VERTEX_AI_MODEL_NAME` | Direct | `gemini-2.0-flash-lite` |
| `LOG_LEVEL` | Direct | `INFO` |
| `DEBUG` | Direct | `false` |
| `SECRET_KEY` | Secret Manager | `app-secret-key:latest` |
| `FIREBASE_API_KEY` | Secret Manager | `firebase-api-key:latest` |
| `BACKEND_CORS_ORIGINS` | Direct | `http://localhost:4000,https://drfirst-business-case-gen.web.app` |

### Frontend (Firebase Hosting)
- **Hosting ID:** `drfirst-business-case-gen`
- **Build Directory:** `frontend/dist`
- **Framework:** React + Vite
- **Environment:** Development

#### Build-time Variables
| Variable | Value | Description |
|----------|-------|-------------|
| `VITE_API_BASE_URL` | `https://drfirst-backend-dev-782346002710.us-central1.run.app` | Backend API URL |
| `VITE_API_VERSION` | `v1` | API version |
| `VITE_FIREBASE_API_KEY` | `AIzaSyBSsGH6ihs8GINwee8fBRGI84P3LqbVQ4w` | Firebase Web API key |
| `VITE_FIREBASE_AUTH_DOMAIN` | `drfirst-business-case-gen.firebaseapp.com` | Firebase auth domain |
| `VITE_FIREBASE_PROJECT_ID` | `drfirst-business-case-gen` | Firebase project ID |
| `VITE_ENVIRONMENT` | `development` | Environment mode |
| `VITE_ENABLE_ANALYTICS` | `false` | Analytics disabled |
| `VITE_ENABLE_DEBUG_LOGGING` | `true` | Debug logging enabled |

---

## 🛡️ Security Configuration

### Firestore Security Rules
- **Status:** ✅ Deployed
- **Source:** `FIRESTORE_SECURITY_RULES_ANALYSIS.md` - Complete Rules Implementation
- **Features:**
  - Role-based access control (RBAC)
  - Workflow-based permissions
  - Admin collection protection
  - Audit log security
  - User ownership validation

### Secret Manager
| Secret Name | Description | Usage |
|-------------|-------------|-------|
| `app-secret-key` | Application JWT signing key | Backend authentication |
| `firebase-api-key` | Firebase server API key | Backend Firebase operations |

### IAM Permissions
- **Cloud Run Service Account:** `782346002710-compute@developer.gserviceaccount.com`
- **Permissions:** `roles/secretmanager.secretAccessor` for both secrets

---

## 📖 Deployment Process

### Prerequisites
1. ✅ gcloud CLI authenticated
2. ✅ Firebase CLI authenticated
3. ✅ Docker configured for Artifact Registry
4. ✅ Required APIs enabled:
   - Cloud Run API
   - Artifact Registry API
   - Secret Manager API
   - Firestore API

### Step-by-Step Deployment

#### 1. Firestore Security Rules
```bash
# From project root
firebase use drfirst-business-case-gen
firebase deploy --only firestore:rules
```

#### 2. Backend Deployment
```bash
# Build and push Docker image
cd backend
docker buildx build --platform linux/amd64 -t drfirst-backend:dev . --load
docker tag drfirst-backend:dev us-central1-docker.pkg.dev/drfirst-business-case-gen/drfirst-backend/drfirst-backend:dev
docker push us-central1-docker.pkg.dev/drfirst-business-case-gen/drfirst-backend/drfirst-backend:dev

# Create secrets
python3 -c "import secrets; print(secrets.token_urlsafe(32))" | gcloud secrets create app-secret-key --data-file=- --project=drfirst-business-case-gen
echo -n "AIzaSyBSsGH6ihs8GINwee8fBRGI84P3LqbVQ4w" | gcloud secrets create firebase-api-key --data-file=- --project=drfirst-business-case-gen

# Grant permissions
gcloud secrets add-iam-policy-binding app-secret-key --member="serviceAccount:782346002710-compute@developer.gserviceaccount.com" --role="roles/secretmanager.secretAccessor" --project=drfirst-business-case-gen
gcloud secrets add-iam-policy-binding firebase-api-key --member="serviceAccount:782346002710-compute@developer.gserviceaccount.com" --role="roles/secretmanager.secretAccessor" --project=drfirst-business-case-gen

# Deploy to Cloud Run
gcloud run deploy drfirst-backend-dev \
  --image=us-central1-docker.pkg.dev/drfirst-business-case-gen/drfirst-backend/drfirst-backend:dev \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --memory=1Gi \
  --cpu=1 \
  --port=8000 \
  --set-env-vars="ENVIRONMENT=development,GOOGLE_CLOUD_PROJECT_ID=drfirst-business-case-gen,FIREBASE_PROJECT_ID=drfirst-business-case-gen,VERTEX_AI_LOCATION=us-central1,VERTEX_AI_MODEL_NAME=gemini-2.0-flash-lite,LOG_LEVEL=INFO,DEBUG=false" \
  --set-secrets="SECRET_KEY=app-secret-key:latest,FIREBASE_API_KEY=firebase-api-key:latest" \
  --project=drfirst-business-case-gen
```

#### 3. Frontend Deployment
```bash
# Configure environment
cd frontend
cp .env.development .env

# Build and deploy
npm ci
npx vite build
cd ..
firebase deploy --only hosting
```

#### 4. Update CORS (after frontend deployment)
```bash
# Create CORS config file
echo 'BACKEND_CORS_ORIGINS: "http://localhost:4000,https://drfirst-business-case-gen.web.app"' > cors_env.yaml

# Update Cloud Run service
gcloud run services update drfirst-backend-dev --env-vars-file=cors_env.yaml --region=us-central1 --project=drfirst-business-case-gen

# Cleanup
rm cors_env.yaml
```

---

## 🧪 Testing & Verification

### Automated Tests
```bash
# Backend health check
curl -s -o /dev/null -w "%{http_code}" https://drfirst-backend-dev-782346002710.us-central1.run.app/

# Frontend accessibility
curl -s -o /dev/null -w "%{http_code}" https://drfirst-business-case-gen.web.app

# API connectivity
curl -s https://drfirst-backend-dev-782346002710.us-central1.run.app/
```

### Manual Testing Checklist
- [ ] **Frontend loads** at https://drfirst-business-case-gen.web.app
- [ ] **Authentication works** (Google sign-in)
- [ ] **API calls succeed** (check browser network tab)
- [ ] **CORS configured** (no cross-origin errors)
- [ ] **Firestore rules active** (role-based access working)

### Expected Test Results
- Backend health: `200 OK`
- Frontend load: `200 OK`
- API response: `{"message":"DrFirst Business Case Generator API is running"}`
- No CORS errors in browser console
- Firestore operations respect security rules

---

## 🚨 Troubleshooting

### Common Issues

#### Backend Not Starting
- **Symptom:** Cloud Run deployment fails
- **Check:** Container logs in Cloud Console
- **Common Causes:** Port mismatch, missing environment variables, secret access issues

#### CORS Errors
- **Symptom:** Frontend can't reach backend
- **Check:** `BACKEND_CORS_ORIGINS` environment variable
- **Solution:** Ensure both localhost and deployed frontend URLs are included

#### Firebase Authentication Issues
- **Symptom:** Login doesn't work
- **Check:** Authorized domains in Firebase Console
- **Solution:** Add deployment domain to authorized domains

#### Secret Access Denied
- **Symptom:** Backend can't access secrets
- **Check:** IAM permissions for Cloud Run service account
- **Solution:** Grant `roles/secretmanager.secretAccessor` role

### Debug Commands
```bash
# Check Cloud Run logs
gcloud logs read --project=drfirst-business-case-gen --service=drfirst-backend-dev

# Check environment variables
gcloud run services describe drfirst-backend-dev --region=us-central1 --project=drfirst-business-case-gen

# Test backend endpoints
curl -v https://drfirst-backend-dev-782346002710.us-central1.run.app/api/v1/health

# Check Firestore rules
firebase firestore:rules:get --project=drfirst-business-case-gen
```

---

## 🔄 Update Process

### Updating Backend
```bash
# Rebuild and push new image
cd backend
docker buildx build --platform linux/amd64 -t drfirst-backend:dev . --load
docker tag drfirst-backend:dev us-central1-docker.pkg.dev/drfirst-business-case-gen/drfirst-backend/drfirst-backend:dev
docker push us-central1-docker.pkg.dev/drfirst-business-case-gen/drfirst-backend/drfirst-backend:dev

# Deploy new revision
gcloud run deploy drfirst-backend-dev --image=us-central1-docker.pkg.dev/drfirst-business-case-gen/drfirst-backend/drfirst-backend:dev --region=us-central1 --project=drfirst-business-case-gen
```

### Updating Frontend
```bash
# Rebuild and deploy
cd frontend
npm run build
cd ..
firebase deploy --only hosting
```

### Updating Firestore Rules
```bash
# Deploy updated rules
firebase deploy --only firestore:rules
```

---

## 📊 Monitoring & Maintenance

### Key Metrics to Monitor
- **Cloud Run:** Request count, latency, error rate, memory usage
- **Firebase Hosting:** Page views, bandwidth, cache hit ratio
- **Firestore:** Read/write operations, security rule violations

### Recommended Monitoring Setup
1. **Cloud Monitoring:** Set up alerts for high error rates or latency
2. **Firebase Analytics:** Monitor user engagement and errors
3. **Log Analysis:** Regular review of Cloud Run and Firebase logs

### Backup Strategy
- **Firestore:** Enable automatic backups in Firebase Console
- **Code:** Ensure all configurations are in version control
- **Secrets:** Document secret recreation process

---

## 📝 Notes

### Important Considerations
- This is a **development/staging** deployment with relaxed security settings
- For production, consider:
  - Enabling authentication on Cloud Run
  - Setting up API Gateway
  - Implementing proper monitoring and alerting
  - Using dedicated service accounts with minimal permissions
  - Setting up CI/CD pipelines

### Version Information
- **Backend Image Tag:** `dev`
- **Frontend Build:** Development configuration
- **Firestore Rules:** Production-ready security rules
- **Firebase Project:** `drfirst-business-case-gen`

### Contact Information
- **Project Repository:** [Repository URL]
- **Documentation:** `docs/` directory
- **Deployment Guide:** This document

---

*Last Updated: January 2025*  
*Deployment Status: ✅ Active and Operational* 