from __future__ import annotations

import uuid
from typing import Any, Optional

import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.config import Settings as ChromaSettings
from src.config import settings
from src.models import Chunk


class ChromaStore:
    def __init__(self, embedder: Optional[Any] = None) -> None:
        self._client: Optional[chromadb.Client] = None
        self._knowledge_collection: Optional[Collection] = None
        self._history_collection: Optional[Collection] = None
        self._embedder = embedder

    def _get_client(self) -> chromadb.Client:
        if self._client is None:
            try:
                self._client = chromadb.HttpClient(
                    host=settings.chroma_host,
                    port=settings.chroma_port,
                )
            except Exception:
                self._client = chromadb.EphemeralClient(ChromaSettings())
        return self._client

    def _embed_query(self, query_text: str) -> list[float]:
        if self._embedder is None:
            raise RuntimeError("Embedder is required for query")
        embeddings = self._embedder.embed_texts([query_text])
        return embeddings[0]

    def _get_knowledge_collection(self) -> Collection:
        if self._knowledge_collection is None:
            client = self._get_client()
            self._knowledge_collection = client.get_or_create_collection(
                name=settings.chroma_collection_knowledge,
                metadata={"hnsw:space": "cosine"},
            )
        return self._knowledge_collection

    def _get_history_collection(self) -> Collection:
        if self._history_collection is None:
            client = self._get_client()
            self._history_collection = client.get_or_create_collection(
                name=settings.chroma_collection_history,
                metadata={"hnsw:space": "cosine"},
            )
        return self._history_collection

    def populate_knowledge(
        self,
        chunks: list[Chunk],
        session_id: str = "",
    ) -> None:
        collection = self._get_knowledge_collection()
        if not chunks:
            return

        ids = []
        embeddings = []
        documents = []
        metadatas = []

        for chunk in chunks:
            if not chunk.embedding:
                continue
            ids.append(chunk.chunk_id)
            embeddings.append(chunk.embedding)
            documents.append(chunk.text)
            meta = dict(chunk.metadata)
            meta["type"] = "chunk"
            meta["document_id"] = chunk.document_id
            meta["session_id"] = session_id
            meta["element_ids"] = ",".join(chunk.element_ids)
            metadatas.append(meta)

        if ids:
            collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )

    def query_knowledge(
        self,
        query_text: str,
        n_results: int = 0,
        where: Optional[dict[str, Any]] = None,
        session_id: str = "",
    ) -> list[Chunk]:
        collection = self._get_knowledge_collection()
        n = n_results or settings.top_k_rag

        conditions: list[dict[str, Any]] = [{"type": "chunk"}]
        if session_id:
            conditions.append({"session_id": session_id})
        if where:
            conditions.append(where)

        base_where: dict[str, Any]
        if len(conditions) == 1:
            base_where = conditions[0]
        else:
            base_where = {"$and": conditions}

        kwargs: dict[str, Any] = {"n_results": n, "where": base_where}
        if self._embedder is not None and query_text:
            kwargs["query_embeddings"] = [self._embed_query(query_text)]
        else:
            kwargs["query_texts"] = [query_text or " "]

        results = collection.query(**kwargs)

        return self._results_to_chunks(results)

    def get_knowledge_by_filter(
        self,
        where: dict[str, Any],
        limit: int = 1000,
    ) -> list[Chunk]:
        collection = self._get_knowledge_collection()
        results = collection.get(
            where=where,
            limit=limit,
            include=["metadatas", "documents"],
        )
        return self._get_results_to_chunks(results)

    def populate_history(self, entries: list[dict[str, Any]]) -> None:
        collection = self._get_history_collection()
        if not entries:
            return

        ids = []
        embeddings = []
        documents = []
        metadatas = []

        for entry in entries:
            entry_id = entry.get("entry_id", f"hist_{uuid.uuid4().hex[:8]}")
            ids.append(entry_id)
            embeddings.append(entry.get("embedding", []))
            documents.append(entry.get("hypothesis_text", ""))
            meta = {
                "problem": entry.get("problem", ""),
                "verdict": entry.get("verdict", ""),
                "is_positive_example": entry.get("is_positive_example", False),
                "scores": str(entry.get("scores", {})),
                "review_comment": entry.get("review_comment", ""),
                "user_feedback": entry.get("user_feedback", "") or "",
                "user_id": entry.get("user_id", ""),
            }
            metadatas.append(meta)

        embedding_list = [e for e in embeddings if e]
        if not embedding_list:
            return

        collection.upsert(
            ids=ids,
            embeddings=embedding_list,
            documents=documents,
            metadatas=metadatas,
        )

    def query_history(
        self,
        query_text: str,
        n_results: int = 0,
        where: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        collection = self._get_history_collection()
        n = n_results or settings.top_k_history

        kwargs: dict[str, Any] = {"n_results": n, "where": where}
        if self._embedder is not None:
            kwargs["query_embeddings"] = [self._embed_query(query_text)]
        else:
            kwargs["query_texts"] = [query_text]

        results = collection.query(**kwargs)

        entries = []
        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for i in range(len(ids)):
            entries.append(
                {
                    "entry_id": ids[i],
                    "hypothesis_text": documents[i]
                    if i < len(documents)
                    else "",
                    "metadata": metadatas[i] if i < len(metadatas) else {},
                    "distance": distances[i] if i < len(distances) else 0.0,
                }
            )

        return entries

    def _results_to_chunks(self, results: dict) -> list[Chunk]:
        chunks = []
        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas_list = results.get("metadatas", [[]])[0]

        for i in range(len(ids)):
            meta = metadatas_list[i] if i < len(metadatas_list) else {}
            element_ids_str = meta.pop("element_ids", "")
            chunks.append(
                Chunk(
                    chunk_id=ids[i],
                    document_id=meta.pop("document_id", ""),
                    element_ids=element_ids_str.split(",")
                    if element_ids_str
                    else [],
                    text=documents[i] if i < len(documents) else "",
                    metadata=meta,
                )
            )

        return chunks

    def _get_results_to_chunks(self, results: dict) -> list[Chunk]:
        chunks = []
        ids = results.get("ids", [])
        documents = results.get("documents", [])
        metadatas_list = results.get("metadatas", [])

        for i in range(len(ids)):
            meta = metadatas_list[i] if i < len(metadatas_list) else {}
            element_ids_str = meta.pop("element_ids", "")
            chunks.append(
                Chunk(
                    chunk_id=ids[i],
                    document_id=meta.pop("document_id", ""),
                    element_ids=element_ids_str.split(",")
                    if element_ids_str
                    else [],
                    text=documents[i] if i < len(documents) else "",
                    metadata=meta,
                )
            )

        return chunks
