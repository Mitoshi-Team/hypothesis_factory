"""Admin user creation seeding script."""

import argparse
import asyncio
import sys

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from src.config import get_settings
from src.database.models import User

settings = get_settings()


async def create_admin(username: str, password: str) -> None:
    """Create an admin user in the database if it doesn't already exist.

    Args:
        username: Target administrator username.
        password: Clear text password.
    """
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with async_session() as session:
        # Check if username already exists
        result = await session.execute(select(User).where(User.username == username))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"Error: User '{username}' already exists.")
            sys.exit(1)

        # Create new admin user
        admin_user = User(
            id="usr_admin001",
            username=username,
            role="admin",
            is_active=True,
        )
        admin_user.set_password(password)

        session.add(admin_user)
        await session.commit()
        print(f"Successfully created admin user: {username}")

    await engine.dispose()


def main() -> None:
    """Parse command line arguments and execute admin creation."""
    parser = argparse.ArgumentParser(description="Seed database with admin user.")
    parser.add_argument(
        "--username",
        required=True,
        help="Administrator username",
    )
    parser.add_argument(
        "--password",
        required=True,
        help="Administrator password",
    )

    args = parser.parse_args()
    asyncio.run(create_admin(args.username, args.password))


if __name__ == "__main__":
    main()
