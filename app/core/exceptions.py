"""Custom application exceptions hierarchy."""


class RAGException(Exception):
    """Base exception for all RAG system exceptions."""
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class DocumentNotFoundError(RAGException):
    """Raised when an indexed document or file cannot be located."""
    pass


class IngestionError(RAGException):
    """Raised when document parsing, chunking, or indexing fails."""
    pass


class LLMProviderError(RAGException):
    """Raised when generation fails at the LLM level."""
    pass


class EvaluationThresholdError(RAGException):
    """Raised when evaluation quality gates fail required thresholds."""
    pass

