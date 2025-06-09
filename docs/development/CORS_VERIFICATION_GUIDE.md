# CORS Verification Guide - DrFirst Business Case Generator

**Task:** 10.4.2 - Verify Deployed Backend CORS Configuration  
**Version:** 1.0.0  
**Last Updated:** June 8, 2025

---

## Overview

This guide provides comprehensive instructions for verifying that the Cross-Origin Resource Sharing (CORS) configuration on deployed backend FastAPI applications correctly allows requests from authorized frontend domains and blocks unauthorized ones.

## Prerequisites

- Backend deployed to Cloud Run (e.g., `https://your-backend-staging.run.app`)
- Frontend deployed (e.g., Firebase Hosting at `https://your-frontend-staging.web.app`)
- `BACKEND_CORS_ORIGINS` environment variable configured according to [ENVIRONMENT_SETUP.md](./ENVIRONMENT_SETUP.md)
- Python 3.11+ and `requests` library for automated testing
- Access to browser developer tools

---

## Verification Methods

### Method 1: Automated CORS Verification Script

**Recommended for comprehensive testing**

#### Usage

```bash
# Install dependencies
pip install requests

# Test local development setup
python scripts/cors_verification.py --local

# Test deployed environment
python scripts/cors_verification.py \
  --backend-url https://your-backend-staging.run.app \
  --frontend-url https://your-frontend-staging.web.app

# Test with multiple authorized origins
python scripts/cors_verification.py \
  --backend-url https://your-backend-staging.run.app \
  --authorized-origins https://your-frontend-staging.web.app https://your-admin-staging.web.app

# Save detailed results
python scripts/cors_verification.py \
  --backend-url https://your-backend-staging.run.app \
  --frontend-url https://your-frontend-staging.web.app \
  --output cors_test_results.json
```

#### What It Tests

1. **Backend Health Check**: Verifies backend is accessible
2. **CORS Configuration**: Retrieves and validates configured origins
3. **Authorized Origins**: Tests that allowed origins can make requests
4. **Unauthorized Origins**: Tests that disallowed origins are blocked
5. **Preflight Requests**: Tests CORS preflight (OPTIONS) behavior
6. **Authentication Headers**: Tests requests with Authorization headers

#### Expected Results

```
🎉 CORS CONFIGURATION IS WORKING CORRECTLY!
✅ All authorized origins are allowed
✅ All unauthorized origins are blocked
```

### Method 2: Browser-Based Testing

**Good for visual verification and real browser behavior**

#### Step 1: Test Authorized Frontend

1. Open your deployed frontend in a browser
2. Open Developer Tools (F12) → Network tab
3. Perform actions that trigger API calls:
   - Log in with Google
   - Load dashboard
   - Open case details
   - Create new case

**Expected Results:**
- ✅ API calls succeed (HTTP 200 OK)
- ✅ Response headers include `Access-Control-Allow-Origin: https://your-frontend-domain.web.app`
- ✅ No CORS errors in browser console

#### Step 2: Test Unauthorized Origin

1. Open `scripts/cors_test.html` in a browser
2. Serve it from a different port/domain than your authorized frontend:
   ```bash
   # Option A: Simple HTTP server
   cd scripts/
   python -m http.server 5000
   # Then open http://localhost:5000/cors_test.html
   
   # Option B: Use any other local server
   npx serve scripts/ -p 5001
   # Then open http://localhost:5001/cors_test.html
   ```
3. Configure the backend URL in the test page
4. Run all CORS tests

**Expected Results:**
- ❌ All requests should fail with CORS errors
- ✅ Browser console shows CORS policy violations
- ✅ Test page confirms requests were blocked

### Method 3: Command Line Testing (curl/httpie)

**Quick verification for specific scenarios**

#### Test with curl

```bash
# Test authorized origin
curl -H "Origin: https://your-frontend-staging.web.app" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: authorization,content-type" \
     -X OPTIONS \
     https://your-backend-staging.run.app/api/v1/auth/me

# Test unauthorized origin  
curl -H "Origin: https://unauthorized-domain.com" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: authorization,content-type" \
     -X OPTIONS \
     https://your-backend-staging.run.app/api/v1/auth/me

# Test simple request with origin header
curl -H "Origin: https://your-frontend-staging.web.app" \
     https://your-backend-staging.run.app/health
```

#### Expected curl Results

**Authorized Origin:**
```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://your-frontend-staging.web.app
Access-Control-Allow-Methods: *
Access-Control-Allow-Headers: *
Access-Control-Allow-Credentials: true
```

**Unauthorized Origin:**
```
HTTP/1.1 200 OK
# No Access-Control-Allow-Origin header or different value
```

---

## Configuration Verification

### 1. Check Backend CORS Code

Verify the CORS middleware configuration in `backend/app/main.py`:

```python
# Should use settings.cors_origins_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # ← This line
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Check Environment Variable

#### Local Development
```bash
cd backend/
cat .env | grep BACKEND_CORS_ORIGINS
```

#### Cloud Run Deployment
```bash
gcloud run services describe your-backend-service \
  --region=us-central1 \
  --format="get(spec.template.spec.containers[0].env[].name,spec.template.spec.containers[0].env[].value)" \
  | grep CORS
```

### 3. Verify Origins Format

Ensure `BACKEND_CORS_ORIGINS` is properly formatted:

```bash
# Correct format (comma-separated, no spaces)
BACKEND_CORS_ORIGINS=https://domain1.com,https://domain2.com,http://localhost:4000

