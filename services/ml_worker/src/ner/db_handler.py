from __future__ import annotations

import logging
from typing import Optional

from src.models import Entity, Relation, UnifiedDocument

logger = logging.getLogger(__name__)


class DBHandler:
    def __init__(self, connection_string: Optional[str] = None):
        self._connection_string = connection_string

    def copy_tables(self, document: UnifiedDocument) -> None:
        logger.info(
            (  # noqa: E501
                "STUB: copy_tables( doc_id=%s, tables=%d ) —"
                " PostgreSQL insert skipped"
            ),
            document.document_id,
            len(document.get_tables()),
        )

    def save_entities(self, entities: list[Entity]) -> None:
        logger.info(
            "STUB: save_entities( count=%d ) — PostgreSQL insert skipped",
            len(entities),
        )

    def save_relations(self, relations: list[Relation]) -> None:
        logger.info(
            "STUB: save_relations( count=%d ) — PostgreSQL insert skipped",
            len(relations),
        )
