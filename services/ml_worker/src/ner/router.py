from pathlib import Path

from src.models import SourceType

EXTENSION_MAP: dict[str, SourceType] = {
    ".txt": SourceType.TEXT,
    ".md": SourceType.MARKDOWN,
    ".markdown": SourceType.MARKDOWN,
    ".mdown": SourceType.MARKDOWN,
    ".pdf": SourceType.PDF,
    ".xls": SourceType.EXCEL,
    ".xlsx": SourceType.EXCEL,
    ".doc": SourceType.WORD,
    ".docx": SourceType.WORD,
    ".csv": SourceType.DATABASE,
    ".sql": SourceType.DATABASE,
    ".db": SourceType.DATABASE,
    ".sqlite": SourceType.DATABASE,
    ".sqlite3": SourceType.DATABASE,
}


def route_file(file_path: str) -> SourceType:
    ext = Path(file_path).suffix.lower()
    source_type = EXTENSION_MAP.get(ext)
    if source_type is None:
        raise ValueError(f"Unsupported file extension: {ext}")
    return source_type
