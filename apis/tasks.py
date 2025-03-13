import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import UUID4, ValidationError

import services.responses
import services.tasks
from apis.auth import current_admin, current_user
from apis.utils import create_docs
from models.task import Task, TaskRead, TaskResponseCreate, TaskResponseRead
from models.task_config.examples import sample_task_config
from models.user import User

router = APIRouter(prefix="/tasks")


NOT_FOUND = HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
FORBIDDEN = HTTPException(status.HTTP_403_FORBIDDEN, "Forbidden")
CLIENT_ERROR = HTTPException(status.HTTP_400_BAD_REQUEST, "Client error")


@router.get("/", response_model=list[TaskRead])
async def get_tasks(_: User = Depends(current_admin)):
    return await Task.all()


@router.get(
    "/{task_id}", response_model=TaskRead, responses=create_docs(FORBIDDEN, NOT_FOUND)
)
async def get_task(task_id: UUID4, user_id: UUID4 = Depends(current_user)):
    task, authorized = await services.tasks.get_participant_task(task_id, user_id)
    if task is None:
        raise NOT_FOUND
    if not authorized:
        raise FORBIDDEN
    return task


@router.get("/sample", response_model=TaskRead)
async def get_sample_task():
    return sample_task_config


@router.get("/{task_id}/responses", response_model=TaskResponseRead)
async def get_task_responses(task_id: UUID, _=Depends(current_admin)):
    return sample_task_config


COMPLETED_ERROR = HTTPException(
    status_code=status.HTTP_409_CONFLICT, detail="Task already completed"
)


@router.post(
    "/{task_id}/response",
    response_model=TaskResponseRead,
    responses=create_docs(NOT_FOUND, FORBIDDEN, COMPLETED_ERROR),
)
async def create_task_response(
    task_id: UUID4,
    response: TaskResponseCreate,
    user_id: UUID4 | None = Depends(current_user),
):
    try:
        (
            response_read,
            task_exists,
            is_participant,
            completed,
        ) = await services.responses.create_response(task_id, response, user_id)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=jsonable_encoder(e.errors()))
    if not task_exists:
        raise NOT_FOUND
    if not is_participant:
        raise FORBIDDEN
    if completed:
        raise COMPLETED_ERROR
    return response_read


# @router.post("/{id}/response")
# async def create_response(id: str, response: TaskResponse):
#     ...
