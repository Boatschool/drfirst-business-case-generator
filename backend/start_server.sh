#!/bin/bash
# Start the DrFirst Business Case Generator Backend Server
# with the correct credentials

# Set the correct Google Cloud credentials
export GOOGLE_APPLICATION_CREDENTIALS="/Users/ronwince/.gcp/drfirst-firebase-admin-key.json"

# Verify credentials
echo "🔑 Using credentials: $GOOGLE_APPLICATION_CREDENTIALS"
echo "🏢 Project: $(python -c "import os, json; creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS'); creds = json.load(open(creds_path)); print(creds['project_id'])")"

# Start the server
echo "🚀 Starting backend server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level info 