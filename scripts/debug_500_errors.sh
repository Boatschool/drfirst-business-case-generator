#!/bin/bash

echo "🔍 Debugging 500 Errors - Step by Step Analysis"
echo "================================================"

echo ""
echo "1. 📊 Service Health Check:"
echo "   Frontend: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:4000)"
echo "   Backend: $(curl -s http://localhost:8000/health | jq -r '.status // "error"')"

echo ""
echo "2. 🔐 Authentication Endpoints (should return 401/403 without auth):"
echo "   Cases List: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/cases)"
echo "   Agent Invoke: $(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/api/v1/agents/invoke -H 'Content-Type: application/json' -d '{}')"

echo ""
echo "3. 🌐 Frontend Proxy Tests:"
echo "   Via Frontend Proxy - Cases: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:4000/api/v1/cases)"
echo "   Via Frontend Proxy - Health: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:4000/api/health)"

echo ""
echo "4. 📱 Firebase Configuration Check:"
firebase_api_key=$(docker-compose exec frontend cat /app/.env | grep "VITE_FIREBASE_API_KEY=" | cut -d'=' -f2)
if [[ ${#firebase_api_key} -gt 20 ]]; then
    echo "   Firebase API Key: ✅ Configured (${#firebase_api_key} chars)"
else
    echo "   Firebase API Key: ❌ Missing or invalid"
fi

echo ""
echo "5. 📋 Recent Backend Logs (Errors Only):"
docker-compose logs backend --tail=50 | grep -i -E "(error|exception|failed|500)" | tail -5

echo ""
echo "6. 📋 Recent Frontend Logs (Errors Only):"
docker-compose logs frontend --tail=20 | grep -i -E "(error|failed)" | tail -3

echo ""
echo "🎯 DEBUGGING STEPS:"
echo "1. Open browser: http://localhost:4000"
echo "2. Open Developer Tools (F12) → Console"
echo "3. Try to sign in and watch for errors"
echo "4. Check Network tab for failed requests"
echo "5. Look for 500 errors and share the error details"

echo ""
echo "💡 LIKELY CAUSES:"
echo "- User not signed in when API calls are made"
echo "- Firebase authentication not working properly"
echo "- API endpoints being called before authentication completes" 