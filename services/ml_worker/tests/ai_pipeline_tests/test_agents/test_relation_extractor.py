from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from src.ai_pipeline.agents.relation_extractor import RelationExtractor
from src.models import Entity, EntityLabel, RelationType


class TestRelationExtractor:
    @pytest.mark.asyncio
    async def test_extract_empty_entities(self):
        agent = RelationExtractor()
        agent.client = MagicMock()
        relations = await agent.extract([], "some text")
        assert relations == []

    @pytest.mark.asyncio
    async def test_extract_empty_text(self, chroma_fx):
        agent = RelationExtractor()
        agent.client = MagicMock()
        entity = Entity(name="Nickel", label=EntityLabel.MATERIAL)
        relations = await agent.extract([entity], "")
        assert relations == []

    def test_parse_relations_empty(self):
        agent = RelationExtractor()
        entity = Entity(name="Nickel", label=EntityLabel.MATERIAL)
        relations = agent._parse_relations("", {"Nickel"}, [entity])
        assert relations == []

    def test_parse_relations_invalid_json(self, chroma_fx):
        agent = RelationExtractor()
        entity = Entity(name="Nickel", label=EntityLabel.MATERIAL)
        relations = agent._parse_relations("not json", {"Nickel"}, [entity])
        assert relations == []

    def test_parse_relations_valid(self, chroma_fx):
        agent = RelationExtractor()
        entity_a = Entity(name="Nickel", label=EntityLabel.MATERIAL)
        entity_b = Entity(name="Strength", label=EntityLabel.PROPERTY)
        text = (
            '{"relations": ['
            '{"source": "Nickel", "target": "Strength",'
            ' "relation": "influences", "confidence": 0.9,'
            ' "evidence": "nickel improves strength"}'
            "]}"
        )
        relations = agent._parse_relations(
            text, {"Nickel", "Strength"}, [entity_a, entity_b]
        )
        assert len(relations) > 0
        assert relations[0].relation_type == RelationType.INFLUENCES
        assert relations[0].source_id == entity_a.entity_id
        assert relations[0].target_id == entity_b.entity_id

    def test_parse_relations_skips_unknown_entities(self, chroma_fx):
        agent = RelationExtractor()
        entity = Entity(name="Nickel", label=EntityLabel.MATERIAL)
        text = (
            '{"relations": ['
            '{"source": "Nickel", "target": "UnknownEntity",'
            ' "relation": "influences", "confidence": 0.9, "evidence": ""}'
            "]}"
        )
        relations = agent._parse_relations(text, {"Nickel"}, [entity])
        assert len(relations) == 0

    def test_parse_relations_all_types(self, chroma_fx):
        agent = RelationExtractor()
        entity_a = Entity(name="A", label=EntityLabel.MATERIAL)
        entity_b = Entity(name="B", label=EntityLabel.PROCESS)
        text = (
            '{"relations": ['
            '{"source": "A", "target": "B", "relation": "produces",'
            ' "confidence": 0.9, "evidence": ""},'
            '{"source": "B", "target": "A", "relation": "requires",'
            ' "confidence": 0.8, "evidence": ""},'
            '{"source": "A", "target": "B", "relation": "part_of",'
            ' "confidence": 0.7, "evidence": ""}'
            "]}"
        )
        relations = agent._parse_relations(
            text, {"A", "B"}, [entity_a, entity_b]
        )
        assert len(relations) == 3
        types = {r.relation_type for r in relations}
        assert RelationType.PRODUCES in types
        assert RelationType.REQUIRES in types
        assert RelationType.PART_OF in types

    def test_parse_relations_deduplicates_source_target(self, chroma_fx):
        agent = RelationExtractor()
        entity = Entity(name="X", label=EntityLabel.PROPERTY)
        text = (
            '{"relations": ['
            '{"source": "X", "target": "X", "relation": "similar_to",'
            ' "confidence": 0.5, "evidence": ""}'
            "]}"
        )
        relations = agent._parse_relations(text, {"X"}, [entity])
        assert len(relations) == 1
        assert relations[0].source_id == entity.entity_id
        assert relations[0].target_id == entity.entity_id
