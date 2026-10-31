"""Continuous Integration Quality Gate Tests for Ragas Evaluation Suite."""

import pytest
from evaluation.evaluator import RagasEvaluator


@pytest.fixture
def evaluator(rag_engine, quality_thresholds):
    return RagasEvaluator(rag_engine=rag_engine, thresholds=quality_thresholds, provider="mock")


@pytest.mark.eval
@pytest.mark.asyncio
async def test_full_ragas_benchmark_quality_gates(evaluator, golden_dataset, quality_thresholds):
    """Executes complete benchmark and asserts that all enterprise quality gates pass."""
    report = await evaluator.run_benchmark(golden_dataset)

    # 1. Overall Pass check
    assert report.all_passed is True, "All Ragas quality gates must pass"

    # 2. Individual metric checks against defined thresholds
    metrics = report.metrics_summary

    assert metrics["faithfulness"].score >= quality_thresholds.min_faithfulness, (
        f"Faithfulness {metrics['faithfulness'].score} breached threshold {quality_thresholds.min_faithfulness}"
    )

    assert metrics["response_relevance"].score >= quality_thresholds.min_response_relevance, (
        f"Response relevance {metrics['response_relevance'].score} breached threshold {quality_thresholds.min_response_relevance}"
    )

    assert metrics["context_precision"].score >= quality_thresholds.min_context_precision, (
        f"Context precision {metrics['context_precision'].score} breached threshold {quality_thresholds.min_context_precision}"
    )

    assert metrics["context_recall"].score >= quality_thresholds.min_context_recall, (
        f"Context recall {metrics['context_recall'].score} breached threshold {quality_thresholds.min_context_recall}"
    )

    assert metrics["negative_refusal_rate"].score >= quality_thresholds.min_negative_refusal_rate, (
        f"Negative refusal rate {metrics['negative_refusal_rate'].score} breached threshold {quality_thresholds.min_negative_refusal_rate}"
    )

    # 3. Operational SLA checks
    assert report.latency_p95_ms <= quality_thresholds.max_latency_p95_ms, (
        f"p95 latency {report.latency_p95_ms}ms exceeded SLA limit {quality_thresholds.max_latency_p95_ms}ms"
    )

    assert report.multi_turn_score >= 0.80, (
        f"Multi-turn adherence {report.multi_turn_score} below minimum 0.80"
    )

