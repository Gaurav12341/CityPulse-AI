# CityPulse AI

AI-powered municipal complaint and knowledge assistant built with FastAPI,
Google Vertex AI Gemini, Retrieval-Augmented Generation, FAISS, and a
presentable web UI.

CityPulse AI helps municipalities classify citizen complaints, answer official
service questions from local documents, route incidents to departments, and
assign SLA/officer escalation metadata.

## Live App

The current Cloud Run deployment is available at:

```text
https://citypulse-ai-553620546392.us-central1.run.app
```

API documentation is available at:

```text
https://citypulse-ai-553620546392.us-central1.run.app/docs
```

## Features

- Unified web UI for citizen questions and complaints
- Hybrid assistant endpoint that detects whether a message is a complaint or a municipal knowledge question
- Complaint classification using Gemini
- RAG-based municipal Q&A grounded in local municipal documents
- LangChain document loading and chunking
- Sentence Transformers embeddings
- FAISS vector search
- Source citations for knowledge answers
- Department routing with SLA, escalation, and officer assignment
- In-memory session history for assistant conversations
- Docker and Google Cloud Run deployment support

## Current Milestones

| Milestone | Status | Summary |
| --- | --- | --- |
| M1 - Complaint Classification | Complete | Classifies complaints into structured municipal incident data |
| M2 - Retrieval-Augmented Generation | Complete | Loads docs, chunks text, embeds content, retrieves with FAISS, answers with Gemini |
| M3 - Hybrid AI Agent | Complete | Detects intent, routes to complaint or RAG flow, tracks session history |
| M4 - Department Routing | Complete | Maps complaints to departments, SLAs, escalation levels, and officers |
| M5 - GIS & Location Intelligence | Planned | Ward lookup, geocoding, maps, and location intelligence |
| M6 - Citizen AI Assistant | Planned | Deeper conversation management and citizen workflows |
| M7 - Analytics Dashboard | Planned | Trends, KPIs, filters, and frontend dashboard |
| M8 - Cloud Deployment | In progress | Cloud Run deployment is available; persistence and production hardening remain |

## Tech Stack

### Backend

- Python 3.13
- FastAPI
- Pydantic
- Uvicorn

### AI and RAG

- Google Vertex AI
- Gemini
- LangChain
- Sentence Transformers
- FAISS

### Frontend

- Static HTML, CSS, and JavaScript served by FastAPI
- Single chat-style interface backed by `/assistant`

### Deployment

- Docker
- Google Cloud Build
- Artifact Registry
- Google Cloud Run

## Project Structure

```text
CityPulse-AI/
  backend/
    app/
      data/
        municipal_docs/
      models/
      rag/
      services/
      static/
      main.py
    Dockerfile
    requirements.txt
  docs/
    deploy-cloud-run.md
  PROJECT_CONTEXT.md
  ROADMAP.md
  README.md
```

## Environment Variables

Create `backend/.env` for local development:

```text
PROJECT_ID=<your-google-cloud-project-id>
LOCATION=<vertex-ai-region>
MODEL_NAME=<gemini-model-name>
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
```

Do not commit `.env` files. They are ignored by Git.

## Local Setup

From the repository root:

```powershell
cd backend
python -m venv ..\venv
..\venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run the app:

```powershell
$env:EMBEDDING_MODEL_NAME="sentence-transformers/all-MiniLM-L6-v2"
..\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

Swagger docs:

```text
http://127.0.0.1:8000/docs
```

## Main Endpoints

### `GET /`

Serves the CityPulse AI web UI.

### `GET /health`

Health check endpoint.

Response:

```json
{
  "status": "healthy"
}
```

### `POST /assistant`

Unified assistant endpoint. Detects intent, routes the message, and returns
the result with conversation history.

Request:

```json
{
  "message": "When is garbage collected in Ward 12?"
}
```

Question response:

```json
{
  "intent": "question",
  "confidence": 0.95,
  "reason": "The user is asking for municipal service schedule information.",
  "response_type": "question",
  "result": {
    "answer": "Garbage is collected in Ward 12 on Monday, Wednesday, and Friday, from 6:00 AM to 9:00 AM.\n\nSources: garbage_collection.txt",
    "sources": ["garbage_collection.txt"]
  },
  "session_id": "generated-session-id",
  "history": []
}
```

Complaint request:

```json
{
  "message": "There is a huge pothole near MG Road causing accidents every day."
}
```

Complaint response includes classification and routing:

```json
{
  "intent": "complaint",
  "response_type": "complaint",
  "result": {
    "category": "Road Damage",
    "department": "Road Maintenance",
    "severity": "Critical",
    "priority": 1,
    "location": "MG Road",
    "routing": {
      "department": "Road Maintenance",
      "priority": "Critical",
      "sla": "4 hours",
      "officer": "Municipal Incident Commander",
      "escalation_required": true,
      "escalation_level": "department_head",
      "reason": "Road Damage complaint at MG Road routed to Road Maintenance with critical priority."
    }
  }
}
```

### `POST /ask`

Direct municipal knowledge Q&A endpoint backed by RAG.

Request:

```json
{
  "question": "When is garbage collected in Ward 12?"
}
```

Response:

```json
{
  "answer": "Garbage is collected in Ward 12 on Monday, Wednesday, and Friday, from 6:00 AM to 9:00 AM.\n\nSources: garbage_collection.txt",
  "sources": ["garbage_collection.txt"]
}
```

### `POST /chat`

Direct complaint classification endpoint.

### `POST /route`

Direct department routing endpoint for an already-classified complaint.

## RAG Pipeline

The RAG pipeline lives in `backend/app/rag/`:

- `loader.py` loads municipal `.txt` documents as LangChain `Document` objects
- `retriever.py` chunks documents and performs semantic retrieval
- `embeddings.py` generates Sentence Transformers embeddings
- `vector_store.py` builds, saves, loads, and searches a FAISS index
- `prompt.py` builds grounded prompts with source labels

Municipal documents are stored in:

```text
backend/app/data/municipal_docs/
```

The local FAISS index is generated at runtime and ignored by Git:

```text
backend/app/data/faiss_index/
```

## Department Routing

M4 routing is implemented in:

```text
backend/app/services/department_routing_service.py
```

Routing includes:

- department mapping
- priority normalization
- SLA lookup
- escalation rules
- officer assignment

## Web UI

The UI is served directly by FastAPI:

```text
backend/app/static/
```

It provides:

- a single assistant input box
- quick prompt buttons
- session ID display
- classification cards
- routing SLA/officer tags
- RAG source display

## Deploy to Google Cloud Run

Detailed deployment instructions are in:

```text
docs/deploy-cloud-run.md
```

The deployed service runs as one container that serves both the UI and API.

## Important Notes

- The first RAG request can be slow on cold start because the embedding model loads lazily.
- Conversation memory is currently process-local and resets when the Cloud Run instance restarts or scales down.
- Production persistence should use Redis, Firestore, PostgreSQL, or another shared store.
- Local/generated FAISS artifacts are intentionally not committed.

## Recent Commits

```text
edaa97a Add web UI and Cloud Run deployment
da68eb1 Implement M4 department routing
6ef625d Implement M3 hybrid assistant
5a617a0 Implement M2 RAG pipeline
87d3d51 classification agent
```
