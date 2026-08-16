import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "stt_model" in data

def test_text_query_endpoint():
    response = client.post(
        "/api/query",
        data={"text_query": "What languages are included in MSMARCO-XI?", "strategy_override": "auto"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    assert "answer" in data
    assert "latency_breakdown_ms" in data
    assert "total_latency_ms" in data

def test_stt_endpoint():
    # Send dummy audio bytes
    response = client.post(
        "/api/stt",
        files={"file": ("test.wav", b"RIFF....WAVEfmt ....data....", "audio/wav")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "transcript" in data
    assert "latency_ms" in data
