#!/usr/bin/env python3
"""Create default users for API Gateway.

Usage:
    python create_default_users.py

Creates:
- admin / admin (role=admin)
- tmp_researcher / tmp_researcher_password (role=user)
"""

from __future__ import annotations

import asyncio
import os
import sys
import uuid

import asyncpg
import bcrypt


DEFAULT_DSN = (
    "postgresql://hypothesis-factory:hypothesis-factory@localhost:5432/"
    "hypothesis-factory"
)

USERS = [
    ("admin", "admin", "admin"),
    ("tmp_researcher", "tmp_researcher_password", "user"),
]


async def create_user(
    conn: asyncpg.Connection, username: str, password: str, role: str
) -> None:
    existing = await conn.fetchval("SELECT id FROM users WHERE username = $1", username)
    if existing:
        print(f"User '{username}' already exists, skipping.")
        return

    user_id = f"usr_{uuid.uuid4().hex[:12]}"
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    await conn.execute(
        "INSERT INTO users (id, username, hashed_password, role, is_active) "
        "VALUES ($1, $2, $3, $4, $5)",
        user_id,
        username,
        hashed,
        role,
        True,
    )
    print(f"Created {role} user '{username}' with id {user_id}")


async def main() -> None:
    dsn = os.environ.get("DATABASE_URL", DEFAULT_DSN).replace(
        "postgresql+asyncpg://", "postgresql://"
    )
    conn = await asyncpg.connect(dsn)
    try:
        for username, password, role in USERS:
            await create_user(conn, username, password, role)
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
