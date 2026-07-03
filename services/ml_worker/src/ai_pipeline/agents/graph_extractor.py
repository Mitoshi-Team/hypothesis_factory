from __future__ import annotations

import json

from models import Chunk, Entity, EntityLabel, Relation, RelationType

from ai_pipeline.clients.yandex_ai_studio import YandexAIStudioClient


class GraphExtractorAgent:
    def __init__(self) -> None:
        self.client = YandexAIStudioClient()

    async def extract(
        self, chunks: list[Chunk]
    ) -> tuple[list[Entity], list[Relation]]:
        if not chunks:
            return [], []

        all_entities: list[Entity] = []
        all_relations: list[Relation] = []

        for chunk in chunks:
            entities, relations = await self._extract_from_chunk(chunk)
            all_entities.extend(entities)
            all_relations.extend(relations)

        return all_entities, all_relations

    async def _extract_from_chunk(
        self,
        chunk: Chunk,
    ) -> tuple[list[Entity], list[Entity]]:
        system_prompt = (
            "Извлеки сущности и связи из текста для графа знаний.\n"
            "Типы сущностей: Material (материал), Process (процесс), "
            "Property (свойство), Parameter (параметр).\n"
            "Типы связей: contains, influences, produces, requires, "
            "cites, part_of, similar_to.\n\n"
            "Верни JSON:\n"
            "{\n"
            '  "entities": [\n'
            '    {"name": "...",'
            ' "label": "Material|Process|Property|Parameter",'
            ' "surface_form": "..."}\n'
            "  ],\n"
            '  "relations": [\n'
            '    {"source": "...", "target": "...", '
            '"relation": "contains|influences|...", "confidence": 1.0}\n'
            "  ]\n"
            "}"
        )

        user_prompt = f"Текст:\n{chunk.text[:2000]}"

        text = self.client.complete(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=2000,
        )

        return self._parse_extraction(text, chunk)

    def _parse_extraction(
        self,
        text: str,
        chunk: Chunk,
    ) -> tuple[list[Entity], list[Relation]]:
        json_start = text.find("{")
        json_end = text.rfind("}")
        if json_start == -1 or json_end == -1:
            return [], []

        json_str = text[json_start : json_end + 1]
        try:
            data = json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            return [], []

        entities = []
        label_map = {
            "Material": EntityLabel.MATERIAL,
            "Process": EntityLabel.PROCESS,
            "Property": EntityLabel.PROPERTY,
            "Parameter": EntityLabel.PARAMETER,
        }
        for ent_data in data.get("entities", []):
            label_str = ent_data.get("label", "Property")
            label = label_map.get(label_str, EntityLabel.PROPERTY)
            entity = Entity(
                name=ent_data.get("name", ""),
                label=label,
                surface_form=ent_data.get("surface_form"),
                chunk_ids=[chunk.chunk_id],
            )
            entities.append(entity)

        entity_map = {e.name: e.entity_id for e in entities}
        relation_type_map = {
            "contains": RelationType.CONTAINS,
            "influences": RelationType.INFLUENCES,
            "produces": RelationType.PRODUCES,
            "requires": RelationType.REQUIRES,
            "cites": RelationType.CITES,
            "part_of": RelationType.PART_OF,
            "similar_to": RelationType.SIMILAR_TO,
        }

        relations = []
        for rel_data in data.get("relations", []):
            source_name = rel_data.get("source", "")
            target_name = rel_data.get("target", "")
            source_id = entity_map.get(source_name, "")
            target_id = entity_map.get(target_name, "")
            rel_str = rel_data.get("relation", "related")
            rel_type = relation_type_map.get(rel_str, RelationType.CONTAINS)

            if source_id and target_id:
                relation = Relation(
                    source_id=source_id,
                    target_id=target_id,
                    relation_type=rel_type,
                    confidence=float(rel_data.get("confidence", 1.0)),
                    chunk_ids=[chunk.chunk_id],
                )
                relations.append(relation)

        return entities, relations
