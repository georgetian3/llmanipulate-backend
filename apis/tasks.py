from fastapi import APIRouter

from models.task_config import TaskConfig, sample_task_config


router = APIRouter(prefix="/tasks")


@router.get("/{id}", response_model=TaskConfig)
async def get_task(id: str):
    return sample_task_config


# @router.post("/{id}/response")
# async def create_response(id: str, response: TaskResponse):
#     ...
