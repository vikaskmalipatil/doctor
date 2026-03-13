from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class Consultation(BaseModel):
    patient_id: str
    transcript: str

class StructuredRecord(BaseModel):
    patient_id: str
    symptoms: List[str]
    diagnosis: str
    prescription: List[Dict[str, str]]
    tests: List[str]
    followup: str