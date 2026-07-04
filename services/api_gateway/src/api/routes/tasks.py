"""Celery Task Status API routes."""

from fastapi import APIRouter, Depends, status
from src.api.dependencies import get_current_user
from src.api.schemas import TaskStatusResponse
from src.database.models import User
from src.utils.celery_client import get_task_status

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get(
    "/{task_id}",
    response_model=TaskStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Celery Task Status",
)
async def check_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
) -> TaskStatusResponse:
    """Retrieve execution status and optional outcome of a queued Celery task."""
    task_result = get_task_status(task_id)

    # Prepare response payload
    status_name = task_result.status

    # Get execution result if successful
    result_val = None
    if status_name == "SUCCESS":
        result_val = task_result.result
    elif status_name == "FAILURE":
        # Return string representation of the exception
        result_val = str(task_result.result)

    return TaskStatusResponse(
        task_id=task_id,
        status=status_name,
        result=result_val,
    )
