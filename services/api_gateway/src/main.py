"""Main application entrypoint for the API Gateway service."""

import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.api.router import router as api_router
from src.api.schemas import ErrorDetail, HTTPErrorResponse
from src.config import get_settings
from src.utils.exceptions import (
    BaseAppError,
    EntityNotFoundError,
    ValidationAppError,
)
from src.utils.log_config import setup_logging

# Load settings and setup logging
settings = get_settings()
setup_logging(debug=settings.DEBUG)

logger = logging.getLogger("api-gateway")

app = FastAPI(
    title=settings.APP_NAME,
    description="API Gateway for the Hypothesis Factory system",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Middleware to log incoming request details and execution duration.

    Args:
        request: The incoming FastAPI request.
        call_next: Next handler in the ASGI chain.

    Returns:
        The processed FastAPI response.
    """
    start_time = time.perf_counter()
    method = request.method
    path = request.url.path

    logger.debug("Received request: %s %s", method, path)

    try:
        response = await call_next(request)
        process_time = (time.perf_counter() - start_time) * 1000
        logger.info(
            "%s %s - Status: %d - Time: %.2fms",
            method,
            path,
            response.status_code,
            process_time,
        )
        return response
    except Exception:
        process_time = (time.perf_counter() - start_time) * 1000
        logger.exception(
            "Unhandled error processing request: %s %s - Time: %.2fms",
            method,
            path,
            process_time,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=HTTPErrorResponse(
                error=ErrorDetail(
                    code="INTERNAL_SERVER_ERROR",
                    message="An unexpected error occurred on the server.",
                )
            ).model_dump(),
        )


# Include API routes
app.include_router(api_router, prefix=settings.API_PREFIX)


# Exception Handlers
@app.exception_handler(EntityNotFoundError)
async def entity_not_found_handler(
    request: Request, exc: EntityNotFoundError
) -> JSONResponse:
    """Handle custom EntityNotFoundError and return 404 response.

    Args:
        request: The FastAPI request context.
        exc: Raised exception instance.

    Returns:
        JSONResponse: Mapped error details.
    """
    logger.warning("Resource not found: %s", exc.message)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=HTTPErrorResponse(
            error=ErrorDetail(code="NOT_FOUND", message=exc.message)
        ).model_dump(),
    )


@app.exception_handler(ValidationAppError)
async def validation_app_error_handler(
    request: Request, exc: ValidationAppError
) -> JSONResponse:
    """Handle custom ValidationAppError and return 422 response.

    Args:
        request: The FastAPI request context.
        exc: Raised exception instance.

    Returns:
        JSONResponse: Mapped error details.
    """
    logger.warning("Validation failure: %s", exc.message)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=HTTPErrorResponse(
            error=ErrorDetail(code="VALIDATION_ERROR", message=exc.message)
        ).model_dump(),
    )


@app.exception_handler(BaseAppError)
async def base_app_error_handler(request: Request, exc: BaseAppError) -> JSONResponse:
    """Fallback handler for generic BaseAppError and return 400 response.

    Args:
        request: The FastAPI request context.
        exc: Raised exception instance.

    Returns:
        JSONResponse: Mapped error details.
    """
    logger.warning("Application error: %s", exc.message)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=HTTPErrorResponse(
            error=ErrorDetail(code="BAD_REQUEST", message=exc.message)
        ).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle FastAPI validation errors and map to uniform error structure.

    Args:
        request: The FastAPI request context.
        exc: Raised exception instance.

    Returns:
        JSONResponse: Standardized validation error details.
    """
    logger.warning("Request schema validation failed: %s", str(exc))

    errors: dict[str, list[str]] = {}
    for err in exc.errors():
        loc = ".".join(map(str, err["loc"]))
        errors.setdefault(loc, []).append(err["msg"])

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=HTTPErrorResponse(
            error=ErrorDetail(
                code="VALIDATION_ERROR",
                message="Request validation failed.",
                details=errors,
            )
        ).model_dump(),
    )


def start() -> None:
    """Entry point for local development server execution."""
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
    )


if __name__ == "__main__":
    start()
