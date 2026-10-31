"""End-to-end RAG orchestrator engine."""

import time
from typing import List, Optional
from app.config import Settings, settings as default_settings
from app.core.models import (
    QueryRequest,
    QueryResponse,
    Citation,
    ChatRequest,
    ChatResponse,
    HealthResponse,
    DocumentsListResponse,
    DocumentInfo,
)
from app.core.logging import get_logger
from app.services.vector_store import BaseVectorStore, InMemoryVectorStore
from app.services.llm_provider import BaseLLMProvider, get_llm_provider

logger = get_logger("cloudpulse.rag_engine")

SYSTEM_PROMPT_TEMPLATE = """You are CloudPulse AI, a trusted enterprise assistant for cloud operations, security compliance, and service policies.
Follow these operational directives strictly:
1. Ground your answer solely in the provided documentation contexts.
2. If the context does not contain sufficient facts to answer the question, respond exactly with:
   "I do not have sufficient information in the knowledge base to answer this question."
3. Do not speculate, extrapolate, or hallucinate facts beyond the retrieved context.
4. Keep the answer direct, concise, and professional.

Documentation Context:
{context_block}

Question: {question}

Answer:"""


class RAGEngine:
    """Orchestrates document retrieval, context formulation, prompt grounding, and answer generation."""

    def __init__(
        self,
        vector_store: Optional[BaseVectorStore] = None,
        llm_provider: Optional[BaseLLMProvider] = None,
        cfg: Optional[Settings] = None,
    ):
        self.config = cfg or default_settings
        self.vector_store = vector_store or InMemoryVectorStore()
        self.llm_provider = llm_provider or get_llm_provider(
            provider_name=self.config.LLM_PROVIDER,
            api_key=self.config.OPENAI_API_KEY,
            model_name=self.config.OPENAI_MODEL if self.config.LLM_PROVIDER == "openai" else self.config.OLLAMA_MODEL,
            base_url=self.config.OLLAMA_BASE_URL,
            temperature=self.config.TEMPERATURE,
        )

    def _build_context_block(self, contexts: List[str]) -> str:
        if not contexts:
            return "No relevant documentation found."
        formatted = []
        for i, ctx in enumerate(contexts, 1):
            formatted.append(f"[Source {i}]:\n{ctx}")
        return "\n\n".join(formatted)

    def query(self, request: QueryRequest) -> QueryResponse:
        start_time = time.perf_counter()
        top_k = request.top_k or self.config.TOP_K

        # Retrieve relevant chunks from vector store
        matched_chunks = self.vector_store.search(
            query=request.question,
            top_k=top_k,
            threshold=self.config.SIMILARITY_THRESHOLD,
            category=request.category_filter,
        )

        contexts = [chunk.text for chunk in matched_chunks]
        citations = [
            Citation(
                source=chunk.metadata.source,
                chunk_id=chunk.chunk_id,
                snippet=chunk.text[:140] + ("..." if len(chunk.text) > 140 else ""),
            )
            for chunk in matched_chunks
        ]

        # Calculate confidence score based on top chunk similarity
        confidence = matched_chunks[0].metadata.score if matched_chunks and matched_chunks[0].metadata.score else 0.0

        # Build grounded prompt
        prompt = SYSTEM_PROMPT_TEMPLATE.format(
            context_block=self._build_context_block(contexts),
            question=request.question,
        )

        # Generate answer from LLM provider
        answer = self.llm_provider.generate_answer(prompt, contexts)
        duration_ms = (time.perf_counter() - start_time) * 1000.0

        logger.info(
            f"Query processed: '{request.question[:40]}...' in {duration_ms:.1f}ms (sources: {len(contexts)})"
        )

        return QueryResponse(
            question=request.question,
            answer=answer,
            retrieved_contexts=contexts,
            citations=citations,
            latency_ms=round(duration_ms, 2),
            confidence_score=round(float(confidence), 3),
            model_name=self.config.LLM_PROVIDER,
            sources_count=len(contexts),
        )

    def chat(self, request: ChatRequest) -> ChatResponse:
        """Multi-turn chat interaction maintaining conversation flow."""
        start_time = time.perf_counter()

        # Augment query with recent conversation context if available
        augmented_query = request.message
        if request.history:
            recent_user_messages = [m.content for m in request.history[-2:] if m.role == "user"]
            if recent_user_messages:
                augmented_query = f"{' '.join(recent_user_messages)} {request.message}"

        query_req = QueryRequest(question=augmented_query)
        res = self.query(query_req)

        duration_ms = (time.perf_counter() - start_time) * 1000.0

        return ChatResponse(
            answer=res.answer,
            session_id=request.session_id or "default_session",
            retrieved_contexts=res.retrieved_contexts,
            latency_ms=round(duration_ms, 2),
        )

    def get_documents_summary(self) -> DocumentsListResponse:
        chunks = self.vector_store.get_all()
        doc_stats: dict[str, dict] = {}

        for c in chunks:
            src = c.metadata.source
            if src not in doc_stats:
                doc_stats[src] = {"chunks": 0, "category": c.metadata.category or "general"}
            doc_stats[src]["chunks"] += 1

        docs = [
            DocumentInfo(file_name=src, chunks_count=info["chunks"], category=info["category"])
            for src, info in doc_stats.items()
        ]
        return DocumentsListResponse(total_chunks=len(chunks), documents=docs)

    def get_health(self) -> HealthResponse:
        return HealthResponse(
            status="healthy",
            app_name=self.config.APP_NAME,
            version=self.config.APP_VERSION,
            environment=self.config.ENVIRONMENT,
            total_chunks_indexed=self.vector_store.count(),
            llm_provider=self.config.LLM_PROVIDER,
            embedding_provider=self.config.EMBEDDING_PROVIDER,
        )

