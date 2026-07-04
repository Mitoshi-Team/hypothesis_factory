"""JWT authentication and verification utilities."""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from src.config import get_settings

settings = get_settings()
ALGORITHM = "HS256"


def create_access_token(
    data: dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Generate a JWT access token.

    Args:
        data: Payload data to encode.
        expires_delta: Optional custom token lifetime.

    Returns:
        str: Encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(
    data: dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Generate a JWT refresh token.

    Args:
        data: Payload data to encode.
        expires_delta: Optional custom token lifetime.

    Returns:
        str: Encoded JWT refresh token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str, expected_type: str = "access") -> dict[str, Any]:
    """Decode and verify a JWT token.

    Args:
        token: JWT token string.
        expected_type: Expected token type ("access" or "refresh").

    Returns:
        dict[str, Any]: The decoded payload.

    Raises:
        JWTError: If token is invalid, expired, or has incorrect type.
    """
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    token_type = payload.get("type")
    if token_type != expected_type:
        raise JWTError("Invalid token type")
    return payload
