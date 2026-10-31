"""FastAPI route handlers for CloudPulse RAG engine."""

from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from app.config import settings
from app.core.models import (
    QueryRequest,
    QueryResponse,
    ChatRequest,
    ChatResponse,
    IngestRequest,
    IngestResponse,
    HealthResponse,
    DocumentsListResponse,
)
from app.core.exceptions import RAGException, IngestionError
from app.services.rag_engine import RAGEngine
from app.services.ingestion import DocumentIngestionService

router = APIRouter(prefix="/api/v1", tags=["RAG Services"])

# Global engine instance holder (configured in app lifespan)
_engine_instance: RAGEngine | None = None
_ingestion_service = DocumentIngestionService(
    chunk_size=settings.CHUNK_SIZE,
    chunk_overlap=settings.CHUNK_OVERLAP,
)


def get_rag_engine() -> RAGEngine:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = RAGEngine()
    return _engine_instance


def set_rag_engine(engine: RAGEngine) -> None:
    global _engine_instance
    _engine_instance = engine


@router.post(
    "/query",
    response_model=QueryResponse,
    summary="Query Knowledge Base",
    description="Submits a natural language query, retrieves relevant document chunks, and generates a grounded response.",
)
async def query_knowledge_base(
    request: QueryRequest,
    engine: RAGEngine = Depends(get_rag_engine),
) -> QueryResponse:
    try:
        return engine.query(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query execution error: {str(e)}",
        )


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Multi-turn Conversational Chat",
    description="Maintains conversation state and answers questions with conversational context.",
)
async def chat_conversation(
    request: ChatRequest,
    engine: RAGEngine = Depends(get_rag_engine),
) -> ChatResponse:
    try:
        return engine.chat(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing error: {str(e)}",
        )


@router.post(
    "/ingest",
    response_model=IngestResponse,
    summary="Ingest & Index Documents",
    description="Scans the knowledge base directory, generates semantic chunks and updates the vector store.",
)
async def ingest_documents(
    request: IngestRequest = IngestRequest(),
    engine: RAGEngine = Depends(get_rag_engine),
) -> IngestResponse:
    target_dir = Path(request.directory_path) if request.directory_path else settings.DATA_DIR
    try:
        response = _ingestion_service.ingest_directory(
            directory_path=target_dir,
            vector_store=engine.vector_store,
            force_reindex=request.force_reindex,
        )
        return response
    except IngestionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(e)}",
        )


@router.get(
    "/documents",
    response_model=DocumentsListResponse,
    summary="List Indexed Documents",
    description="Returns metadata and chunk statistics for all currently indexed knowledge documents.",
)
async def get_indexed_documents(
    engine: RAGEngine = Depends(get_rag_engine),
) -> DocumentsListResponse:
    return engine.get_documents_summary()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="System Health & Diagnostic Check",
    description="Returns live system operational status, active LLM/Embedding providers, and indexed chunks count.",
)
async def get_system_health(
    engine: RAGEngine = Depends(get_rag_engine),
) -> HealthResponse:
    return engine.get_health()

