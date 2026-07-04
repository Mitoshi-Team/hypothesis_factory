from __future__ import annotations

from unittest.mock import patch

from src.ai_pipeline.rag.history_rag import HistoryRAG
from src.ai_pipeline.state import HypothesisCard, HypothesisReview


class TestHistoryRAG:
    def test_store_result_accept(self):
        rag = HistoryRAG()
        hypothesis = HypothesisCard(
            title="Test",
            problem="Test problem",
            hypothesis="Test hypothesis",
        )
        review = HypothesisReview(
            scores={"novelty": 8, "feasibility": 7, "effect": 9, "risk": 3},
            verdict="accept",
            comments={"general": "Good work"},
        )

        with patch.object(rag.store, "populate_history") as mock:
            rag.store_result(hypothesis=hypothesis, review=review)
            mock.assert_called_once()

    def test_store_result_reject(self):
        rag = HistoryRAG()
        hypothesis = HypothesisCard(problem="Bad", hypothesis="Bad idea")
        review = HypothesisReview(
            scores={"novelty": 2, "feasibility": 3, "effect": 1, "risk": 9},
            verdict="reject",
            comments={"general": "Not feasible"},
        )

        with patch.object(rag.store, "populate_history") as mock:
            rag.store_result(
                hypothesis=hypothesis,
                review=review,
                user_feedback="Too risky",
            )
            mock.assert_called_once()

    def test_store_result_with_user_id(self):
        rag = HistoryRAG()
        hypothesis = HypothesisCard(
            title="Test", problem="Problem", hypothesis="Hypothesis"
        )
        review = HypothesisReview(verdict="accept")

        with patch.object(rag.store, "populate_history") as mock:
            rag.store_result(
                hypothesis=hypothesis,
                review=review,
                user_id="alice",
            )
            args = mock.call_args[0][0]
            assert args[0]["user_id"] == "alice"

    def test_retrieve_empty(self):
        rag = HistoryRAG()
        with patch.object(rag.store, "query_history", return_value=[]):
            result = rag.retrieve_similar("test")
            assert result == ""

    def test_retrieve_with_mixed_examples(self, chroma_fx):
        rag = HistoryRAG()
        entry = chroma_fx.make_history_entry("Good one", "accept", True)
        entry2 = chroma_fx.make_history_entry("Bad one", "reject", False)
        mock_entries = [
            {
                "entry_id": entry["entry_id"],
                "hypothesis_text": entry["hypothesis_text"],
                "metadata": {
                    "is_positive_example": True,
                    "scores": str(entry["scores"]),
                    "review_comment": entry["review_comment"],
                    "user_feedback": entry["user_feedback"],
                },
            },
            {
                "entry_id": entry2["entry_id"],
                "hypothesis_text": entry2["hypothesis_text"],
                "metadata": {
                    "is_positive_example": False,
                    "scores": str(entry2["scores"]),
                    "review_comment": entry2["review_comment"],
                    "user_feedback": entry2["user_feedback"],
                },
            },
        ]

        with patch.object(
            rag.store, "query_history", return_value=mock_entries
        ):
            result = rag.retrieve_similar("test problem")
            assert "Положительные примеры" in result
            assert "Ошибки из прошлого" in result

    def test_retrieve_only_positive(self, chroma_fx):
        rag = HistoryRAG()
        entry = chroma_fx.make_history_entry("Good one", "accept", True)
        mock_entries = [
            {
                "entry_id": entry["entry_id"],
                "hypothesis_text": entry["hypothesis_text"],
                "metadata": {
                    "is_positive_example": True,
                    "scores": str(entry["scores"]),
                    "review_comment": entry["review_comment"],
                    "user_feedback": entry["user_feedback"],
                },
            },
        ]

        with patch.object(
            rag.store, "query_history", return_value=mock_entries
        ):
            result = rag.retrieve_similar("test")
            assert "Положительные примеры" in result
            assert "Ошибки из прошлого" not in result

    def test_retrieve_with_user_id_filter(self):
        rag = HistoryRAG()
        with patch.object(rag.store, "query_history", return_value=[]) as mock:
            rag.retrieve_similar("test", user_id="alice")
            mock.assert_called_once_with(
                query_text="test",
                n_results=0,
                where={"type": "history", "user_id": "alice"},
            )

    def test_retrieve_without_user_id_passes_type_where(self):
        rag = HistoryRAG()
        with patch.object(rag.store, "query_history", return_value=[]) as mock:
            rag.retrieve_similar("test")
            mock.assert_called_once_with(
                query_text="test", n_results=0, where={"type": "history"}
            )

    def test_store_without_review(self):
        rag = HistoryRAG()
        hypothesis = HypothesisCard(problem="Test", hypothesis="Simple")

        with patch.object(rag.store, "populate_history") as mock:
            rag.store_result(
                hypothesis=hypothesis,
                review=None,
                user_feedback=None,
            )
            mock.assert_called_once()
