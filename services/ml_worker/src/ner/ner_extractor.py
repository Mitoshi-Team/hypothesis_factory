from __future__ import annotations

import logging
from typing import Any

from src.config import settings
from src.models import Entity, EntityLabel, UnifiedElement

logger = logging.getLogger(__name__)

DEFAULT_NER_MODEL = settings.ner_model_name

NER_LABELS = ["MATERIAL", "PROCESS", "PROPERTY", "PARAMETER"]

NER_LABEL_MAP: dict[str, EntityLabel] = {
    "MATERIAL": EntityLabel.MATERIAL,
    "PROCESS": EntityLabel.PROCESS,
    "PROPERTY": EntityLabel.PROPERTY,
    "PARAMETER": EntityLabel.PARAMETER,
}

_LABEL_TO_ENTITY_LABEL = {
    "material": EntityLabel.MATERIAL,
    "process": EntityLabel.PROCESS,
    "property": EntityLabel.PROPERTY,
    "parameter": EntityLabel.PARAMETER,
}


class NERExtractor:
    def __init__(
        self,
        model_name: str = DEFAULT_NER_MODEL,
        device: int = -1,
        threshold: float = 0.5,
    ):
        self._model_name = model_name
        self._device = device
        self._threshold = threshold
        self._model: Any = None

    def _get_model(self):
        if self._model is not None:
            return self._model
        from gliner import GLiNER
        from huggingface_hub import login as hf_login

        if settings.hf_token:
            hf_login(settings.hf_token)

        logger.info(
            "Loading GLiNER model: %s (device=%s)",
            self._model_name,
            self._device,
        )
        self._model = GLiNER.from_pretrained(self._model_name)
        return self._model

    def extract_entities(self, elements: list[UnifiedElement]) -> list[Entity]:
        entities: list[Entity] = []
        non_empty = [el for el in elements if el.embedding_payload.strip()]
        if not non_empty:
            return entities

        model = self._get_model()
        seen_names: set[tuple[str, str]] = set()

        for el in non_empty:
            payload = el.embedding_payload

            try:
                raw = model.predict_entities(
                    payload,
                    labels=NER_LABELS,
                    threshold=self._threshold,
                )
            except Exception as exc:
                logger.warning(
                    "GLiNER prediction failed on element %s: %s",
                    el.element_id,
                    exc,
                )
                continue

            for item in raw:
                name = self._normalize_name(item["text"])
                label = item.get("label", "")
                entity_label = _LABEL_TO_ENTITY_LABEL.get(label.lower())

                if not name or not entity_label:
                    continue

                key = (name, entity_label.value)
                if key in seen_names:
                    continue
                seen_names.add(key)

                entity = Entity(
                    label=entity_label,
                    name=name,
                    surface_form=item["text"],
                    chunk_ids=[el.element_id],
                    metadata={
                        "model": self._model_name,
                        "score": round(item.get("score", 0), 4),
                    },
                )
                entities.append(entity)

        return entities

    @staticmethod
    def _normalize_name(word: str) -> str:
        word = word.strip().lower()
        return word
