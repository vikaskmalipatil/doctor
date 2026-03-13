import sys
import unittest
from fastapi.testclient import TestClient
from main import app
from models import Consultation, StructuredRecord

client = TestClient(app)

class TestSanitizeEndpoint(unittest.TestCase):
    def test_sanitize_success(self):
        # We'll test the /sanitize endpoint
        payload = {
            "patient_id": "PAT-12345",
            "transcript": "Doctor: Hello, what brings you in today? Patient: I have a mild headache and fever for the last two days. Doctor: I'll prescribe some Paracetamol, take it twice a day. Also, get a complete blood count test."
        }
        
        response = client.post("/sanitize", json=payload)
        self.assertEqual(response.status_code, 200, f"Expected 200 but got {response.status_code}. Response: {response.text}")
        
        data = response.json()
        self.assertIn("patient_id", data)
        self.assertEqual(data["patient_id"], "PAT-12345")
        self.assertIn("symptoms", data)
        self.assertIn("diagnosis", data)
        self.assertIn("prescription", data)
        self.assertIn("tests", data)
        self.assertIn("followup", data)
        
        print("Sanitize endpoint response:")
        print(data)

if __name__ == '__main__':
    unittest.main()
