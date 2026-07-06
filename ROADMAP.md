# CityPulse AI Roadmap

> **Project:** CityPulse AI  
> **Version:** v0.2.0  
> **Status:** Active Development

---

# Vision

Build an enterprise-grade AI-powered municipal complaint management platform using FastAPI, Google Vertex AI, Retrieval-Augmented Generation (RAG), and cloud-native architecture.

---

# Overall Progress

| Milestone | Status | Progress |
|------------|--------|----------|
| M1 - Complaint Classification | ✅ Completed | 100% |
| M2 - Knowledge Retrieval (RAG) | 🚧 In Progress | 15% |
| M3 - Hybrid AI Agent | ⏳ Planned | 0% |
| M4 - Department Routing | ⏳ Planned | 0% |
| M5 - GIS & Location Intelligence | ⏳ Planned | 0% |
| M6 - Citizen AI Assistant | ⏳ Planned | 0% |
| M7 - Analytics Dashboard | ⏳ Planned | 0% |
| M8 - Cloud Deployment | ⏳ Planned | 0% |

---

# ✅ Milestone M1
## Complaint Classification Agent

### Goal

Convert natural language complaints into structured municipal incident data.

### Completed

- [x] FastAPI backend
- [x] Vertex AI setup
- [x] Gemini integration
- [x] `/chat` endpoint
- [x] Prompt engineering
- [x] Structured JSON output
- [x] Pydantic response model

### Output

```json
{
  "category": "",
  "department": "",
  "severity": "",
  "priority": 1,
  "location": "",
  "ward": "",
  "summary": "",
  "estimated_resolution_hours": 48,
  "citizen_impact": "",
  "recommended_action": ""
}
```

---

# 🚧 Milestone M2
## Retrieval-Augmented Generation (RAG)

### Goal

Answer municipal questions using official knowledge instead of hallucination.

---

## Phase 1
### Knowledge Base

Status: ✅ Completed

- [x] Municipal documents folder
- [x] Garbage collection document
- [x] Road repair policy
- [x] Water supply information

---

## Phase 2
### Document Loader

Status: ⏳ Pending

Tasks

- [ ] Load all documents
- [ ] Support TXT files
- [ ] Support PDF files
- [ ] Add metadata
- [ ] Unit tests

Deliverable

```
List[Document]
```

---

## Phase 3
### Text Chunking

Status: ⏳ Pending

Tasks

- [ ] RecursiveCharacterTextSplitter
- [ ] Chunk size = 500
- [ ] Overlap = 100
- [ ] Preserve metadata

Deliverable

```
Chunked LangChain Documents
```

---

## Phase 4
### Embeddings

Status: ⏳ Pending

Tasks

- [ ] Sentence Transformers
- [ ] Generate embeddings
- [ ] Create reusable embedding service

Future

- [ ] Vertex AI Embeddings

---

## Phase 5
### Vector Database

Status: ⏳ Pending

Tasks

- [ ] Build FAISS index
- [ ] Save locally
- [ ] Reload automatically
- [ ] Version index

Deliverable

```
faiss_index/
```

---

## Phase 6
### Semantic Retriever

Status: ⏳ Pending

Tasks

- [ ] Top-k retrieval
- [ ] Metadata filtering
- [ ] Similarity search
- [ ] Source tracking

---

## Phase 7
### Prompt Engineering

Status: ⏳ Pending

Tasks

- [ ] Context injection
- [ ] Citation prompt
- [ ] Hallucination prevention

Prompt

```
Context

Question

Answer ONLY using the supplied context.
```

---

## Phase 8
### Gemini Integration

Status: ⏳ Pending

Tasks

- [ ] Combine retriever + Gemini
- [ ] Ground responses
- [ ] Return sources

---

## Phase 9
### API

Status: ⏳ Pending

Tasks

- [ ] POST /ask
- [ ] Validation
- [ ] Error handling
- [ ] Response model

Example

```
POST /ask
```

```json
{
    "question":"When is garbage collected in Ward 12?"
}
```

Response

```json
{
    "answer":"Garbage is collected...",
    "sources":[
        "garbage_collection.txt"
    ]
}
```

---

# ⏳ Milestone M3
## Hybrid AI Agent

### Goal

Automatically determine whether the user is:

- Asking a question
- Reporting a complaint

Flow

```
User Input

↓

Intent Detection

↓

Complaint Agent
OR
Knowledge Agent
```

Tasks

- [ ] Intent classifier
- [ ] Routing engine
- [ ] Unified endpoint
- [ ] Conversation memory

---

# ⏳ Milestone M4
## Department Routing Agent

Tasks

- [ ] Department mapping
- [ ] SLA lookup
- [ ] Escalation rules
- [ ] Officer assignment

Output

```json
{
    "department":"",
    "priority":"",
    "sla":"",
    "officer":""
}
```

---

# ⏳ Milestone M5
## GIS Integration

Tasks

- [ ] Ward lookup
- [ ] Reverse geocoding
- [ ] Nearby complaints
- [ ] Heatmaps
- [ ] Map integration

Future

- Google Maps
- Leaflet
- PostGIS

---

# ⏳ Milestone M6
## Citizen AI Assistant

Capabilities

- Complaint registration
- Complaint status
- Municipal FAQs
- Follow-up questions
- Multi-turn conversation

Tasks

- [ ] Conversation memory
- [ ] Context management
- [ ] Session IDs
- [ ] Chat history

---

# ⏳ Milestone M7
## Analytics Dashboard

Backend

- [ ] Complaint trends
- [ ] Resolution time
- [ ] Ward analytics
- [ ] Department KPIs

Frontend

- [ ] Dashboard
- [ ] Charts
- [ ] Filters

---

# ⏳ Milestone M8
## Google Cloud Deployment

Infrastructure

- [ ] Docker
- [ ] Cloud Run
- [ ] Artifact Registry
- [ ] Cloud Storage
- [ ] Secret Manager

AI

- [ ] Vertex AI
- [ ] Vertex Embeddings

Data

- [ ] PostgreSQL
- [ ] BigQuery

Monitoring

- [ ] Cloud Logging
- [ ] Error Reporting
- [ ] Cloud Monitoring

CI/CD

- [ ] GitHub Actions
- [ ] Automatic deployment

---

# Stretch Goals

- [ ] Voice complaint registration
- [ ] OCR document processing
- [ ] Image-based complaint analysis
- [ ] Multilingual support
- [ ] WhatsApp integration
- [ ] SMS notifications
- [ ] Mobile application
- [ ] Predictive maintenance
- [ ] AI-generated municipal reports

---

# Technical Debt

- [ ] Improve logging
- [ ] Add configuration management
- [ ] Increase unit test coverage
- [ ] Integration testing
- [ ] API documentation
- [ ] Performance benchmarking

---

# Definition of Done

A milestone is considered complete only when:

- [ ] Feature implemented
- [ ] Code reviewed
- [ ] Unit tested
- [ ] API tested
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Production-ready code

---

# Current Focus

🎯 **Active Milestone:** M2 - Retrieval-Augmented Generation (RAG)

### Immediate Next Task

- [ ] Implement `loader.py`
- [ ] Implement `retriever.py`
- [ ] Implement `prompt.py`
- [ ] Build FAISS index
- [ ] Integrate Gemini with RAG
- [ ] Expose `/ask` endpoint

---

Last Updated: July 2026