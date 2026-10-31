"""Integration tests for FastAPI REST API endpoints."""

import pytest
from fastapi import status


@pytest.mark.integration
def test_health_endpoint(test_client):
    """GET /api/v1/health should return system status and indexed chunks count."""
    res = test_client.get("/api/v1/health")
    assert res.status_code == status.HTTP_200_OK

    data = res.json()
    assert data["status"] == "healthy"
    assert data["total_chunks_indexed"] > 0
    assert "CloudPulse" in data["app_name"]


@pytest.mark.integration
def test_documents_endpoint(test_client):
    """GET /api/v1/documents should return all indexed documents and chunk statistics."""
    res = test_client.get("/api/v1/documents")
    assert res.status_code == status.HTTP_200_OK

    data = res.json()
    assert data["total_chunks"] > 0
    assert len(data["documents"]) >= 4

    doc_names = [d["file_name"] for d in data["documents"]]
    assert "incident_response_playbook.md" in doc_names
    assert "security_compliance_policy.md" in doc_names


@pytest.mark.integration
def test_query_endpoint_success(test_client):
    """POST /api/v1/query should return structured answer with citations and timing headers."""
    payload = {
        "question": "What is the initial response SLA for a Severity 1 incident?",
        "top_k": 3,
    }
    res = test_client.post("/api/v1/query", json=payload)
    assert res.status_code == status.HTTP_200_OK
    assert "X-Process-Time-Ms" in res.headers
    assert "X-Request-ID" in res.headers

    data = res.json()
    assert "5 minutes" in data["answer"]
    assert len(data["citations"]) > 0
    assert data["citations"][0]["source"] == "incident_response_playbook.md"
    assert data["latency_ms"] > 0.0


@pytest.mark.integration
def test_query_endpoint_validation_error(test_client):
    """POST /api/v1/query with invalid query should return 422 Unprocessable Entity."""
    # Question too short (min length is 3)
    res = test_client.post("/api/v1/query", json={"question": "ab"})
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.integration
def test_reingest_endpoint(test_client):
    """POST /api/v1/ingest should re-index knowledge documents and return stats."""
    res = test_client.post("/api/v1/ingest", json={"force_reindex": True})
    assert res.status_code == status.HTTP_200_OK

    data = res.json()
    assert data["status"] == "success"
    assert data["documents_indexed"] >= 4
    assert data["total_chunks"] > 0
    assert data["duration_seconds"] >= 0.0

