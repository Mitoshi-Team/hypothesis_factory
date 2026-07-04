from __future__ import annotations

import os

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_load_path = os.environ.get("ML_WORKER_ENV_FILE", ".env")
load_dotenv(_load_path, override=False)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_load_path,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    yandex_api_key: str = ""
    yandex_folder_id: str = ""

    embed_model: str = Field(
        default="text-embedding",
        alias="YANDEX_EMBED_MODEL",
    )
    llm_model: str = Field(
        default="deepseek-4",
        alias="YANDEX_LLM_MODEL",
    )
    llm_temperature: float = Field(
        default=0.7,
        alias="YANDEX_LLM_TEMPERATURE",
    )
    llm_max_tokens: int = Field(
        default=4096,
        alias="YANDEX_LLM_MAX_TOKENS",
    )

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

    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    report_dir: str = "./reports"

    ner_model_name: str = "urchade/gliner_multi-v2.1"
    hf_token: str = ""


settings = Settings()
