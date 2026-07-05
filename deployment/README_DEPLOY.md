# KaggleBot Deployment Guide

## Option 1: Local (ADK Web UI)

```bash
cd kagglebot
source venv/bin/activate
adk web
# Open http://localhost:8000
```

## Option 2: Docker

```bash
# Build
docker build -t kagglebot -f deployment/Dockerfile .

# Run
docker run -p 8080:8080 -e GOOGLE_API_KEY=your_key kagglebot

# Open http://localhost:8080
```

## Option 3: Google Cloud Run

### Prerequisites

1. [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
2. A GCP project with billing enabled
3. Cloud Run API enabled: `gcloud services enable run.googleapis.com`

### Quick Deploy

```bash
# Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Set API key
export GOOGLE_API_KEY=your_gemini_api_key

# Deploy (one command)
./deployment/deploy.sh
```

### Manual Deploy

```bash
# Build and push
PROJECT_ID=$(gcloud config get-value project)
docker build -t gcr.io/${PROJECT_ID}/kagglebot -f deployment/Dockerfile .
docker push gcr.io/${PROJECT_ID}/kagglebot

# Deploy to Cloud Run
gcloud run deploy kagglebot \
    --image gcr.io/${PROJECT_ID}/kagglebot \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars "GOOGLE_API_KEY=${GOOGLE_API_KEY}" \
    --memory 1Gi \
    --timeout 300s
```

### CI/CD with Cloud Build

```bash
gcloud builds submit \
    --config deployment/cloudbuild.yaml \
    --substitutions "_GOOGLE_API_KEY=${GOOGLE_API_KEY}"
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Yes | Gemini API key from [AI Studio](https://aistudio.google.com/apikey) |
| `GCP_PROJECT_ID` | For Cloud Run | Your GCP project ID |
| `GCP_REGION` | For Cloud Run | Deploy region (default: us-central1) |

## Troubleshooting

- **"No module named google.adk"**: Run `pip install google-adk`
- **"GOOGLE_API_KEY not set"**: Copy `.env.example` to `.env` and add your key
- **Docker build fails**: Ensure Docker Desktop is running
- **Cloud Run 403**: Enable the Cloud Run API and check IAM permissions
