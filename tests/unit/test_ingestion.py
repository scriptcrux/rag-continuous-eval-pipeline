"""Unit tests for document ingestion and chunking service."""

import pytest
from pathlib import Path
from app.services.ingestion import DocumentIngestionService
from app.core.exceptions import IngestionError


@pytest.mark.unit
def test_document_chunking_and_metadata(ingestion_service, test_settings):
    """Verify markdown documents are chunked with accurate metadata and category tagging."""
    playbook_path = test_settings.DATA_DIR / "incident_response_playbook.md"
    assert playbook_path.exists(), "Playbook markdown file must exist"

    chunks = ingestion_service.process_file(playbook_path)
    assert len(chunks) > 0, "Ingestion should produce non-empty chunks"

    first_chunk = chunks[0]
    assert first_chunk.metadata.source == "incident_response_playbook.md"
    assert first_chunk.metadata.category == "incident_management"
    assert "incident_response_playbook_chunk_" in first_chunk.chunk_id


@pytest.mark.unit
def test_category_determination(ingestion_service):
    """Test category mapping heuristics for different document domains."""
    assert ingestion_service.determine_category("incident_response_playbook.md") == "incident_management"
    assert ingestion_service.determine_category("security_compliance_policy.md") == "security_compliance"
    assert ingestion_service.determine_category("cloud_infrastructure_guide.md") == "infrastructure"
    assert ingestion_service.determine_category("service_level_agreements.md") == "sla"
    assert ingestion_service.determine_category("unknown_guide.txt") == "general"


@pytest.mark.unit
def test_ingestion_error_on_missing_dir(ingestion_service, vector_store):
    """Verify IngestionError is raised when targeting an invalid directory."""
    with pytest.raises(IngestionError):
        ingestion_service.ingest_directory(
            directory_path=Path("non_existent_directory_xyz"),
            vector_store=vector_store,
        )

