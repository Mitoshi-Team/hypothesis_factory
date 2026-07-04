from __future__ import annotations

import os
from unittest.mock import patch

import chromadb
import pytest
from chromadb.config import Settings as ChromaSettings

# Set dummy credentials for testing Yandex AI Studio Client / OpenAI client
os.environ.setdefault("YANDEX_API_KEY", "dummy_yandex_api_key")
os.environ.setdefault("YANDEX_FOLDER_ID", "dummy_yandex_folder_id")


@pytest.fixture(autouse=True)
def mock_chroma_http_client():
    """Mock HttpClient to avoid slow network/timeout requests during testing."""
    with patch("chromadb.HttpClient") as mock_http:
        mock_http.side_effect = lambda *args, **kwargs: (
            chromadb.EphemeralClient(ChromaSettings())
        )
        yield mock_http
