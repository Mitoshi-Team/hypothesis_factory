from __future__ import annotations

from src.ai_pipeline.agents.reviewer import ReviewerAgent


class TestReviewerAgent:
    def test_parse_review_valid_json(self):
        agent = ReviewerAgent()
        text = (
            '{"scores": {"novelty": 8, "feasibility": 7, "effect": 9, "risk": 3,'
            '"physical_correctness": 8, "prompt_alignment": 7, "metric_realism": 6},'
            '"comments": {"general": "Good"},'
            '"verdict": "accept",'
            '"suggestions": ["Add more details"]}'
        )
        review = agent._parse_review(text)
        assert review.verdict == "accept"
        assert review.scores["novelty"] == 8
        assert review.scores["physical_correctness"] == 8

    def test_parse_review_reject(self):
        agent = ReviewerAgent()
        text = (
            '{"scores": {"novelty": 2, "feasibility": 3, "effect": 1, "risk": 9,'
            '"physical_correctness": 8, "prompt_alignment": 7, "metric_realism": 6},'
            '"comments": {"general": "Not feasible"},'
            '"verdict": "reject",'
            '"suggestions": ["Completely rework"]}'
        )
        review = agent._parse_review(text)
        assert review.verdict == "reject"

    def test_parse_review_invalid_json(self):
        agent = ReviewerAgent()
        review = agent._parse_review("Not JSON")
        assert review.verdict == "revise"

    def test_parse_review_empty(self):
        agent = ReviewerAgent()
        review = agent._parse_review("")
        assert review.verdict == "revise"

    def test_enforce_verdict_downgrades_low_critical_scores(self):
        agent = ReviewerAgent()
        text = (
            '{"scores": {"novelty": 9, "feasibility": 9, "effect": 9, "risk": 9,'
            '"physical_correctness": 3, "prompt_alignment": 8, "metric_realism": 8},'
            '"comments": {"general": "Good but physically wrong"},'
            '"verdict": "accept",'
            '"suggestions": []}'
        )
        review = agent._parse_review(text)
        assert review.verdict == "revise"
