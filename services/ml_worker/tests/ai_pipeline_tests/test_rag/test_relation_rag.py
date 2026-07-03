from __future__ import annotations

from unittest.mock import MagicMock

from src.ai_pipeline.rag.relation_rag import RelationRAG
from src.models import Entity, EntityLabel, Relation, RelationType


class TestRelationRAG:
    def test_retrieve_empty_query(self):
        rag = RelationRAG()
        rag.store = MagicMock()
        rag.store.query_knowledge.return_value = []
        relations, context = rag.retrieve("")
        assert relations == []
        assert context == ""

    def test_retrieve_with_results(self, chroma_fx):
        rag = RelationRAG()
        mock_chunks = [
            chroma_fx.make_chunk(
                text="Nickel [influences] Strength — improves mechanical properties"
            ),
            chroma_fx.make_chunk(
                text="Temperature [requires] Cooling — high temp needs cooling"
            ),
        ]
        rag.store = MagicMock()
        rag.store.query_knowledge.return_value = mock_chunks

        relations, context = rag.retrieve("nickel strength")
        assert context != ""
        assert "Nickel" in context
        assert "influences" in context

    def test_index_relations_empty(self):
        rag = RelationRAG()
        rag.store = MagicMock()
        rag.index_relations([], [], "doc_1")

    def test_index_relations_calls_upsert(self):
        rag = RelationRAG()
        rag.embedder = MagicMock()
        rag.embedder.embed_texts.return_value = [[0.1] * 384]
        mock_collection = MagicMock()
        rag.store = MagicMock()
        rag.store._get_knowledge_collection.return_value = mock_collection

        entity = Entity(
            entity_id="ent_1", name="Nickel", label=EntityLabel.MATERIAL
        )
        relation = Relation(
            relation_id="rel_1",
            source_id="ent_1",
            target_id="ent_2",
            relation_type=RelationType.INFLUENCES,
            confidence=0.9,
            metadata={"evidence": "nickel improves strength"},
        )

        rag.index_relations([relation], [entity], "doc_1")
        mock_collection.upsert.assert_called_once()
        _, kwargs = mock_collection.upsert.call_args
        assert "rel_1" in kwargs["ids"]
        assert kwargs["metadatas"][0]["source_name"] == "Nickel"
        assert kwargs["metadatas"][0]["relation_type"] == "influences"

    def test_index_and_retrieve_roundtrip(self):
        rag = RelationRAG()
        rag.embedder = MagicMock()
        rag.embedder.embed_texts.return_value = [[0.1] * 384]

        rag.store = MagicMock()
        rag.store.query_knowledge.return_value = [
            MagicMock(
                chunk_id="c1",
                text="Nickel [produces] Alloy — produces alloy",
                metadata={"type": "relation"},
            )
        ]

        relations, context = rag.retrieve("nickel produces")
        assert context != ""
        assert "Nickel" in context

    def test_retrieve_with_custom_where(self, chroma_fx):
        rag = RelationRAG()
        mock_chunks = [
            chroma_fx.make_chunk(text="Test [contains] Data — test data"),
        ]
        rag.store = MagicMock()
        rag.store.query_knowledge.return_value = mock_chunks

        relations, context = rag.retrieve(
            "test", where={"document_id": "doc_test"}
        )
        assert context != ""
        assert "Test" in context

    def test_retrieve_by_document_empty(self):
        rag = RelationRAG()
        rag.store = MagicMock()
        rag.store.query_knowledge.return_value = []
        relations = rag.retrieve_by_document("")
        assert relations == []

    def test_retrieve_by_document_returns_relations(self, chroma_fx):
        rag = RelationRAG()
        rag.embedder = MagicMock()
        rag.embedder.embed_texts.return_value = [[0.1] * 384]

        entity = Entity(
            entity_id="ent_a", name="A", label=EntityLabel.MATERIAL
        )
        relation = Relation(
            relation_id="rel_doc",
            source_id="ent_a",
            target_id="ent_b",
            relation_type=RelationType.INFLUENCES,
        )
        rag.index_relations([relation], [entity], "doc_123")

        result = rag.retrieve_by_document("doc_123")
        assert len(result) >= 1
        assert result[0].source_id == "ent_a"
        assert result[0].relation_type == RelationType.INFLUENCES

    def test_index_chains_empty(self):
        rag = RelationRAG()
        rag.embedder = MagicMock()
        rag.embedder.embed_texts.return_value = [[0.1] * 384]
        mock_collection = MagicMock()
        rag.store = MagicMock()
        rag.store._get_knowledge_collection.return_value = mock_collection

        rag.index_chains([], "doc_1")
        mock_collection.upsert.assert_not_called()

    def test_index_chains_calls_upsert(self):
        rag = RelationRAG()
        rag.embedder = MagicMock()
        rag.embedder.embed_texts.return_value = [[0.1] * 384]
        mock_collection = MagicMock()
        rag.store = MagicMock()
        rag.store._get_knowledge_collection.return_value = mock_collection

        from src.ai_pipeline.graph.graph_schema import Chain

        chain = Chain(
            chain_id="ch_test",
            node_ids=["e1", "e2"],
            edge_labels=["influences"],
            summary="A → B",
        )

        rag.index_chains([chain], "doc_1")
        mock_collection.upsert.assert_called_once()
        _, kwargs = mock_collection.upsert.call_args
        assert "ch_test" in kwargs["ids"]
        assert kwargs["metadatas"][0]["type"] == "chain"
        assert kwargs["metadatas"][0]["document_id"] == "doc_1"
