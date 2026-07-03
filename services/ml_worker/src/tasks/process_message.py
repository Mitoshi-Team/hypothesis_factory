from __future__ import annotations

import asyncio
import logging
from typing import Any

from sqlalchemy.orm import Session as SASession
from src.ai_pipeline import run_pipeline
from src.ai_pipeline.state import PipelineInput
from src.celery_app import celery_app
from src.db import SessionLocal
from src.db.models import NEREntity as NEREntityORM
from src.db.models import PipelineResult as PipelineResultORM
from src.db.models import Session as SessionORM
from src.models import Entity, UnifiedDocument
from src.ner import extract_document, extract_entities
from src.report import save_report
from src.storage import download_file

logger = logging.getLogger(__name__)


def _dedup_entities(entities: list[Entity]) -> list[Entity]:
    seen: set[tuple[str, str]] = set()
    result: list[Entity] = []
    for ent in entities:
        key = (ent.name.lower(), ent.label.value)
        if key not in seen:
            seen.add(key)
            result.append(ent)
    return result


def _merge_documents(documents: list[UnifiedDocument]) -> UnifiedDocument:
    if not documents:
        msg = "No documents to merge"
        raise ValueError(msg)
    if len(documents) == 1:
        return documents[0]

    first = documents[0]
    import uuid

    merged = UnifiedDocument(
        document_id=str(uuid.uuid4()),
        source_type=first.source_type,
        source_uri=";".join(d.source_uri for d in documents),
        title=first.title,
        elements=[el for d in documents for el in d.elements],
        extractor="merged",
    )
    return merged


@celery_app.task(bind=True, max_retries=3, acks_late=True)
def process_message(
    self,
    user_id: str,
    uuid: str,
    first_message: bool,
    upload_files: list[str],
    prompt: str,
) -> dict[str, Any]:
    logger.info(
        "Processing message: user=%s session=%s files=%d",
        user_id,
        uuid,
        len(upload_files),
    )

    # 1. NER for all uploaded files
    documents: list[UnifiedDocument] = []
    all_entities: list[Entity] = []

    for fp in upload_files:
        local_path = download_file(fp)
        doc = extract_document(local_path)
        entities = extract_entities(doc)
        documents.append(doc)
        all_entities.extend(entities)
        logger.info("Extracted %d entities from %s", len(entities), fp)

    # 2. Merge documents and deduplicate entities
    merged_doc = _merge_documents(documents) if documents else None
    dedup_entities = _dedup_entities(all_entities)

    # 3. Save session + entities to DB
    db: SASession
    with SessionLocal() as db:
        db.add(SessionORM(id=uuid, user_id=user_id, status="processing"))
        for ent in dedup_entities:
            db.add(
                NEREntityORM(
                    session_id=uuid,
                    entity_id=ent.entity_id,
                    name=ent.name,
                    label=ent.label.value,
                    source_file=";".join(upload_files),
                )
            )
        db.commit()
        logger.info(
            "Saved session %s with %d entities", uuid, len(dedup_entities)
        )

    # 4. Run ai_pipeline
    input_data = PipelineInput(
        session_id=uuid,
        user_id=user_id,
        problem=prompt,
        file_paths=upload_files,
        file_path=upload_files[0] if upload_files else None,
        document=merged_doc,
        entities=dedup_entities,
    )

    try:
        result = asyncio.run(run_pipeline(input_data))
    except Exception:
        logger.exception("Pipeline failed for session %s", uuid)
        with SessionLocal() as db:
            ses = db.get(SessionORM, uuid)
            if ses:
                ses.status = "failed"
                db.commit()
        raise

    # 5. Save result to DB + local report
    with SessionLocal() as db:
        db.add(
            PipelineResultORM(
                session_id=uuid,
                hypothesis_json=(
                    result.hypothesis.model_dump_json()
                    if result.hypothesis
                    else ""
                ),
                review_json=(
                    result.review.model_dump_json() if result.review else ""
                ),
                graph_json=(
                    result.graph.model_dump_json() if result.graph else "{}"
                ),
            )
        )
        ses = db.get(SessionORM, uuid)
        if ses:
            ses.status = "done"
        db.commit()

    report_path = asyncio.run(save_report(uuid, result))
    logger.info("Report saved to %s", report_path)

    return result.model_dump()
