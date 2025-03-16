from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import UUID4, ValidationError

import services.responses
import services.tasks
from apis.auth import current_admin, current_user
from apis.utils import create_docs
from models.task import (
    Task,
    TaskCreate,
    TaskParticipantCreate,
    TaskParticipantRead,
    TaskRead,
    TaskResponseCreate,
    TaskResponseRead,
)
from models.task_config.examples import sample_task_config
from models.user import User

router = APIRouter(prefix="/tasks")


NOT_FOUND = HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
FORBIDDEN = HTTPException(status.HTTP_403_FORBIDDEN, "Forbidden")
CLIENT_ERROR = HTTPException(status.HTTP_400_BAD_REQUEST, "Client error")


@router.get("/", response_model=list[TaskRead])
async def get_tasks(_: User = Depends(current_admin)):
    return await Task.all()


@router.post("/", response_model=TaskRead, dependencies=[Depends(current_admin)])
async def create_task(task_create: TaskCreate):
    return await services.tasks.create_task(task_create)


@router.get(
    "/{task_id}", response_model=TaskRead, responses=create_docs(FORBIDDEN, NOT_FOUND)
)
async def get_task(task_id: UUID4, user_id: UUID4 = Depends(current_user)):
    user = await User.get(user_id)
    if user and user.is_admin:
        task = await Task.get(task_id)
        if not task:
            raise NOT_FOUND
        return TaskRead.model_validate(task)

    task, authorized = await services.tasks.get_participant_task(task_id, user_id)
    if task is None:
        raise NOT_FOUND
    if not authorized:
        raise FORBIDDEN
    return task


@router.delete("/{task_id}", dependencies=[Depends(current_admin)])
async def delete_task(task_id: UUID4):
    await services.tasks.delete_task(task_id)


@router.get("/sample", response_model=TaskRead)
async def get_sample_task():
    return sample_task_config


@router.get(
    "/{task_id}/responses",
    response_model=list[TaskResponseRead],
    dependencies=[Depends(current_admin)],
)
async def get_task_responses(task_id: UUID):
    return await services.responses.get_responses(task_id)


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


@router.get(
    "/{task_id}/participants",
    response_model=list[TaskParticipantRead],
    dependencies=[Depends(current_admin)],
)
async def get_task_participants(task_id: UUID4):
    return await services.tasks.get_task_participants(task_id)


@router.put(
    "/{task_id}/participants",
    response_model=TaskParticipantRead,
    dependencies=[Depends(current_admin)],
)
async def create_task_participant(
    task_id: UUID4, task_participant_create: TaskParticipantCreate
):
    tp = await services.tasks.create_participant(task_id, task_participant_create.user)
    if not tp:
        raise NOT_FOUND
    return tp
