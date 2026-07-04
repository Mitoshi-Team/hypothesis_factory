from __future__ import annotations

import logging
import re
from typing import Any, Optional

from sqlalchemy import create_engine, text
from src.ai_pipeline.clients.yandex_ai_studio import YandexAIStudioClient
from src.config import settings
from src.models import Entity, Relation, TableData, UnifiedDocument

logger = logging.getLogger(__name__)


class DBHandler:
    """Handler for PostgreSQL ingestion and table mapping."""

    def __init__(self, connection_string: Optional[str] = None) -> None:
        self._connection_string = connection_string

    def _sanitize_name(self, name: str) -> str:
        sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", name)
        sanitized = sanitized.lower()
        if sanitized and sanitized[0].isdigit():
            sanitized = "t_" + sanitized
        sanitized = re.sub(r"_+", "_", sanitized).strip("_")
        return sanitized or "table"

    def _infer_column_type(self, rows: list[list[Any]], col_idx: int) -> str:
        has_int = False
        has_float = False
        has_text = False
        for row in rows:
            if col_idx >= len(row):
                continue
            val = row[col_idx]
            if (
                val is None
                or str(val).strip() == ""
                or str(val).strip().lower() in ("nan", "none", "null")
            ):
                continue
            val_str = str(val).strip()
            try:
                int(val_str)
                has_int = True
            except ValueError:
                try:
                    float(val_str)
                    has_float = True
                except ValueError:
                    has_text = True

        if has_text:
            return "TEXT"
        if has_float:
            return "DOUBLE PRECISION"
        if has_int:
            return "BIGINT"
        return "TEXT"

    def _generate_caption(
        self, table_data: TableData, ai_client: YandexAIStudioClient
    ) -> str:
        preview_rows_str = ""
        if table_data.rows:
            preview_rows_str = "\n".join(
                " | ".join(str(v) if v is not None else "" for v in row)
                for row in table_data.rows[:5]
            )

        prompt = (
            f"Пожалуйста, предоставь краткое описание (1-2 предложения на "
            f"русском языке) следующей таблицы.\nОписание должно четко "
            f"объяснять суть таблицы (какие технологические параметры, "
            f"показатели, или реагенты в ней описаны).\n\n"
            f"Название таблицы: {table_data.name or 'Без названия'}\n"
            f"Колонки: {', '.join(table_data.columns)}\n"
            f"Данные (первые строки):\n{preview_rows_str}\n\n"
            f"Краткое описание:"
        )

        system_prompt = (
            "Ты — профессиональный ИИ-ассистент, помогающий в анализе "
            "металлургических и технологических таблиц для обогащения "
            "медно-никелевых руд. Твоя задача — составить краткое емкое "
            "описание таблицы на русском языке."
        )

        try:
            description = ai_client.complete(
                prompt=prompt, system_prompt=system_prompt
            )
            return description.strip()
        except Exception as e:
            logger.exception(
                "Failed to generate table caption via Yandex AI Studio: %s",
                e,
            )
            return (
                f"Таблица {table_data.name or ''} "
                f"с колонками {', '.join(table_data.columns)}"
            )

    def _prepare_insert_params(
        self,
        rows: list[list[Any]],
        sanitized_cols: list[str],
        col_definitions: list[str],
    ) -> list[dict[str, Any]]:
        insert_params = []
        for row in rows:
            row_dict = {}
            for i in range(len(sanitized_cols)):
                val = row[i] if i < len(row) else None
                if (
                    val is None
                    or str(val).strip() == ""
                    or str(val).strip().lower() in ("nan", "none", "null")
                ):
                    row_dict[f"col_{i}"] = None
                else:
                    col_type = col_definitions[i].split()[-1]
                    val_str = str(val).strip()
                    if col_type == "BIGINT":
                        try:
                            row_dict[f"col_{i}"] = int(val_str)
                        except ValueError:
                            row_dict[f"col_{i}"] = None
                    elif col_type == "DOUBLE PRECISION":
                        try:
                            row_dict[f"col_{i}"] = float(val_str)
                        except ValueError:
                            row_dict[f"col_{i}"] = None
                    else:
                        row_dict[f"col_{i}"] = val_str
            insert_params.append(row_dict)
        return insert_params

    def _execute_db_insertion(
        self,
        engine: Any,
        table_name: str,
        create_table_sql: str,
        sanitized_cols: list[str],
        insert_params: list[dict[str, Any]],
        caption: Optional[str],
    ) -> None:
        with engine.begin() as conn:
            conn.execute(text(f'DROP TABLE IF EXISTS "{table_name}" CASCADE;'))
            conn.execute(text(create_table_sql))

            if insert_params:
                columns_str = ", ".join(f'"{c}"' for c in sanitized_cols)
                param_placeholders = ", ".join(
                    f":col_{i}" for i in range(len(sanitized_cols))
                )
                insert_sql = text(
                    f'INSERT INTO "{table_name}" ({columns_str}) '  # noqa: S608
                    f"VALUES ({param_placeholders})"
                )
                conn.execute(insert_sql, insert_params)

            if caption:
                conn.execute(
                    text(f'COMMENT ON TABLE "{table_name}" IS :comment'),
                    {"comment": caption},
                )
            logger.info("Copied table %s to PostgreSQL", table_name)

    def _copy_single_table(
        self,
        engine: Any,
        doc_id_short: str,
        table_data: TableData,
        ai_client: Optional[YandexAIStudioClient],
    ) -> None:
        # 1. Generate Yandex AI Studio description if not present
        if not table_data.caption and ai_client:
            table_data.caption = self._generate_caption(table_data, ai_client)

        # 2. Sanitize and prepare schema
        sanitized_sheet_name = self._sanitize_name(table_data.name or "sheet")
        table_name = f"t_{doc_id_short}_{sanitized_sheet_name}"

        if not table_data.columns and table_data.rows:
            table_data.columns = [
                f"col_{i}" for i in range(len(table_data.rows[0]))
            ]

        col_definitions = []
        sanitized_cols = []
        for i, col in enumerate(table_data.columns):
            col_name = self._sanitize_name(col or f"col_{i}")
            orig_col_name = col_name
            counter = 1
            while col_name in sanitized_cols:
                col_name = f"{orig_col_name}_{counter}"
                counter += 1
            sanitized_cols.append(col_name)
            col_type = self._infer_column_type(table_data.rows, i)
            col_definitions.append(f'"{col_name}" {col_type}')

        create_table_sql = (
            f'CREATE TABLE "{table_name}" (\n  '
            + ",\n  ".join(col_definitions)
            + "\n);"
        )

        insert_params = self._prepare_insert_params(
            table_data.rows, sanitized_cols, col_definitions
        )

        self._execute_db_insertion(
            engine=engine,
            table_name=table_name,
            create_table_sql=create_table_sql,
            sanitized_cols=sanitized_cols,
            insert_params=insert_params,
            caption=table_data.caption,
        )

    def copy_tables(self, document: UnifiedDocument) -> None:
        """Copy all tables from document to PostgreSQL database."""
        tables = document.get_tables()
        if not tables:
            logger.info(
                "No tables to copy for document %s", document.document_id
            )
            return

        engine = create_engine(
            self._connection_string or settings.postgres_dsn
        )

        try:
            ai_client = YandexAIStudioClient()
        except Exception as e:
            logger.warning("Failed to initialize YandexAIStudioClient: %s", e)
            ai_client = None

        doc_id_short = document.document_id.replace("-", "")[:8]

        for el in tables:
            if not el.table_data:
                continue
            self._copy_single_table(
                engine=engine,
                doc_id_short=doc_id_short,
                table_data=el.table_data,
                ai_client=ai_client,
            )

    def save_entities(self, entities: list[Entity]) -> None:
        """Save extracted entities to database."""
        logger.info(
            "STUB: save_entities( count=%d ) — PostgreSQL insert skipped",
            len(entities),
        )

    def save_relations(self, relations: list[Relation]) -> None:
        """Save extracted relations to database."""
        logger.info(
            "STUB: save_relations( count=%d ) — PostgreSQL insert skipped",
            len(relations),
        )
