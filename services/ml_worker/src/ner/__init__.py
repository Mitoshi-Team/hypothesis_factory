from __future__ import annotations

import logging
from typing import Optional

from pydantic import BaseModel
from src.config import settings
from src.models import Entity, UnifiedDocument
from src.ner.db_handler import DBHandler
from src.ner.extractors import get_extractor
from src.ner.ner_extractor import NERExtractor
from src.ner.router import route_file

logger = logging.getLogger(__name__)


class NERResult(BaseModel):
    document: UnifiedDocument
    entities: list[Entity]


class NERPipeline:
    def __init__(
        self,
        ner_model_name: Optional[str] = None,
        ner_device: int = -1,
        db_connection_string: Optional[str] = None,
        ner_threshold: float = 0.5,
    ):
        self._ner_model_name = ner_model_name
        self._ner_device = ner_device
        self._ner_threshold = ner_threshold
        self._db_connection_string = db_connection_string
        self._ner: Optional[NERExtractor] = None
        self._db: Optional[DBHandler] = None

    @property
    def ner(self) -> NERExtractor:
        if self._ner is None:
            self._ner = NERExtractor(
                model_name=self._ner_model_name or settings.ner_model_name,
                device=self._ner_device,
                threshold=self._ner_threshold,
            )
        return self._ner

    @property
    def db(self) -> DBHandler:
        if self._db is None:
            self._db = DBHandler(connection_string=self._db_connection_string)
        return self._db

    def extract_document(self, file_path: str) -> UnifiedDocument:
        source_type = route_file(file_path)
        extractor = get_extractor(source_type)
        logger.info(
            "Extracting document: %s (type=%s)", file_path, source_type.value
        )
        return extractor.extract(file_path)

    def extract_entities(self, document: UnifiedDocument) -> list[Entity]:
        logger.info(
            "Extracting entities from document %s",
            document.document_id,
        )
        return self.ner.extract_entities(document.elements)

    def process(self, file_path: str) -> NERResult:
        document = self.extract_document(file_path)

        entities = self.extract_entities(document)

        self.db.save_entities(entities)

        return NERResult(document=document, entities=entities)


_pipeline: Optional[NERPipeline] = None


def get_pipeline(
    ner_model_name: Optional[str] = None,
    ner_device: int = -1,
    db_connection_string: Optional[str] = None,
) -> NERPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = NERPipeline(
            ner_model_name=ner_model_name,
            ner_device=ner_device,
            db_connection_string=db_connection_string,
        )
    return _pipeline


def extract_document(file_path: str) -> UnifiedDocument:
    """Функция 1: из файла получить UnifiedDocument."""
    return get_pipeline().extract_document(file_path)


def extract_entities(document: UnifiedDocument) -> list[Entity]:
    """Функция 2: из UnifiedDocument получить список Entity."""
    return get_pipeline().extract_entities(document)
