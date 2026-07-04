from __future__ import annotations

import re
from typing import Optional

from src.ai_pipeline.state import HypothesisCard, ValidationResult


class ValidatorAgent:
    """Domain validator for Cu/Ni sulfide beneficiation hypotheses.

    Blocks hallucinated physics, equipment misuse and unrealistic KPIs before
    the hypothesis reaches the reviewer.
    """

    _FLOTATION_KEYWORDS = {
        "флотация",
        "флотомашина",
        "флотокамера",
        "собиратель",
        "регулятор",
        "пенообразователь",
        "аэрация",
        "перечистка",
        "контрольная флотация",
        "колонная флотомашина",
        "колонная",
        "flotation",
        "flot machine",
        "flotation cell",
        "collector",
        "regulator",
        "frother",
        "aeration",
        "cleaning",
        "scavenger",
        "column flotation",
    }

    _GRAVITY_KEYWORDS = {
        "гравитационное обогащение",
        "гравитация",
        "отсадка",
        "спиральный сепаратор",
        "центробежный концентратор",
        "knelson",
        "falcon",
        "gravity separation",
        "gravity concentration",
        "jigging",
        "spiral separator",
        "centrifugal concentrator",
    }

    _GOLD_MISFIT_KEYWORDS = {
        "золото",
        "золотоносный",
        "цианирование",
        "углерод",
        "уголь",
        "gold",
        "cyanidation",
        "carbon",
        "coal",
    }

    def validate(
        self,
        hypothesis: HypothesisCard,
        problem: str,
        constraints: str = "",
        required_domain: Optional[str] = None,
    ) -> ValidationResult:
        result = ValidationResult()
        text = self._normalize(
            " ".join(
                [
                    hypothesis.title,
                    hypothesis.hypothesis,
                    hypothesis.expected_effect,
                    " ".join(hypothesis.risks),
                ]
            )
        )
        problem_norm = self._normalize(problem)

        self._check_flotation_scope(
            text, problem_norm, required_domain, result
        )
        self._check_gravity_misuse(text, result)
        self._check_gold_misfit(text, problem_norm, result)
        self._check_hydrocyclone_misuse(text, result)
        self._check_locked_particles(text, result)
        self._check_kpi_realism(text, result)
        self._check_scale_realism(text, result)

        result.is_valid = not result.violations
        return result

    def _normalize(self, text: str) -> str:
        return " ".join(text.lower().split())

    def _check_flotation_scope(
        self,
        text: str,
        problem: str,
        required_domain: Optional[str],
        result: ValidationResult,
    ) -> None:
        domain = required_domain or self._detect_required_domain(problem)
        if domain != "flotation":
            return

        if not any(kw in text for kw in self._FLOTATION_KEYWORDS):
            result.violations.append(
                "Ответ не содержит предложений по флотации, "
                "хотя запрос требует изменений в схеме флотации."
            )
            result.corrected_prompt_hints.append(
                "Предложите конкретные изменения в реагентном режиме, "
                "гидродинамике флотомашин, pH или схеме стадий флотации."
            )

    def _detect_required_domain(self, problem: str) -> Optional[str]:
        problem_norm = self._normalize(problem)
        if "флотац" in problem_norm or "flotation" in problem_norm:
            return "flotation"
        return None

    def _check_gravity_misuse(
        self, text: str, result: ValidationResult
    ) -> None:
        if any(kw in text for kw in self._GRAVITY_KEYWORDS):
            result.violations.append(
                "Гравитационное обогащение неприменимо для сульфидов Ni/Cu "
                "из-за близкой плотности пирротита, пентландита и халькопирита."
            )
            result.corrected_prompt_hints.append(
                "Замените гравитацию на флотационные решения: изменение "
                "собирателей, pH, аэрации, типа флотомашин или схемы стадий."
            )

    def _check_gold_misfit(
        self, text: str, problem: str, result: ValidationResult
    ) -> None:
        problem_norm = self._normalize(problem)
        if (
            "золот" in problem_norm
            or "au" in problem_norm
            or "pgm" in problem_norm
            or "gold" in problem_norm
        ):
            return

        if any(kw in text for kw in self._GOLD_MISFIT_KEYWORDS):
            result.violations.append(
                "Упоминание золота/цианирования/угольных процессов "
                "неуместно для медно-никелевого сульфидного контура."
            )
            result.corrected_prompt_hints.append(
                "Сфокусируйтесь на Ni, Cu и сопутствующих сульфидах, "
                "исключите золоторудные шаблоны."
            )

    def _check_hydrocyclone_misuse(
        self, text: str, result: ValidationResult
    ) -> None:
        if "гидроциклон" not in text and "hydrocyclone" not in text:
            return

        gravity_phrases = [
            "гравитационно",
            "гравитационное",
            "доизвлечени",
            "концентрат",
            "gravitational",
            "pre-concentration",
            "concentrate",
        ]
        if any(ph in text for ph in gravity_phrases):
            result.violations.append(
                "Гидроциклон — аппарат для классификации по крупности, "
                "а не для гравитационного доизвлечения."
            )
            result.corrected_prompt_hints.append(
                "Используйте гидроциклоны только для классификации/сгущения; "
                "извлечение сульфидов предложите флотацией."
            )

    def _check_locked_particles(
        self, text: str, result: ValidationResult
    ) -> None:
        if (
            "полутораплот" not in text
            and "сростк" not in text
            and "locked" not in text
        ):
            return

        if any(kw in text for kw in self._GRAVITY_KEYWORDS):
            result.violations.append(
                "Полутораплотные частицы (сростки) невозможно эффективно "
                "извлечь гравитацией — требуется доизмельчение или флотация."
            )
            result.corrected_prompt_hints.append(
                "Для сростков предложите изменение границы измельчения, "
                "flash flotation или селективные реагенты."
            )

    def _check_kpi_realism(self, text: str, result: ValidationResult) -> None:
        matches = re.findall(r"(\d+(?:[.,]\d+)?)\s*%", text)
        for m in matches:
            value = float(m.replace(",", "."))
            if value > 1.5 and "абсолют" not in text and "пилот" not in text:
                result.violations.append(
                    f"Заявленный эффект {value}% превышает реалистичный "
                    f"прирост извлечения на действующей фабрике без пилотных данных."
                )
                result.corrected_prompt_hints.append(
                    "Укажите консервативный эффект (до 0.5–1.5% абсолютных) "
                    "или обоснуйте цифру ссылкой на пилотные/лабораторные испытания."
                )
                return

    def _check_scale_realism(
        self, text: str, result: ValidationResult
    ) -> None:
        matches = re.findall(
            r"(\d+(?:[.,]\d+)?)\s*(?:тыс\.?|tys\.?|thousand)\s*т/сут",
            text,
        )
        for m in matches:
            value = float(m.replace(",", "."))
            if value >= 50:
                result.violations.append(
                    f"Объём {value} тыс. т/сут нереалистичен для одной "
                    f"никелевой обогатительной фабрики."
                )
                result.corrected_prompt_hints.append(
                    "Используйте реальные производственные мощности конкретного "
                    "предприятия или укажите диапазон без конкретных цифр."
                )
                return
