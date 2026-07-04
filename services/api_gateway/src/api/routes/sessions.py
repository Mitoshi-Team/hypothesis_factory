"""Sessions and Messages API routes."""

import datetime
import os
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Form, UploadFile, status
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.dependencies import get_current_user, get_db
from src.api.schemas import (
    GraphResponse,
    HypothesisCard,
    HypothesisReview,
    MessageCreateResponse,
    MessageListResponse,
    MessageResponse,
    ResultResponse,
    SessionCreate,
    SessionDetailResponse,
    SessionListResponse,
    SessionResponse,
    TraceResult,
)
from src.config import get_settings
from src.database.models import File as FileORM
from src.database.models import Message as MessageORM
from src.database.models import PipelineResult as PipelineResultORM
from src.database.models import Session as SessionORM
from src.database.models import User
from src.utils.celery_client import send_process_message_task
from src.utils.exceptions import EntityNotFoundError, ValidationAppError

router = APIRouter(prefix="/sessions", tags=["sessions"])
settings = get_settings()

MAX_FILE_SIZE = 150 * 1024 * 1024  # 150 MB


@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Session",
)
async def create_session(
    payload: SessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SessionResponse:
    """Initialize a new research session with KPI weights and constraints."""
    session_id = f"sess_{uuid.uuid4().hex[:12]}"
    import datetime

    new_session = SessionORM(
        id=session_id,
        user_id=current_user.id,
        title=payload.title,
        constraints=payload.constraints,
        weights=payload.weights,
        status="created",
        created_at=datetime.datetime.now(datetime.UTC),
        updated_at=datetime.datetime.now(datetime.UTC),
    )
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)

    return SessionResponse(
        id=new_session.id,
        title=new_session.title,
        status=new_session.status,
        created_at=new_session.created_at,
        updated_at=new_session.updated_at,
    )


@router.get(
    "",
    response_model=SessionListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Sessions",
)
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SessionListResponse:
    """Retrieve list of all active sessions for the current authenticated user."""
    result = await db.execute(
        select(SessionORM)
        .where(SessionORM.user_id == current_user.id)
        .order_by(desc(SessionORM.created_at))
    )
    sessions = result.scalars().all()

    items = [
        SessionResponse(
            id=s.id,
            title=s.title,
            status=s.status,
            created_at=s.created_at,
            updated_at=s.updated_at,
        )
        for s in sessions
    ]

    return SessionListResponse(
        items=items,
        total=len(items),
    )


