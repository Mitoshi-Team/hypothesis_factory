from __future__ import annotations

from typing import Optional
from unittest.mock import MagicMock

import httpx


class LLMTestMixin:
    """Mock Yandex AI Studio client for testing."""

    @staticmethod
    def mock_embedding(dim: int = 384) -> list[float]:
        return [float(i % 10) / 10.0 for i in range(dim)]

    @staticmethod
    def mock_completion(text: str = "Mock response") -> str:
        return text

    def patch_client(
        self,
        embed_return: Optional[list[list[float]]] = None,
        complete_return: Optional[str] = None,
    ) -> MagicMock:
        mock = MagicMock()

        if embed_return is not None:
            mock.embed.return_value = embed_return
        else:
            mock.embed.return_value = [self.mock_embedding()]

        if complete_return is not None:
            mock.complete.return_value = complete_return
        else:
            mock.complete.return_value = "{}"

        mock.complete_with_tools.return_value = (
            complete_return or "{}",
            [],
        )

        return mock

    def patch_httpx(
        self,
        embed_response: Optional[dict] = None,
        completion_response: Optional[dict] = None,
    ) -> MagicMock:
        mock = MagicMock(spec=httpx.Response)
        mock.status_code = 200

        if embed_response:
            mock.json.return_value = embed_response
        elif completion_response:
            mock.json.return_value = completion_response
        else:
            mock.json.return_value = {
                "result": {
                    "alternatives": [{"message": {"text": "Mock response"}}]
                }
            }

        mock.raise_for_status = MagicMock()
        return mock
