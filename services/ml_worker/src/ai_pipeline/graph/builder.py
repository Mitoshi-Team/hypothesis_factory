from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ai_pipeline.state import HypothesisCard

from src.ai_pipeline.graph.graph_schema import (
    GraphEdge,
    GraphNode,
    KnowledgeGraph,
    SourceRef,
)
from src.models import Entity, Relation


class GraphBuilder:
    def build(
        self,
        entities: list[Entity],
        relations: list[Relation],
        hypothesis: Optional[HypothesisCard] = None,
        source_refs: Optional[dict[str, list[SourceRef]]] = None,
    ) -> KnowledgeGraph:
        nodes = self._build_nodes(entities, source_refs or {})
        edges = self._build_edges(relations, nodes)

        if hypothesis:
            hypothesis_node = GraphNode(
                id=f"hyp_{uuid.uuid4().hex[:8]}",
                label="Hypothesis",
                name=hypothesis.title,
                metadata={
                    "type": "hypothesis",
                    "hypothesis_text": hypothesis.hypothesis[:200],
                },
            )
            nodes.append(hypothesis_node)

            for node_id in hypothesis.supporting_nodes:
                if any(n.id == node_id for n in nodes):
                    edges.append(
                        GraphEdge(
                            source=hypothesis_node.id,
                            target=node_id,
                            relation="based_on",
                            confidence=1.0,
                            metadata={"evidence_type": "direct"},
                        )
                    )

        return KnowledgeGraph(nodes=nodes, edges=edges)

    def _build_nodes(
        self,
        entities: list[Entity],
        source_refs: dict[str, list[SourceRef]],
    ) -> list[GraphNode]:
        seen: dict[str, GraphNode] = {}

        for entity in entities:
            node_id = entity.entity_id
            if node_id in seen:
                existing = seen[node_id]
                for cid in entity.chunk_ids:
                    if cid not in existing.source_chunks:
                        for ref in source_refs.get(cid, []):
                            existing.source_chunks.append(ref)
                continue

            refs = []
            for cid in entity.chunk_ids:
                refs.extend(source_refs.get(cid, []))

            node = GraphNode(
                id=node_id,
                label=entity.label.value,
                name=entity.name,
                source_chunks=refs,
                metadata=entity.metadata,
            )
            seen[node_id] = node

        return list(seen.values())

    def _build_edges(
        self,
        relations: list[Relation],
        nodes: list[GraphNode],
    ) -> list[GraphEdge]:
        node_ids = {n.id for n in nodes}
        seen: dict[tuple[str, str], float] = {}
        edge_map: dict[tuple[str, str], list[str]] = {}

        for relation in relations:
            if (
                relation.source_id not in node_ids
                or relation.target_id not in node_ids
            ):
                continue
            key = (relation.source_id, relation.target_id)
            if key in seen:
                seen[key] = max(seen[key], relation.confidence)
            else:
                seen[key] = relation.confidence
                edge_map[key] = []
            edge_map[key].append(relation.relation_type.value)

        edges = []
        for (source, target), confidence in seen.items():
            types = edge_map.get((source, target), ["related"])
            edges.append(
                GraphEdge(
                    source=source,
                    target=target,
                    relation=types[0],
                    confidence=confidence,
                    metadata={"all_relations": types},
                )
            )

        return edges
