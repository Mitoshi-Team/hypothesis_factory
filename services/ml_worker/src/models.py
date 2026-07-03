from __future__ import annotations

import hashlib
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, computed_field


class EntityLabel(str, Enum):
    MATERIAL = "Material"
    PROCESS = "Process"
    PROPERTY = "Property"
    PARAMETER = "Parameter"


# Тип источника, что за конкретно файл был загружен
class SourceType(str, Enum):
    TEXT = "text"
    PDF = "pdf"
    EXCEL = "excel"
    DATABASE = "database"
    MARKDOWN = "markdown"
    WORD = "word"


class ElementType(str, Enum):
    TITLE = "title"  # Заголовок любого уровня
    TEXT = "text"  # Обычный параграф
    LIST_ITEM = "list_item"  # Элемент списка
    TABLE = "table"  # Таблица (структурированная)
    IMAGE = "image"  # Изображение / рисунок / скриншот
    FORMULA = "formula"  # Математическая формула (LaTeX)
    CODE = "code"  # Блок кода
    CAPTION = "caption"  # Подпись к рисунку/таблице
    HEADER = "header"  # Колонтитул (верхний)
    FOOTER = "footer"  # Колонтитул (нижний)
    REFERENCE = "reference"  # Библиографическая ссылка
    METADATA = "metadata"  # Технические метаданные (DOI, авторы)


class RelationType(str, Enum):
    CONTAINS = "contains"
    INFLUENCES = "influences"
    PRODUCES = "produces"
    REQUIRES = "requires"
    CITES = "cites"
    PART_OF = "part_of"
    SIMILAR_TO = "similar_to"


class BoundingBox(BaseModel):
    """Координаты элемента на странице (для PDF/изображений)."""

    x: float
    y: float
    width: float
    height: float
    page: int = 1


class TableCell(BaseModel):
    """Ячейка таблицы с иерархией."""

    row: int
    col: int
    row_span: int = 1
    col_span: int = 1
    text: str
    is_header: bool = False


class TableData(BaseModel):
    """Структурированное представление таблицы для PostgreSQL."""

    table_id: str = Field(
        default_factory=lambda: f"tbl_{uuid.uuid4().hex[:8]}"
    )
    name: Optional[str] = None  # Название таблицы (если есть)
    caption: Optional[str] = None  # Подпись к таблице
    columns: list[str] = Field(default_factory=list)
    rows: list[list[str | float | None]] = Field(default_factory=list)
    cells: list[TableCell] = Field(default_factory=list)  # Для сложных таблиц
    markdown: Optional[str] = None  # Markdown-представление (для Chroma)


class ImageData(BaseModel):
    """Метаданные изображения."""

    image_id: str = Field(
        default_factory=lambda: f"img_{uuid.uuid4().hex[:8]}"
    )
    mime_type: str = "image/png"
    storage_uri: Optional[str] = None  # s3://bucket/... или file://...
    base64: Optional[str] = None  # Для inline (< 1MB)
    caption: Optional[str] = None  # Текст подписи
    ocr_text: Optional[str] = None  # Распознанный текст на изображении
    width: Optional[int] = None
    height: Optional[int] = None


class Entity(BaseModel):
    """Сущность для Knowledge Graph."""

    entity_id: str = Field(
        default_factory=lambda: f"ent_{uuid.uuid4().hex[:8]}"
    )
    label: EntityLabel  # Тип: Material, Process, Property...
    name: str  # Нормализованное имя
    surface_form: Optional[str] = None  # Как написано в тексте
    chunk_ids: list[str] = Field(default_factory=list)  # Ссылки на чанки
    metadata: dict[str, Any] = Field(default_factory=dict)


