from __future__ import annotations

from typing import Any, Optional

from src.ai_pipeline.embeddings.yandex_embedder import YandexEmbedder
from src.ai_pipeline.graph.graph_schema import Chain
from src.ai_pipeline.vector_store.chroma_store import ChromaStore
from src.models import Entity, Relation, RelationType


class RelationRAG:
    def __init__(self) -> None:
        self.store = ChromaStore()
        self.embedder = YandexEmbedder()

    def index_relations(
        self,
        relations: list[Relation],
        entities: list[Entity],
        document_id: str,
    ) -> None:
        if not relations:
            return

        entity_id_to_name = {e.entity_id: e.name for e in entities}

        documents = []
        ids = []
        metadatas_list: list[dict[str, Any]] = []

        for rel in relations:
            source_name = entity_id_to_name.get(rel.source_id, rel.source_id)
            target_name = entity_id_to_name.get(rel.target_id, rel.target_id)
            text = f"{source_name} [{rel.relation_type.value}] {target_name}"
            if rel.metadata.get("evidence"):
                text += f" — {rel.metadata['evidence']}"

            documents.append(text)
            ids.append(rel.relation_id)
            metadatas_list.append(
                {
                    "type": "relation",
                    "source_id": rel.source_id,
                    "source_name": source_name,
                    "target_id": rel.target_id,
                    "target_name": target_name,
                    "relation_type": rel.relation_type.value,
                    "document_id": document_id,
                    "confidence": rel.confidence,
                    "evidence": rel.metadata.get("evidence", ""),
                }
            )

        embeddings = self.embedder.embed_texts(documents)

        collection = self.store._get_knowledge_collection()
        collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas_list,
        )

    def retrieve(
        self,
        query: str,
        n_results: int = 0,
        where: Optional[dict[str, Any]] = None,
    ) -> tuple[list[Relation], str]:
        if where:
            base_where = {"$and": [{"type": "relation"}, where]}
        else:
            base_where = {"type": "relation"}

        chunks = self.store.query_knowledge(
            query_text=query,
            n_results=n_results,
            where=base_where,
        )

        if not chunks:
            return [], ""

        relations = self._chunks_to_relations(chunks)

        context_lines = []
        for chunk in chunks:
            context_lines.append(chunk.text)

        context = "\n".join(context_lines)
        return relations, context

    def retrieve_by_document(
        self,
        document_id: str,
    ) -> list[Relation]:
        if not document_id:
            return []
        relations, _ = self.retrieve(
            query="",
            n_results=1000,
            where={"document_id": document_id},
        )
        return relations

    def index_chains(
        self,
        chains: list[Chain],
        document_id: str,
    ) -> None:
        if not chains:
            return

        documents = []
        ids = []
        metadatas_list: list[dict[str, Any]] = []

        for chain in chains:
            documents.append(chain.summary)
            ids.append(chain.chain_id)
            metadatas_list.append(
                {
                    "type": "chain",
                    "document_id": document_id,
                    "chain_id": chain.chain_id,
                    "node_ids": ",".join(chain.node_ids),
                    "edge_labels": ",".join(chain.edge_labels),
                    "summary": chain.summary,
                }
            )

        embeddings = self.embedder.embed_texts(documents)

        collection = self.store._get_knowledge_collection()
        collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas_list,
        )

    def _chunks_to_relations(self, chunks: list) -> list[Relation]:
        relation_type_map = {
            "influences": RelationType.INFLUENCES,
            "produces": RelationType.PRODUCES,
            "requires": RelationType.REQUIRES,
            "part_of": RelationType.PART_OF,
            "contains": RelationType.CONTAINS,
            "similar_to": RelationType.SIMILAR_TO,
            "cites": RelationType.CITES,
        }

        relations: list[Relation] = []
        for chunk in chunks:
            meta = chunk.metadata
            if meta.get("type") != "relation":
                continue
            rel_type = relation_type_map.get(
                meta.get("relation_type", ""), RelationType.CONTAINS
            )
            relations.append(
                Relation(
                    relation_id=chunk.chunk_id,
                    source_id=meta.get("source_id", ""),
                    target_id=meta.get("target_id", ""),
                    relation_type=rel_type,
                    confidence=float(meta.get("confidence", 0.5)),
                    chunk_ids=[],
                    metadata={
                        "evidence": meta.get("evidence", ""),
                        "source_name": meta.get("source_name", ""),
                        "target_name": meta.get("target_name", ""),
                    },
                )
            )
        return relations
