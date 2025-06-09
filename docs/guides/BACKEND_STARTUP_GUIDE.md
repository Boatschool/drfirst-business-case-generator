# DrFirst Backend Startup Guide

## Quick Start

### From Project Root (Recommended)
```bash
./scripts/start_backend.sh
```

### From Backend Directory
```bash
cd backend
./start_server_fixed.sh
```

## 🧪 Comprehensive Pre-Startup Testing

The startup script now includes **8 comprehensive tests** that validate your environment before starting the server:

### Test 1: 🖥️ System Environment Validation
- **Platform compatibility** - Checks operating system and architecture
- **Python version** - Ensures Python 3.8+ compatibility
- **Process information** - Logs system details for debugging

### Test 2: 🔧 Environment Variables Validation  
- **PYTHONPATH** - Verifies module path configuration
- **GOOGLE_APPLICATION_CREDENTIALS** - Validates credentials file path and existence
- **Required variables** - Ensures all critical environment variables are set

### Test 3: 📦 Python Dependencies Check
- **Critical packages** - Validates FastAPI, Firebase Admin, VertexAI, etc.
- **Import verification** - Tests that all required packages can be imported
- **Missing package detection** - Provides clear guidance for installation

### Test 4: 🌐 Port Availability Check
- **Port 8000 status** - Checks if the required port is available
- **Conflict detection** - Identifies if server is already running
- **Network connectivity** - Basic network stack validation

### Test 5: 🔐 Google Cloud Credentials Validation
- **File format** - Validates JSON structure of credentials file
- **Required fields** - Ensures all necessary credential fields are present
- **Project information** - Displays project ID and service account details

### Test 6: 💾 Disk Space Check
- **Available space** - Reports free disk space in GB
- **Usage warnings** - Alerts if disk space is critically low
- **Storage health** - Monitors disk usage percentage

### Test 7: 📦 Critical Application Imports
- **FastAPI app** - Validates main application can be imported
- **Authentication service** - Tests Firebase Auth service import
- **VertexAI service** - Validates AI service availability
- **API routes** - Ensures routing modules are accessible
- **Dependencies** - Tests core dependency injection system

