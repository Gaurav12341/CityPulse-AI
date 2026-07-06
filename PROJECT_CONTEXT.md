# CityPulse AI
### AI-Powered Smart Municipal Complaint Management System

---

# Project Overview

CityPulse AI is an enterprise-grade AI platform that assists municipalities in managing citizen complaints, retrieving municipal knowledge, prioritizing incidents, and supporting city officials with intelligent decision-making.

The long-term vision is to build a multi-agent AI system capable of:

- Complaint Classification
- Retrieval-Augmented Generation (RAG)
- Incident Prioritization
- Department Routing
- GIS & Ward Mapping
- Analytics Dashboard
- Citizen Chat Assistant
- AI Workflow Automation

The project is being developed incrementally through milestones.

---

# Current Technology Stack

## Backend

- Python 3.13
- FastAPI
- Pydantic
- Uvicorn

## AI

- Google Vertex AI
- Gemini 2.5 Flash
- Prompt Engineering

## RAG

- LangChain
- FAISS
- Sentence Transformers
- PyPDF

## Future

- Vertex AI Embeddings
- Cloud Storage
- BigQuery
- PostgreSQL
- Redis
- Docker
- Kubernetes
- Google Cloud Run

---

# Current Project Structure

backend/

    app/

        agents/

        api/

        config/

        data/

            municipal_docs/

                garbage_collection.txt

                road_repair_policy.txt

                water_supply.txt

        models/

            classification.py

        prompts/

        rag/

            loader.py

            retriever.py

            prompt.py

        services/

            gemini_service.py

        tests/

        utils/

        main.py

    requirements.txt

    README.md

    .env

frontend/

docs/

---

# Coding Standards

Always follow these principles.

## Code Style

- Follow PEP8
- Use Python type hints
- Write modular code
- Keep functions under ~50 lines where practical
- Avoid duplicated logic
- Prefer pathlib over os.path
- Add docstrings for public functions
- Use descriptive variable names

## Error Handling

- Raise meaningful exceptions
- Never silently ignore failures
- Validate all external inputs

## Logging

Future logging should use Python's logging module.

Avoid print statements except for debugging.

## Configuration

Never hardcode:

- API Keys
- Project IDs
- Model Names
- File Paths

Read configuration from:

.env

---

# AI Coding Guidelines

Whenever implementing new features:

1. Preserve existing APIs unless instructed otherwise.
2. Maintain backward compatibility.
3. Do not break completed milestones.
4. Reuse existing services whenever possible.
5. Keep AI prompts centralized.
6. Avoid business logic inside FastAPI routes.
7. Keep Gemini interaction inside services/agents.

---

# Current Completed Milestones

## ✅ Milestone M1

### Complaint Classification Agent

Status:

Completed

Capabilities:

- Vertex AI configured
- Gemini working
- FastAPI backend running
- /chat endpoint available
- Complaint classification using Gemini
- Structured JSON response

Current schema:

```python
category: str
department: str
severity: str
priority: int
location: str
summary: str
ward: str
estimated_resolution_hours: int
citizen_impact: str
recommended_action: str