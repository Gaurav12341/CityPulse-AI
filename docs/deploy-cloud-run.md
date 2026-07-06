# Deploy CityPulse AI to Google Cloud Run

This project deploys as one FastAPI service that serves both:

- the CityPulse web UI at `/`
- backend APIs such as `/assistant`, `/ask`, `/chat`, and `/route`

## Prerequisites

- Google Cloud CLI installed and authenticated
- A Google Cloud project with billing enabled
- Cloud Run, Cloud Build, Artifact Registry, and Vertex AI APIs enabled
- A Cloud Run service account with permission to call Vertex AI

## Required Environment Variables

Set these on Cloud Run:

```text
PROJECT_ID=<your-google-cloud-project-id>
LOCATION=<vertex-ai-region>
MODEL_NAME=<gemini-model-name>
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
```

## Build and Deploy

Run these commands from the repository root:

```powershell
$PROJECT_ID="<your-google-cloud-project-id>"
$REGION="<cloud-run-region>"
$SERVICE="citypulse-ai"
$REPOSITORY="citypulse"
$IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$SERVICE"

gcloud config set project $PROJECT_ID
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com aiplatform.googleapis.com
gcloud artifacts repositories create $REPOSITORY `
  --repository-format docker `
  --location $REGION `
  --description "CityPulse AI containers"

gcloud builds submit backend --tag $IMAGE
gcloud run deploy $SERVICE `
  --image $IMAGE `
  --region $REGION `
  --platform managed `
  --allow-unauthenticated `
  --memory 2Gi `
  --cpu 2 `
  --timeout 300 `
  --set-env-vars PROJECT_ID=$PROJECT_ID,LOCATION=$REGION,MODEL_NAME=<gemini-model-name>,EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
```

After deployment, open the Cloud Run service URL. The UI should load at `/`.

## Notes

- The first RAG request can be slower because the embedding model loads and
  the local FAISS index may be generated.
- The current conversation memory is in-process. It resets when Cloud Run
  starts a new instance or scales to zero.
- For production persistence, replace in-memory conversation storage with
  Redis, Firestore, or PostgreSQL.
