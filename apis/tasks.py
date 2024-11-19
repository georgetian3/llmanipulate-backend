from fastapi import APIRouter

import services.user
from models.models import Task, NewTask

task_router = APIRouter()


# @task_router.post("/submit_task", response_model=Task)
# async def create_task(new_task: NewTask):
#     task = await services.task.create_task(new_task)
#     return task

# @task_router.get("/get_all_tasks", response_model=list[Task])
# async def get_all_tasks():
#     return await services.task.get_all_tasks()


