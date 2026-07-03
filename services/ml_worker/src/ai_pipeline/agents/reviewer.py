from __future__ import annotations

import json

from ai_pipeline.clients.yandex_ai_studio import YandexAIStudioClient
from ai_pipeline.state import HypothesisCard, HypothesisReview


class ReviewerAgent:
    def __init__(self) -> None:
        self.client = YandexAIStudioClient()

    async def review(self, hypothesis: HypothesisCard) -> HypothesisReview:
        system_prompt = (
            "Ты — ревьюер технологических гипотез для Норникеля.\n"
            "Оцени гипотезу по 4 критериям (1-10) и дай вердикт:\n"
            "- Новизна: насколько идея нова\n"
            "- Реализуемость: насколько реалистична\n"
            "- Эффект: потенциальный эффект\n"
            "- Риски: уровень рисков\n\n"
            "Вердикты: accept / revise / reject.\n\n"
            "Ответь строго в формате JSON:\n"
            "{\n"
            '  "scores": {"novelty": 0-10, "feasibility": 0-10,'
            ' "effect": 0-10, "risk": 0-10},\n'
            '  "comments": {"novelty": "...", "feasibility": "...",'
            ' "effect": "...", "risk": "...", "general": "..."},\n'
            '  "verdict": "accept|revise|reject",\n'
            '  "suggestions": ["совет 1", "совет 2"]\n'
            "}"
        )

        user_prompt = (
            f"Проблема: {hypothesis.problem}\n\n"
            f"Гипотеза: {hypothesis.hypothesis}\n\n"
            f"Ожидаемый эффект: {hypothesis.expected_effect}\n\n"
            f"Риски: {', '.join(hypothesis.risks)}\n\n"
            f"Самооценка — Новизна: {hypothesis.novelty_score}, "
            f"Реализуемость: {hypothesis.feasibility_score}, "
            f"Эффект: {hypothesis.effect_score}, "
            f"Риски: {hypothesis.risk_score}\n\n"
            "Оцени гипотезу."
        )

        text = self.client.complete(
            prompt=user_prompt,
            system_prompt=system_prompt,
        )

        review = self._parse_review(text)
        review.hypothesis_id = hypothesis.title
        return review

    def _parse_review(self, text: str) -> HypothesisReview:
        json_start = text.find("{")
        json_end = text.rfind("}")
        if json_start != -1 and json_end != -1:
            json_str = text[json_start : json_end + 1]
            try:
                data = json.loads(json_str)
                return HypothesisReview(
                    scores=data.get("scores", {}),
                    comments=data.get("comments", {}),
                    verdict=data.get("verdict", "revise"),
                    suggestions=data.get("suggestions", []),
                )
            except (json.JSONDecodeError, ValueError):
                pass

        return HypothesisReview(verdict="revise")
