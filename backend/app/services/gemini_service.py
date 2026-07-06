from google import genai
from google.genai.types import HttpOptions
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(
    vertexai=True,
    project=os.getenv("PROJECT_ID"),
    location=os.getenv("LOCATION"),
    http_options=HttpOptions(api_version="v1"),
)

def ask_gemini(prompt: str) -> str:
    response = client.models.generate_content(
        model=os.getenv("MODEL_NAME"),
        contents=prompt,
    )
    return response.text