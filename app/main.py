"""CloudPulse Enterprise RAG Service - Main Application Entrypoint."""

import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.logging import get_logger
from app.core.exceptions import RAGException
from app.api.routes import router, get_rag_engine, _ingestion_service

logger = get_logger("cloudpulse.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context: auto-indexes knowledge base on startup."""
    logger.info(f"Initializing {settings.APP_NAME} v{settings.APP_VERSION} ({settings.ENVIRONMENT})")
    engine = get_rag_engine()

    # Pre-index default knowledge base if directory exists
    if settings.DATA_DIR.exists():
        try:
            logger.info(f"Auto-ingesting knowledge base from {settings.DATA_DIR}")
            _ingestion_service.ingest_directory(
                directory_path=settings.DATA_DIR,
                vector_store=engine.vector_store,
                force_reindex=False,
            )
            logger.info(f"Startup complete: {engine.vector_store.count()} chunks indexed.")
        except Exception as e:
            logger.warning(f"Startup ingestion notice: {e}")

    yield

    logger.info(f"Shutting down {settings.APP_NAME} gracefully.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise Knowledge Assistant with End-to-End RAG Retrieval, Citation Attribution, and Ragas Quality Benchmark Suite.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_and_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start_time = time.perf_counter()

    response = await call_next(request)

    process_time_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
    response.headers["X-Process-Time-Ms"] = str(process_time_ms)
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(RAGException)
async def rag_exception_handler(request: Request, exc: RAGException):
    return JSONResponse(
        status_code=400,
        content={"error": exc.__class__.__name__, "message": exc.message, "details": exc.details},
    )


@app.get("/", tags=["Root"])
async def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "online",
        "documentation": "/docs",
        "health": "/api/v1/health",
    }


app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)

