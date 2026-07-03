from __future__ import annotations

import logging
from typing import Optional

from models import Entity, Relation, UnifiedDocument, UnifiedElement

logger = logging.getLogger(__name__)


class DBHandler:
    def __init__(self, connection_string: Optional[str] = None):
        self._connection_string = connection_string

    def copy_tables(self, document: UnifiedDocument) -> None:
        tables = document.get_tables()
        if not tables:
            logger.info("No tables found in document %s", document.document_id)
            return

        logger.info(
            "STUB: Would insert %d table(s) from document %s into PostgreSQL `structured_tables`",
            len(tables),
            document.document_id,
        )
        for table_el in tables:
            if table_el.table_data:
                self._stub_insert_table(document.document_id, table_el)

    def save_entities(self, entities: list[Entity]) -> None:
        if not entities:
            logger.info("No entities to save")
            return

        logger.info(
            "STUB: Would insert %d entity/ies into PostgreSQL `entities` table",
            len(entities),
        )
        for ent in entities:
            logger.debug(
                "  INSERT INTO entities (id, label, name) VALUES ('%s', '%s', '%s')",
                ent.entity_id,
                ent.label.value,
                ent.name,
            )

    def save_relations(self, relations: list[Relation]) -> None:
        if not relations:
            logger.info("No relations to save")
            return

        logger.info(
            "STUB: Would insert %d relation(s) into PostgreSQL `relations` table",
            len(relations),
        )
        for rel in relations:
            logger.debug(
                "  INSERT INTO relations (id, source, target, type) VALUES ('%s', '%s', '%s', '%s')",
                rel.relation_id,
                rel.source_id,
                rel.target_id,
                rel.relation_type.value,
            )

    @staticmethod
    def _stub_insert_table(document_id: str, element: UnifiedElement) -> None:
        td = element.table_data
        logger.debug(
            "  STUB: INSERT INTO structured_tables (doc_id, table_id, name, columns, rows) "
            "VALUES ('%s', '%s', '%s', %s, %d)",
            document_id,
            td.table_id,
            td.name or "unnamed",
            td.columns,
            len(td.rows),
        )
