"""Unit tests for Vector Store operations and similarity search."""

import pytest
from app.services.vector_store import InMemoryVectorStore
from app.core.models import RetrievedChunk, SourceMetadata


@pytest.fixture
def fresh_store(embedder):
    return InMemoryVectorStore(embedding_provider=embedder)


@pytest.mark.unit
def test_vector_store_add_and_count(fresh_store):
    """Test adding chunks to vector store updates count properly."""
    assert fresh_store.count() == 0

    chunk = RetrievedChunk(
        chunk_id="test_chunk_1",
        text="The SLA for Sev-1 incidents is 5 minutes.",
        metadata=SourceMetadata(source="test.md", category="sla", chunk_id="test_chunk_1"),
    )
    fresh_store.add_documents([chunk])
    assert fresh_store.count() == 1


@pytest.mark.unit
def test_vector_store_similarity_search_ranking(fresh_store):
    """Verify semantic search returns relevant chunks with highest similarity first."""
    chunks = [
        RetrievedChunk(
            chunk_id="c_incident",
            text="Initial Response SLA for Sev-1 incident is 5 minutes from automated alert.",
            metadata=SourceMetadata(source="incident.md", category="incident", chunk_id="c_incident"),
        ),
        RetrievedChunk(
            chunk_id="c_cloud",
            text="Kubernetes clusters use AWS Graviton ARM64 c7g.2xlarge compute instances.",
            metadata=SourceMetadata(source="cloud.md", category="infrastructure", chunk_id="c_cloud"),
        ),
        RetrievedChunk(
            chunk_id="c_security",
            text="Security audit logs must be retained for a minimum of 7 years.",
            metadata=SourceMetadata(source="sec.md", category="security", chunk_id="c_security"),
        ),
    ]
    fresh_store.add_documents(chunks)

    results = fresh_store.search("What is the Sev-1 incident response SLA?", top_k=2, threshold=0.1)
    assert len(results) > 0
    top_result = results[0]
    assert top_result.chunk_id == "c_incident"
    assert top_result.metadata.score > 0.3


@pytest.mark.unit
def test_vector_store_threshold_filtering(fresh_store):
    """Verify low-similarity chunks below threshold are filtered out."""
    chunk = RetrievedChunk(
        chunk_id="c_irrelevant",
        text="Chocolate cake requires flour, sugar, and cocoa powder.",
        metadata=SourceMetadata(source="recipe.md", category="cooking", chunk_id="c_irrelevant"),
    )
    fresh_store.add_documents([chunk])

    # Search with high threshold for unrelated topic
    results = fresh_store.search("Kubernetes disaster recovery failover", top_k=1, threshold=0.4)
    assert len(results) == 0


@pytest.mark.unit
def test_vector_store_clear(fresh_store):
    """Verify clearing vector store empties all indexed entries."""
    chunk = RetrievedChunk(
        chunk_id="c_1",
        text="Temporary text chunk.",
        metadata=SourceMetadata(source="temp.md", chunk_id="c_1"),
    )
    fresh_store.add_documents([chunk])
    assert fresh_store.count() == 1

    fresh_store.clear()
    assert fresh_store.count() == 0
    assert len(fresh_store.get_all()) == 0

