"""Ragas metric-specific automated tests."""

import pytest
from evaluation.evaluator import RagasEvaluator


@pytest.fixture
def evaluator(rag_engine, quality_thresholds):
    return RagasEvaluator(rag_engine=rag_engine, thresholds=quality_thresholds, provider="mock")


@pytest.mark.eval
@pytest.mark.asyncio
async def test_faithfulness_metric_on_grounded_sample(evaluator, golden_dataset):
    """Verify faithfulness score is >= 0.85 when answer is grounded in retrieved context."""
    case = golden_dataset.single_turn_cases[0]  # tc_001
    result = await evaluator.evaluate_single_sample(case)

    assert result.scores["faithfulness"] >= 0.85
    assert len(result.retrieved_contexts) > 0


@pytest.mark.eval
@pytest.mark.asyncio
async def test_context_recall_and_precision_metrics(evaluator, golden_dataset):
    """Verify retrieved contexts contain ground truth reference facts with top rank precision."""
    case = golden_dataset.single_turn_cases[0]  # tc_001
    result = await evaluator.evaluate_single_sample(case)

    assert result.scores["context_recall"] >= 0.80
    assert result.scores["context_precision"] >= 0.80


@pytest.mark.eval
@pytest.mark.asyncio
async def test_adversarial_negative_refusal_metric(evaluator, golden_dataset):
    """Verify adversarial out-of-domain query gets 1.0 refusal score without hallucination."""
    adv_case = [c for c in golden_dataset.single_turn_cases if c["is_adversarial"]][0]
    result = await evaluator.evaluate_single_sample(adv_case)

    assert result.scores["negative_refusal"] == 1.0
    assert "not have sufficient information" in result.response.lower()


@pytest.mark.eval
@pytest.mark.asyncio
async def test_multi_turn_topic_adherence(evaluator, golden_dataset):
    """Verify multi-turn conversation maintains topic coherence across turns."""
    mt_case = golden_dataset.multi_turn_cases[0]
    score = await evaluator.evaluate_multi_turn_sample(mt_case)

    assert score >= 0.80

