from __future__ import annotations

import json
import logging
from typing import Any, Optional

from openai import OpenAI
from src.config import settings

logger = logging.getLogger(__name__)


class YandexAIStudioClient:
    def __init__(self) -> None:
        self.api_key = settings.yandex_api_key
        self.folder_id = settings.yandex_folder_id
        self.embed_model = settings.embed_model
        self.llm_model = settings.llm_model
        self._client = OpenAI(
            api_key=self.api_key,
            base_url="https://ai.api.cloud.yandex.net/v1",
            project=self.folder_id,
        )

    def _llm_uri(self, model: str) -> str:
        if model.startswith("gpt://"):
            return model
        return f"gpt://{self.folder_id}/{model}"

    def _embed_uri(self, model: str) -> str:
        if model.startswith("emb://"):
            return model
        return f"emb://{self.folder_id}/{model}"

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        model_uri = self._embed_uri(self.embed_model)
        logger.info(
            "Yandex embed: model=%s, embed_model=%s",
            model_uri,
            self.embed_model,
        )

        response = self._client.embeddings.create(
            model=model_uri,
            input=texts,
            encoding_format="float",
        )
        return [item.embedding for item in response.data]

    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        tools: Optional[list[dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        model_uri = self._llm_uri(self.llm_model)
        logger.info(
            "Yandex complete: model=%s, llm_model=%s",
            model_uri,
            self.llm_model,
        )

        response = self._client.chat.completions.create(
            model=model_uri,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
        )
        return response.choices[0].message.content or ""

    async def complete_with_tools(  # noqa: C901
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        tools: Optional[list[dict[str, Any]]] = None,
        tool_handlers: Optional[dict[str, callable]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        max_tool_rounds: int = 5,
    ) -> tuple[str, list[dict[str, Any]]]:
        messages: list[dict[str, Any]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        tool_calls_log: list[dict[str, Any]] = []

        for _ in range(max_tool_rounds):
            response = self._client.chat.completions.create(
                model=self._llm_uri(self.llm_model),
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools,
            )

            message = response.choices[0].message
            text = message.content or ""

            if text:
                messages.append({"role": "assistant", "content": text})

            tool_calls = message.tool_calls
            if not tool_calls or not tool_handlers:
                break

            for tool_call in tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                handler = tool_handlers.get(func_name)

                if handler:
                    try:
                        result = handler(**func_args)
                        if hasattr(result, "__await__"):
                            result = await result
                        tool_calls_log.append(
                            {
                                "tool": func_name,
                                "args": func_args,
                                "result": str(result),
                            }
                        )
                        messages.append(
                            {
                                "role": "tool",
                                "content": str(result),
                                "tool_call_id": tool_call.id,
                            }
                        )
                    except Exception as e:
                        messages.append(
                            {
                                "role": "tool",
                                "content": f"Error: {e}",
                                "tool_call_id": tool_call.id,
                            }
                        )
                else:
                    break

        final_text = ""
        for msg in reversed(messages):
            if msg["role"] == "assistant":
                final_text = msg.get("content", "")
                break

        if not final_text:
            logger.info("No assistant content after tool rounds, asking again")
            response = self._client.chat.completions.create(
                model=self._llm_uri(self.llm_model),
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            final_text = response.choices[0].message.content or ""
            logger.info("Final follow-up content length=%d", len(final_text))

        logger.info(
            "complete_with_tools final_text length=%d", len(final_text)
        )
        return final_text, tool_calls_log

    def list_models(self) -> list[dict[str, Any]]:
        response = self._client.models.list()
        return [model.model_dump() for model in response.data]
