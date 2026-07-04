"""Results, Graph, and Reports API routes."""

import json
import os
from typing import Optional

from fastapi import APIRouter, Depends, Header, status
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.dependencies import get_current_user, get_db
from src.api.schemas import (
    GraphResponse,
    HypothesisCard,
    HypothesisReview,
    ResultResponse,
    TraceResult,
)
from src.config import get_settings
from src.database.models import Message as MessageORM
from src.database.models import PipelineResult as PipelineResultORM
from src.database.models import Session as SessionORM
from src.database.models import User
from src.utils.exceptions import EntityNotFoundError

router = APIRouter(prefix="/sessions/{session_id}", tags=["results"])
settings = get_settings()


@router.get(
    "/results/{message_id}",
    response_model=ResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Message Results",
)
async def get_message_results(
    session_id: str,
    message_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResultResponse:
    """Retrieve hypothesis generation and review results for a specific message."""
    # Check if session exists and belongs to current user
    sess_result = await db.execute(
        select(SessionORM).where(
            SessionORM.id == session_id, SessionORM.user_id == current_user.id
        )
    )
    if not sess_result.scalar_one_or_none():
        raise EntityNotFoundError("Session not found")

    # Find the pipeline result
    res_result = await db.execute(
        select(PipelineResultORM).where(
            PipelineResultORM.session_id == session_id,
            PipelineResultORM.message_id == message_id,
        )
    )
    result_orm = res_result.scalar_one_or_none()

    if result_orm:
        return ResultResponse(
            message_id=result_orm.message_id,
            status="done",
            hypothesis=HypothesisCard.model_validate(
                json.loads(result_orm.hypothesis_json)
            )
            if result_orm.hypothesis_json
            else None,
            review=HypothesisReview.model_validate(json.loads(result_orm.review_json))
            if result_orm.review_json
            else None,
            graph=GraphResponse.model_validate(json.loads(result_orm.graph_json))
            if result_orm.graph_json
            else None,
            trace=TraceResult.model_validate(json.loads(result_orm.trace_json))
            if result_orm.trace_json
            else None,
        )

    # If result is not found, check the message status
    msg_result = await db.execute(
        select(MessageORM).where(
            MessageORM.id == message_id, MessageORM.session_id == session_id
        )
    )
    message_orm = msg_result.scalar_one_or_none()

    if not message_orm:
        raise EntityNotFoundError("Message not found")

    if message_orm.status in ("queued", "processing"):
        # Return 202 Accepted containing the processing state
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={
                "message_id": message_id,
                "status": message_orm.status,
                "task_id": message_orm.task_id,
            },
        )

    # If the message failed
    return ResultResponse(
        message_id=message_id,
        status="failed",
    )


@router.get(
    "/graph",
    response_model=GraphResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Session Knowledge Graph",
)
async def get_session_graph(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GraphResponse:
    """Retrieve full knowledge graph corresponding to the latest pipeline result."""
    # Check session
    sess_result = await db.execute(
        select(SessionORM).where(
            SessionORM.id == session_id, SessionORM.user_id == current_user.id
        )
    )
    if not sess_result.scalar_one_or_none():
        raise EntityNotFoundError("Session not found")

    # Get latest result
    res_result = await db.execute(
        select(PipelineResultORM)
        .where(PipelineResultORM.session_id == session_id)
        .order_by(desc(PipelineResultORM.id))
        .limit(1)
    )
    latest_orm = res_result.scalar_one_or_none()

    if not latest_orm or not latest_orm.graph_json:
        raise EntityNotFoundError("No graph data found for this session yet")

    return GraphResponse.model_validate(json.loads(latest_orm.graph_json))


@router.get(
    "/reports/latest",
    summary="Download Latest Report",
)
async def download_latest_report(
    session_id: str,
    accept: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download the latest report in JSON or HTML format based on the Accept header."""
    # Check session
    sess_result = await db.execute(
        select(SessionORM).where(
            SessionORM.id == session_id, SessionORM.user_id == current_user.id
        )
    )
    if not sess_result.scalar_one_or_none():
        raise EntityNotFoundError("Session not found")

    # Get latest successful result
    res_result = await db.execute(
        select(PipelineResultORM)
        .where(PipelineResultORM.session_id == session_id)
        .order_by(desc(PipelineResultORM.id))
        .limit(1)
    )
    latest_orm = res_result.scalar_one_or_none()

    if not latest_orm:
        raise EntityNotFoundError("No reports available for this session")

    message_id = latest_orm.message_id
    report_format = "json"
    content_type = "application/json"

    if accept and "text/html" in accept:
        report_format = "html"
        content_type = "text/html"

    report_filename = f"{message_id}.{report_format}"
    report_path = os.path.join(settings.REPORT_DIR, session_id, report_filename)

    # Check if the requested file format exists
    if not os.path.exists(report_path):
        # Fallback to json if HTML was requested but is not available
        if report_format == "html":
            fallback_filename = f"{message_id}.json"
            fallback_path = os.path.join(
                settings.REPORT_DIR, session_id, fallback_filename
            )
            if os.path.exists(fallback_path):
                return FileResponse(
                    path=fallback_path,
                    media_type="application/json",
                    filename=fallback_filename,
                )
        raise EntityNotFoundError(
            f"Report file in {report_format.upper()} format was not found on disk"
        )

    return FileResponse(
        path=report_path,
        media_type=content_type,
        filename=report_filename,
    )
