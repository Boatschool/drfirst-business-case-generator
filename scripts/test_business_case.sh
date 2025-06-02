#!/bin/bash

# Test script for business case creation
echo "🧪 Testing Business Case Creation Flow..."

echo ""
echo "📊 Testing Backend Health..."
health_response=$(curl -s http://localhost:8000/health)
echo "Backend Health: $health_response"

echo ""
echo "📊 Testing API Gateway Health..."
gateway_health=$(curl -s https://drfirst-gateway-6jgi3xc.uc.gateway.dev/health)
echo "Gateway Health: $gateway_health"

echo ""
echo "🌐 Testing Frontend..."
frontend_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:4000)
echo "Frontend Status Code: $frontend_status"

echo ""
echo "✅ Service Status Summary:"
echo "- Backend (Local): ${health_response:-❌ Not responding}"
echo "- API Gateway (Cloud): ${gateway_health:-❌ Not responding}"  
echo "- Frontend: $([ "$frontend_status" -eq 200 ] && echo "✅ OK" || echo "❌ Error ($frontend_status)")"

echo ""
echo "🚀 Next Steps:"
echo "1. Open browser: http://localhost:4000"
echo "2. Sign in with any Google account"
echo "3. Navigate to Dashboard → Create New Business Case"
echo "4. Fill out the form and submit"
echo "5. Check if PRD generation works"

echo ""
echo "🔍 To debug authentication issues:"
echo "   docker-compose logs frontend"
echo "   docker-compose logs backend" 