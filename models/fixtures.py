from models.task import Task
from models.task_config.task_config import TaskConfig
from models.user import UserCreate
from services.user import create_user


async def load_fixtures():
    sample_user = await create_user(
        UserCreate(email="sample_user@example.com", password="secret")
    )
    sample_task = await Task(
        creator=sample_user.id,
        config=TaskConfig(name="sample task"),
    ).save()
