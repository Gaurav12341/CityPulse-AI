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

import json

def classify_complaint(complaint: str):
    prompt = f"""
You are the Complaint Classification Agent for CityPulse AI.

Your task is to analyze a citizen complaint and return ONLY valid JSON.

Return this exact JSON schema:

{{
  "category":"",
  "department":"",
  "severity":"",
  "priority":1,
  "location":"",
  "ward":"",
  "summary":"",
  "estimated_resolution_hours":0,
  "citizen_impact":"",
  "recommended_action":""
}}

Categories:
- Road Damage
- Garbage
- Water Leakage
- Illegal Parking
- Pollution
- Street Light
- Traffic
- Public Safety
- Other

Departments:
- Road Maintenance
- Sanitation
- Water Supply
- Traffic Police
- Pollution Control
- Electrical
- Public Works

Severity:
- Low
- Medium
- High
- Critical

Priority:
1 = Highest
2 = High
3 = Medium
4 = Low

Rules:
- Return ONLY JSON.
- No markdown.
- No explanation.
- If location is not mentioned, use "Unknown".

Citizen Complaint:

{complaint}
"""

    print("Complaint sent to Gemini:", complaint)

    response = client.models.generate_content(
        model=os.getenv("MODEL_NAME"),
        contents=prompt,
    )

    print("\n========== GEMINI RAW RESPONSE ==========")
    print(response.text)
    print("=========================================\n")

    return json.loads(response.text)