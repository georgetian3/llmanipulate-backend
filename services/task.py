from typing import List

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from models.database import get_session
from models.models import NewTask, Task


async def create_task(new_task: NewTask) -> Task:
    task = Task(**new_task.model_dump())
    async with get_session() as session:
        session.add(task)
        await session.commit()
        await session.refresh(task)
    return task


async def get_all_tasks() -> List[Task]:
    async with get_session() as session:
        return list(
            (
                await session.execute(select(Task).options(joinedload(Task.user)))
            ).scalars()
        )
