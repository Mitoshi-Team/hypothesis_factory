from __future__ import annotations

from src.ai_pipeline.chunking.hybrid_chunker import HybridChunker
from src.models import ElementType


class TestHybridChunker:
    def test_empty_document(self, chunk_fx):
        chunker = HybridChunker(chunk_size=100, chunk_overlap=20)
        doc = chunk_fx.make_document(elements=[])
        chunks = chunker.chunk(doc)
        assert len(chunks) == 0

    def test_single_element(self, chunk_fx):
        chunker = HybridChunker(chunk_size=100, chunk_overlap=20)
        doc = chunk_fx.make_document(elements=[chunk_fx.make_text()])
        chunks = chunker.chunk(doc)
        assert len(chunks) >= 1
        assert chunks[0].document_id == doc.document_id

    def test_section_split_by_titles(self, chunk_fx):
        chunker = HybridChunker(chunk_size=500, chunk_overlap=20)
        doc = chunk_fx.make_structured_document()
        chunks = chunker.chunk(doc)
        assert len(chunks) >= 1
        section_paths = [c.metadata.get("section_path", "") for c in chunks]
        assert any("Introduction" in s for s in section_paths)
        assert any("Methods" in s for s in section_paths)
        assert any("Conclusion" in s for s in section_paths)

    def test_section_path_in_metadata(self, chunk_fx):
        chunker = HybridChunker(chunk_size=500, chunk_overlap=20)
        doc = chunk_fx.make_document(
            elements=[
                chunk_fx.make_title("Section 1", level=1),
                chunk_fx.make_text("Content under section 1."),
                chunk_fx.make_title("Section 2", level=1),
                chunk_fx.make_text("Content under section 2."),
            ]
        )
        chunks = chunker.chunk(doc)
        paths = {c.metadata.get("section_path") for c in chunks}
        assert "Section 1" in paths or any(
            "Section 1" in str(p) for p in paths
        )

    def test_structural_elements_skipped(self, chunk_fx):
        chunker = HybridChunker(chunk_size=100, chunk_overlap=20)
        doc = chunk_fx.make_document(
            elements=[
                chunk_fx.make_element(
                    element_type=ElementType.HEADER,
                    text="Header text",
                ),
                chunk_fx.make_element(
                    element_type=ElementType.FOOTER,
                    text="Footer text",
                ),
                chunk_fx.make_text("Actual content"),
            ]
        )
        chunks = chunker.chunk(doc)
        assert len(chunks) >= 1
        for chunk in chunks:
            assert "Header text" not in chunk.text or len(chunk.text) == 0

    def test_large_text_recursive_split(self, chunk_fx):
        chunker = HybridChunker(chunk_size=50, chunk_overlap=10)
        long_text = "Paragraph one. " * 20
        doc = chunk_fx.make_document(
            elements=[
                chunk_fx.make_text(long_text),
            ]
        )
        chunks = chunker.chunk(doc)
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk.text) <= 70

    def test_table_embedding_payload(self, chunk_fx):
        chunker = HybridChunker(chunk_size=500, chunk_overlap=20)
        table_el = chunk_fx.make_table(caption="Test Results", rows=2, cols=2)
        doc = chunk_fx.make_document(elements=[table_el])
        chunks = chunker.chunk(doc)
        assert len(chunks) >= 1

    def test_chunk_metadata(self, chunk_fx):
        chunker = HybridChunker(chunk_size=200, chunk_overlap=20)
        doc = chunk_fx.make_document(
            elements=[chunk_fx.make_text()],
            source_type=chunk_fx.make_text().source_type,
        )
        chunks = chunker.chunk(doc)
        chunk = chunks[0]
        assert chunk.document_id == doc.document_id
        assert "source_type" in chunk.metadata
        assert "section_path" in chunk.metadata

    def test_element_ids_preserved(self, chunk_fx):
        chunker = HybridChunker(chunk_size=100, chunk_overlap=20)
        el = chunk_fx.make_text()
        doc = chunk_fx.make_document(elements=[el])
        chunks = chunker.chunk(doc)
        assert el.element_id in chunks[0].element_ids
