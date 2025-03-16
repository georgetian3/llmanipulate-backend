from uuid import uuid4

from models.database import _DATABASE, get_session
from models.task import TaskCreate, TaskParticipant, TaskResponseCreate
from models.task_config.base_component import Translations
from models.task_config.task_config import TaskConfig
from models.user import UserUpsert
from services.responses import create_response
from services.tasks import create_task
from services.user import get_user_tasks, upsert_user
from tests.services.conftest import SAMPLE_TASK_CONFIG


async def test_upsert_user():
    await _DATABASE.reset()
    # test create
    task1 = await create_task(
        TaskCreate(
            config=TaskConfig(
                name=Translations(languages={"en": "sample private task"}),
                pages=[],
                public=False,
            )
        )
    )
    task2 = await create_task(
        TaskCreate(
            config=TaskConfig(
                name=Translations(languages={"en": "sample public task"}),
                pages=[],
                public=True,
            )
        )
    )
    user_upsert1 = UserUpsert(
        id=uuid4(),
        attributes={"test": "attribute"},
        active=True,
        tasks_add=[task1.id, task2.id, task1.id, task2.id],  # test dedup
    )
    user_read = await upsert_user(user_upsert1)
    assert (  # test all user fields are saved correctly
        user_read.id == user_upsert1.id
        and user_read.active == user_upsert1.active
        and user_read.attributes == user_upsert1.attributes
    )
    task_participants = await TaskParticipant.all()
    assert (
        len(task_participants) == 1
    )  # test dedup + only insert private tasks into task_participants
    assert (
        task_participants[0].user == user_read.id
        and task_participants[0].task == task1.id
    )

    await create_response(task1.id, response=TaskResponseCreate(response={}), user_id=user_read.id)

    # test get tasks

    user_tasks = await get_user_tasks(user_read.id)
    for task in user_tasks:
        if task.id == task1.id:
            assert task.completed
    assert set(task.id for task in user_tasks) == set([task1.id, task2.id])

    # test update

    user_upsert2 = UserUpsert(
        id=user_read.id,
        attributes={"updated": "attributes"},
        tasks_remove=[task1.id]
        # leave out active to test persistance of original value
    )
    user_read = await upsert_user(user_upsert2)
    assert (
        user_read.id == user_upsert2.id
        and user_read.active == user_upsert1.active
        and user_read.attributes == user_upsert2.attributes
    )
