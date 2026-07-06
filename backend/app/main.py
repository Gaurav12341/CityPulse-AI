from fastapi import FastAPI
from app.services.gemini_service import ask_gemini

app = FastAPI(title="CityPulse AI")

@app.get("/")
def root():
    return {"message": "CityPulse AI is running!"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/chat")
def chat(prompt: str):
    response = ask_gemini(prompt)
    return {"response": response}