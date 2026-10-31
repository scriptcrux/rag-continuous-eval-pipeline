"""Pydantic schemas and data transfer objects."""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field


class SourceMetadata(BaseModel):
    source: str = Field(..., description="Source document file name or URI")
    category: Optional[str] = Field(default="general", description="Document domain category")
    chunk_id: str = Field(..., description="Unique chunk identifier")
    score: Optional[float] = Field(default=None, description="Similarity score (0.0 to 1.0)")


class RetrievedChunk(BaseModel):
    chunk_id: str
    text: str
    metadata: SourceMetadata


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, description="The user query to be answered by the RAG system")
    top_k: Optional[int] = Field(default=None, ge=1, le=10, description="Override top-K chunks retrieved")
    category_filter: Optional[str] = Field(default=None, description="Optional category filter")


class Citation(BaseModel):
    source: str
    chunk_id: str
    snippet: str


class QueryResponse(BaseModel):
    question: str
    answer: str
    retrieved_contexts: List[str] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)
    latency_ms: float
    confidence_score: float
    model_name: str
    sources_count: int


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: Optional[str] = Field(default="default_session")
    history: List[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    retrieved_contexts: List[str] = Field(default_factory=list)
    latency_ms: float


class IngestRequest(BaseModel):
    directory_path: Optional[str] = Field(default=None, description="Optional custom directory path to ingest")
    force_reindex: bool = Field(default=False, description="Whether to clear existing index before ingesting")


class IngestResponse(BaseModel):
    status: str
    documents_indexed: int
    total_chunks: int
    duration_seconds: float
    directory: str


class DocumentInfo(BaseModel):
    file_name: str
    chunks_count: int
    category: str


class DocumentsListResponse(BaseModel):
    total_chunks: int
    documents: List[DocumentInfo]


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    environment: str
    total_chunks_indexed: int
    llm_provider: str
    embedding_provider: str

