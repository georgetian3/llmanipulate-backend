import pytest

from models.task import Task
from models.task_config.base_component import Translations
from models.task_config.task_config import TaskConfig
from models.user import UserCreate
from services.tasks import get_task
from services.user import create_user
from tests.utils import reset_db


@pytest.mark.asyncio
@reset_db
async def test_get_tasks():
    user = await create_user(UserCreate(
        email="me@example.com",
        password="secret",
    ))
    task = await Task(
        id=0,
        creator=user.id,
        config=TaskConfig(name="test task config")
    ).save()

    task, authorized = await get_task(task.id, user.id)
    print(task, authorized)