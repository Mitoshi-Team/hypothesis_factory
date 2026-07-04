"""Celery client configuration and helper functions."""

from celery import Celery
from celery.result import AsyncResult
from src.config import get_settings

settings = get_settings()

celery_app = Celery(
    "api_gateway",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)


def send_process_message_task(
    user_id: str,
    session_id: str,
    message_id: str,
    first_message: bool,
    upload_files: list[str],
    prompt: str,
    task_id: str | None = None,
) -> AsyncResult:
    """Send message processing task to Celery queue.

    Args:
        user_id: Authenticated user ID.
        session_id: Active session UUID.
        message_id: System message ID where output will be stored.
        first_message: True if it is the first iteration in the session.
        upload_files: List of absolute file paths to uploaded files.
        prompt: Content description / problem statement.
        task_id: Optional explicit Celery task ID.

    Returns:
        AsyncResult: Celery async result object.
    """
    return celery_app.send_task(
        "src.tasks.process_message.process_message",
        args=[user_id, session_id, message_id, first_message, upload_files, prompt],
        task_id=task_id,
    )


def get_task_status(task_id: str) -> AsyncResult:
    """Retrieve the status of a Celery task.

    Args:
        task_id: Celery task ID.

    Returns:
        AsyncResult: Task status details.
    """
    return AsyncResult(task_id, app=celery_app)