@router.get(
    "/{session_id}",
    response_model=SessionDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Session Details",
)
async def get_session_details(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SessionDetailResponse:
    """Retrieve complete metadata, message history and last result for a session."""
    # Check if session exists and belongs to current user
    result = await db.execute(
        select(SessionORM).where(
            SessionORM.id == session_id, SessionORM.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise EntityNotFoundError("Session not found")

    # Fetch message history
    msg_result = await db.execute(
        select(MessageORM)
        .where(MessageORM.session_id == session_id)
        .order_by(MessageORM.created_at.asc())
    )
    messages = msg_result.scalars().all()

    # Fetch latest pipeline result
    pipeline_result = await db.execute(
        select(PipelineResultORM)
        .where(PipelineResultORM.session_id == session_id)
        .order_by(desc(PipelineResultORM.id))
        .limit(1)
    )
    latest_orm = pipeline_result.scalar_one_or_none()

    latest_result = None
    if latest_orm:
        try:
            hypothesis_data = (
                json.loads(latest_orm.hypothesis_json)
                if latest_orm.hypothesis_json
                else None
            )
            review_data = (
                json.loads(latest_orm.review_json) if latest_orm.review_json else None
            )
            graph_data = (
                json.loads(latest_orm.graph_json) if latest_orm.graph_json else None
            )
            trace_data = (
                json.loads(latest_orm.trace_json) if latest_orm.trace_json else None
            )

            latest_result = ResultResponse(
                message_id=latest_orm.message_id,
                status="done",
                hypothesis=HypothesisCard.model_validate(hypothesis_data)
                if hypothesis_data
                else None,
                review=HypothesisReview.model_validate(review_data)
                if review_data
                else None,
                graph=GraphResponse.model_validate(graph_data) if graph_data else None,
                trace=TraceResult.model_validate(trace_data) if trace_data else None,
            )
        except Exception:
            # Fallback if validation fails
            latest_result = None

    return SessionDetailResponse(
        id=session.id,
        title=session.title,
        constraints=session.constraints,
        weights=session.weights,
        status=session.status,
        created_at=session.created_at,
        updated_at=session.updated_at,
        messages=[
            MessageResponse(
                id=m.id,
                role=m.role,
                content=m.content,
                iteration=m.iteration,
                status=m.status,
                task_id=m.task_id,
                created_at=m.created_at,
            )
            for m in messages
        ],
        latest_result=latest_result,
    )


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Session",
)
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a session, cascaded database entries and uploaded files."""
    result = await db.execute(
        select(SessionORM).where(
            SessionORM.id == session_id, SessionORM.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise EntityNotFoundError("Session not found")

    # Delete physically uploaded files
    session_upload_dir = os.path.join(settings.UPLOAD_DIR, session_id)
    if os.path.exists(session_upload_dir):
        import shutil

        shutil.rmtree(session_upload_dir, ignore_errors=True)

    await db.delete(session)
    await db.commit()


@router.post(
    "/{session_id}/messages",
    response_model=MessageCreateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit Message with Files",
)
async def submit_message(
    session_id: str,
    content: str = Form(..., description="Researcher query content"),
    files: Optional[List[UploadFile]] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageCreateResponse:
    """Submit a message and attachments to trigger scientific hypothesis generation."""
    # Check if session exists and belongs to current user
    result = await db.execute(
        select(SessionORM).where(
            SessionORM.id == session_id, SessionORM.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise EntityNotFoundError("Session not found")

    # Determine iteration number (number of successfully processed system messages)
    count_result = await db.execute(
        select(func.count(MessageORM.id)).where(
            MessageORM.session_id == session_id,
            MessageORM.role == "system",
            MessageORM.status == "done",
        )
    )
    iteration = count_result.scalar() or 0
    first_message = iteration == 0

    # 1. Create User Message ORM record
    user_msg_id = f"msg_{uuid.uuid4().hex[:12]}"
    import datetime

    user_message = MessageORM(
        id=user_msg_id,
        session_id=session_id,
        role="user",
        content=content,
        iteration=iteration,
        status="done",  # User message is processed instantly
        created_at=datetime.datetime.now(datetime.UTC),
    )
    db.add(user_message)

    # 2. Create System Message ORM record (to receive ML pipeline results)
    system_msg_id = f"msg_{uuid.uuid4().hex[:12]}"
    system_message = MessageORM(
        id=system_msg_id,
        session_id=session_id,
        role="system",
        content="",
        iteration=iteration,
        status="queued",
        created_at=datetime.datetime.now(datetime.UTC),
    )
    db.add(system_message)

    # Handle file uploads
    saved_file_paths: list[str] = []
    if files:
        session_upload_dir = os.path.join(settings.UPLOAD_DIR, session_id)
        os.makedirs(session_upload_dir, exist_ok=True)

        for file in files:
            # Read file content and check size limit
            file_content = await file.read()
            file_size = len(file_content)

            if file_size > MAX_FILE_SIZE:
                raise ValidationAppError(
                    f"File '{file.filename}' exceeds limit of 150MB"
                )

            # Generate unique local filename
            file_ext = os.path.splitext(file.filename)[1]
            file_id = f"file_{uuid.uuid4().hex[:12]}"
            local_filename = f"{file_id}{file_ext}"
            file_path = os.path.join(session_upload_dir, local_filename)

            # Save file content
            with open(file_path, "wb") as f_out:
                f_out.write(file_content)

            # Save File details to DB
            file_record = FileORM(
                id=file_id,
                session_id=session_id,
                message_id=user_msg_id,
                original_name=file.filename,
                storage_path=file_path,
                mime_type=file.content_type or "application/octet-stream",
            )
            db.add(file_record)
            saved_file_paths.append(file_path)

    # Assign task id and mark session processing before commit
    celery_task_id = f"task_{uuid.uuid4().hex[:12]}"
    system_message.task_id = celery_task_id
    session.status = "processing"

    # Commit everything before enqueuing Celery task so worker sees the records
    await db.commit()

    # Trigger Celery Task after commit to avoid race condition
    celery_task = send_process_message_task(
        user_id=current_user.id,
        session_id=session_id,
        message_id=system_msg_id,
        first_message=first_message,
        upload_files=saved_file_paths,
        prompt=content,
        task_id=celery_task_id,
    )

    return MessageCreateResponse(
        message_id=system_msg_id,
        task_id=celery_task.id,
        status="queued",
    )


@router.get(
    "/{session_id}/messages",
    response_model=MessageListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Session Messages",
)
async def get_session_messages(
    session_id: str,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageListResponse:
    """Retrieve message history for a session with pagination support."""
    # Check if session exists and belongs to current user
    result = await db.execute(
        select(SessionORM).where(
            SessionORM.id == session_id, SessionORM.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise EntityNotFoundError("Session not found")

    if page < 1 or page_size < 1 or page_size > 100:
        raise ValidationAppError("Invalid page or page_size parameter")

    # Get total messages count
    total_result = await db.execute(
        select(func.count(MessageORM.id)).where(MessageORM.session_id == session_id)
    )
    total = total_result.scalar() or 0

    # Fetch paginated messages
    msg_result = await db.execute(
        select(MessageORM)
        .where(MessageORM.session_id == session_id)
        .order_by(MessageORM.created_at.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    messages = msg_result.scalars().all()

    return MessageListResponse(
        items=[
            MessageResponse(
                id=m.id,
                role=m.role,
                content=m.content,
                iteration=m.iteration,
                status=m.status,
                task_id=m.task_id,
                created_at=m.created_at,
            )
            for m in messages
        ],
        total=total,
        page=page,
        page_size=page_size,
    )
