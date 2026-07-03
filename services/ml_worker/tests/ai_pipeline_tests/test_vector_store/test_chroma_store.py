from __future__ import annotations

from unittest.mock import patch

from ai_pipeline.vector_store.chroma_store import ChromaStore


class TestChromaStore:
    def test_populate_and_query_knowledge(self, chroma_fx):
        store = ChromaStore()
        with patch.object(
            store,
            "_get_knowledge_collection",
            return_value=chroma_fx.ephemeral_client().get_or_create_collection(
                "knowledge"
            ),
        ):
            chunks = chroma_fx.make_chunks(3)
            store.populate_knowledge(chunks)
            results = store.query_knowledge("test", n_results=3)
            assert len(results) > 0

    def test_populate_history(self, chroma_fx):
        store = ChromaStore()
        with patch.object(
            store,
            "_get_history_collection",
            return_value=chroma_fx.ephemeral_client().get_or_create_collection(
                "hypothesis_history"
            ),
        ):
            entries = [chroma_fx.make_history_entry("Test 1")]
            store.populate_history(entries)

    def test_query_knowledge_empty(self, chroma_fx):
        store = ChromaStore()
        with patch.object(
            store,
            "_get_knowledge_collection",
            return_value=chroma_fx.ephemeral_client().get_or_create_collection(
                "empty"
            ),
        ):
            results = store.query_knowledge("nothing", n_results=5)
            assert isinstance(results, list)

    def test_populate_knowledge_empty_list(self, chroma_fx):
        store = ChromaStore()
        store.populate_knowledge([])

    def test_chunks_without_embedding_skipped(self, chroma_fx):
        store = ChromaStore()
        with patch.object(
            store,
            "_get_knowledge_collection",
            return_value=chroma_fx.ephemeral_client().get_or_create_collection(
                "knowledge_skip"
            ),
        ):
            chunk = chroma_fx.make_chunk(text="No embedding")
            chunk.embedding = None
            store.populate_knowledge([chunk])

    def test_history_entry_with_all_fields(self, chroma_fx):
        store = ChromaStore()
        with patch.object(
            store,
            "_get_history_collection",
            return_value=chroma_fx.ephemeral_client().get_or_create_collection(
                "history_full"
            ),
        ):
            entry = chroma_fx.make_history_entry(
                hypothesis_text="Full test",
                verdict="reject",
                is_positive=False,
            )
            store.populate_history([entry])
