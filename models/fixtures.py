from uuid import UUID

from models.task import Task, TaskParticipant
from models.task_config.task_config import TaskConfig
from models.user import UserCreate
from services.user import create_user


async def load_fixtures():
    sample_creator = await create_user(
        UserCreate(email="sample_creator@example.com", password="secret")
    )
    sample_participant = await create_user(
        UserCreate(email="sample_participant@example.com", password="secret")
    )

    sample_task = Task(
        id=UUID("b9b5251db0c6485ba33f94e416aa77f0"),
        creator=sample_creator.id,
        config=TaskConfig(name="sample task", pages=[]),
    )

    try:
        await sample_task.save()
    except:
        sample_task = await Task.get(sample_task.id)

    sample_task_participant = TaskParticipant(
        task=sample_task.id, user=sample_participant.id
    )
    try:
        await sample_task_participant.save()
    except:
        ...