# Incorrect formats
BACKEND_CORS_ORIGINS="https://domain1.com, https://domain2.com"  # ❌ Spaces
BACKEND_CORS_ORIGINS=https://domain1.com/                        # ❌ Trailing slash
BACKEND_CORS_ORIGINS=domain1.com                                 # ❌ Missing protocol
```

---

## Common Issues and Solutions

### Issue 1: Frontend Can't Reach Backend

**Symptoms:**
- All API calls fail from authorized frontend
- Network tab shows CORS errors
- Console shows: `Access to fetch at '...' has been blocked by CORS policy`

**Solutions:**
1. Check `BACKEND_CORS_ORIGINS` includes the exact frontend URL
2. Verify no trailing slashes or extra spaces
3. Ensure protocol (https/http) matches exactly
4. Restart backend service after CORS changes

### Issue 2: Unauthorized Domains Not Blocked

**Symptoms:**
- Requests from test page succeed
- No CORS errors when they should occur
- `Access-Control-Allow-Origin: *` in responses

**Solutions:**
1. Check if `BACKEND_CORS_ORIGINS` contains `*` (wildcard)
2. Verify CORS middleware is using `settings.cors_origins_list`
3. Ensure environment variable is loaded correctly
4. Check for multiple CORS middleware configurations

### Issue 3: Preflight Requests Failing

**Symptoms:**
- Simple GET requests work, but POST/PUT/DELETE fail
- OPTIONS requests return errors
- Requests with custom headers fail

**Solutions:**
1. Verify `allow_methods=["*"]` in CORS middleware
2. Check `allow_headers=["*"]` for custom headers
3. Ensure `allow_credentials=True` for authenticated requests
4. Test preflight specifically with the verification script

### Issue 4: Localhost Development Issues

**Symptoms:**
- Frontend can't reach backend in local development
- Mixed content warnings
- Port-specific CORS errors

**Solutions:**
1. Add all development ports to `BACKEND_CORS_ORIGINS`:
   ```
   http://localhost:4000,http://localhost:4002,http://localhost:4003,http://127.0.0.1:4000
   ```
2. Use consistent protocol (http for local, https for production)
3. Consider using `127.0.0.1` instead of `localhost` if needed

---

## Environment-Specific Configurations

### Development
```bash
BACKEND_CORS_ORIGINS=http://localhost:4000,http://localhost:4002,http://localhost:4003,http://127.0.0.1:4000
```

### Staging
```bash
BACKEND_CORS_ORIGINS=https://staging-frontend.web.app,https://staging-admin.web.app
```

### Production
```bash
BACKEND_CORS_ORIGINS=https://drfirst-business-case.com,https://admin.drfirst-business-case.com
```

---

## Security Best Practices

### ✅ Do's

1. **Specific Origins**: Always specify exact domain names
2. **Environment Separation**: Use different origins for dev/staging/prod
3. **Regular Testing**: Verify CORS after each deployment
4. **Monitor Access**: Check logs for unauthorized access attempts
5. **Document Changes**: Update this guide when adding new domains

### ❌ Don'ts

1. **Never use `*`**: Avoid wildcard origins in production
2. **No HTTP in Production**: Only use HTTPS origins for deployed environments
3. **No Trailing Slashes**: Keep origins clean (e.g., `https://domain.com`)
4. **No Spaces**: Ensure comma-separated format without spaces
5. **No Debug Origins**: Remove development URLs from production

---

## Verification Checklist

### Before Deployment
- [ ] `BACKEND_CORS_ORIGINS` environment variable is set
- [ ] Origins match deployed frontend URLs exactly
- [ ] No wildcard (`*`) origins in production
- [ ] CORS middleware uses `settings.cors_origins_list`

### After Deployment
- [ ] Run automated CORS verification script
- [ ] Test frontend can make API calls successfully
- [ ] Verify CORS headers in browser Network tab
- [ ] Test unauthorized origins are blocked
- [ ] Check browser console for CORS errors
- [ ] Test both simple and preflight requests

### Security Verification
- [ ] Only authorized domains can make requests
- [ ] Unauthorized domains receive CORS errors
- [ ] No `Access-Control-Allow-Origin: *` in responses
- [ ] Preflight requests work for authorized origins
- [ ] Authentication headers are properly handled

---

## Troubleshooting Commands

### Check Backend Status
```bash
curl https://your-backend.run.app/health
curl https://your-backend.run.app/api/v1/diagnostics/status
```

### Check CORS Headers
```bash
curl -I -H "Origin: https://your-frontend.web.app" \
     https://your-backend.run.app/health
```

### Check Environment Variables
```bash
gcloud run services describe your-backend-service \
  --region=us-central1 \
  --format="value(spec.template.spec.containers[0].env[].name,spec.template.spec.containers[0].env[].value)"
```

### Check Logs
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=your-backend-service" \
  --limit=50 --format="table(timestamp,textPayload)"
```

---

## Success Criteria

After completing CORS verification, you should confirm:

✅ **Authorized Frontend Access**
- Deployed frontend can make all API calls
- No CORS errors in browser console
- Correct `Access-Control-Allow-Origin` headers

✅ **Unauthorized Access Blocked**
- Test page from different origin shows CORS errors
- Command line tests with fake origins fail appropriately
- No security vulnerabilities detected

✅ **Code Configuration**
- CORS middleware uses environment variable
- Settings are loaded correctly
- No hardcoded origins in source code

✅ **Environment Consistency**
- Staging and production have appropriate origins
- Development setup works locally
- Documentation matches actual configuration

---

## Resources

- [ENVIRONMENT_SETUP.md](./ENVIRONMENT_SETUP.md) - Complete environment setup guide
- [MDN CORS Documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [FastAPI CORS Documentation](https://fastapi.tiangolo.com/tutorial/cors/)
- [Google Cloud Run Environment Variables](https://cloud.google.com/run/docs/configuring/environment-variables)

---

**Last Updated:** January 2025  
**Next Review:** After major deployment changes 