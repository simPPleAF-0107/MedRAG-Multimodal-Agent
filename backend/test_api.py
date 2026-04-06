from fastapi.testclient import TestClient
from backend.main import app
import asyncio

client = TestClient(app)

def test():
    print("Testing generate_report...")
    with open("backend/test.txt", "w") as f:
        f.write("test document")
    
    # Try with text and image
    files = [
        ("files", ("test.txt", open("backend/test.txt", "rb"), "text/plain")),
        ("files", ("dummy.jpg", b"fakeimagebytes", "image/jpeg"))
    ]
    res = client.post("/api/v1/rag/generate-report", data={"query": "chest pain"}, files=files)
    print("Status code:", res.status_code)
    print("Response obj:", res.json())

if __name__ == "__main__":
    test()
