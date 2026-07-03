from __future__ import annotations

from src.ai_pipeline.vector_store.chroma_store import ChromaStore
from src.models import Chunk


class KnowledgeRAG:
    def __init__(self) -> None:
        self.store = ChromaStore()

    def retrieve(
        self,
        query: str,
        n_results: int = 0,
    ) -> tuple[list[Chunk], str]:
        chunks = self.store.query_knowledge(
            query_text=query,
            n_results=n_results,
            where={"type": "chunk"},
        )

        context = self._format_context(chunks)

        return chunks, context

    def _format_context(self, chunks: list[Chunk]) -> str:
        if not chunks:
            return ""

        sections: dict[str, list[str]] = {}
        for chunk in chunks:
            section = chunk.metadata.get("section_path", "general")
            if section not in sections:
                sections[section] = []
            sections[section].append(chunk.text)

        parts = []
        for section, texts in sections.items():
            section_block = f"## {section}\n"
            section_block += "\n\n".join(texts)
            parts.append(section_block)

        return "\n\n---\n\n".join(parts)
