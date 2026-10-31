"""Dataset loader and Ragas schema adapter."""

import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
from ragas.dataset_schema import SingleTurnSample, MultiTurnSample
from ragas.messages import HumanMessage, AIMessage

from app.config import settings


class BenchmarkDataset:
    """Manages loading and formatting the golden evaluation benchmark."""

    def __init__(self, dataset_path: Path | None = None):
        self.path = dataset_path or (settings.BASE_DIR / "evaluation" / "golden_dataset.json")
        self.raw_data = self._load()

    def _load(self) -> Dict[str, Any]:
        if not self.path.exists():
            raise FileNotFoundError(f"Golden dataset not found at {self.path}")
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    @property
    def single_turn_cases(self) -> List[Dict[str, Any]]:
        return self.raw_data.get("single_turn_samples", [])

    @property
    def standard_cases(self) -> List[Dict[str, Any]]:
        """Non-adversarial cases that expect factual retrieval."""
        return [c for c in self.single_turn_cases if not c.get("is_adversarial", False)]

    @property
    def adversarial_cases(self) -> List[Dict[str, Any]]:
        """Negative/adversarial cases that must be safely refused."""
        return [c for c in self.single_turn_cases if c.get("is_adversarial", False)]

    @property
    def multi_turn_cases(self) -> List[Dict[str, Any]]:
        return self.raw_data.get("multi_turn_samples", [])

    def to_ragas_single_turn_sample(
        self,
        question: str,
        response: str,
        retrieved_contexts: List[str],
        reference: str,
    ) -> SingleTurnSample:
        """Create a Ragas SingleTurnSample instance."""
        return SingleTurnSample(
            user_input=question,
            response=response,
            retrieved_contexts=retrieved_contexts,
            reference=reference,
        )

    def to_ragas_multi_turn_sample(self, case: Dict[str, Any]) -> MultiTurnSample:
        """Create a Ragas MultiTurnSample instance from dialogue history."""
        messages = []
        for msg in case.get("dialogue", []):
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))

        return MultiTurnSample(
            user_input=messages,
            reference_topics=case.get("reference_topics", []),
        )

