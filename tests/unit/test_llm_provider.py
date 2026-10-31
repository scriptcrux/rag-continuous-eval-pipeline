"""Unit tests for LLM provider abstraction and deterministic guardrails."""

import pytest
from app.services.llm_provider import MockDeterministicLLMProvider


@pytest.fixture
def mock_llm():
    return MockDeterministicLLMProvider()


@pytest.mark.unit
def test_mock_llm_grounded_answer_extraction(mock_llm):
    """Verify mock LLM accurately extracts facts when context contains the answer."""
    prompt = "Question: What is the initial response SLA for a Severity 1 incident?\nAnswer:"
    contexts = [
        "Severity 1 (Critical / Sev-1): Initial Response SLA: 5 minutes from automated alert."
    ]
    answer = mock_llm.generate_answer(prompt, contexts)
    assert "5 minutes" in answer
    assert "Severity 1" in answer or "Sev-1" in answer


@pytest.mark.unit
def test_mock_llm_anti_hallucination_refusal_on_empty_context(mock_llm):
    """Verify LLM refuses to answer when no context is provided."""
    prompt = "Question: What is the SLA?\nAnswer:"
    answer = mock_llm.generate_answer(prompt, contexts=[])
    assert answer == MockDeterministicLLMProvider.NEGATIVE_RESPONSE


@pytest.mark.unit
def test_mock_llm_refusal_on_adversarial_out_of_domain_query(mock_llm):
    """Verify LLM intercepts adversarial or out-of-domain questions with negative refusal."""
    prompt = "Question: What is the best recipe for baking chocolate cake?\nAnswer:"
    contexts = ["CloudPulse operates on AWS us-east-1 and us-west-2 regions."]
    answer = mock_llm.generate_answer(prompt, contexts)
    assert answer == MockDeterministicLLMProvider.NEGATIVE_RESPONSE

