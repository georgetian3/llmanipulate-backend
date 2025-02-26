from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import UUID4

import services.tasks
from apis.utils import create_docs
from models.task import TaskRead, TaskResponseCreate, TaskResponseRead
from models.task_config.examples import sample_task_config
from models.user import User
from services.user import current_active_user

router = APIRouter(prefix="/tasks")


NOT_FOUND = HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
FORBIDDEN = HTTPException(status.HTTP_403_FORBIDDEN, "Forbidden")


@router.get("/{task_id}", response_model=TaskRead, responses=create_docs(FORBIDDEN))
async def get_task(task_id: UUID4, user: User = Depends(current_active_user)):
    task, authorized = await services.tasks.get_task(task_id, user.id)
    if not authorized:
        raise FORBIDDEN
    if task is None:
        raise NOT_FOUND
    return TaskRead.model_validate(task)


@router.get("/{task_id}/response", response_model=TaskResponseRead)
async def get_task_response(task_id: UUID4, user: User = Depends(current_active_user)):
    return sample_task_config


@router.post("/{task_id}/response", response_model=TaskResponseRead)
async def get_task_response(
    task_id: UUID4,
    response: TaskResponseCreate,
    user: User = Depends(current_active_user),
):
    return sample_task_config


# @router.post("/{id}/response")
# async def create_response(id: str, response: TaskResponse):
#     ...
