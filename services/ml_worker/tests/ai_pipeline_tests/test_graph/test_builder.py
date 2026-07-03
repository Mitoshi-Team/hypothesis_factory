from __future__ import annotations

from ai_pipeline.graph.builder import GraphBuilder
from ai_pipeline.state import HypothesisCard
from models import Entity, EntityLabel, Relation, RelationType


class TestGraphBuilder:
    def test_build_empty(self):
        builder = GraphBuilder()
        graph = builder.build([], [])
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0

    def test_build_with_entities(self):
        builder = GraphBuilder()
        entities = [
            Entity(
                entity_id="ent_001",
                label=EntityLabel.MATERIAL,
                name="Nickel",
            ),
            Entity(
                entity_id="ent_002",
                label=EntityLabel.PROCESS,
                name="Smelting",
            ),
        ]
        relations = [
            Relation(
                relation_id="rel_001",
                source_id="ent_001",
                target_id="ent_002",
                relation_type=RelationType.REQUIRES,
                confidence=0.9,
            ),
        ]
        graph = builder.build(entities, relations)
        assert len(graph.nodes) == 2
        assert len(graph.edges) == 1
        assert graph.edges[0].source == "ent_001"
        assert graph.edges[0].target == "ent_002"

    def test_deduplicate_entities(self):
        builder = GraphBuilder()
        entities = [
            Entity(
                entity_id="ent_001",
                label=EntityLabel.MATERIAL,
                name="Nickel",
                chunk_ids=["chunk_1"],
            ),
            Entity(
                entity_id="ent_001",
                label=EntityLabel.MATERIAL,
                name="Nickel",
                chunk_ids=["chunk_2"],
            ),
        ]
        graph = builder.build(entities, [])
        assert len(graph.nodes) == 1

    def test_build_with_hypothesis(self):
        builder = GraphBuilder()
        entities = [
            Entity(
                entity_id="ent_001",
                label=EntityLabel.MATERIAL,
                name="Nickel",
            ),
        ]
        hypothesis = HypothesisCard(
            title="Test Hypothesis",
            problem="Test",
            hypothesis="Test",
            supporting_nodes=["ent_001"],
        )
        graph = builder.build(
            entities=entities,
            relations=[],
            hypothesis=hypothesis,
        )
        assert len(graph.nodes) == 2
        hypothesis_nodes = [n for n in graph.nodes if n.label == "Hypothesis"]
        assert len(hypothesis_nodes) == 1
        assert hypothesis_nodes[0].name == "Test Hypothesis"

    def test_filter_out_unrelated_relations(self):
        builder = GraphBuilder()
        entities = [
            Entity(
                entity_id="ent_001",
                label=EntityLabel.MATERIAL,
                name="Nickel",
            ),
        ]
        relations = [
            Relation(
                relation_id="rel_001",
                source_id="ent_001",
                target_id="ent_999",
                relation_type=RelationType.CONTAINS,
            ),
        ]
        graph = builder.build(entities, relations)
        assert len(graph.edges) == 0

    def test_aggregate_relation_confidences(self):
        builder = GraphBuilder()
        ent_1 = Entity(
            entity_id="ent_001",
            label=EntityLabel.MATERIAL,
            name="Nickel",
        )
        ent_2 = Entity(
            entity_id="ent_002",
            label=EntityLabel.PROCESS,
            name="Smelting",
        )
        relations = [
            Relation(
                source_id="ent_001",
                target_id="ent_002",
                relation_type=RelationType.REQUIRES,
                confidence=0.7,
            ),
            Relation(
                source_id="ent_001",
                target_id="ent_002",
                relation_type=RelationType.INFLUENCES,
                confidence=0.9,
            ),
        ]
        graph = builder.build([ent_1, ent_2], relations)
        assert len(graph.edges) == 1
        assert graph.edges[0].confidence == 0.9
