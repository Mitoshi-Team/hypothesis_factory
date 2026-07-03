from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    yandex_api_key: str = ""
    yandex_folder_id: str = ""

    embed_model: str = "text-embedding"
    llm_model: str = "deepseek-4"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 4096

    chroma_host: str = "localhost"
    chroma_port: int = 8000
    chroma_collection_knowledge: str = "knowledge"
    chroma_collection_history: str = "hypothesis_history"

    postgres_dsn: str = (
        "postgresql://postgres:postgres@localhost:5432/hypothesis_factory"
    )

    chunk_size: int = 1000
    chunk_overlap: int = 200
    embed_batch_size: int = 32

    top_k_rag: int = 10
    top_k_history: int = 6
    max_revision_iterations: int = 10


settings = Settings()
