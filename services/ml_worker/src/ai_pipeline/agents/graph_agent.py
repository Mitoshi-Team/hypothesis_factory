from __future__ import annotations

import uuid
from collections import deque
from typing import Optional

from src.ai_pipeline.graph.graph_schema import (
    Chain,
    GraphEdge,
    GraphNode,
    KnowledgeGraph,
    SourceRef,
)
from src.models import Entity, Relation


class GraphAgent:
    def build(
        self,
        entities: list[Entity],
        relations: list[Relation],
        hypothesis_id: Optional[str] = None,
    ) -> KnowledgeGraph:
        if not entities:
            return KnowledgeGraph()

        entity_map = {e.entity_id: e for e in entities}
        nodes = self._build_nodes(entities)

        adj, reverse_adj = self._build_adjacency(relations, entity_map)
        undirected_adj = self._build_undirected_adjacency(
            relations, entity_map
        )
        node_ids = {e.entity_id for e in entities}

        components = self._find_components(node_ids, undirected_adj)

        edges: list[GraphEdge] = []
        chains: list[Chain] = []
        edge_keys: set[tuple[str, str]] = set()

        for comp_nodes in components:
            comp_edges = self._collect_edges(
                comp_nodes, adj, reverse_adj, relations, edge_keys
            )
            edges.extend(comp_edges)

            comp_chains = self._find_chains(comp_nodes, adj, reverse_adj)
            chains.extend(comp_chains)

        if hypothesis_id:
            hyp_node = self._build_hypothesis_node(hypothesis_id)
            nodes.append(hyp_node)

        return KnowledgeGraph(nodes=nodes, edges=edges, chains=chains)

    def _build_nodes(self, entities: list[Entity]) -> list[GraphNode]:
        seen: dict[str, GraphNode] = {}
        for entity in entities:
            if entity.entity_id in seen:
                existing = seen[entity.entity_id]
                for cid in entity.chunk_ids:
                    if cid not in existing.source_chunks:
                        existing.source_chunks.append(SourceRef(chunk_id=cid))
                continue
            node = GraphNode(
                id=entity.entity_id,
                label=entity.label.value,
                name=entity.name,
                source_chunks=[
                    SourceRef(chunk_id=cid) for cid in entity.chunk_ids
                ],
                metadata=entity.metadata,
            )
            seen[entity.entity_id] = node
        return list(seen.values())

    def _build_adjacency(
        self,
        relations: list[Relation],
        entity_map: dict[str, Entity],
    ) -> tuple[
        dict[str, list[tuple[str, str, float]]],
        dict[str, list[tuple[str, str, float]]],
    ]:
        adj: dict[str, list[tuple[str, str, float]]] = {}
        reverse_adj: dict[str, list[tuple[str, str, float]]] = {}

        for rel in relations:
            if rel.source_id not in entity_map:
                continue
            if rel.target_id not in entity_map:
                continue
            if rel.source_id not in adj:
                adj[rel.source_id] = []
            if rel.target_id not in reverse_adj:
                reverse_adj[rel.target_id] = []
            adj[rel.source_id].append(
                (rel.target_id, rel.relation_type.value, rel.confidence)
            )
            reverse_adj[rel.target_id].append(
                (rel.source_id, rel.relation_type.value, rel.confidence)
            )

        return adj, reverse_adj

    def _build_undirected_adjacency(
        self,
        relations: list[Relation],
        entity_map: dict[str, Entity],
    ) -> dict[str, set[str]]:
        undirected: dict[str, set[str]] = {}
        for rel in relations:
            if rel.source_id not in entity_map:
                continue
            if rel.target_id not in entity_map:
                continue
            if rel.source_id not in undirected:
                undirected[rel.source_id] = set()
            if rel.target_id not in undirected:
                undirected[rel.target_id] = set()
            undirected[rel.source_id].add(rel.target_id)
            undirected[rel.target_id].add(rel.source_id)
        return undirected

    def _find_components(
        self,
        node_ids: set[str],
        undirected_adj: dict[str, set[str]],
    ) -> list[set[str]]:
        visited: set[str] = set()
        components: list[set[str]] = []

        for nid in node_ids:
            if nid in visited:
                continue
            component: set[str] = set()
            queue = deque([nid])
            while queue:
                cur = queue.popleft()
                if cur in visited:
                    continue
                visited.add(cur)
                component.add(cur)
                for neighbor in undirected_adj.get(cur, set()):
                    if neighbor not in visited:
                        queue.append(neighbor)
            components.append(component)

        return components

    def _collect_edges(
        self,
        comp_nodes: set[str],
        adj: dict[str, list[tuple[str, str, float]]],
        reverse_adj: dict[str, list[tuple[str, str, float]]],
        relations: list[Relation],
        edge_keys: set[tuple[str, str]],
    ) -> list[GraphEdge]:
        edges: list[GraphEdge] = []
        for rel in relations:
            if rel.source_id not in comp_nodes:
                continue
            if rel.target_id not in comp_nodes:
                continue
            key = (rel.source_id, rel.target_id)
            if key in edge_keys:
                continue
            edge_keys.add(key)
            edges.append(
                GraphEdge(
                    source=rel.source_id,
                    target=rel.target_id,
                    relation=rel.relation_type.value,
                    confidence=rel.confidence,
                    metadata={"evidence": rel.metadata.get("evidence", "")},
                )
            )
        return edges

    def _find_chains(
        self,
        comp_nodes: set[str],
        adj: dict[str, list[tuple[str, str, float]]],
        reverse_adj: dict[str, list[tuple[str, str, float]]],
    ) -> list[Chain]:
        if not comp_nodes:
            return []

        sources = self._find_source_nodes(comp_nodes, adj, reverse_adj)

        all_paths: list[list[str]] = []
        for src in sources:
            paths = self._dfs_all_paths(src, adj, comp_nodes, set())
            all_paths.extend(paths)

        if not all_paths:
            all_paths = [[n] for n in comp_nodes]

        return self._build_chains(all_paths, adj)

    def _find_source_nodes(
        self,
        comp_nodes: set[str],
        adj: dict[str, list[tuple[str, str, float]]],
        reverse_adj: dict[str, list[tuple[str, str, float]]],
    ) -> list[str]:
        in_degree = {n: 0 for n in comp_nodes}
        for n in comp_nodes:
            for src, _, _ in reverse_adj.get(n, []):
                if src in comp_nodes:
                    in_degree[n] = in_degree.get(n, 0) + 1

        out_degree = {n: 0 for n in comp_nodes}
        for n in comp_nodes:
            for tgt, _, _ in adj.get(n, []):
                if tgt in comp_nodes:
                    out_degree[n] = out_degree.get(n, 0) + 1

        sources = [n for n in comp_nodes if in_degree.get(n, 0) == 0]
        if not sources:
            sources = [n for n in comp_nodes if out_degree.get(n, 0) > 0]
        if not sources:
            sources = [next(iter(comp_nodes))]
        return sources

    def _build_chains(
        self,
        paths: list[list[str]],
        adj: dict[str, list[tuple[str, str, float]]],
    ) -> list[Chain]:
        chains: list[Chain] = []
        for path in paths:
            if len(path) < 2:
                continue
            edge_labels: list[str] = []
            for i in range(len(path) - 1):
                src_id = path[i]
                tgt_id = path[i + 1]
                edges_out = adj.get(src_id, [])
                matched = [r for r in edges_out if r[0] == tgt_id]
                if matched:
                    edge_labels.append(matched[0][1])
                else:
                    edge_labels.append("related")
            cid = f"ch_{uuid.uuid4().hex[:8]}"
            chains.append(
                Chain(
                    chain_id=cid,
                    node_ids=path,
                    edge_labels=edge_labels,
                    summary=" → ".join(edge_labels),
                )
            )
        return chains

    def _dfs_all_paths(
        self,
        current: str,
        adj: dict[str, list[tuple[str, str, float]]],
        comp_nodes: set[str],
        visited: set[str],
    ) -> list[list[str]]:
        new_visited = visited | {current}
        neighbors = [
            (tgt, rel, conf)
            for tgt, rel, conf in adj.get(current, [])
            if tgt in comp_nodes and tgt not in new_visited
        ]

        if not neighbors:
            return [[current]]

        all_paths: list[list[str]] = []
        for tgt, _, _ in neighbors:
            sub_paths = self._dfs_all_paths(tgt, adj, comp_nodes, new_visited)
            for sub in sub_paths:
                all_paths.append([current] + sub)

        return all_paths

    def _build_hypothesis_node(self, hypothesis_id: str) -> GraphNode:
        return GraphNode(
            id=hypothesis_id,
            label="Hypothesis",
            name=hypothesis_id,
            metadata={"type": "hypothesis"},
        )
