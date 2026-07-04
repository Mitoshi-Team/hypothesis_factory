from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

from sqlalchemy.orm import Session as SASession
from src.ai_pipeline import run_pipeline
from src.ai_pipeline.state import (
    HypothesisCard,
    HypothesisReview,
    PipelineInput,
)
from src.celery_app import celery_app
from src.db import SessionLocal
from src.db.models import Message as MessageORM
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


def _load_session(db: SASession, session_id: str) -> Optional[SessionORM]:
    return db.get(SessionORM, session_id)


def _load_message(db: SASession, message_id: str) -> Optional[MessageORM]:
    return db.get(MessageORM, message_id)


def _count_processed_messages(db: SASession, session_id: str) -> int:
    from sqlalchemy import func

    count = (
        db.query(func.count(MessageORM.id))
        .filter(
            MessageORM.session_id == session_id,
            MessageORM.role == "system",
            MessageORM.status == "done",
        )
        .scalar()
    )
    return count or 0


def _load_previous_feedback(
    db: SASession,
    session_id: str,
    current_iteration: int,
) -> Optional[str]:
    if current_iteration <= 0:
        return None

    previous_user = (
        db.query(MessageORM)
        .filter(
            MessageORM.session_id == session_id,
            MessageORM.role == "user",
            MessageORM.iteration == current_iteration - 1,
        )
        .order_by(MessageORM.created_at.desc())
        .first()
    )

    if previous_user:
        return previous_user.content
    return None


def _load_previous_result(
    db: SASession,
    session_id: str,
    iteration: int,
) -> Optional[PipelineResultORM]:
    if iteration <= 0:
        return None

    previous_message = (
        db.query(MessageORM)
        .filter(
            MessageORM.session_id == session_id,
            MessageORM.role == "system",
            MessageORM.iteration == iteration - 1,
            MessageORM.status == "done",
        )
        .order_by(MessageORM.created_at.desc())
        .first()
    )

    if not previous_message:
        return None

    return (
        db.query(PipelineResultORM)
        .filter(
            PipelineResultORM.session_id == session_id,
            PipelineResultORM.message_id == previous_message.id,
        )
        .order_by(PipelineResultORM.created_at.desc())
        .first()
    )


def _ingest_files(
    upload_files: list[str],
) -> tuple[list[UnifiedDocument], list[Entity]]:
    documents: list[UnifiedDocument] = []
    all_entities: list[Entity] = []

    for fp in upload_files:
        local_path = download_file(fp)
        doc = extract_document(local_path)
        entities = extract_entities(doc)
        documents.append(doc)
        all_entities.extend(entities)
        logger.info("Extracted %d entities from %s", len(entities), fp)

    return documents, all_entities


def _save_entities(
    db: SASession,
    session_id: str,
    upload_files: list[str],
    entities: list[Entity],
) -> None:
    for ent in entities:
        db.add(
            NEREntityORM(
                session_id=session_id,
                entity_id=ent.entity_id,
                name=ent.name,
                label=ent.label.value,
                source_file=";".join(upload_files),
            )
        )
    db.commit()
    logger.info("Saved session %s with %d entities", session_id, len(entities))


def _mark_failed(
    db: SASession,
    message_id: str,
    session_id: str,
) -> None:
    message = _load_message(db, message_id)
    if message:
        message.status = "failed"
    session = _load_session(db, session_id)
    if session:
        session.status = "failed"
    db.commit()


def _persist_result(
    db: SASession,
    session_id: str,
    message_id: str,
    result: Any,
) -> None:
    db.add(
        PipelineResultORM(
            session_id=session_id,
            message_id=message_id,
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

    message = _load_message(db, message_id)
    if message:
        message.status = "done"
        message.content = (
            result.hypothesis.hypothesis if result.hypothesis else ""
        )

    session = _load_session(db, session_id)
    if session:
        session.status = "done"

    db.commit()


@celery_app.task(bind=True, max_retries=3, acks_late=True)
def process_message(
    self,
    user_id: str,
    uuid: str,
    message_id: str,
    first_message: bool,
    upload_files: list[str],
    prompt: str,
) -> dict[str, Any]:
    logger.info(
        "Processing message: user=%s session=%s message=%s files=%d",
        user_id,
        uuid,
        message_id,
        len(upload_files),
    )

    db: SASession
    with SessionLocal() as db:
        session = _load_session(db, uuid)
        if not session:
            msg = f"Session {uuid} not found"
            raise ValueError(msg)

        message = _load_message(db, message_id)
        if not message:
            msg = f"Message {message_id} not found"
            raise ValueError(msg)

        message.status = "processing"
        session.status = "processing"
        db.commit()

        iteration = _count_processed_messages(db, uuid)
        if first_message and iteration != 0:
            iteration = 0

        feedback = _load_previous_feedback(db, uuid, iteration)
        previous_result = _load_previous_result(db, uuid, iteration)
        constraints = session.constraints or ""
        weights = session.weights or {}

    documents, all_entities = _ingest_files(upload_files)
    merged_doc = _merge_documents(documents) if documents else None
    dedup_entities = _dedup_entities(all_entities)

    with SessionLocal() as db:
        _save_entities(db, uuid, upload_files, dedup_entities)

    input_data = _build_pipeline_input(
        user_id=user_id,
        session_id=uuid,
        prompt=prompt,
        upload_files=upload_files,
        merged_doc=merged_doc,
        dedup_entities=dedup_entities,
        constraints=constraints,
        weights=weights,
        iteration=iteration,
        feedback=feedback,
        previous_result=previous_result,
    )

    try:
        result = asyncio.run(run_pipeline(input_data))
    except Exception:
        logger.exception("Pipeline failed for session %s", uuid)
        with SessionLocal() as db:
            _mark_failed(db, message_id, uuid)
        raise

    with SessionLocal() as db:
        _persist_result(db, uuid, message_id, result)

    report_path = asyncio.run(save_report(uuid, message_id, result))
    logger.info("Report saved to %s", report_path)

    return result.model_dump()


def _parse_previous_result(
    previous_result: Optional[PipelineResultORM],
) -> tuple[Optional[HypothesisCard], Optional[HypothesisReview]]:
    previous_hypothesis = None
    previous_review = None
    if previous_result:
        if previous_result.hypothesis_json:
            previous_hypothesis = HypothesisCard.model_validate_json(
                previous_result.hypothesis_json
            )
        if previous_result.review_json:
            previous_review = HypothesisReview.model_validate_json(
                previous_result.review_json
            )
    return previous_hypothesis, previous_review


def _build_pipeline_input(
    user_id: str,
    session_id: str,
    prompt: str,
    upload_files: list[str],
    merged_doc: Optional[UnifiedDocument],
    dedup_entities: list[Entity],
    constraints: str,
    weights: dict[str, Any],
    iteration: int,
    feedback: Optional[str],
    previous_result: Optional[PipelineResultORM],
) -> PipelineInput:
    previous_hypothesis, previous_review = _parse_previous_result(
        previous_result
    )
    return PipelineInput(
        session_id=session_id,
        user_id=user_id,
        problem=prompt,
        file_paths=upload_files,
        file_path=upload_files[0] if upload_files else None,
        document=merged_doc,
        entities=dedup_entities,
        constraints=constraints,
        weights=weights,
        iteration=iteration,
        feedback=feedback,
        previous_hypothesis=previous_hypothesis,
        previous_review=previous_review,
    )
