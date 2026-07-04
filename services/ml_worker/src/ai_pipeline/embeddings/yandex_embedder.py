from __future__ import annotations

from src.ai_pipeline.clients.yandex_ai_studio import YandexAIStudioClient
from src.config import settings
from src.models import Chunk


class YandexEmbedder:
    def __init__(
        self,
        batch_size: int = 0,
    ) -> None:
        self.client = YandexAIStudioClient()
        self.batch_size = batch_size or settings.embed_batch_size

    def embed(self, chunks: list[Chunk]) -> list[Chunk]:
        if not chunks:
            return chunks

        texts = [chunk.text for chunk in chunks]
        all_embeddings = self.embed_texts(texts)

        for chunk, embedding in zip(chunks, all_embeddings):
            chunk.embedding = embedding

        return chunks

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        all_embeddings: list[list[float]] = []

        for text in texts:
            embedding = self.client.embed([text])
            all_embeddings.append(embedding[0])

        return all_embeddings
