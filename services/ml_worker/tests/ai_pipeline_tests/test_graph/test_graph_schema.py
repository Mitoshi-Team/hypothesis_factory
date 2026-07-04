from __future__ import annotations

from src.ai_pipeline.graph.graph_schema import (
    GraphEdge,
    GraphNode,
    KnowledgeGraph,
    SourceRef,
)


class TestGraphSchema:
    def test_graph_node_creation(self):
        node = GraphNode(
            id="ent_001",
            label="Material",
            name="Nickel",
        )
        assert node.id == "ent_001"
        assert node.label == "Material"
        assert node.name == "Nickel"

    def test_graph_node_with_sources(self):
        source = SourceRef(
            chunk_id="chunk_001",
            element_id="el_001",
            text="Nickel is a metal",
            document_title="Materials Guide",
            section_path="Introduction",
        )
        node = GraphNode(
            id="ent_001",
            label="Material",
            name="Nickel",
            source_chunks=[source],
        )
        assert len(node.source_chunks) == 1
        assert node.source_chunks[0].text == "Nickel is a metal"

    def test_graph_edge_creation(self):
        edge = GraphEdge(
            source="ent_001",
            target="ent_002",
            relation="influences",
            confidence=0.85,
        )
        assert edge.source == "ent_001"
        assert edge.target == "ent_002"
        assert edge.relation == "influences"
        assert edge.confidence == 0.85

    def test_knowledge_graph_empty(self):
        kg = KnowledgeGraph()
        assert len(kg.nodes) == 0
        assert len(kg.edges) == 0

    def test_knowledge_graph_to_json(self):
        kg = KnowledgeGraph(
            nodes=[
                GraphNode(id="n1", label="Material", name="Nickel"),
                GraphNode(id="n2", label="Process", name="Smelting"),
            ],
            edges=[
                GraphEdge(
                    source="n1",
                    target="n2",
                    relation="requires",
                ),
            ],
        )
        json_data = kg.to_json()
        assert "nodes" in json_data
        assert "edges" in json_data
        assert len(json_data["nodes"]) == 2
        assert len(json_data["edges"]) == 1

    def test_source_ref_serialization(self):
        ref = SourceRef(
            chunk_id="chunk_001",
            element_id="el_001",
            text="Some text",
            document_title="Doc",
            section_path="root",
        )
        data = ref.model_dump()
        assert data["chunk_id"] == "chunk_001"
        assert data["text"] == "Some text"
