from __future__ import annotations

from pydantic import BaseModel


class SourceRef(BaseModel):
    chunk_id: str = ""
    element_id: str = ""
    text: str = ""
    document_title: str = ""
    section_path: str = ""


class GraphNode(BaseModel):
    id: str = ""
    label: str = ""
    name: str = ""
    source_chunks: list[SourceRef] = []
    metadata: dict = {}


class GraphEdge(BaseModel):
    source: str = ""
    target: str = ""
    relation: str = ""
    confidence: float = 1.0
    metadata: dict = {}


class Chain(BaseModel):
    chain_id: str = ""
    node_ids: list[str] = []
    edge_labels: list[str] = []
    summary: str = ""


class KnowledgeGraph(BaseModel):
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []
    chains: list[Chain] = []

    def to_json(self) -> dict:
        return {
            "nodes": [n.model_dump() for n in self.nodes],
            "edges": [e.model_dump() for e in self.edges],
            "chains": [c.model_dump() for c in self.chains],
        }
