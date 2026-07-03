"""Main API router and endpoint definitions for the API Gateway service."""

from fastapi import APIRouter, Depends, status
from src.api.dependencies import get_app_settings
from src.api.schemas import (
    HypothesisCreate,
    HypothesisResponse,
    PingResponse,
    VerificationPlanSchema,
)
from src.config import Settings

router = APIRouter()


@router.get(
    "/health",
    response_model=PingResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Returns the service health status, environment, and current version.",
)
async def health_check(
    settings: Settings = Depends(get_app_settings),
) -> PingResponse:
    """Return health details of the API gateway.

    Args:
        settings: Application settings.

    Returns:
        PingResponse: Status and environment of the gateway.
    """
    return PingResponse(environment=settings.ENVIRONMENT)


@router.post(
    "/hypotheses",
    response_model=HypothesisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate scientific hypothesis",
    description=(
        "Generate a ranked scientific hypothesis based on the "
        "problem statement and constraints."
    ),
)
async def generate_hypothesis(
    payload: HypothesisCreate,
    settings: Settings = Depends(get_app_settings),
) -> HypothesisResponse:
    """Generate a scientific hypothesis for metallurgical tasks.

    Args:
        payload: Inputs for hypothesis creation.
        settings: Application settings.

    Returns:
        HypothesisResponse: Generated and ranked hypothesis details.
    """
    # Placeholder implementation
    return HypothesisResponse(
        id="hyp_001",
        formulation=(
            f"Использовать собиратель Бутилксантогенат калия в дозировке 45 г/т "
            f"с добавлением депрессора жидкого стекла 150 г/т для решения проблемы: "
            f"'{payload.problem_statement}'"
        ),
        scientific_basis=(
            "Согласно теории гидрофобности минералов сульфидных руд, селективное "
            "покрытие ксантогенатом никелевых минералов усиливает их флотируемость, "
            "тогда как силикаты депрессируются жидким стеклом."
        ),
        expected_mechanism=(
            "Повышение поверхностного натяжения на границе раздела фаз "
            "и гидрофобизация пентландита."
        ),
        novelty=3,
        risks={
            "technical": (
                "Возможное перевыпадение силикатов при "
                "превышении дозировки жидкого стекла."
            ),
            "economic": "Увеличение себестоимости реагентов на 4% при перерасходе.",
            "ecological": "Незначительное увеличение ПДК кремния в сточных водах.",
        },
        expected_value="Снижение потерь никеля в хвостах флотации на 0.03% абс.",
        verification_plan=VerificationPlanSchema(
            experiments=[
                "Лабораторные опыты флотации на фракции руды крупностью 74 мкм.",
                "Сравнительный анализ выхода концентрата с бутилксантогенатом.",
            ],
            resources=["Лабораторная флотомашина ФЛ-189", "Реагентный набор"],
            success_criteria=(
                "Извлечение Ni в концентрат > 82.5% при аналогичном качестве хвостов."
            ),
        ),
        score=4.25,
    )
