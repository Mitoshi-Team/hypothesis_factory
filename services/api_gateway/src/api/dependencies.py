"""Dependency injection utilities for the API endpoints."""

from typing import AsyncGenerator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import Settings, get_settings
from src.database.models import User
from src.database.session import get_db_session
from src.utils.auth import verify_token
from src.utils.exceptions import ForbiddenError, UnauthorizedError

security = HTTPBearer(auto_error=False)


def get_app_settings() -> Settings:
    """Dependency injection helper to retrieve application settings.

    Returns:
        The Settings instance configured for the application.
    """
    return get_settings()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection helper for database session.

    Yields:
        AsyncSession: The database session.
    """
    async for session in get_db_session():
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Validate access token and retrieve current authenticated user.

    Args:
        credentials: The Authorization header Bearer token.
        db: Database session.

    Returns:
        User: Database model representing the authenticated user.

    Raises:
        UnauthorizedError: If validation fails or user is inactive.
    """
    if not credentials:
        raise UnauthorizedError("Missing authorization credentials")

    token = credentials.credentials
    try:
        payload = verify_token(token, expected_type="access")
        username: str = payload.get("sub")
        if not username:
            raise UnauthorizedError("Token missing user identifier")
    except Exception as exc:
        raise UnauthorizedError(f"Could not validate credentials: {str(exc)}")

    # Fetch user from database
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if not user:
        raise UnauthorizedError("User not found")
    if not user.is_active:
        raise UnauthorizedError("User is inactive")

    return user


async def check_admin_role(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency to enforce admin-only access on endpoints.

    Args:
        current_user: The authenticated user.

    Returns:
        User: The authenticated admin user.

    Raises:
        ForbiddenError: If the user role is not admin.
    """
    if current_user.role != "admin":
        raise ForbiddenError("Not enough permissions (admin role required)")
    return current_user