### Test 8: 🔄 Resource Management Mechanisms
- **Singleton reset** - Tests singleton state management (Issue #3 fix)
- **Resource cleanup** - Validates comprehensive cleanup mechanisms (Issue #5 fix)
- **Memory management** - Ensures proper resource lifecycle management

## Service Health Monitoring

### Health Check Endpoints
- **Basic Health**: `GET http://localhost:8000/health`
- **Detailed Health**: `GET http://localhost:8000/api/v1/diagnostics/health`
- **Full Diagnostics**: `GET http://localhost:8000/api/v1/diagnostics/diagnostics`
- **Resource Monitoring**: `GET http://localhost:8000/api/v1/diagnostics/resources`

### Service Recovery
If services become unhealthy during runtime:
```bash
curl -X POST http://localhost:8000/debug/recover-services
```

## Startup Troubleshooting

### Common Issues & Solutions

**1. "No such file or directory" when running startup script**
```bash
# Solution: Use the convenience script from project root
./scripts/start_backend.sh
```

**2. Python version compatibility errors**
```bash
# Check Python version
python --version

# Ensure Python 3.8+ is installed
# macOS: brew install python@3.11
# Ubuntu: sudo apt install python3.11
```

**3. Missing dependencies**
```bash
# Install all requirements
cd backend
pip install -r requirements.txt
```

**4. Environment variable issues**
```bash
# Set required environment variables
export PYTHONPATH="$(pwd):$PYTHONPATH"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
```

**5. Google Cloud credentials errors**
```bash
# Verify credentials file
cat $GOOGLE_APPLICATION_CREDENTIALS | jq .

# Check service account permissions
gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS
gcloud projects list
```

**6. Port already in use**
```bash
# Kill existing processes
pkill -f uvicorn
lsof -ti :8000 | xargs kill -9
```

### Pre-Startup Test Failures

If any test fails, the script will:
1. **Stop execution** - Prevents starting with invalid configuration
2. **Display clear error** - Shows exactly what failed and why
3. **Provide guidance** - Suggests specific steps to fix the issue
4. **Log details** - Outputs detailed information for debugging

### Test Results Interpretation

**✅ All Tests Pass**: Server will start normally
**❌ Any Test Fails**: Startup is aborted with specific error guidance

Example failure output:
```
❌ Test 3: Python Dependencies Check failed
   Missing packages: ['fastapi', 'firebase_admin']
   💡 Run: pip install -r requirements.txt
❌ Dependencies test failed. Aborting startup.
```

## Performance Baselines

### Expected Startup Times
- **Pre-startup tests**: < 10 seconds
- **Total Startup**: < 15 seconds  
- **Firebase Auth**: < 0.06 seconds
- **VertexAI**: < 0.01 seconds

### Memory Usage
- **Normal Operation**: 200-300 MB
- **Warning Level**: > 500 MB
- **Critical Level**: > 1 GB

### Resource Warnings
The system automatically detects:
- High memory usage
- Connection leaks (>10 CLOSE_WAIT connections)
- Service health issues
- Low disk space (<5 GB)

## Emergency Procedures

### Server Won't Start
1. **Run comprehensive tests**: `./scripts/start_backend.sh` (tests will identify the issue)
2. **Check specific test failure**: Review the failed test output for guidance
3. **Manual verification**: Run individual test commands to isolate issues
4. **Check logs**: Review `backend/backend.log` for detailed error information

### Pre-Startup Test Failures
1. **Follow test-specific guidance**: Each test provides specific remediation steps
2. **Verify environment**: Ensure all environment variables are correctly set
3. **Check dependencies**: Run `pip install -r requirements.txt`
4. **Validate credentials**: Verify Google Cloud service account file

### Services Become Unhealthy
1. Check service status: `GET /api/v1/diagnostics/health`
2. Try service recovery: `POST /debug/recover-services`
3. If recovery fails, restart server with full validation

## Monitoring Best Practices

### Regular Health Checks
```bash
# Automated health monitoring
while true; do
  curl -s http://localhost:8000/api/v1/diagnostics/health | jq '.status'
  sleep 30
done
```

### Resource Monitoring
```bash
# Check resource usage and warnings
curl -s http://localhost:8000/api/v1/diagnostics/resources | jq '.resource_warnings'
```

### Pre-Startup Test Validation
```bash
# Run just the tests (without starting server)
cd backend
# Extract test sections from start_server_fixed.sh and run individually
```

## Configuration Management

### Environment Variables
Required:
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account key
- `PYTHONPATH`: Should include backend directory

Optional:
- `GOOGLE_CLOUD_PROJECT`: Override project ID
- `FIREBASE_PROJECT_ID`: Override Firebase project

### Service Account Permissions
Required IAM roles:
- Firebase Admin SDK Administrator Service Agent
- Vertex AI User
- Basic Viewer

## Stability Features

✅ **All Critical Issues Resolved**:
1. Firebase Admin SDK conflicts - Resolved
2. VertexAI initialization conflicts - Resolved  
3. Global singleton state corruption - Resolved
4. FastAPI lifecycle management - Resolved
5. Resource leak accumulation - Resolved
6. Import-time initialization - Resolved

✅ **Enhanced Reliability Features**:
- **8 comprehensive pre-startup tests** - Catch issues before they cause crashes
- **Detailed error diagnostics** - Clear guidance for resolving issues
- **Automatic environment validation** - Verify all prerequisites are met
- **Resource monitoring and leak detection** - Proactive resource management
- **Health check endpoints** - Real-time service monitoring
- **Service recovery mechanisms** - Automatic recovery from common failures
- **Graceful shutdown handling** - Clean resource cleanup

## Test Summary Output

When all tests pass, you'll see:
```
🎉 ALL PRE-STARTUP TESTS PASSED!
=================================
   ✅ System Environment (Python version, platform)
   ✅ Environment Variables (PYTHONPATH, credentials)
   ✅ Python Dependencies (FastAPI, Firebase, VertexAI, etc.)
   ✅ Port Availability (8000)
   ✅ Google Cloud Credentials (format and content)
   ✅ Disk Space (availability check)
   ✅ Critical Imports (app modules and services)
   ✅ Resource Management (singleton reset and cleanup)
```

This comprehensive testing ensures your backend starts reliably every time! 🚀 