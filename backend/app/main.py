from fastapi import FastAPI, HTTPException
from app.services.gemini_service import classify_complaint
from app.models.chat import ChatRequest
from app.models.rag import AskRequest, AskResponse
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
