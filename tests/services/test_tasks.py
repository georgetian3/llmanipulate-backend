from uuid import uuid4

import pytest

from models.task import Task, TaskParticipant
from models.task_config.base_component import Translations
from models.task_config.task_config import TaskConfig
from models.user import UserCreate
from services.tasks import get_task
from services.user import create_user
from tests.utils import reset_db


@pytest.mark.asyncio
@reset_db
async def test_get_tasks():
    creator = await create_user(
        UserCreate(
            email="creator@example.com",
            password="secret",
        )
    )
    participant = await create_user(
        UserCreate(
            email="participant@example.com",
            password="secret",
        )
    )
    task = await Task(
        creator=creator.id, config=TaskConfig(name="test task config")
    ).save()
    await TaskParticipant(task=task.id, user=participant.id).save()

    # user is task participant
    assert await get_task(task.id, participant.id) == (task, True)
    # user is task creator
    assert await get_task(task.id, creator.id) == (task, True)
    # user is neither
    assert await get_task(task.id, uuid4()) == (task, False)
    # task doesn't exist
    assert await get_task(uuid4(), uuid4()) == (None, None)
