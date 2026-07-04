from __future__ import annotations

from pathlib import Path


def download_file(remote_path: str) -> str:
    """Resolve uploaded file path.

    Currently expects absolute local filesystem path and verifies existence.
    Future: download from S3/MinIO to a temp directory.
    """
    path = Path(remote_path)
    if not path.exists():
        msg = f"File not found: {remote_path}"
        raise FileNotFoundError(msg)
    return str(path)
