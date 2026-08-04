import os
import unittest
from fastapi.testclient import TestClient

# Ensure we're in the backend dir for imports
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.main import app

client = TestClient(app)

class TestAPI(unittest.TestCase):
    def test_healthcheck(self):
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "service": "AI Health Assistant API"})

    def test_analyze_endpoint(self):
        file_data = b"Patient John Doe (age 45) presents with elevated LDL cholesterol (190 mg/dL). Needs a diet change and should see a cardiologist."
        files = {"file": ("report.txt", file_data, "text/plain")}
        data = {"session_id": "test_session_123", "patient_name": "John Doe"}
        response = client.post("/analyze", files=files, data=data)
        if response.status_code != 200:
            print("Analyze error:", response.text)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertEqual(res_json["session_id"], "test_session_123")
        self.assertIn("condition", res_json)
        print("Analyze response:", res_json)

    def test_large_pdf_simulation(self):
        import uuid
        session_id = str(uuid.uuid4())
        # 15,000 characters simulating Z615.pdf (19 chunks)
        large_text = (b"Patient Jane Smith (age 52) medical report details. " * 300)
        files = {"file": ("Z615.pdf", large_text, "application/pdf")}
        data = {"session_id": session_id, "patient_name": "Jane Smith"}
        response = client.post("/analyze", files=files, data=data)
        if response.status_code != 200:
            print("Large PDF Analyze error:", response.text)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertEqual(res_json["session_id"], session_id)
        self.assertIn("condition", res_json)
        print("Large PDF Analyze SUCCESS! Condition:", res_json.get("condition"))

    def test_chat_endpoint(self):
        payload = {
            "session_id": "test_session_123",
            "message": "What is my cholesterol level?"
        }
        response = client.post("/chat", json=payload)
        self.assertEqual(response.status_code, 200)
        print("Chat response:", response.text)
        self.assertGreater(len(response.text), 0)

    def test_pipeline_runs_endpoint(self):
        response = client.get("/pipeline-runs/test_session_123")
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertEqual(res_json["session_id"], "test_session_123")
        self.assertGreater(len(res_json["pipeline_runs"]), 0)
        latest_run = res_json["pipeline_runs"][0]
        self.assertEqual(latest_run["status"], "COMPLETED")
        self.assertEqual(latest_run["filename"], "report.txt")
        print("Pipeline runs response:", res_json)

if __name__ == "__main__":
    unittest.main()
