"""Document ingestion, chunking, and metadata parsing service."""

import os
import time
from pathlib import Path
from typing import List, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.models import RetrievedChunk, SourceMetadata, IngestResponse
from app.core.exceptions import IngestionError
from app.core.logging import get_logger
from app.services.vector_store import BaseVectorStore

logger = get_logger("cloudpulse.ingestion")

CATEGORY_MAPPING = {
    "incident_response_playbook": "incident_management",
    "security_compliance_policy": "security_compliance",
    "cloud_infrastructure_guide": "infrastructure",
    "service_level_agreements": "sla",
}


class DocumentIngestionService:
    """Service responsible for loading, chunking, and indexing knowledge documents."""

    def __init__(
        self,
        chunk_size: int = 400,
        chunk_overlap: int = 80,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
        )

    def determine_category(self, filename: str) -> str:
        stem = Path(filename).stem.lower()
        for key, category in CATEGORY_MAPPING.items():
            if key in stem:
                return category
        return "general"

    def process_file(self, file_path: Path) -> List[RetrievedChunk]:
        """Read and chunk a single document file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            raise IngestionError(f"Failed to read file {file_path}: {e}")

        splits = self.splitter.split_text(content)
        category = self.determine_category(file_path.name)
        file_stem = file_path.stem

        chunks: List[RetrievedChunk] = []
        for idx, text in enumerate(splits):
            chunk_id = f"{file_stem}_chunk_{idx + 1}"
            metadata = SourceMetadata(
                source=file_path.name,
                category=category,
                chunk_id=chunk_id,
            )
            chunks.append(RetrievedChunk(chunk_id=chunk_id, text=text.strip(), metadata=metadata))

        return chunks

    def ingest_directory(
        self,
        directory_path: Path,
        vector_store: BaseVectorStore,
        force_reindex: bool = False,
    ) -> IngestResponse:
        """Scan directory and index all markdown/txt files into vector store."""
        start_time = time.time()
        dir_path = Path(directory_path)

        if not dir_path.exists() or not dir_path.is_dir():
            raise IngestionError(f"Directory not found: {directory_path}")

        if force_reindex:
            vector_store.clear()

        all_chunks: List[RetrievedChunk] = []
        doc_count = 0

        for file_path in dir_path.glob("*.*"):
            if file_path.suffix.lower() in [".md", ".txt"]:
                chunks = self.process_file(file_path)
                all_chunks.extend(chunks)
                doc_count += 1

        if all_chunks:
            vector_store.add_documents(all_chunks)

        duration = time.time() - start_time
        logger.info(
            f"Successfully ingested {doc_count} documents ({len(all_chunks)} chunks) in {duration:.2f}s"
        )

        return IngestResponse(
            status="success",
            documents_indexed=doc_count,
            total_chunks=len(all_chunks),
            duration_seconds=round(duration, 3),
            directory=str(dir_path),
        )

