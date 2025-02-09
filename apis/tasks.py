

from fastapi import APIRouter

from models.task_config import TaskConfig


router = APIRouter(prefix="tasks")

@router.get("/{id}", response_model=TaskConfig)
async def get_task(id: str):
    ...