class Relation(BaseModel):
    """Связь между сущностями."""

    relation_id: str = Field(
        default_factory=lambda: f"rel_{uuid.uuid4().hex[:8]}"
    )
    source_id: str
    target_id: str
    relation_type: RelationType
    confidence: float = 1.0
    chunk_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class UnifiedElement(BaseModel):
    """
    Единый элемент документа.
    Независимо от источника (Docling, unstructured, pandas, SQL) —
    всё приводится к этому формату.
    """

    element_id: str = Field(
        default_factory=lambda: f"el_{uuid.uuid4().hex[:8]}"
    )
    type: ElementType

    # Основное содержимое
    text: str = ""  # Текстовое представление (для чанков)
    content: Optional[str] = None  # Альтернативное (HTML, LaTeX, markdown)

    # Иерархия
    level: Optional[int] = None  # Для заголовков: 1, 2, 3...
    parent_id: Optional[str] = None  # ID родительского элемента
    children_ids: list[str] = Field(default_factory=list)

    # Layout / provenance
    bbox: Optional[BoundingBox] = None
    page: Optional[int] = None

    # Специфичные данные
    table_data: Optional[TableData] = None  # Если type == TABLE
    image_data: Optional[ImageData] = None  # Если type == IMAGE

    # Метаданные для downstream
    metadata: dict[str, Any] = Field(default_factory=dict)

    # Ссылки на источник
    extractor: str = "unknown"  # docling | unstructured | pandas | sqlalchemy
    source_type: SourceType = SourceType.TEXT

    @computed_field
    @property
    def embedding_payload(self) -> str:
        """
        Текст, который реально уйдёт в эмбеддинг.
        Для таблиц — caption + markdown.
        Для изображений — caption + OCR.
        """
        if self.type == ElementType.TABLE and self.table_data:
            parts = [
                self.table_data.caption or "",
                self.table_data.markdown or self.text,
            ]
            return "\n".join(p for p in parts if p).strip()

        if self.type == ElementType.IMAGE and self.image_data:
            parts = [
                self.image_data.caption or "",
                self.image_data.ocr_text or "",
            ]
            return "\n".join(p for p in parts if p).strip()

        return self.text or self.content or ""

    def is_structural(self) -> bool:
        """Элементы, которые не несут семантики, но задают иерархию."""
        return self.type in (
            ElementType.HEADER,
            ElementType.FOOTER,
            ElementType.METADATA,
        )


class UnifiedDocument(BaseModel):
    """
    Корневой документ.
    Создаётся один раз при ingestion и живёт через весь pipeline.
    """

    document_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_type: SourceType
    source_uri: str  # Путь/URL к оригиналу
    mime_type: Optional[str] = None

    # Метаданные документа
    title: Optional[str] = None
    authors: list[str] = Field(default_factory=list)
    doi: Optional[str] = None
    date: Optional[datetime] = None
    language: Optional[str] = "en"

    # Элементы
    elements: list[UnifiedElement] = Field(default_factory=list)

    # Техническое
    created_at: datetime = Field(default_factory=datetime.utcnow)
    extractor: str = "unknown"
    checksum: Optional[str] = None  # SHA256 оригинального файла

    # ── Методы ──

    def get_tables(self) -> list[UnifiedElement]:
        """Все таблицы документа (для Postgres-pipeline)."""
        return [el for el in self.elements if el.type == ElementType.TABLE]

    def get_images(self) -> list[UnifiedElement]:
        """Все изображения (для captioning / vision pipeline)."""
        return [el for el in self.elements if el.type == ElementType.IMAGE]

    def get_sections(self) -> list[UnifiedElement]:
        """Иерархия заголовков."""
        return [el for el in self.elements if el.type == ElementType.TITLE]

    def get_text_elements(self) -> list[UnifiedElement]:
        """Все текстовые элементы (для чанкирования)."""
        return [
            el
            for el in self.elements
            if el.type
            in (ElementType.TEXT, ElementType.TITLE, ElementType.LIST_ITEM)
            and not el.is_structural()
        ]

    def compute_checksum(self, file_bytes: bytes) -> None:
        self.checksum = hashlib.sha256(file_bytes).hexdigest()


class Chunk(BaseModel):
    """
    Готовый чанк для Chroma.
    Создаётся на этапе chunking из UnifiedElement.
    """

    chunk_id: str = Field(
        default_factory=lambda: f"chunk_{uuid.uuid4().hex[:8]}"
    )
    document_id: str
    element_ids: list[str] = Field(
        default_factory=list
    )  # Из каких элементов собран

    text: str  # Текст для эмбеддинга
    embedding: Optional[list[float]] = None

    metadata: dict[str, Any] = Field(default_factory=dict)
    # Примеры метаданных:
    # - section_path: "Introduction > Methods"
    # - source_type: "pdf"
    # - sql_table: "sales_q1"  (если чанк — строка таблицы)
    # - page: 3
    # - has_formula: true
