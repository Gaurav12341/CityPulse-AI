from fastapi import FastAPI
from app.services.gemini_service import classify_complaint
from app.models.chat import ChatRequest

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