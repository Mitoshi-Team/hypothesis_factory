from __future__ import annotations

import pytest

from .mixins.chroma_mixins import ChromaTestMixin
from .mixins.chunking_mixins import ChunkingTestMixin
from .mixins.db_mixins import DatabaseTestMixin
from .mixins.llm_mixins import LLMTestMixin


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
