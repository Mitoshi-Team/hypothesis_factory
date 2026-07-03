from __future__ import annotations

import json
from pathlib import Path

from src.ai_pipeline.state import PipelineOutput
from src.config import settings


async def save_report(session_id: str, output: PipelineOutput) -> str:
    """Save pipeline output as a local JSON file.

    Future: persist to MongoDB instead.
    """
    report_dir = Path(settings.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    path = report_dir / f"{session_id}.json"
    data = output.model_dump(exclude={"trace"})
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=str)
    )
    return str(path)
