#!/bin/bash

echo "🔧 Fixing backend credentials configuration..."

# Update the backend .env file with the correct service account path
sed -i '' 's|GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json|GOOGLE_APPLICATION_CREDENTIALS=/app/gcp-service-account-key.json|g' backend/.env

echo "✅ Updated backend/.env with correct service account path"

# Check if the service account key exists
if [ -f "gcp-service-account-key.json" ]; then
    echo "✅ Service account key found: gcp-service-account-key.json"
else
    echo "❌ Service account key not found!"
    echo "   Expected: gcp-service-account-key.json"
    exit 1
fi

echo ""
echo "🐳 Docker Compose needs to mount the service account key..."
echo "📝 Checking docker-compose.yml configuration..."

# Check if the volume mount exists
if grep -q "gcp-service-account-key.json" docker-compose.yml; then
    echo "✅ Service account key volume mount already configured"
else
    echo "⚠️  Need to add volume mount to docker-compose.yml"
    echo ""
    echo "Add this to the backend service volumes in docker-compose.yml:"
    echo "  volumes:"
    echo "    - ./gcp-service-account-key.json:/app/gcp-service-account-key.json:ro"
fi

echo ""
echo "🚀 Next step: Restart backend to apply changes"
echo "   docker-compose restart backend" 