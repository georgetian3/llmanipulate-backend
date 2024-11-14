import asyncio
from datetime import datetime

from config import Config
from models.database import Database
from models.models import NewTask, NewUser
from services.task import TaskService
from services.user import UserService

db = Database(Config().DATABASE)


async def main():
    await db.reset()
    user_service = UserService(Config(), db)

    new_user = NewUser(
        demographics={"a": "b"},
        personality={"mb": "ti"},
        task_type="task_type",
        agent_type="agent_type",
    )

    user = await user_service.create_user(new_user)
    # print(user)

    task_service = TaskService(Config(), db)
    new_task = NewTask(
        task_name="test task name",
        initial_scores={"a": "b"},
        conv_history={"d": "e"},
        final_scores={"f": "g"},
        timestamp=datetime.now(),
        user_id=user.id,
    )
    await task_service.create_task(new_task)
    task = (await task_service.get_all_tasks())[0]
    print(task)
    users = await user_service.get_all_users()
    print(users)


asyncio.run(main())


# from fastapi import FastAPI

# app = FastAPI()


# @app.get("/")
# async def root():
#     return {"message": "Hello World"}
