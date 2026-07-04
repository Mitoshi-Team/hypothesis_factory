from __future__ import annotations

import json
from pathlib import Path

from src.ai_pipeline.state import PipelineOutput
from src.config import settings


def _hypothesis_to_html(data: dict) -> str:
    hypothesis = data.get("hypothesis", {}) or {}
    review = data.get("review", {}) or {}

    rows = []
    for key, value in hypothesis.items():
        if isinstance(value, list):
            value = (
                "<ul>"
                + "".join(f"<li>{item}</li>" for item in value)
                + "</ul>"
            )
        rows.append(f"<tr><td>{key}</td><td>{value}</td></tr>")

    review_rows = []
    for key, value in review.items():
        if isinstance(value, dict):
            value = (
                "<ul>"
                + "".join(f"<li>{k}: {v}</li>" for k, v in value.items())
                + "</ul>"
            )
        elif isinstance(value, list):
            value = (
                "<ul>"
                + "".join(f"<li>{item}</li>" for item in value)
                + "</ul>"
            )
        review_rows.append(f"<tr><td>{key}</td><td>{value}</td></tr>")

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>{hypothesis.get("title", "Отчёт")}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 24px;
        }}
        th, td {{
            border: 1px solid #ccc;
            padding: 8px;
            text-align: left;
            vertical-align: top;
        }}
        th {{ background: #f5f5f5; }}
        h1 {{ font-size: 24px; }}
        h2 {{ font-size: 20px; margin-top: 32px; }}
    </style>
</head>
<body>
    <h1>{hypothesis.get("title", "Отчёт")}</h1>
    <h2>Гипотеза</h2>
    <table>
        {"".join(rows)}
    </table>
    <h2>Ревью</h2>
    <table>
        {"".join(review_rows)}
    </table>
</body>
</html>"""


async def save_report(
    session_id: str,
    message_id: str,
    output: PipelineOutput,
) -> str:
    """Save pipeline output as JSON and HTML files.

    Files are stored under REPORT_DIR/session_id/message_id.{json,html}.
    """
    report_dir = Path(settings.report_dir) / session_id
    report_dir.mkdir(parents=True, exist_ok=True)

    data = output.model_dump()

    json_path = report_dir / f"{message_id}.json"
    json_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )

    html_path = report_dir / f"{message_id}.html"
    html_path.write_text(_hypothesis_to_html(data), encoding="utf-8")

    return str(json_path)
