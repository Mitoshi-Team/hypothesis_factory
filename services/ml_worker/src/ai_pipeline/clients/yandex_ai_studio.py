from __future__ import annotations

import json
from typing import Any, Optional

import httpx
from config import settings


class YandexAIStudioClient:
    def __init__(self) -> None:
        self.api_key = settings.yandex_api_key
        self.folder_id = settings.yandex_folder_id
        self.base_url = "https://llm.api.cloud.yandex.net/foundationModels/v1"
        self.embed_model = settings.embed_model
        self.llm_model = settings.llm_model

    def _headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Api-Key {self.api_key}"
        if self.folder_id:
            headers["x-folder-id"] = self.folder_id
        return headers

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        payload = {
            "modelUri": f"emb://{self.folder_id}/{self.embed_model}",
            "texts": texts,
        }

        response = httpx.post(
            f"{self.base_url}/textEmbedding",
            headers=self._headers(),
            json=payload,
            timeout=60.0,
        )
        response.raise_for_status()
        data = response.json()

        embeddings = []
        for item in data.get("embeddings", []):
            embeddings.append(item.get("embedding", []))
        return embeddings

    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        tools: Optional[list[dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "text": system_prompt})
        messages.append({"role": "user", "text": prompt})

        payload: dict[str, Any] = {
            "modelUri": f"gpt://{self.folder_id}/{self.llm_model}",
            "completionOptions": {
                "stream": False,
                "temperature": temperature,
                "maxTokens": max_tokens,
            },
            "messages": messages,
        }

        if tools:
            payload["tools"] = tools

        response = httpx.post(
            f"{self.base_url}/completion",
            headers=self._headers(),
            json=payload,
            timeout=120.0,
        )
        response.raise_for_status()
        data = response.json()

        alternatives = data.get("result", {}).get("alternatives", [])
        if alternatives:
            return alternatives[0].get("message", {}).get("text", "")
        return ""

    def complete_with_tools(  # noqa: C901
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        tools: Optional[list[dict[str, Any]]] = None,
        tool_handlers: Optional[dict[str, callable]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        max_tool_rounds: int = 5,
    ) -> tuple[str, list[dict[str, Any]]]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "text": system_prompt})
        messages.append({"role": "user", "text": prompt})

        tool_calls_log: list[dict[str, Any]] = []

        for _ in range(max_tool_rounds):
            payload: dict[str, Any] = {
                "modelUri": f"gpt://{self.folder_id}/{self.llm_model}",
                "completionOptions": {
                    "stream": False,
                    "temperature": temperature,
                    "maxTokens": max_tokens,
                },
                "messages": messages,
            }
            if tools:
                payload["tools"] = tools

            response = httpx.post(
                f"{self.base_url}/completion",
                headers=self._headers(),
                json=payload,
                timeout=120.0,
            )
            response.raise_for_status()
            data = response.json()

            alternatives = data.get("result", {}).get("alternatives", [])
            if not alternatives:
                break

            message = alternatives[0].get("message", {})
            text = message.get("text", "")

            if text:
                messages.append({"role": "assistant", "text": text})

            function_call = message.get("functionCall")
            if not function_call or not tool_handlers:
                break

            func_name = function_call.get("name", "")
            func_args = json.loads(function_call.get("arguments", "{}"))
            handler = tool_handlers.get(func_name)

            if handler:
                try:
                    result = handler(**func_args)
                    tool_calls_log.append(
                        {
                            "tool": func_name,
                            "args": func_args,
                            "result": str(result),
                        }
                    )
                    messages.append(
                        {
                            "role": "function",
                            "text": str(result),
                            "name": func_name,
                        }
                    )
                except Exception as e:
                    messages.append(
                        {
                            "role": "function",
                            "text": f"Error: {e}",
                            "name": func_name,
                        }
                    )
            else:
                break

        final_text = ""
        for msg in reversed(messages):
            if msg["role"] == "assistant":
                final_text = msg.get("text", "")
                break

        return final_text, tool_calls_log
