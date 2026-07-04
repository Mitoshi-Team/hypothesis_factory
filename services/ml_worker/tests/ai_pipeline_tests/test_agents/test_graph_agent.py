from __future__ import annotations

from src.ai_pipeline.agents.graph_agent import GraphAgent
from src.models import (
    ElementType,
    Entity,
    EntityLabel,
    Relation,
    RelationType,
    UnifiedDocument,
    UnifiedElement,
)


class TestGraphAgent:
    def test_build_empty_entities(self):
        agent = GraphAgent()
        graph = agent.build([], [])
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0
        assert len(graph.chains) == 0

    def test_build_single_chain(self):
        agent = GraphAgent()
        a = Entity(entity_id="e1", name="A", label=EntityLabel.MATERIAL)
        b = Entity(entity_id="e2", name="B", label=EntityLabel.PROCESS)
        c = Entity(entity_id="e3", name="C", label=EntityLabel.PROPERTY)
        relations = [
            Relation(
                source_id="e1",
                target_id="e2",
                relation_type=RelationType.INFLUENCES,
            ),
            Relation(
                source_id="e2",
                target_id="e3",
                relation_type=RelationType.PRODUCES,
            ),
        ]

        graph = agent.build([a, b, c], relations)
        assert len(graph.nodes) == 3
        assert len(graph.edges) == 2
        assert len(graph.chains) == 1
        assert graph.chains[0].node_ids == ["e1", "e2", "e3"]
        assert "influences" in graph.chains[0].summary
        assert "produces" in graph.chains[0].summary

    def test_build_multiple_chains(self):
        agent = GraphAgent()
        a = Entity(entity_id="e1", name="A", label=EntityLabel.MATERIAL)
        b = Entity(entity_id="e2", name="B", label=EntityLabel.PROCESS)
        x = Entity(entity_id="e3", name="X", label=EntityLabel.MATERIAL)
        y = Entity(entity_id="e4", name="Y", label=EntityLabel.PARAMETER)

        relations = [
            Relation(
                source_id="e1",
                target_id="e2",
                relation_type=RelationType.INFLUENCES,
            ),
            Relation(
                source_id="e3",
                target_id="e4",
                relation_type=RelationType.SIMILAR_TO,
            ),
        ]

        graph = agent.build([a, b, x, y], relations)
        assert len(graph.chains) == 2
        chain_ids = [c.node_ids for c in graph.chains]
        assert ["e1", "e2"] in chain_ids
        assert ["e3", "e4"] in chain_ids

    def test_build_with_branching(self):
        agent = GraphAgent()
        a = Entity(entity_id="e1", name="A", label=EntityLabel.MATERIAL)
        b = Entity(entity_id="e2", name="B", label=EntityLabel.PROCESS)
        c = Entity(entity_id="e3", name="C", label=EntityLabel.PROPERTY)

        relations = [
            Relation(
                source_id="e1",
                target_id="e2",
                relation_type=RelationType.INFLUENCES,
            ),
            Relation(
                source_id="e1",
                target_id="e3",
                relation_type=RelationType.PRODUCES,
            ),
        ]

        graph = agent.build([a, b, c], relations)
        # A branches to B and C → two chains
        assert len(graph.chains) == 2
        assert len(graph.edges) == 2

    def test_build_self_loop_ignored(self):
        agent = GraphAgent()
        a = Entity(entity_id="e1", name="A", label=EntityLabel.MATERIAL)
        relations = [
            Relation(
                source_id="e1",
                target_id="e1",
                relation_type=RelationType.SIMILAR_TO,
            ),
        ]

        graph = agent.build([a], relations)
        # Self-loop: no chain (len < 2), but edge exists
        assert len(graph.chains) == 0
        assert len(graph.nodes) == 1

    def test_build_unknown_entity_skipped(self):
        agent = GraphAgent()
        a = Entity(entity_id="e1", name="A", label=EntityLabel.MATERIAL)
        b = Entity(entity_id="e2", name="B", label=EntityLabel.PROCESS)
        relations = [
            Relation(
                source_id="e1",
                target_id="e2",
                relation_type=RelationType.INFLUENCES,
            ),
            Relation(
                source_id="e1",
                target_id="unknown",
                relation_type=RelationType.PRODUCES,
            ),
        ]

        graph = agent.build([a, b], relations)
        # Only valid relations should be included
        assert len(graph.edges) == 1
        assert len(graph.chains) == 1

    def test_build_to_json_includes_chains(self):
        agent = GraphAgent()
        a = Entity(entity_id="e1", name="A", label=EntityLabel.MATERIAL)
        b = Entity(entity_id="e2", name="B", label=EntityLabel.PROCESS)
        relations = [
            Relation(
                source_id="e1",
                target_id="e2",
                relation_type=RelationType.INFLUENCES,
            ),
        ]

        graph = agent.build([a, b], relations)
        j = graph.to_json()
        assert "chains" in j
        assert len(j["chains"]) == 1
        assert "node_ids" in j["chains"][0]
        assert "edge_labels" in j["chains"][0]

    def test_build_nodes_deduplicates(self):
        agent = GraphAgent()
        a1 = Entity(
            entity_id="e1",
            name="A",
            label=EntityLabel.MATERIAL,
            chunk_ids=["c1"],
        )
        a2 = Entity(
            entity_id="e1",
            name="A",
            label=EntityLabel.MATERIAL,
            chunk_ids=["c2"],
        )

        graph = agent._build_nodes([a1, a2], {}, None)
        assert len(graph) == 1
        assert len(graph[0].source_chunks) == 2

    def test_build_nodes_fill_source_text(self):
        agent = GraphAgent()
        element = UnifiedElement(
            element_id="el_1",
            type=ElementType.TEXT,
            text="Nickel improves strength",
            metadata={"section_path": "Introduction"},
        )
        document = UnifiedDocument(
            source_type="text",
            source_uri="/app/uploads/test.txt",
            title="Test Document",
            elements=[element],
        )
        entity = Entity(
            entity_id="e1",
            name="Nickel",
            label=EntityLabel.MATERIAL,
            chunk_ids=["el_1"],
        )

        graph = agent.build([entity], [], document=document)
        assert len(graph.nodes) == 1
        ref = graph.nodes[0].source_chunks[0]
        assert ref.chunk_id == "el_1"
        assert ref.element_id == "el_1"
        assert ref.text == "Nickel improves strength"
        assert ref.document_title == "Test Document"
        assert ref.section_path == "Introduction"
