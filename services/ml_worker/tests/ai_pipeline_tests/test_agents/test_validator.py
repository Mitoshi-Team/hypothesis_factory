from __future__ import annotations

import pytest
from src.ai_pipeline.agents.validator import ValidatorAgent
from src.ai_pipeline.state import HypothesisCard


@pytest.fixture()
def validator() -> ValidatorAgent:
    return ValidatorAgent()


@pytest.fixture()
def base_hypothesis() -> HypothesisCard:
    return HypothesisCard(
        title="Test hypothesis",
        problem="Test problem",
        hypothesis="Some flotation hypothesis",
        expected_effect="Increase recovery by 1%",
        risks=["Risk 1"],
    )


class TestValidatorAgent:
    def test_valid_flotation_hypothesis(self, validator, base_hypothesis):
        result = validator.validate(
            base_hypothesis,
            problem="Предложи изменения в схеме флотации",
        )
        assert result.is_valid
        assert not result.violations

    def test_floating_scope_missing(self, validator, base_hypothesis):
        base_hypothesis.hypothesis = (
            "Use gravity separation for Ni/Cu sulfides"
        )
        base_hypothesis.expected_effect = "Better recovery"
        result = validator.validate(
            base_hypothesis,
            problem="Предложи изменения в схеме флотации",
        )
        assert not result.is_valid
        assert any("флотации" in v for v in result.violations)

    def test_gravity_misuse(self, validator, base_hypothesis):
        base_hypothesis.hypothesis = (
            "Use gravity separation to recover Ni/Cu sulfides"
        )
        base_hypothesis.expected_effect = "Higher recovery"
        result = validator.validate(
            base_hypothesis,
            problem="Как снизить потери Ni/Cu в хвостах",
        )
        assert not result.is_valid
        assert any("гравитационное" in v.lower() for v in result.violations)

    def test_gold_misfit(self, validator, base_hypothesis):
        base_hypothesis.hypothesis = (
            "Flotation with cyanidation to recover gold from tails"
        )
        base_hypothesis.expected_effect = "Gold recovery"
        result = validator.validate(
            base_hypothesis,
            problem="Как снизить потери Ni/Cu в хвостах никелевой фабрики",
        )
        assert not result.is_valid
        assert any(
            "золота" in v.lower() or "cyanidation" in v.lower()
            for v in result.violations
        )

    def test_hydrocyclone_misuse(self, validator, base_hypothesis):
        base_hypothesis.hypothesis = (
            "Use hydrocyclones for gravitational pre-concentration of sulfides"
        )
        base_hypothesis.expected_effect = "Pre-concentrate sulfides"
        result = validator.validate(
            base_hypothesis,
            problem="Предложи изменения в схеме флотации",
        )
        assert not result.is_valid
        assert any("гидроциклон" in v.lower() for v in result.violations)

    def test_locked_particles_gravity(self, validator, base_hypothesis):
        base_hypothesis.hypothesis = (
            "Extract locked particles by gravity concentration"
        )
        base_hypothesis.expected_effect = "Unlock sulfides"
        result = validator.validate(
            base_hypothesis,
            problem="Как снизить потери Ni/Cu в хвостах",
        )
        assert not result.is_valid
        assert any(
            "сростк" in v or "полутораплот" in v for v in result.violations
        )

    def test_kpi_realism_too_high(self, validator, base_hypothesis):
        base_hypothesis.hypothesis = (
            "Flotation optimization to increase recovery by 5%"
        )
        base_hypothesis.expected_effect = "Recovery increase by 5%"
        result = validator.validate(
            base_hypothesis,
            problem="Как снизить потери Ni/Cu в хвостах",
        )
        assert not result.is_valid
        assert any("5" in v for v in result.violations)

    def test_kpi_realism_acceptable(self, validator, base_hypothesis):
        base_hypothesis.hypothesis = (
            "Flotation optimization to increase recovery by 0.8%"
        )
        base_hypothesis.expected_effect = "Recovery increase by 0.8%"
        result = validator.validate(
            base_hypothesis,
            problem="Как снизить потери Ni/Cu в хвостах",
        )
        assert result.is_valid

    def test_scale_realism_too_high(self, validator, base_hypothesis):
        base_hypothesis.expected_effect = (
            "Переработка до 50 тыс. т/сут на одной линии"
        )
        result = validator.validate(
            base_hypothesis,
            problem="Как снизить потери Ni/Cu в хвостах КГМК",
        )
        assert not result.is_valid
        assert any("50" in v for v in result.violations)

    def test_scale_realism_acceptable(self, validator, base_hypothesis):
        base_hypothesis.expected_effect = (
            "Process up to 5 thousand tons per day"
        )
        result = validator.validate(
            base_hypothesis,
            problem="Как снизить потери Ni/Cu в хвостах",
        )
        assert result.is_valid

    def test_multiple_violations(self, validator, base_hypothesis):
        base_hypothesis.hypothesis = (
            "Use gravity separation and hydrocyclones to recover gold"
        )
        base_hypothesis.expected_effect = "Recovery increase by 20%"
        result = validator.validate(
            base_hypothesis,
            problem="Предложи изменения в схеме флотации",
        )
        assert not result.is_valid
        assert len(result.violations) >= 3
        assert len(result.corrected_prompt_hints) >= 3
