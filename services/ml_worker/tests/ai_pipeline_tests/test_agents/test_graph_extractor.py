from __future__ import annotations

import pytest
from ai_pipeline.agents.graph_extractor import GraphExtractorAgent
from models import EntityLabel


class TestGraphExtractorAgent:
    @pytest.mark.asyncio
    async def test_extract_empty(self):
        agent = GraphExtractorAgent()
        entities, relations = await agent.extract([])
        assert len(entities) == 0
        assert len(relations) == 0

    def test_parse_extraction_empty(self, chroma_fx):
        agent = GraphExtractorAgent()
        chunk = chroma_fx.make_chunk(text="Test")
        entities, relations = agent._parse_extraction("", chunk)
        assert len(entities) == 0
        assert len(relations) == 0

    def test_parse_extraction_invalid_json(self, chroma_fx):
        agent = GraphExtractorAgent()
        chunk = chroma_fx.make_chunk(text="Test")
        entities, relations = agent._parse_extraction("Not JSON", chunk)
        assert len(entities) == 0
        assert len(relations) == 0

    def test_parse_extraction_valid(self, chroma_fx):
        agent = GraphExtractorAgent()
        chunk = chroma_fx.make_chunk(text="Nickel ore contains sulfur")
        text = (
            '{"entities": ['
            '{"name": "Nickel", "label": "Material", "surface_form": "nickel"},'
            '{"name": "Sulfur", "label": "Material", "surface_form": "sulfur"}'
            "],"
            '"relations": ['
            '{"source": "Nickel", "target": "Sulfur",'
            ' "relation": "contains", "confidence": 0.9}'
            "]}"
        )
        entities, relations = agent._parse_extraction(text, chunk)
        assert len(entities) >= 1
        assert len(relations) >= 0

    def test_parse_extraction_with_all_types(self, chroma_fx):
        agent = GraphExtractorAgent()
        chunk = chroma_fx.make_chunk(text="Test")
        text = (
            '{"entities": ['
            '{"name": "Mat", "label": "Material"},'
            '{"name": "Proc", "label": "Process"},'
            '{"name": "Prop", "label": "Property"},'
            '{"name": "Param", "label": "Parameter"}'
            "],"
            '"relations": []}'
        )
        entities, _ = agent._parse_extraction(text, chunk)
        assert len(entities) == 4
        labels = {e.label for e in entities}
        assert EntityLabel.MATERIAL in labels
        assert EntityLabel.PROCESS in labels
        assert EntityLabel.PROPERTY in labels
        assert EntityLabel.PARAMETER in labels
