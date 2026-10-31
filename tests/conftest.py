"""Pytest configuration and shared test fixtures."""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from app.config import Settings
from app.services.embedding import DenseSemanticEmbedder
from app.services.vector_store import InMemoryVectorStore
from app.services.llm_provider import MockDeterministicLLMProvider
from app.services.ingestion import DocumentIngestionService
from app.services.rag_engine import RAGEngine
from app.api.routes import set_rag_engine
from app.main import app
from evaluation.dataset import BenchmarkDataset
from evaluation.thresholds import DEFAULT_THRESHOLDS


@pytest.fixture(scope="session")
def test_settings():
    return Settings(
        ENVIRONMENT="testing",
        LLM_PROVIDER="mock",
        EMBEDDING_PROVIDER="local",
        CHUNK_SIZE=600,
        CHUNK_OVERLAP=100,
        SIMILARITY_THRESHOLD=0.20,
    )


@pytest.fixture(scope="session")
def embedder():
    return DenseSemanticEmbedder()


@pytest.fixture(scope="session")
def vector_store(embedder):
    return InMemoryVectorStore(embedding_provider=embedder)


@pytest.fixture(scope="session")
def ingestion_service(test_settings):
    return DocumentIngestionService(
        chunk_size=test_settings.CHUNK_SIZE,
        chunk_overlap=test_settings.CHUNK_OVERLAP,
    )


@pytest.fixture(scope="session")
def populated_vector_store(vector_store, ingestion_service, test_settings):
    ingestion_service.ingest_directory(
        directory_path=test_settings.DATA_DIR,
        vector_store=vector_store,
        force_reindex=True,
    )
    return vector_store


@pytest.fixture(scope="session")
def rag_engine(populated_vector_store, test_settings):
    llm = MockDeterministicLLMProvider()
    engine = RAGEngine(
        vector_store=populated_vector_store,
        llm_provider=llm,
        cfg=test_settings,
    )
    set_rag_engine(engine)
    return engine


@pytest.fixture(scope="session")
def test_client(rag_engine):
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def golden_dataset():
    return BenchmarkDataset()


@pytest.fixture(scope="session")
def quality_thresholds():
    return DEFAULT_THRESHOLDS

