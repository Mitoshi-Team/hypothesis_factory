from __future__ import annotations

from ai_pipeline.agents.generator import GeneratorAgent


class TestGeneratorAgent:
    def test_build_system_prompt_with_weights(self):
        agent = GeneratorAgent()
        prompt = agent._build_system_prompt(
            {
                "novelty": 1.5,
                "feasibility": 1.0,
                "effect": 2.0,
                "risk": 0.5,
            }
        )
        assert "Новизна" in prompt
        assert "Реализуемость" in prompt
        assert "Эффект" in prompt
        assert "Риски" in prompt
        assert "1.5" in prompt
        assert "0.5" in prompt

    def test_build_system_prompt_empty_weights(self):
        agent = GeneratorAgent()
        prompt = agent._build_system_prompt(None)
        assert "1.0" in prompt

    def test_build_user_prompt_with_all_fields(self):
        agent = GeneratorAgent()
        prompt = agent._build_user_prompt(
            problem="Test problem",
            constraints="Some limits",
            rag_context="Relevant docs",
            history_context="Past cases",
            feedback="Fix this part",
        )
        assert "Test problem" in prompt
        assert "Some limits" in prompt
        assert "Relevant docs" in prompt
        assert "Past cases" in prompt
        assert "Fix this part" in prompt

    def test_build_user_prompt_minimal(self):
        agent = GeneratorAgent()
        prompt = agent._build_user_prompt(
            problem="",
            constraints="",
            rag_context="",
            history_context="",
            feedback=None,
        )
        assert len(prompt) > 0

    def test_parse_hypothesis_valid_json(self):
        agent = GeneratorAgent()
        text = (
            '{"title": "Test", "hypothesis": "My hypothesis", '
            '"expected_effect": "Big impact", "risks": ["risk1"], '
            '"feasibility_score": 7, "novelty_score": 8, '
            '"effect_score": 9, "risk_score": 3}'
        )
        result = agent._parse_hypothesis(text, "Problem X")
        assert result.title == "Test"
        assert result.hypothesis == "My hypothesis"
        assert result.expected_effect == "Big impact"
        assert result.risks == ["risk1"]
        assert result.feasibility_score == 7.0
        assert result.novelty_score == 8.0

    def test_parse_hypothesis_invalid_json(self):
        agent = GeneratorAgent()
        text = "Some random text without JSON"
        result = agent._parse_hypothesis(text, "Problem X")
        assert result.title == "Parsing Error"
        assert result.hypothesis == text

    def test_parse_hypothesis_partial_json(self):
        agent = GeneratorAgent()
        text = '{"title": "Partial"}'
        result = agent._parse_hypothesis(text, "Problem")
        assert result.title == "Partial"
