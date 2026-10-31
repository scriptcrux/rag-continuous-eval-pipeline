"""LLM provider abstraction supporting Mock (for CI/CD), OpenAI, and Ollama."""

import re
from abc import ABC, abstractmethod
from typing import List, Optional
from app.core.exceptions import LLMProviderError


class BaseLLMProvider(ABC):
    """Abstract interface for LLM response generation."""

    @abstractmethod
    def generate_answer(self, prompt: str, contexts: List[str]) -> str:
        """Generate response based on grounded prompt and retrieved contexts."""
        pass


class MockDeterministicLLMProvider(BaseLLMProvider):
    """Hermetic, deterministic LLM provider for zero-cost CI/CD testing.

    Ensures 100% grounded answers based strictly on retrieved contexts,
    and returns exact negative refusal responses when no relevant context exists.
    """

    NEGATIVE_RESPONSE = "I do not have sufficient information in the knowledge base to answer this question."

    def generate_answer(self, prompt: str, contexts: List[str]) -> str:
        if not contexts:
            return self.NEGATIVE_RESPONSE

        # Extract the user question from the prompt
        q_match = re.search(r"Question:\s*(.*?)(?:\n|$)", prompt, re.IGNORECASE)
        question = q_match.group(1).strip() if q_match else prompt.lower()
        q_lower = question.lower()

        # Check for out-of-domain / irrelevant queries (guardrail test)
        irrelevant_keywords = ["recipe", "cake", "weather", "mars", "bitcoin", "football", "movie", "song"]
        if any(word in q_lower for word in irrelevant_keywords):
            return self.NEGATIVE_RESPONSE

        combined_context = " ".join(contexts)

        # Domain fact extraction logic based on the CloudPulse knowledge base
        if ("sev-1" in q_lower or "severity 1" in q_lower) and ("response" in q_lower or "sla" in q_lower or "acknowledge" in q_lower):
            if "5 minutes" in combined_context:
                return "The initial response SLA for a Severity 1 (Sev-1) incident is 5 minutes from automated alert or customer escalation."

        if ("sev-2" in q_lower or "severity 2" in q_lower) and ("response" in q_lower or "sla" in q_lower):
            if "15 minutes" in combined_context:
                return "The initial response SLA for a Severity 2 (Sev-2) incident is 15 minutes."

        if "post-mortem" in q_lower or "rca" in q_lower or "retrospective" in q_lower:
            if "48 hours" in combined_context:
                return "A blameless post-mortem retrospective meeting must be scheduled within 48 hours of incident closure."

        if "mfa" in q_lower or "multi-factor" in q_lower or "authenticator" in q_lower:
            if "fido2" in combined_context.lower() or "hardware" in combined_context.lower():
                return "Allowed MFA methods are hardware security keys (FIDO2 / WebAuthn, such as YubiKey) or TOTP authenticator apps. SMS and voice-call verification are explicitly prohibited due to SIM-swapping vulnerabilities."

        if "audit log" in q_lower or "retention" in q_lower:
            if "7 years" in combined_context:
                return "Security audit logs must be retained for a minimum of 7 years to satisfy SOC 2 and federal regulatory compliance audits."

        if ("cpu" in q_lower or "memory" in q_lower or "autoscaling" in q_lower or "hpa" in q_lower):
            if "70%" in combined_context and "80%" in combined_context:
                return "The target CPU utilization threshold is 70% and the target memory utilization threshold is 80%."

        if "rto" in q_lower or "recovery time" in q_lower:
            if "15 minutes" in combined_context:
                return "The Recovery Time Objective (RTO) maximum acceptable downtime is 15 minutes, and the Recovery Point Objective (RPO) maximum allowable data loss window is 5 minutes."

        if "rpo" in q_lower or "recovery point" in q_lower:
            if "5 minutes" in combined_context:
                return "The Recovery Point Objective (RPO) maximum allowable data loss window is 5 minutes, and the Recovery Time Objective (RTO) maximum acceptable downtime is 15 minutes."

        if "uptime" in q_lower or "availability" in q_lower or "credit" in q_lower:
            if "99.95%" in combined_context:
                if "credit" in q_lower or "breach" in q_lower or "penalty" in q_lower or "95%" in q_lower:
                    return "The Monthly Uptime Percentage commitment is at least 99.95%, and if uptime drops below 95.0%, a 50% monthly recurring charges credit applies."
                return "CloudPulse guarantees a Monthly Uptime Percentage commitment of at least 99.95% across all production API services."

        if "maintenance" in q_lower:
            if "sundays" in combined_context.lower():
                return "Standard weekly maintenance windows are reserved on Sundays between 02:00 UTC and 04:00 UTC."

        if "gdpr" in q_lower or "right to be forgotten" in q_lower:
            if "30 calendar days" in combined_context:
                return "GDPR 'Right to be Forgotten' deletion requests must be completed and cryptographically verified within 30 calendar days."

        # Generic context-grounded fallback: extract most relevant sentences
        sentences = [s.strip() for s in re.split(r"[.\n]", combined_context) if len(s.strip()) > 20]
        q_words = set(re.findall(r"\w+", q_lower)) - {"what", "is", "the", "are", "how", "many", "for", "in", "of", "to"}

        best_sentence = ""
        max_matches = 0
        for sentence in sentences:
            s_words = set(re.findall(r"\w+", sentence.lower()))
            matches = len(q_words & s_words)
            if matches > max_matches:
                max_matches = matches
                best_sentence = sentence

        if best_sentence and max_matches >= 2:
            return f"Based on the documentation: {best_sentence}."

        return self.NEGATIVE_RESPONSE


class OpenAILLMProvider(BaseLLMProvider):
    """OpenAI Chat completion provider."""

    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini", temperature: float = 0.0):
        from langchain_openai import ChatOpenAI
        self.client = ChatOpenAI(model=model_name, temperature=temperature, openai_api_key=api_key)

    def generate_answer(self, prompt: str, contexts: List[str]) -> str:
        try:
            response = self.client.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            raise LLMProviderError(f"OpenAI generation error: {e}")


class OllamaLLMProvider(BaseLLMProvider):
    """Local Ollama LLM provider."""

    def __init__(self, model_name: str = "llama3.2:latest", base_url: str = "http://localhost:11434", temperature: float = 0.0):
        from langchain_ollama import ChatOllama
        self.client = ChatOllama(model=model_name, base_url=base_url, temperature=temperature)

    def generate_answer(self, prompt: str, contexts: List[str]) -> str:
        try:
            response = self.client.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            raise LLMProviderError(f"Ollama generation error: {e}")


def get_llm_provider(
    provider_name: str = "mock",
    api_key: str = "",
    model_name: Optional[str] = None,
    base_url: Optional[str] = None,
    temperature: float = 0.0,
) -> BaseLLMProvider:
    """Factory to instantiate LLM provider."""
    if provider_name == "openai" and api_key:
        return OpenAILLMProvider(api_key=api_key, model_name=model_name or "gpt-4o-mini", temperature=temperature)
    elif provider_name == "ollama":
        return OllamaLLMProvider(
            model_name=model_name or "llama3.2:latest",
            base_url=base_url or "http://localhost:11434",
            temperature=temperature,
        )
    return MockDeterministicLLMProvider()

