from __future__ import annotations

from ai_pipeline.agents.reviewer import ReviewerAgent


class TestReviewerAgent:
    def test_parse_review_valid_json(self):
        agent = ReviewerAgent()
        text = (
            '{"scores": {"novelty": 8, "feasibility": 7, "effect": 9, "risk": 3},'
            '"comments": {"general": "Good"},'
            '"verdict": "accept",'
            '"suggestions": ["Add more details"]}'
        )
        review = agent._parse_review(text)
        assert review.verdict == "accept"
        assert review.scores["novelty"] == 8
        assert review.scores["feasibility"] == 7
        assert review.scores["effect"] == 9
        assert review.scores["risk"] == 3
        assert "Add more details" in review.suggestions

    def test_parse_review_reject(self):
        agent = ReviewerAgent()
        text = (
            '{"scores": {"novelty": 2, "feasibility": 3, "effect": 1, "risk": 9},'
            '"comments": {"general": "Not feasible"},'
            '"verdict": "reject",'
            '"suggestions": ["Completely rework"]}'
        )
        review = agent._parse_review(text)
        assert review.verdict == "reject"
        assert review.scores["novelty"] == 2

    def test_parse_review_invalid_json(self):
        agent = ReviewerAgent()
        review = agent._parse_review("Not JSON")
        assert review.verdict == "revise"

    def test_parse_review_empty(self):
        agent = ReviewerAgent()
        review = agent._parse_review("")
        assert review.verdict == "revise"
