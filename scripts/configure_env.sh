#!/bin/bash

# DrFirst Business Case Generator - Environment Configuration Script
# This script configures the .env files with known values from development

echo "🔧 Configuring environment files..."

# Configure Frontend .env
echo "📱 Configuring frontend/.env..."
sed -i '' 's|VITE_API_BASE_URL=http://localhost:8000|VITE_API_BASE_URL=https://drfirst-gateway-6jgi3xc.uc.gateway.dev|g' frontend/.env
sed -i '' 's|VITE_FIREBASE_API_KEY=your_firebase_api_key_here|VITE_FIREBASE_API_KEY=placeholder_need_real_key|g' frontend/.env
sed -i '' 's|VITE_FIREBASE_AUTH_DOMAIN=your_project_id.firebaseapp.com|VITE_FIREBASE_AUTH_DOMAIN=drfirst-business-case-gen.firebaseapp.com|g' frontend/.env
sed -i '' 's|VITE_FIREBASE_PROJECT_ID=your_project_id_here|VITE_FIREBASE_PROJECT_ID=drfirst-business-case-gen|g' frontend/.env

# Configure Backend .env  
echo "⚙️ Configuring backend/.env..."
sed -i '' 's|GOOGLE_CLOUD_PROJECT_ID=your-project-id|GOOGLE_CLOUD_PROJECT_ID=drfirst-business-case-gen|g' backend/.env
sed -i '' 's|FIREBASE_PROJECT_ID=your-firebase-project-id|FIREBASE_PROJECT_ID=drfirst-business-case-gen|g' backend/.env

echo "✅ Environment files configured!"
echo ""
echo "🚨 NEXT STEPS REQUIRED:"
echo "1. Get Firebase credentials from: https://console.firebase.google.com/"
echo "   - Select project: drfirst-business-case-gen"
echo "   - Go to Project Settings → General → Your apps"
echo "   - Create/select web app"
echo "   - Copy the config values"
echo ""
echo "2. Update frontend/.env with real Firebase credentials:"
echo "   - VITE_FIREBASE_API_KEY=real_api_key_here"
echo ""
echo "3. Enable Google Sign-in in Firebase Console:"
echo "   - Go to Authentication → Sign-in method"
echo "   - Enable Google"
echo "   - Add localhost to authorized domains"
echo ""
echo "4. Start the application:"
echo "   docker-compose up" 