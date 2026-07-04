from __future__ import annotations

from typing import Any, Optional

import asyncpg
from src.config import settings


class PostgresTools:
    def __init__(self, dsn: Optional[str] = None) -> None:
        self.dsn = dsn or settings.postgres_dsn
        self._pool: Optional[asyncpg.Pool] = None

    async def _get_pool(self) -> asyncpg.Pool:
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                self.dsn, min_size=1, max_size=5
            )
        return self._pool

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()
            self._pool = None

    async def list_tables(self) -> str:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT 
                    c.relname AS table_name,
                    d.description AS comment
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                LEFT JOIN pg_description d ON d.objoid = c.oid AND d.objsubid = 0
                WHERE c.relkind = 'r'
                  AND n.nspname = 'public'
                ORDER BY table_name
                """
            )
            if not rows:
                return "No tables found."
            parts = []
            for row in rows:
                name = row["table_name"]
                comment = (
                    row.get("comment")
                    if hasattr(row, "get")
                    else (row["comment"] if "comment" in row else None)
                )
                if comment:
                    parts.append(f"- {name}: {comment}")
                else:
                    parts.append(f"- {name}")
            return "Tables:\n" + "\n".join(parts)

    async def get_table_schema(self, table_name: str) -> str:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT column_name, data_type, is_nullable "
                "FROM information_schema.columns "
                "WHERE table_schema = 'public' AND table_name = $1 "
                "ORDER BY ordinal_position",
                table_name,
            )
            if not rows:
                return f"Table '{table_name}' not found."
            parts = [f"Schema for {table_name}:"]
            for row in rows:
                nullable = (
                    "NULL" if row["is_nullable"] == "YES" else "NOT NULL"
                )
                col = row["column_name"]
                typ = row["data_type"]
                parts.append(f"  - {col}: {typ} ({nullable})")
            return "\n".join(parts)

    async def query_table(
        self,
        table_name: str,
        columns: Optional[str] = None,
        where: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> str:
        pool = await self._get_pool()
        cols = columns or "*"
        query = f"SELECT {cols} FROM {table_name}"  # noqa: S608
        params: list[Any] = []

        if where:
            query += f" WHERE {where}"  # noqa: S608
        query += " ORDER BY 1"
        query += f" LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
        params.extend([limit, offset])

        async with pool.acquire() as conn:
            try:
                rows = await conn.fetch(query, *params)
                if not rows:
                    return "No results."
                column_names = list(rows[0].keys())
                result_parts = [" | ".join(column_names)]
                result_parts.append("-|-" * len(column_names))
                for row in rows:
                    values = [str(row[col]) for col in column_names]
                    result_parts.append(" | ".join(values))
                return "\n".join(result_parts)
            except Exception as e:
                return f"Query error: {e}"

    async def get_table_preview(self, table_name: str, n_rows: int = 5) -> str:
        return await self.query_table(table_name, limit=n_rows)

    async def execute_sql(self, sql: str) -> str:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            try:
                rows = await conn.fetch(sql)  # noqa: S608
                if not rows:
                    return "Query executed. No rows returned."
                column_names = list(rows[0].keys())
                result_parts = [" | ".join(column_names)]
                result_parts.append("-|-" * len(column_names))
                for row in rows[:100]:
                    values = [str(row[col]) for col in column_names]
                    result_parts.append(" | ".join(values))
                if len(rows) > 100:
                    result_parts.append(f"... and {len(rows) - 100} more rows")
                return "\n".join(result_parts)
            except Exception as e:
                return f"SQL error: {e}"

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        tools = [
            {
                "name": "list_tables",
                "description": "List all tables in the public schema",
                "parameters": {"type": "object", "properties": {}},
            },
            {
                "name": "get_table_schema",
                "description": "Get the schema of a specific table",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Table name",
                        },
                    },
                    "required": ["table_name"],
                },
            },
            {
                "name": "query_table",
                "description": "Query rows from a table",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string"},
                        "columns": {
                            "type": "string",
                            "description": "Comma-separated columns",
                        },
                        "where": {
                            "type": "string",
                            "description": "SQL WHERE clause",
                        },
                        "limit": {"type": "integer", "default": 50},
                        "offset": {"type": "integer", "default": 0},
                    },
                    "required": ["table_name"],
                },
            },
            {
                "name": "get_table_preview",
                "description": "Preview first N rows of a table",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string"},
                        "n_rows": {"type": "integer", "default": 5},
                    },
                    "required": ["table_name"],
                },
            },
            {
                "name": "execute_sql",
                "description": "Execute an arbitrary read-only SQL query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sql": {
                            "type": "string",
                            "description": "SELECT query",
                        },
                    },
                    "required": ["sql"],
                },
            },
        ]
        return [{"type": "function", "function": tool} for tool in tools]

    async def get_tool_handlers(self) -> dict[str, callable]:
        return {
            "list_tables": self.list_tables,
            "get_table_schema": self.get_table_schema,
            "query_table": self.query_table,
            "get_table_preview": self.get_table_preview,
            "execute_sql": self.execute_sql,
        }
