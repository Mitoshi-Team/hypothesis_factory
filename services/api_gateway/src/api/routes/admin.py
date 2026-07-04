"""Admin API routes."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.dependencies import check_admin_role, get_db
from src.api.schemas import UserCreate, UserResponse
from src.database.models import User
from src.utils.exceptions import ValidationAppError

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create User",
)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(check_admin_role),
) -> UserResponse:
    """Create a new user. Only accessible by administrators."""
    # Check if username already exists
    result = await db.execute(select(User).where(User.username == payload.username))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise ValidationAppError(f"Username '{payload.username}' already exists")

    if payload.role not in ("admin", "user"):
        raise ValidationAppError("Invalid role. Allowed roles: 'admin', 'user'")

    import datetime

    # Create new user record
    user_id = f"usr_{uuid.uuid4().hex[:12]}"
    new_user = User(
        id=user_id,
        username=payload.username,
        role=payload.role,
        is_active=True,
        created_at=datetime.datetime.now(datetime.UTC),
    )
    new_user.set_password(payload.password)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        role=new_user.role,
        is_active=new_user.is_active,
        created_at=new_user.created_at,
    )
