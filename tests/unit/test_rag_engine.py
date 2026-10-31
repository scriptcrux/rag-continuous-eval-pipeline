"""Unit tests for RAG engine orchestration and citation generation."""

import pytest
from app.core.models import QueryRequest, ChatRequest


@pytest.mark.unit
def test_rag_engine_factual_query(rag_engine):
    """Test standard factual query returns grounded answer with citations and low latency."""
    req = QueryRequest(question="What is the initial response SLA for a Severity 1 incident?")
    res = rag_engine.query(req)

    assert "5 minutes" in res.answer
    assert len(res.retrieved_contexts) > 0
    assert len(res.citations) > 0
    assert res.citations[0].source == "incident_response_playbook.md"
    assert res.latency_ms > 0.0
    assert res.confidence_score > 0.2


@pytest.mark.unit
def test_rag_engine_adversarial_refusal(rag_engine):
    """Test out-of-domain query triggers guardrail refusal and returns 0 sources."""
    req = QueryRequest(question="What is the recipe for chocolate cake?")
    res = rag_engine.query(req)

    assert "not have sufficient information" in res.answer.lower()
    assert res.sources_count == 0


@pytest.mark.unit
def test_rag_engine_chat_flow(rag_engine):
    """Test multi-turn chat interaction through RAG engine."""
    chat_req = ChatRequest(
        message="When are standard weekly maintenance windows scheduled?",
        session_id="test_session_42",
    )
    chat_res = rag_engine.chat(chat_req)

    assert "Sundays" in chat_res.answer or "02:00 UTC" in chat_res.answer
    assert chat_res.session_id == "test_session_42"
    assert chat_res.latency_ms > 0.0

