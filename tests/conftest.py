from uuid import UUID

import pytest

from models.database import _DATABASE
from models.task import Task, TaskParticipant
from models.task_config.base_component import Translations
from models.task_config.components import FreeText
from models.task_config.task_config import ComponentGroup, TaskConfig, TaskPage
from models.user import User, UserCreate
from services.user import create_user


@pytest.fixture
async def sample_data() -> tuple[User, User, Task, TaskParticipant]:
    await _DATABASE.reset()

    sample_creator = await create_user(
        UserCreate(email="sample_creator@example.com", password="secret")
    )
    sample_participant = await create_user(
        UserCreate(email="sample_participant@example.com", password="secret")
    )

    sample_task = Task(
        id=UUID("b9b5251db0c6485ba33f94e416aa77f0"),
        creator=sample_creator.id,
        config=TaskConfig(
            name=Translations(languages={"en": "sample task"}),
            pages=[
                TaskPage(
                    component_groups=[
                        ComponentGroup(components=[FreeText(id="1"), FreeText(id="2")])
                    ]
                )
            ],
        ),
    )

    try:
        await sample_task.save()
    except:
        ...

    sample_task_participant = TaskParticipant(
        task=sample_task.id, user=sample_participant.id
    )
    try:
        await sample_task_participant.save()
    except:
        ...

    return sample_creator, sample_participant, sample_task, sample_task_participant
