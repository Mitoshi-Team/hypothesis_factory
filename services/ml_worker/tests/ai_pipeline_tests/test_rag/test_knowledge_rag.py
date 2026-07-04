from __future__ import annotations

from unittest.mock import patch

from src.ai_pipeline.rag.knowledge_rag import KnowledgeRAG


class TestKnowledgeRAG:
    def test_retrieve_empty_query(self):
        rag = KnowledgeRAG()
        chunks, context = rag.retrieve("")
        assert len(chunks) == 0
        assert context == ""

    def test_format_context_with_chunks(self, chroma_fx):
        rag = KnowledgeRAG()
        chunks = chroma_fx.make_chunks(3)
        context = rag._format_context(chunks)
        assert "Chunk" in context
        assert "section_" in context

    def test_format_context_empty(self):
        rag = KnowledgeRAG()
        context = rag._format_context([])
        assert context == ""

    def test_context_groups_by_section(self, chroma_fx):
        rag = KnowledgeRAG()
        doc_id = chroma_fx.make_chunk().document_id
        chunks = [
            chroma_fx.make_chunk(
                text="Intro text",
                document_id=doc_id,
                section_path="Introduction",
            ),
            chroma_fx.make_chunk(
                text="Method text",
                document_id=doc_id,
                section_path="Methods",
            ),
            chroma_fx.make_chunk(
                text="More intro",
                document_id=doc_id,
                section_path="Introduction",
            ),
        ]
        context = rag._format_context(chunks)
        assert "Introduction" in context
        assert "Methods" in context
        assert "Intro text" in context
        assert "More intro" in context

    def test_retrieve_with_mocked_store(self, chroma_fx):
        rag = KnowledgeRAG()
        expected_chunks = chroma_fx.make_chunks(2)
        with patch.object(
            rag.store, "query_knowledge", return_value=expected_chunks
        ):
            chunks, context = rag.retrieve("test problem")
            assert len(chunks) == 2
            assert "Chunk" in context
