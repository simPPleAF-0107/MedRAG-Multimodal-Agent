import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_endpoint():
    """
    Basic connectivity validation for the FastAPI application.
    """
    response = client.get("/")
    assert response.status_code == 200

def test_generate_report_api():
    """
    Tests the RAG endpoint interface for handling requests and data formats.
    """
    response = client.post(
        "/api/v1/rag/generate-report",
        data={"query": "Mild headache for three days."}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "final_report" in data["data"]
