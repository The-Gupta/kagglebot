#!/bin/bash
# deploy.sh — Quick deploy KaggleBot to Cloud Run
#
# Prerequisites:
#   1. gcloud CLI installed and authenticated
#   2. GOOGLE_API_KEY set in environment
#   3. GCP project configured: gcloud config set project YOUR_PROJECT_ID
#
# Usage:
#   ./deployment/deploy.sh

set -euo pipefail

# Configuration
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="kagglebot"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "============================================"
echo "  🤖 Deploying KaggleBot to Cloud Run"
echo "============================================"
echo ""
echo "  Project:  ${PROJECT_ID}"
echo "  Region:   ${REGION}"
echo "  Service:  ${SERVICE_NAME}"
echo ""

# Check for API key
if [ -z "${GOOGLE_API_KEY:-}" ]; then
    echo "❌ ERROR: GOOGLE_API_KEY not set."
    echo "   Export it: export GOOGLE_API_KEY=your_key_here"
    exit 1
fi

# Build
echo "📦 Building Docker image..."
docker build -t "${IMAGE}" -f deployment/Dockerfile .

# Push
echo "⬆️  Pushing to Container Registry..."
docker push "${IMAGE}"

# Deploy
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
    --image "${IMAGE}" \
    --region "${REGION}" \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars "GOOGLE_API_KEY=${GOOGLE_API_KEY}" \
    --memory 1Gi \
    --timeout 300s

# Get URL
URL=$(gcloud run services describe "${SERVICE_NAME}" \
    --region "${REGION}" \
    --format 'value(status.url)')

echo ""
echo "============================================"
echo "  ✅ KaggleBot deployed successfully!"
echo "  🌐 URL: ${URL}"
echo "============================================"
