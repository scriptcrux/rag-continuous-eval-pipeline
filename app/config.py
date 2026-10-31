"""Application Configuration Module using Pydantic Settings."""

import os
from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # Environment & Server
    APP_NAME: str = "CloudPulse RAG Intelligence Engine"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: Literal["development", "testing", "production"] = "development"
    DEBUG: bool = False
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # Paths
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data" / "knowledge_base"
    CHROMA_PERSIST_DIR: Path = BASE_DIR / "data" / "chroma_db"
    EVALUATION_DIR: Path = BASE_DIR / "evaluation"

    # RAG Retrieval Settings
    TOP_K: int = 3
    SIMILARITY_THRESHOLD: float = 0.20
    CHUNK_SIZE: int = 600
    CHUNK_OVERLAP: int = 100

    # Providers: "mock" (for deterministic local tests & CI), "openai", or "ollama"
    LLM_PROVIDER: Literal["mock", "openai", "ollama"] = "mock"
    EMBEDDING_PROVIDER: Literal["local", "openai"] = "local"

    # Model Names
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_API_KEY: str = ""
    OLLAMA_MODEL: str = "llama3.2:latest"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    TEMPERATURE: float = 0.0

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

