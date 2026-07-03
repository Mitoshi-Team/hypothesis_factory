from __future__ import annotations

import pytest

from ai_pipeline_tests.mixins.chroma_mixins import ChromaTestMixin
from ai_pipeline_tests.mixins.chunking_mixins import ChunkingTestMixin
from ai_pipeline_tests.mixins.db_mixins import DatabaseTestMixin
from ai_pipeline_tests.mixins.llm_mixins import LLMTestMixin


@pytest.fixture
def chunk_fx() -> ChunkingTestMixin:
    return ChunkingTestMixin()


@pytest.fixture
def llm_fx() -> LLMTestMixin:
    return LLMTestMixin()


@pytest.fixture
def chroma_fx() -> ChromaTestMixin:
    return ChromaTestMixin()


@pytest.fixture
def db_fx() -> DatabaseTestMixin:
    return DatabaseTestMixin()
