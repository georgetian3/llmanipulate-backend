from models.models import NewTask, Task
from services.base import BaseService


class TaskService(BaseService):
    async def create_task(self, new_task: NewTask) -> Task:
        task = Task(**new_task.model_dump())
        async with self._database.get_session() as session:
            session.add(task)
        return task
