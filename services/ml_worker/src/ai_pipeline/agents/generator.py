from __future__ import annotations

import json
from typing import Optional

from src.ai_pipeline.clients.yandex_ai_studio import YandexAIStudioClient
from src.ai_pipeline.state import HypothesisCard, HypothesisReview
from src.ai_pipeline.tools.postgres_tools import PostgresTools
from src.models import Chunk


class GeneratorAgent:
    def __init__(self) -> None:
        self.client = YandexAIStudioClient()
        self.postgres_tools = PostgresTools()

    async def generate(
        self,
        problem: str,
        constraints: str,
        weights: Optional[dict[str, float]],
        rag_context: str,
        history_context: str,
        feedback: Optional[str] = None,
        previous_hypothesis: Optional[HypothesisCard] = None,
        previous_review: Optional[HypothesisReview] = None,
        chunks: Optional[list[Chunk]] = None,
    ) -> HypothesisCard:
        system_prompt = self._build_system_prompt(weights)
        user_prompt = self._build_user_prompt(
            problem=problem,
            constraints=constraints,
            rag_context=rag_context,
            history_context=history_context,
            feedback=feedback,
            previous_hypothesis=previous_hypothesis,
            previous_review=previous_review,
        )

        tools = self.postgres_tools.get_tool_definitions()
        tool_handlers = await self.postgres_tools.get_tool_handlers()

        final_text, tool_calls_log = self.client.complete_with_tools(
            prompt=user_prompt,
            system_prompt=system_prompt,
            tools=tools,
            tool_handlers=tool_handlers,
        )

        hypothesis = self._parse_hypothesis(final_text, problem)

        for call in tool_calls_log:
            hypothesis.evidence_sources.append(
                f"postgres:{call['tool']}({call['args']})"
            )

        if chunks:
            for chunk in chunks:
                hypothesis.source_chunks.append(chunk.chunk_id)

        return hypothesis

    def _build_system_prompt(
        self,
        weights: Optional[dict[str, float]],
    ) -> str:
        w = weights or {}
        lines = [
            "Ты — генератор технологических гипотез для Норникеля.",
            "На основе документов, таблиц и исторических примеров",
            "сгенерируй технологическую гипотезу.\n",
            "Критерии оценки (веса):",
            f"- Новизна (вес {w.get('novelty', 1.0):.1f})",
            f"- Реализуемость (вес {w.get('feasibility', 1.0):.1f})",
            f"- Эффект (вес {w.get('effect', 1.0):.1f})",
            f"- Риски (вес {w.get('risk', 1.0):.1f})\n",
            "Используй Postgres для дополнительных данных.",
            "Ответь JSON:",
            "{",
            '  "title": "Название гипотезы",',
            '  "hypothesis": "Описание гипотезы",',
            '  "expected_effect": "Ожидаемый эффект",',
            '  "risks": ["риск 1", "риск 2"],',
            '  "feasibility_score": 0-10,',
            '  "novelty_score": 0-10,',
            '  "effect_score": 0-10,',
            '  "risk_score": 0-10',
            "}",
        ]
        return "\n".join(lines)

    def _build_user_prompt(
        self,
        problem: str,
        constraints: str,
        rag_context: str,
        history_context: str,
        feedback: Optional[str],
        previous_hypothesis: Optional[HypothesisCard] = None,
        previous_review: Optional[HypothesisReview] = None,
    ) -> str:
        parts = [f"Проблема: {problem}"]

        if constraints:
            parts.append(f"\nОграничения: {constraints}")

        if previous_hypothesis:
            parts.append(
                f"\nПредыдущая гипотеза: {previous_hypothesis.hypothesis}"
            )
            parts.append(
                f"\nОжидаемый эффект предыдущей версии: {previous_hypothesis.expected_effect}"
            )

        if previous_review:
            parts.append(
                f"\nРевью предыдущей версии: {previous_review.comments}"
            )
            parts.append(
                f"\nПредложения по улучшению: {previous_review.suggestions}"
            )

        if feedback:
            parts.append(f"\nФидбек пользователя (исправь это): {feedback}")

        if rag_context:
            parts.append(f"\n\nКонтекст из документов:\n{rag_context}")

        if history_context:
            parts.append(f"\n\nИстория генераций:\n{history_context}")

        parts.append("\n\nСгенерируй гипотезу в формате JSON.")

        return "\n".join(parts)

    def _parse_hypothesis(self, text: str, problem: str) -> HypothesisCard:
        json_start = text.find("{")
        json_end = text.rfind("}")
        if json_start != -1 and json_end != -1:
            json_str = text[json_start : json_end + 1]
            try:
                data = json.loads(json_str)
                return HypothesisCard(
                    title=data.get("title", ""),
                    problem=problem,
                    hypothesis=data.get("hypothesis", ""),
                    expected_effect=data.get("expected_effect", ""),
                    risks=data.get("risks", []),
                    feasibility_score=float(data.get("feasibility_score", 0)),
                    novelty_score=float(data.get("novelty_score", 0)),
                    effect_score=float(data.get("effect_score", 0)),
                    risk_score=float(data.get("risk_score", 0)),
                )
            except (json.JSONDecodeError, ValueError):
                pass

        return HypothesisCard(
            title="Parsing Error",
            problem=problem,
            hypothesis=text,
        )
