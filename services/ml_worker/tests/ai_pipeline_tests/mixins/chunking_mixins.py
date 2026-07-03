from __future__ import annotations

import uuid
from typing import Any, Optional

from models import (
    ElementType,
    SourceType,
    TableCell,
    TableData,
    UnifiedDocument,
    UnifiedElement,
)


class ChunkingTestMixin:
    """Factory methods for creating test data with consistent defaults."""

    def make_element(
        self,
        element_type: ElementType = ElementType.TEXT,
        text: str = "",
        level: Optional[int] = None,
        parent_id: Optional[str] = None,
        page: Optional[int] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> UnifiedElement:
        return UnifiedElement(
            element_id=f"el_{uuid.uuid4().hex[:8]}",
            type=element_type,
            text=text or f"Test {element_type.value} content",
            level=level,
            parent_id=parent_id,
            page=page,
            source_type=SourceType.TEXT,
            metadata=metadata or {},
        )

    def make_title(
        self,
        text: str,
        level: int = 1,
        parent_id: Optional[str] = None,
    ) -> UnifiedElement:
        return self.make_element(
            element_type=ElementType.TITLE,
            text=text,
            level=level,
            parent_id=parent_id,
        )

    def make_text(
        self,
        text: str = "",
        parent_id: Optional[str] = None,
    ) -> UnifiedElement:
        return self.make_element(
            element_type=ElementType.TEXT,
            text=text or "Some text content for testing.",
            parent_id=parent_id,
        )

    def make_table(
        self,
        caption: str = "",
        rows: int = 3,
        cols: int = 3,
    ) -> UnifiedElement:
        cells = []
        for r in range(rows):
            for c in range(cols):
                cells.append(
                    TableCell(
                        row=r,
                        col=c,
                        text=f"cell_{r}_{c}",
                        is_header=(r == 0),
                    )
                )
        table_data = TableData(
            name="test_table",
            caption=caption or "Test table",
            columns=[f"col_{c}" for c in range(cols)],
            rows=[[f"val_{r}_{c}" for c in range(cols)] for r in range(rows)],
            cells=cells,
            markdown=f"| {' | '.join(f'col_{c}' for c in range(cols))} |\n"
            f"|{'---|' * cols}\n"
            f"| {' | '.join(f'val_0_{c}' for c in range(cols))} |",
        )
        return UnifiedElement(
            element_id=f"el_{uuid.uuid4().hex[:8]}",
            type=ElementType.TABLE,
            text=f"Table: {caption}",
            table_data=table_data,
            source_type=SourceType.TEXT,
        )

    def make_document(
        self,
        elements: Optional[list[UnifiedElement]] = None,
        title: str = "Test Document",
        source_type: SourceType = SourceType.TEXT,
    ) -> UnifiedDocument:
        return UnifiedDocument(
            document_id=str(uuid.uuid4()),
            source_type=source_type,
            source_uri="/test/path.txt",
            title=title,
            elements=elements or [],
        )

    def make_structured_document(self) -> UnifiedDocument:
        """Creates a document with realistic section structure for testing."""
        return self.make_document(
            elements=[
                self.make_title("Introduction", level=1),
                self.make_text(
                    "This is the introduction section. "
                    "It contains background information."
                ),
                self.make_title("Methods", level=1),
                self.make_title("Data Collection", level=2),
                self.make_text(
                    "We collected data from multiple sources. "
                    "The process involved several steps. "
                    "Each step was carefully documented."
                ),
                self.make_title("Analysis", level=2),
                self.make_text(
                    "The analysis was performed using statistical methods. "
                    "Results were validated through cross-validation."
                ),
                self.make_title("Results", level=1),
                self.make_table("Experimental results"),
                self.make_text("The results show significant improvement."),
                self.make_title("Conclusion", level=1),
                self.make_text("In conclusion, the hypothesis was validated."),
            ],
            title="Research Paper",
        )
