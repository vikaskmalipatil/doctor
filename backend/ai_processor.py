def process_consultation(transcript):

    structured = {
        "symptoms": ["fever", "headache"],
        "clinical_notes": transcript,
        "prescription": [
            {"medicine": "Paracetamol", "dosage": "500mg"}
        ],
        "tests": ["Blood Test"]
    }

    return structured