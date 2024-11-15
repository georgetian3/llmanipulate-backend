from typing import List

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from models.models import NewTask, Task
from services.base import BaseService


class TaskService(BaseService):
    async def create_task(self, new_task: NewTask) -> Task:
        task = Task(**new_task.model_dump())
        async with self._database.get_session() as session:
            session.add(task)
            await session.commit()
            await session.refresh(task)
        return task

    async def get_all_tasks(self) -> List[Task]:
        async with self._database.get_session() as session:
            return list(
                (
                    await session.execute(select(Task).options(joinedload(Task.user)))
                ).scalars()
            )
