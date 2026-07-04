from __future__ import annotations

import uuid

from src.config import settings
from src.models import Chunk, ElementType, UnifiedDocument, UnifiedElement


class HybridChunker:
    def __init__(
        self,
        chunk_size: int = 0,
        chunk_overlap: int = 0,
    ) -> None:
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap

    def chunk(self, document: UnifiedDocument) -> list[Chunk]:
        elements = document.elements
        sections = self._split_by_sections(elements)
        chunks: list[Chunk] = []

        for section_path, section_elements in sections:
            text = self._merge_elements(section_elements)
            section_chunks = self._recursive_split(
                text=text,
                document_id=document.document_id,
                element_ids=[el.element_id for el in section_elements],
                section_path=section_path,
                source_type=document.source_type.value,
            )
            chunks.extend(section_chunks)

        return chunks

    def _split_by_sections(
        self,
        elements: list[UnifiedElement],
    ) -> list[tuple[str, list[UnifiedElement]]]:
        sections: list[tuple[str, list[UnifiedElement]]] = []
        current_section_path: list[str] = []
        current_elements: list[UnifiedElement] = []

        for el in elements:
            if el.type == ElementType.TITLE:
                if current_elements:
                    path = (
                        " > ".join(current_section_path)
                        if current_section_path
                        else "root"
                    )
                    sections.append((path, current_elements))
                    current_elements = []

                title_text = el.text.strip()
                level = el.level or 1
                while len(current_section_path) >= level:
                    current_section_path.pop()
                current_section_path.append(title_text)

            if not el.is_structural():
                current_elements.append(el)

        if current_elements:
            path = (
                " > ".join(current_section_path)
                if current_section_path
                else "root"
            )
            sections.append((path, current_elements))

        return sections

    def _merge_elements(self, elements: list[UnifiedElement]) -> str:
        parts: list[str] = []
        for el in elements:
            text = el.embedding_payload
            if text:
                parts.append(text)
        return "\n\n".join(parts)

    def _recursive_split(
        self,
        text: str,
        document_id: str,
        element_ids: list[str],
        section_path: str,
        source_type: str,
    ) -> list[Chunk]:
        if not text.strip():
            return []

        if len(text) <= self.chunk_size:
            return [
                Chunk(
                    chunk_id=f"chunk_{uuid.uuid4().hex[:8]}",
                    document_id=document_id,
                    element_ids=element_ids,
                    text=text.strip(),
                    metadata={
                        "section_path": section_path,
                        "source_type": source_type,
                    },
                )
            ]

        chunks: list[Chunk] = []
        separators = ["\n\n", "\n", ". ", " "]
        remaining = text

        while remaining:
            if len(remaining) <= self.chunk_size:
                chunks.append(
                    Chunk(
                        chunk_id=f"chunk_{uuid.uuid4().hex[:8]}",
                        document_id=document_id,
                        element_ids=element_ids,
                        text=remaining.strip(),
                        metadata={
                            "section_path": section_path,
                            "source_type": source_type,
                        },
                    )
                )
                break

            split_point = self._find_split(remaining, separators)
            chunk_text = remaining[:split_point].strip()
            if chunk_text:
                chunks.append(
                    Chunk(
                        chunk_id=f"chunk_{uuid.uuid4().hex[:8]}",
                        document_id=document_id,
                        element_ids=element_ids,
                        text=chunk_text,
                        metadata={
                            "section_path": section_path,
                            "source_type": source_type,
                        },
                    )
                )
            remaining = (
                remaining[split_point - self.chunk_overlap :]
                if split_point < len(remaining)
                else ""
            )

        return chunks

    def _find_split(self, text: str, separators: list[str]) -> int:
        target = min(self.chunk_size, len(text))
        best_pos = target

        for sep in separators:
            pos = text.rfind(sep, 0, target)
            if pos != -1 and pos > best_pos - self.chunk_overlap:
                pos += len(sep)
                if self._is_good_split(pos, target):
                    return pos

        for sep in separators:
            pos = text.rfind(sep, 0, target)
            if pos != -1:
                return pos + len(sep)

        return target

    def _is_good_split(self, pos: int, target: int) -> bool:
        distance = abs(pos - target)
        max_distance = max(self.chunk_size // 2, self.chunk_overlap)
        return distance <= max_distance
