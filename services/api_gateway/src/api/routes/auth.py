"""Authentication API routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.dependencies import get_db
from src.api.schemas import LoginRequest, LoginResponse, RefreshRequest, RefreshResponse
from src.database.models import User
from src.utils.auth import create_access_token, create_refresh_token, verify_token
from src.utils.exceptions import UnauthorizedError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login",
)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """Authenticate researcher and return access & refresh JWT tokens."""
    result = await db.execute(select(User).where(User.username == payload.username))
    user = result.scalar_one_or_none()

    if not user or not user.verify_password(payload.password):
        raise UnauthorizedError("Invalid username or password")

    if not user.is_active:
        raise UnauthorizedError("User account is disabled")

    # Generate tokens
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh Token",
)
async def refresh_token(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> RefreshResponse:
    """Validate refresh token and issue a new access token."""
    try:
        token_data = verify_token(payload.refresh_token, expected_type="refresh")
        username = token_data.get("sub")
        if not username:
            raise UnauthorizedError("Token payload missing user info")
    except Exception as exc:
        raise UnauthorizedError(f"Invalid refresh token: {str(exc)}")

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if not user:
        raise UnauthorizedError("User associated with token not found")
    if not user.is_active:
        raise UnauthorizedError("User account is disabled")

    access_token = create_access_token(data={"sub": user.username})

    return RefreshResponse(access_token=access_token)
