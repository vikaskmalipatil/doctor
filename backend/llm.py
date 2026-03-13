import os
import json
import google.generativeai as genai

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY", "dummy")
genai.configure(api_key=api_key)

SYSTEM_PROMPT = """
You are an expert clinical sanitizer and medical scribe.
From the following consultation transcript, generate a structured medical report.

Return ONLY a strictly valid JSON object with the following keys:
{
    "symptoms": ["list", "of", "symptoms"],
    "diagnosis": "Short potential diagnosis description",
    "prescription": [
        {
            "medication": "Medicine Name",
            "dosage": "Dosage instructions",
            "duration": "Duration"
        }
    ],
    "tests": ["list", "of", "diagnostic tests"],
    "followup": "Follow-up instructions"
}

Do NOT wrap the output in ```json ... ``` markdown blocks. Output purely the parseable JSON string.
"""

# We initialize the model. For structure, gemini-1.5-flash is extremely fast.
# In production with correct library versions we can use response_mime_type="application/json"
model = genai.GenerativeModel(
    "gemini-1.5-flash", 
    system_instruction=SYSTEM_PROMPT
)

async def sanitize_and_structure_transcript(transcript: str) -> dict:
    try:
        # Wrap string parsing correctly
        prompt_with_data = f"Consultation Transcript:\n{transcript}"
        
        # We can simulate Async by running generate_content_async if supported, 
        # else fallback to generate_content
        response = await model.generate_content_async(
            prompt_with_data,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                response_mime_type="application/json", # Ensures strict JSON compliance
            )
        )
        
        raw_content = response.text
        
        # Clean up if markdown accidentally bleeds through
        if raw_content.startswith("```json"):
            raw_content = raw_content[7:]
        if raw_content.endswith("```"):
            raw_content = raw_content[:-3]
            
        return json.loads(raw_content.strip())
        
    except Exception as e:
        print(f"Error structuring transcript with Gemini: {e}")
        return {"error": str(e)}
