from __future__ import annotations

import pytest
from src.ai_pipeline.tools.postgres_tools import PostgresTools


class TestPostgresTools:
    def test_tool_definitions_structure(self):
        tools = PostgresTools(dsn="postgresql://localhost/test")
        definitions = tools.get_tool_definitions()
        assert len(definitions) == 5
        names = {d["function"]["name"] for d in definitions}
        assert "list_tables" in names
        assert "get_table_schema" in names
        assert "query_table" in names
        assert "get_table_preview" in names
        assert "execute_sql" in names

    def test_tool_definitions_have_required_params(self):
        tools = PostgresTools(dsn="postgresql://localhost/test")
        definitions = tools.get_tool_definitions()
        for d in definitions:
            func = d["function"]
            assert "parameters" in func
            assert "type" in func["parameters"]

    @pytest.mark.asyncio
    async def test_list_tables(self, db_fx):
        tools = PostgresTools(dsn="postgresql://localhost/test")
        pool = db_fx.mock_pool(tables=["materials", "processes"])
        tools._pool = pool
        result = await tools.list_tables()
        assert "materials" in result
        assert "processes" in result

    @pytest.mark.asyncio
    async def test_get_table_schema(self, db_fx):
        tools = PostgresTools(dsn="postgresql://localhost/test")
        pool = db_fx.mock_pool(schema=db_fx.sample_schema())
        tools._pool = pool
        result = await tools.get_table_schema("materials")
        assert "materials" in result
        assert "id" in result
        assert "name" in result

    @pytest.mark.asyncio
    async def test_get_table_schema_not_found(self, db_fx):
        tools = PostgresTools(dsn="postgresql://localhost/test")
        pool = db_fx.mock_pool(schema=[])
        tools._pool = pool
        result = await tools.get_table_schema("nonexistent")
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_query_table(self, db_fx):
        tools = PostgresTools(dsn="postgresql://localhost/test")
        pool = db_fx.mock_pool(query_result=db_fx.sample_query_result())
        tools._pool = pool
        result = await tools.query_table("materials", limit=3)
        assert "material_a" in result
        assert "material_b" in result
        assert "material_c" in result

    @pytest.mark.asyncio
    async def test_get_table_preview(self, db_fx):
        tools = PostgresTools(dsn="postgresql://localhost/test")
        pool = db_fx.mock_pool(query_result=db_fx.sample_query_result()[:2])
        tools._pool = pool
        result = await tools.get_table_preview("materials", n_rows=2)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_execute_sql(self, db_fx):
        tools = PostgresTools(dsn="postgresql://localhost/test")
        rows = db_fx.sample_query_result()
        pool = db_fx.mock_pool(query_result=rows)
        tools._pool = pool
        result = await tools.execute_sql("SELECT * FROM materials")
        assert "material_a" in result

    @pytest.mark.asyncio
    async def test_tool_handlers(self):
        tools = PostgresTools(dsn="postgresql://localhost/test")
        handlers = await tools.get_tool_handlers()
        assert callable(handlers["list_tables"])
        assert callable(handlers["get_table_schema"])
        assert callable(handlers["query_table"])
        assert callable(handlers["get_table_preview"])
        assert callable(handlers["execute_sql"])
