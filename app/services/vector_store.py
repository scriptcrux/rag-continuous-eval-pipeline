"""Vector Store implementations with In-Memory and ChromaDB backends."""

from abc import ABC, abstractmethod
from typing import List, Optional
import numpy as np
from app.core.models import RetrievedChunk, SourceMetadata
from app.services.embedding import BaseEmbeddingProvider, get_embedding_provider


class BaseVectorStore(ABC):
    """Abstract interface for RAG vector stores."""

    @abstractmethod
    def add_documents(self, chunks: List[RetrievedChunk]) -> None:
        """Add document chunks to vector index."""
        pass

    @abstractmethod
    def search(
        self,
        query: str,
        top_k: int = 3,
        threshold: float = 0.0,
        category: Optional[str] = None,
    ) -> List[RetrievedChunk]:
        """Perform semantic similarity search."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Return total indexed chunks count."""
        pass

    @abstractmethod
    def get_all(self) -> List[RetrievedChunk]:
        """Retrieve all indexed chunks."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all stored vectors and documents."""
        pass


class InMemoryVectorStore(BaseVectorStore):
    """Production-grade In-Memory Vector Store.

    Ideal for fast, hermetic, reproducible CI/CD testing, microservice instances,
    and environments requiring deterministic retrieval without disk locks.
    """

    def __init__(self, embedding_provider: Optional[BaseEmbeddingProvider] = None):
        self.embedding_provider = embedding_provider or get_embedding_provider("local")
        self._chunks: List[RetrievedChunk] = []
        self._vectors: Optional[np.ndarray] = None

    def add_documents(self, chunks: List[RetrievedChunk]) -> None:
        if not chunks:
            return

        texts = [chunk.text for chunk in chunks]
        embeddings = self.embedding_provider.embed_documents(texts)
        new_vecs = np.array(embeddings, dtype=np.float32)

        if self._vectors is None or len(self._chunks) == 0:
            self._vectors = new_vecs
            self._chunks = list(chunks)
        else:
            self._vectors = np.vstack([self._vectors, new_vecs])
            self._chunks.extend(chunks)

    def search(
        self,
        query: str,
        top_k: int = 3,
        threshold: float = 0.0,
        category: Optional[str] = None,
    ) -> List[RetrievedChunk]:
        if not self._chunks or self._vectors is None:
            return []

        query_vec = np.array(self.embedding_provider.embed_query(query), dtype=np.float32)
        # Cosine similarity via dot product (assuming normalized vectors)
        scores = np.dot(self._vectors, query_vec)

        # Pair indices with scores
        scored_indices = []
        for idx, score in enumerate(scores):
            chunk = self._chunks[idx]
            if category and chunk.metadata.category != category:
                continue
            if score >= threshold:
                scored_indices.append((score, idx))

        # Sort descending by similarity score
        scored_indices.sort(key=lambda x: x[0], reverse=True)
        top_matches = scored_indices[:top_k]

        results = []
        for score, idx in top_matches:
            original = self._chunks[idx]
            updated_meta = original.metadata.model_copy()
            updated_meta.score = round(float(score), 4)
            results.append(
                RetrievedChunk(
                    chunk_id=original.chunk_id,
                    text=original.text,
                    metadata=updated_meta,
                )
            )
        return results

    def count(self) -> int:
        return len(self._chunks)

    def get_all(self) -> List[RetrievedChunk]:
        return list(self._chunks)

    def clear(self) -> None:
        self._chunks.clear()
        self._vectors = None


class ChromaVectorStore(BaseVectorStore):
    """ChromaDB-backed Persistent Vector Store."""

    def __init__(
        self,
        persist_directory: str,
        collection_name: str = "cloudpulse_docs",
        embedding_provider: Optional[BaseEmbeddingProvider] = None,
    ):
        import chromadb
        self.embedding_provider = embedding_provider or get_embedding_provider("local")
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self._cache_chunks: dict[str, RetrievedChunk] = {}

    def add_documents(self, chunks: List[RetrievedChunk]) -> None:
        if not chunks:
            return

        texts = [chunk.text for chunk in chunks]
        embeddings = self.embedding_provider.embed_documents(texts)
        ids = [chunk.chunk_id for chunk in chunks]
        metadatas = [
            {
                "source": chunk.metadata.source,
                "category": chunk.metadata.category or "general",
            }
            for chunk in chunks
        ]

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )
        for chunk in chunks:
            self._cache_chunks[chunk.chunk_id] = chunk

    def search(
        self,
        query: str,
        top_k: int = 3,
        threshold: float = 0.0,
        category: Optional[str] = None,
    ) -> List[RetrievedChunk]:
        query_vec = self.embedding_provider.embed_query(query)
        where_filter = {"category": category} if category else None

        results = self.collection.query(
            query_embeddings=[query_vec],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        output: List[RetrievedChunk] = []
        if not results or not results["ids"] or not results["ids"][0]:
            return output

        ids = results["ids"][0]
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        distances = results.get("distances", [[0.0] * len(ids)])[0]

        for chunk_id, doc, meta, dist in zip(ids, docs, metas, distances):
            # Convert distance to similarity score
            similarity = max(0.0, 1.0 - (dist / 2.0)) if dist is not None else 1.0
            if similarity < threshold:
                continue
            output.append(
                RetrievedChunk(
                    chunk_id=chunk_id,
                    text=doc,
                    metadata=SourceMetadata(
                        source=meta.get("source", "unknown"),
                        category=meta.get("category", "general"),
                        chunk_id=chunk_id,
                        score=round(similarity, 4),
                    ),
                )
            )
        return output

    def count(self) -> int:
        return self.collection.count()

    def get_all(self) -> List[RetrievedChunk]:
        return list(self._cache_chunks.values())

    def clear(self) -> None:
        try:
            self.client.delete_collection(self.collection.name)
            self.collection = self.client.create_collection(self.collection.name)
            self._cache_chunks.clear()
        except Exception:
            pass

