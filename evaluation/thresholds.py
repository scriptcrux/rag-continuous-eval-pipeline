"""Quality gates and threshold configurations for RAG evaluation."""

from pydantic import BaseModel, Field


class EvaluationThresholds(BaseModel):
    """Production quality gates for RAG pipeline evaluation."""

    # Ragas Metrics Thresholds (0.0 to 1.0)
    min_faithfulness: float = Field(
        default=0.85,
        description="Minimum faithfulness score required to prevent hallucination",
    )
    min_response_relevance: float = Field(
        default=0.80,
        description="Minimum response relevance required for direct query answering",
    )
    min_context_precision: float = Field(
        default=0.80,
        description="Minimum context precision required for high-ranked retrieval",
    )
    min_context_recall: float = Field(
        default=0.80,
        description="Minimum context recall required for ground-truth coverage",
    )

    # Safety & Operational Thresholds
    min_negative_refusal_rate: float = Field(
        default=1.00,
        description="100% of out-of-scope/adversarial queries must trigger safe refusal",
    )
    max_latency_p95_ms: float = Field(
        default=2500.0,
        description="Maximum allowed 95th percentile latency in milliseconds",
    )


# Default quality gates instance
DEFAULT_THRESHOLDS = EvaluationThresholds()

