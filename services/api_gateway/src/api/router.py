"""Main API router and endpoint definitions for the API Gateway service."""

from fastapi import APIRouter, Depends, status
from src.api.dependencies import get_app_settings
from src.api.routes.admin import router as admin_router
from src.api.routes.auth import router as auth_router
from src.api.routes.results import router as results_router
from src.api.routes.sessions import router as sessions_router
from src.api.routes.tasks import router as tasks_router
from src.api.schemas import PingResponse
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


# Include sub-routers for contract compliance
router.include_router(auth_router)
router.include_router(admin_router)
router.include_router(sessions_router)
router.include_router(results_router)
router.include_router(tasks_router)
