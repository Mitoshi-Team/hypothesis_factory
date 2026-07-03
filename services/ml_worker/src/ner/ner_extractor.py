from __future__ import annotations

import logging
import re
from typing import Any, Optional

from models import (
    Entity,
    EntityLabel,
    Relation,
    RelationType,
    UnifiedElement,
)

logger = logging.getLogger(__name__)

DEFAULT_NER_MODEL = "Babelscape/wikineural-multilingual-ner"

NER_LABEL_MAP: dict[str, EntityLabel] = {
    "MISC": EntityLabel.MATERIAL,
    "ORG": EntityLabel.PROCESS,
    "PER": EntityLabel.PARAMETER,
    "LOC": EntityLabel.MATERIAL,
}

RELATION_PATTERNS: list[tuple[str, RelationType, float]] = [
    (r"(?:увеличивает|повышает|улучшает|increases|enhances|improves|boosts)", RelationType.INFLUENCES, 0.85),
    (r"(?:уменьшает|снижает|понижает|decreases|reduces|lowers|diminishes)", RelationType.INFLUENCES, 0.8),
    (r"(?:содержит|включает|состоит\s+из|contains|includes|consists\s+of|comprises)", RelationType.CONTAINS, 0.9),
    (r"(?:производит|синтезирует|создает|получает|produces|synthesizes|creates|generates)", RelationType.PRODUCES, 0.85),
    (r"(?:требует|необходим|нужен|requires|needs|necessitates)", RelationType.REQUIRES, 0.75),
    (r"(?:является\s+частью|входит\s+в|часть|is\s+part\s+of|belongs\s+to|part\s+of)", RelationType.PART_OF, 0.85),
    (r"(?:аналогичен|подобен|сходен|similar\s+to|analogous\s+to|comparable\s+to)", RelationType.SIMILAR_TO, 0.7),
    (r"(?:согласно|по\s+данным|according\s+to|based\s+on|as\s+per)", RelationType.CITES, 0.65),
]


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

        element_of_text: dict[str, str] = {}
        for el_id, txt in texts_by_id.items():
            element_of_text[txt] = el_id

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

    def _normalize_name(self, word: str) -> str:
        word = re.sub(r"^##", "", word)
        word = word.strip().lower()
        word = re.sub(r"[^\w\s-]", "", word)
        return word

    def _find_chunk_ids(
        self,
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

    def extract_relations(
        self,
        entities: list[Entity],
        elements: list[UnifiedElement],
    ) -> list[Relation]:
        if not entities:
            return []

        full_text = "\n".join(
            el.embedding_payload for el in elements if el.embedding_payload.strip()
        )
        if not full_text:
            return []

        sentences = self._split_sentences(full_text)
        relations: list[Relation] = []
        seen_pairs: set[tuple[str, str, str]] = set()

        for sentence in sentences:
            found_in_sentence = self._find_entities_in_sentence(
                sentence, entities
            )
            if len(found_in_sentence) < 2:
                continue

            pattern_rels = self._match_relation_patterns(
                sentence, found_in_sentence, entities
            )
            for rel in pattern_rels:
                pair = (rel.source_id, rel.target_id, rel.relation_type.value)
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    relations.append(rel)

            cooc_rels = self._extract_cooccurrence_relations(
                found_in_sentence, entities
            )
            for rel in cooc_rels:
                pair = (rel.source_id, rel.target_id, rel.relation_type.value)
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    relations.append(rel)

        return relations

    def extract_entities_and_relations(
        self,
        elements: list[UnifiedElement],
    ) -> tuple[list[Entity], list[Relation]]:
        entities = self.extract_entities(elements)
        relations = self.extract_relations(entities, elements)
        return entities, relations

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if s.strip()]

    @staticmethod
    def _find_entities_in_sentence(
        sentence: str,
        entities: list[Entity],
    ) -> list[Entity]:
        sentence_lower = sentence.lower()
        found: list[Entity] = []
        for ent in entities:
            if ent.name in sentence_lower:
                found.append(ent)
            elif ent.surface_form and ent.surface_form.lower() in sentence_lower:
                found.append(ent)
        return found

    def _match_relation_patterns(
        self,
        sentence: str,
        found_entities: list[Entity],
        all_entities: list[Entity],
    ) -> list[Relation]:
        relations: list[Relation] = []
        sentence_lower = sentence.lower()

        for pattern_str, rel_type, confidence in RELATION_PATTERNS:
            match = re.search(pattern_str, sentence_lower, re.IGNORECASE)
            if not match:
                continue

            match_pos = match.start()
            before = [e for e in found_entities if self._entity_before(e, sentence, match_pos)]
            after = [e for e in found_entities if self._entity_after(e, sentence, match_pos)]

            for source in before:
                for target in after:
                    if source.entity_id != target.entity_id:
                        relations.append(
                            Relation(
                                source_id=source.entity_id,
                                target_id=target.entity_id,
                                relation_type=rel_type,
                                confidence=confidence,
                                metadata={"pattern": pattern_str, "sentence": sentence[:200]},
                            )
                        )

        return relations

    @staticmethod
    def _entity_before(entity: Entity, sentence: str, position: int) -> bool:
        name = entity.name
        surface = entity.surface_form or ""
        for term in [name, surface.lower()]:
            if term and term in sentence.lower():
                pos = sentence.lower().index(term)
                if pos < position:
                    return True
        return False

    @staticmethod
    def _entity_after(entity: Entity, sentence: str, position: int) -> bool:
        name = entity.name
        surface = entity.surface_form or ""
        for term in [name, surface.lower()]:
            if term and term in sentence.lower():
                pos = sentence.lower().index(term)
                if pos > position:
                    return True
        return False

    def _extract_cooccurrence_relations(
        self,
        found_entities: list[Entity],
        all_entities: list[Entity],
    ) -> list[Relation]:
        relations: list[Relation] = []
        if len(found_entities) < 2:
            return relations

        for i in range(len(found_entities)):
            for j in range(i + 1, len(found_entities)):
                e1 = found_entities[i]
                e2 = found_entities[j]
                relations.append(
                    Relation(
                        source_id=e1.entity_id,
                        target_id=e2.entity_id,
                        relation_type=RelationType.CONTAINS,
                        confidence=0.5,
                        metadata={
                            "method": "cooccurrence",
                            "note": "Inferred from co-occurrence in same sentence",
                        },
                    )
                )

        return relations
