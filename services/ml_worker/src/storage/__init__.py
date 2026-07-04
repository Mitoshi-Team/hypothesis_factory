from __future__ import annotations


async def download_file(remote_path: str) -> str:
    """Download file from remote storage (S3 etc.) to local temp path.

    Currently returns the path as-is (local filesystem).
    Future: download from S3 to a temp directory.
    """
    return remote_path
