import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from pydantic import UUID4, ValidationError

import services.responses
import services.tasks
from apis.utils import create_docs
from models.exceptions import ErrorResponse
from models.task import Task, TaskRead, TaskResponseCreate, TaskResponseRead
from models.task_config.examples import sample_task_config
from models.user import User
from services.user import current_active_user, current_superuser

router = APIRouter(prefix="/tasks")


NOT_FOUND = HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
FORBIDDEN = HTTPException(status.HTTP_403_FORBIDDEN, "Forbidden")
CLIENT_ERROR = HTTPException(status.HTTP_400_BAD_REQUEST, "Client error")


@router.get("/", response_model=list[TaskRead])
async def get_all_tasks(_: User = Depends(current_superuser)):
    return await Task.all()


@router.get("/{task_id}", response_model=TaskRead, responses=create_docs(FORBIDDEN))
async def get_task(task_id: UUID4, user: User = Depends(current_active_user)):
    task, authorized = await services.tasks.get_task(task_id, user.id)
    if task is None:
        raise NOT_FOUND
    if not authorized:
        raise FORBIDDEN
    return task


@router.get("/sample", response_model=TaskRead)
async def get_sample_task():
    return sample_task_config


@router.get("/{task_id}/response", response_model=TaskResponseRead)
async def get_task_response(task_id: UUID4, user: User = Depends(current_active_user)):
    return sample_task_config


@router.post(
    "/{task_id}/response",
    response_model=TaskResponseRead,
    responses=create_docs(NOT_FOUND, FORBIDDEN),
)
async def create_task_response(
    task_id: UUID4,
    response: TaskResponseCreate,
    user: User = Depends(current_active_user),
):
    try:
        (
            response_read,
            task_exists,
            is_participant,
        ) = await services.responses.create_response(task_id, response, user.id)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=jsonable_encoder(e.errors()))
    if not task_exists:
        raise NOT_FOUND
    if not is_participant:
        raise FORBIDDEN
    return response_read


# @router.post("/{id}/response")
# async def create_response(id: str, response: TaskResponse):
#     ...
