from __future__ import annotations

import uuid
from typing import Optional

from src.ai_pipeline.state import (
    HistoryEntry,
    HypothesisCard,
    HypothesisReview,
)
from src.ai_pipeline.vector_store.chroma_store import ChromaStore


class HistoryRAG:
    def __init__(self) -> None:
        self.store = ChromaStore()

    def store_result(
        self,
        hypothesis: HypothesisCard,
        review: Optional[HypothesisReview] = None,
        user_feedback: Optional[str] = None,
        user_id: str = "",
    ) -> None:
        scores = {}
        if review:
            scores = review.scores
        else:
            scores = {
                "novelty": hypothesis.novelty_score,
                "feasibility": hypothesis.feasibility_score,
                "effect": hypothesis.effect_score,
                "risk": hypothesis.risk_score,
            }

        is_positive = review is not None and review.verdict == "accept"
        verdict = review.verdict if review else "unknown"

        entry = HistoryEntry(
            entry_id=f"hist_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            problem=hypothesis.problem,
            hypothesis_text=hypothesis.hypothesis,
            verdict=verdict,
            scores=scores,
            review_comment=review.comments.get("general", "")
            if review
            else "",
            user_feedback=user_feedback,
            is_positive_example=is_positive,
        )

        self.store.populate_history([entry.model_dump()])

    def retrieve_similar(
        self,
        problem: str,
        n_results: int = 0,
        user_id: str = "",
    ) -> str:
        where = {"user_id": user_id} if user_id else None
        entries = self.store.query_history(
            query_text=problem,
            n_results=n_results,
            where=where,
        )

        if not entries:
            return ""

        positive_examples = [
            e
            for e in entries
            if e.get("metadata", {}).get("is_positive_example")
            in (True, "True", "true")
        ]
        negative_examples = [
            e
            for e in entries
            if e.get("metadata", {}).get("is_positive_example")
            in (False, "False", "false")
        ]

        parts = []

        if positive_examples:
            parts.append(
                "## Положительные примеры (ВЫСОКИЕ ОЦЕНКИ — ориентир)"
            )
            for ex in positive_examples[:3]:
                meta = ex.get("metadata", {})
                parts.append(
                    f"- Гипотеза: {ex.get('hypothesis_text', '')[:200]}...\n"
                    f"  Оценки: {meta.get('scores', 'N/A')}\n"
                    f"  Комментарий: {meta.get('review_comment', 'N/A')}"
                )

        if negative_examples:
            parts.append(
                "\n## Ошибки из прошлого (НИЗКИЕ ОЦЕНКИ — НЕ ПОВТОРЯТЬ)"
            )
            for ex in negative_examples[:3]:
                meta = ex.get("metadata", {})
                parts.append(
                    f"- Гипотеза: {ex.get('hypothesis_text', '')[:200]}...\n"
                    f"  Оценки: {meta.get('scores', 'N/A')}\n"
                    f"  Почему плохо: {meta.get('review_comment', 'N/A')}\n"
                    f"  Фидбек: {meta.get('user_feedback', 'N/A')}"
                )

        return "\n\n".join(parts)
