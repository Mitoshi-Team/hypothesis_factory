from __future__ import annotations

from ai_pipeline.embeddings.yandex_embedder import YandexEmbedder


class TestYandexEmbedder:
    def test_embed_empty_list(self):
        embedder = YandexEmbedder(batch_size=2)
        result = embedder.embed([])
        assert result == []

    def test_embed_single_chunk(self, chroma_fx, llm_fx):
        embedder = YandexEmbedder(batch_size=2)
        mock_client = llm_fx.patch_client(
            embed_return=[llm_fx.mock_embedding(384)]
        )
        embedder.client = mock_client
        chunk = chroma_fx.make_chunk(text="Test content")
        result = embedder.embed([chunk])
        assert len(result) == 1
        assert result[0].embedding is not None
        assert len(result[0].embedding) == 384

    def test_batch_processing(self, chroma_fx, llm_fx):
        embedder = YandexEmbedder(batch_size=2)
        mock_client = llm_fx.patch_client(
            embed_return=[llm_fx.mock_embedding(384)] * 3
        )
        embedder.client = mock_client
        chunks = chroma_fx.make_chunks(3)
        result = embedder.embed(chunks)
        assert len(result) == 3
        for chunk in result:
            assert chunk.embedding is not None

    def test_embed_batch_boundary(self, chroma_fx, llm_fx):
        embedder = YandexEmbedder(batch_size=2)
        mock_client = llm_fx.patch_client(
            embed_return=[llm_fx.mock_embedding(384)] * 2
        )
        embedder.client = mock_client
        chunks = chroma_fx.make_chunks(2)
        result = embedder.embed(chunks)
        assert len(result) == 2

    def test_chunks_without_text_still_processed(self, chroma_fx, llm_fx):
        embedder = YandexEmbedder(batch_size=2)
        mock_client = llm_fx.patch_client(
            embed_return=[llm_fx.mock_embedding(384)] * 2
        )
        embedder.client = mock_client
        chunk1 = chroma_fx.make_chunk(text="Has text")
        chunk2 = chroma_fx.make_chunk(text="")
        result = embedder.embed([chunk1, chunk2])
        assert len(result) == 2
