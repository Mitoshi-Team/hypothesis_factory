from __future__ import annotations

import json

from src.ai_pipeline.clients.yandex_ai_studio import YandexAIStudioClient
from src.models import Entity, Relation, RelationType

_RELATION_SYSTEM_PROMPT = (
    "Ты — анализатор связей между сущностями в технической документации.\n"
    "На вход получаешь список Entity[] (Material, Process, Property,"
    " Parameter) и текст документа.\n"
    "Определи Relation[] между Entity на основе текста.\n"
    "Типы связей:\n"
    "- influences — одна сущность влияет на другую\n"
    "- produces — производит / образует / создаёт\n"
    "- requires — требует / нуждается в\n"
    "- part_of — является частью\n"
    "- contains — содержит в себе\n"
    "- similar_to — похожа на\n\n"
    "Правила:\n"
    "1. source и target — только имена из переданного списка Entity\n"
    "2. Если связь не очевидна из текста — не выдумывай\n"
    "3. Для каждой связи укажи confidence (0.0-1.0)"
    " и evidence (цитата из текста)\n\n"
    "Верни JSON:\n"
    '{"relations": [\n'
    '  {"source": "entity_name", "target": "entity_name", '
    '"relation": "influences", "confidence": 0.9, "evidence": "..."}\n'
    "]}"
)


class RelationExtractor:
    def __init__(self) -> None:
        self.client = YandexAIStudioClient()

    async def extract(
        self,
        entities: list[Entity],
        document_text: str,
    ) -> list[Relation]:
        if not entities or not document_text:
            return []

        entity_names = {e.name for e in entities}
        user_prompt = (
            "Сущности из документа:\n"
            + "\n".join(f"  - {e.name} ({e.label.value})" for e in entities)
            + f"\n\nТекст документа:\n{document_text[:8000]}"
        )

        text = self.client.complete(
            prompt=user_prompt,
            system_prompt=_RELATION_SYSTEM_PROMPT,
            temperature=0.2,
            max_tokens=4000,
        )

        return self._parse_relations(text, entity_names, entities)

    def _parse_relations(
        self,
        text: str,
        valid_names: set[str],
        entities: list[Entity],
    ) -> list[Relation]:
        json_start = text.find("{")
        json_end = text.rfind("}")
        if json_start == -1 or json_end == -1:
            return []

        json_str = text[json_start : json_end + 1]
        try:
            data = json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            return []

        name_to_id = {e.name: e.entity_id for e in entities}

        relation_type_map = {
            "influences": RelationType.INFLUENCES,
            "produces": RelationType.PRODUCES,
            "requires": RelationType.REQUIRES,
            "part_of": RelationType.PART_OF,
            "contains": RelationType.CONTAINS,
            "similar_to": RelationType.SIMILAR_TO,
            "cites": RelationType.CITES,
        }

        relations = []
        for rel_data in data.get("relations", []):
            source_name = rel_data.get("source", "")
            target_name = rel_data.get("target", "")

            if source_name not in valid_names:
                continue
            if target_name not in valid_names:
                continue

            source_id = name_to_id.get(source_name, "")
            target_id = name_to_id.get(target_name, "")
            if not source_id or not target_id:
                continue

            rel_str = rel_data.get("relation", "related").lower()
            rel_type = relation_type_map.get(rel_str, RelationType.CONTAINS)

            relations.append(
                Relation(
                    source_id=source_id,
                    target_id=target_id,
                    relation_type=rel_type,
                    confidence=float(rel_data.get("confidence", 0.5)),
                    chunk_ids=[],
                    metadata={"evidence": rel_data.get("evidence", "")},
                )
            )

        return relations
