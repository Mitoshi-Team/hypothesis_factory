from __future__ import annotations

import logging
import re
from typing import Any, Optional

from models import Entity, EntityLabel, UnifiedElement

logger = logging.getLogger(__name__)

DEFAULT_NER_MODEL = "AmedeoBonatti/nlp_te_ner_matbert"

NER_LABEL_MAP: dict[str, EntityLabel] = {
    "mat_name": EntityLabel.MATERIAL,
    "mat_class": EntityLabel.MATERIAL,
    "mat_form": EntityLabel.MATERIAL,
    "prop": EntityLabel.PROPERTY,
    "manuf": EntityLabel.PROCESS,
    "number": EntityLabel.PARAMETER,
    "unit_measure": EntityLabel.PARAMETER,
    "attribute": EntityLabel.PROPERTY,
    "char": EntityLabel.PROPERTY,
    "cell": EntityLabel.PROCESS,
    "app": EntityLabel.PROCESS,
}


class NERExtractor:
    def __init__(
        self,
        model_name: str = DEFAULT_NER_MODEL,
        device: int = -1,
    ):
        self._model_name = model_name
        self._device = device
        self._pipeline: Any = None

    def _get_pipeline(self):
        if self._pipeline is not None:
            return self._pipeline
        from transformers import pipeline

        logger.info("Loading NER model: %s (device=%s)", self._model_name, self._device)
        self._pipeline = pipeline(
            "token-classification",
            model=self._model_name,
            device=self._device,
            aggregation_strategy="simple",
        )
        return self._pipeline

    def extract_entities(self, elements: list[UnifiedElement]) -> list[Entity]:
        texts_by_id: dict[str, str] = {}
        for el in elements:
            payload = el.embedding_payload
            if payload.strip():
                texts_by_id[el.element_id] = payload

        all_texts = list(texts_by_id.values())
        if not all_texts:
            return []

        model_entities = self._extract_with_model(all_texts)

        entities: list[Entity] = []
        seen_names: set[str] = set()

        for ent in model_entities:
            name = self._normalize_name(ent["word"])
            if not name or name in seen_names:
                continue
            seen_names.add(name)

            label = self._map_entity_label(ent["entity_group"])
            chunk_ids = self._find_chunk_ids(
                ent["word"], all_texts, texts_by_id
            )

            entity = Entity(
                label=label,
                name=name,
                surface_form=ent["word"],
                chunk_ids=chunk_ids,
                metadata={
                    "model": self._model_name,
                    "score": round(ent["score"], 4),
                },
            )
            entities.append(entity)

        return entities

    def _extract_with_model(self, texts: list[str]) -> list[dict[str, Any]]:
        pipe = self._get_pipeline()
        all_entities: list[dict[str, Any]] = []
        for text in texts:
            chunks = self._chunk_text(text)
            for chunk in chunks:
                try:
                    results = pipe(chunk)
                    all_entities.extend(results)
                except Exception as exc:
                    logger.warning("NER pipeline failed on chunk: %s", exc)
        return all_entities

    def _chunk_text(self, text: str, max_chars: int = 512) -> list[str]:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        chunks: list[str] = []
        current = ""
        for sentence in sentences:
            if len(current) + len(sentence) < max_chars:
                current += " " + sentence if current else sentence
            else:
                if current:
                    chunks.append(current)
                current = sentence
        if current:
            chunks.append(current)
        return chunks if chunks else [text]

    def _map_entity_label(self, ner_label: str) -> EntityLabel:
        return NER_LABEL_MAP.get(ner_label, EntityLabel.MATERIAL)

    @staticmethod
    def _normalize_name(word: str) -> str:
        word = re.sub(r"^##", "", word)
        word = word.strip().lower()
        word = re.sub(r"[^\w\s-]", "", word)
        return word

    @staticmethod
    def _find_chunk_ids(
        word: str,
        all_texts: list[str],
        texts_by_id: dict[str, str],
    ) -> list[str]:
        chunk_ids: list[str] = []
        search_term = word.lower().strip()
        if not search_term:
            return chunk_ids
        for txt, el_id in texts_by_id.items():
            if search_term in txt.lower():
                chunk_ids.append(el_id)
        return chunk_ids
