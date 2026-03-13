from fastapi import FastAPI
from pydantic import BaseModel
from translation import translate_text
from llm import sanitize_and_structure_transcript
from database import save_consultation_record
from fastapi.middleware.cors import CORSMiddleware
from models import Consultation, StructuredRecord

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranslateInput(BaseModel):
    text: str
    source_lang: str = "hi-IN"
    target_lang: str = "en-IN"


@app.post("/translate")
async def translate(data: TranslateInput):

    result = await translate_text(data.text, source=data.source_lang, target=data.target_lang)

    return result

@app.post("/sanitize", response_model=StructuredRecord)
async def sanitize(data: Consultation):
    # Pass the transcript to the LLM to get the clean summary and extracted JSON
    result = await sanitize_and_structure_transcript(data.transcript)
    
    if "error" in result:
        # Return fallback with error message in diagnosis
        return StructuredRecord(
            patient_id=data.patient_id,
            symptoms=[],
            diagnosis=f"Error: {result['error']}",
            prescription=[],
            tests=[],
            followup=""
        )
        
    # Inject patient_id for DB storage
    result["patient_id"] = data.patient_id
    
    # Save asynchronously to MongoDB
    await save_consultation_record(result)
    
    # Extract data from the LLM JSON response and fulfill the response model
    return StructuredRecord(
        patient_id=data.patient_id,
        symptoms=result.get("symptoms", []),
        diagnosis=result.get("diagnosis", "Unknown"),
        prescription=result.get("prescription", []),
        tests=result.get("tests", []),
        followup=result.get("followup", "No follow-up specified")
    )