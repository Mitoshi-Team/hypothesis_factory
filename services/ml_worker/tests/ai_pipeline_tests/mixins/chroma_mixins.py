from __future__ import annotations

import uuid
from typing import Any, Optional

import chromadb
from chromadb.config import Settings
from models import Chunk

_EPHEMERAL_CLIENT: chromadb.Client | None = None


class ChromaTestMixin:
    """In-memory ChromaDB fixtures for testing."""

    @staticmethod
    def ephemeral_client() -> chromadb.Client:
        global _EPHEMERAL_CLIENT
        if _EPHEMERAL_CLIENT is None:
            _EPHEMERAL_CLIENT = chromadb.EphemeralClient(Settings())
        return _EPHEMERAL_CLIENT

    @staticmethod
    def make_chunk(
        text: str = "Test chunk content",
        document_id: str = "",
        element_ids: Optional[list[str]] = None,
        section_path: str = "root",
        embedding: Optional[list[float]] = None,
    ) -> Chunk:
        return Chunk(
            chunk_id=f"chunk_{uuid.uuid4().hex[:8]}",
            document_id=document_id or str(uuid.uuid4()),
            element_ids=element_ids or [f"el_{uuid.uuid4().hex[:8]}"],
            text=text,
            embedding=embedding or [0.1] * 384,
            metadata={
                "section_path": section_path,
                "source_type": "text",
            },
        )

    @staticmethod
    def make_chunks(count: int = 3) -> list[Chunk]:
        doc_id = str(uuid.uuid4())
        return [
            ChromaTestMixin.make_chunk(
                text=f"Chunk {i} content for testing",
                document_id=doc_id,
                section_path=f"section_{i}",
            )
            for i in range(count)
        ]

    @staticmethod
    def make_history_entry(
        hypothesis_text: str = "Test hypothesis",
        verdict: str = "accept",
        is_positive: bool = True,
        user_id: str = "",
    ) -> dict[str, Any]:
        return {
            "entry_id": f"hist_{uuid.uuid4().hex[:8]}",
            "user_id": user_id,
            "problem": "Test problem",
            "hypothesis_text": hypothesis_text,
            "verdict": verdict,
            "is_positive_example": is_positive,
            "scores": {
                "novelty": 8.0,
                "feasibility": 7.0,
                "effect": 9.0,
                "risk": 3.0,
            },
            "review_comment": "Good hypothesis",
            "user_feedback": "",
            "embedding": [0.1] * 128,
        }
