from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock


class _AcquireCM:
    def __init__(self, conn: AsyncMock) -> None:
        self._conn = conn

    async def __aenter__(self) -> AsyncMock:
        return self._conn

    async def __aexit__(self, *args: Any) -> None:
        pass


class DatabaseTestMixin:
    """Mock asyncpg pool and connection for testing Postgres tools."""

    @staticmethod
    def mock_row(**kwargs: Any) -> MagicMock:
        row = MagicMock()
        row.__getitem__.side_effect = lambda k: kwargs.get(k, "")
        row.keys.return_value = list(kwargs.keys())
        return row

    @staticmethod
    def mock_pool(
        tables: list[str] | None = None,
        schema: list[dict[str, str]] | None = None,
        query_result: list[dict[str, Any]] | None = None,
    ) -> AsyncMock:
        pool = MagicMock()
        conn = AsyncMock()
        pool.acquire.return_value = _AcquireCM(conn)

        if tables is not None:
            conn.fetch.side_effect = [
                [{"table_name": t} for t in tables],
            ]
        elif schema is not None:
            conn.fetch.side_effect = [
                [DatabaseTestMixin.mock_row(**row) for row in schema],
            ]
        elif query_result is not None:
            conn.fetch.side_effect = [
                [DatabaseTestMixin.mock_row(**row) for row in query_result],
            ]
        else:
            conn.fetch.side_effect = [
                [
                    DatabaseTestMixin.mock_row(
                        column_name="id",
                        data_type="integer",
                        is_nullable="NO",
                    )
                ],
            ]

        return pool

    @staticmethod
    def sample_tables() -> list[str]:
        return ["materials", "processes", "properties", "experiments"]

    @staticmethod
    def sample_schema() -> list[dict[str, str]]:
        return [
            {"column_name": "id", "data_type": "integer", "is_nullable": "NO"},
            {"column_name": "name", "data_type": "text", "is_nullable": "YES"},
            {
                "column_name": "value",
                "data_type": "float8",
                "is_nullable": "YES",
            },
        ]

    @staticmethod
    def sample_query_result() -> list[dict[str, Any]]:
        return [
            {"id": 1, "name": "material_a", "value": 10.5},
            {"id": 2, "name": "material_b", "value": 20.3},
            {"id": 3, "name": "material_c", "value": 15.7},
        ]
