from fastapi import FastAPI, HTTPException
from app.services.gemini_service import classify_complaint
from app.models.assistant import AssistantRequest, AssistantResponse
from app.models.chat import ChatRequest
from app.models.classification import ComplaintClassification
from app.models.rag import AskRequest, AskResponse
from app.models.routing import DepartmentRoute
from app.services.assistant_service import handle_assistant_message
from app.services.department_routing_service import route_complaint
from app.services.rag_service import answer_municipal_question

app = FastAPI(title="CityPulse AI")


@app.get("/")
def root():
    return {"message": "CityPulse AI is running!"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/chat")
def chat(request: ChatRequest):
    print("Received complaint:", request.message)
    response = classify_complaint(request.message)
    return response


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    try:
        return answer_municipal_question(request.question)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/assistant", response_model=AssistantResponse)
def assistant(request: AssistantRequest):
    try:
        return handle_assistant_message(
            message=request.message,
            session_id=request.session_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/route", response_model=DepartmentRoute)
def route(request: ComplaintClassification):
    try:
        return route_complaint(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
