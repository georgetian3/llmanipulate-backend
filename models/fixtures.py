from uuid import UUID

from models.task import Task, TaskParticipant
from models.task_config.examples import sample_task_config
from models.task_config.task_config import TaskConfig
from models.user import UserCreate
from services.user import create_user


async def load_fixtures():
    sample_users = [
        await create_user(
            UserCreate(email="sample_user1@example.com", password="secret")
        ),
        await create_user(
            UserCreate(email="sample_user2@example.com", password="secret")
        ),
        await create_user(
            UserCreate(email="sample_user3@example.com", password="secret")
        ),
        await create_user(
            UserCreate(email="sample_user4@example.com", password="secret")
        ),
        await create_user(
            UserCreate(email="sample_user5@example.com", password="secret")
        ),
    ]

    sample_task_configs = [
        TaskConfig(**sample_task_config.model_dump()),
        TaskConfig(**sample_task_config.model_dump()),
        TaskConfig(**sample_task_config.model_dump()),
    ]
    sample_task_configs[0].name.languages["en"] = "Sample Task 1"
    sample_task_configs[1].name.languages["en"] = "Sample Task 2"
    sample_task_configs[2].name.languages["en"] = "Sample Task 3"

    sample_tasks = [
        Task(
            id=UUID("b9b5251db0c6485ba33f94e416aa77f0"),
            creator=sample_users[0].id,
            config=sample_task_configs[0],
        ),
        Task(
            id=UUID("b9b5251db0c6485ba33f95e416aa77f0"),
            creator=sample_users[0].id,
            config=sample_task_configs[1],
        ),
        Task(
            id=UUID("b9b5251db0c6485ba33f96e416aa77f0"),
            creator=sample_users[1].id,
            config=sample_task_configs[2],
        ),
    ]

    for task in sample_tasks:
        try:
            await task.save()
        except:
            continue


    sample_task_participants = [
        TaskParticipant(task=sample_tasks[0].id, user=sample_users[0].id),
        TaskParticipant(task=sample_tasks[0].id, user=sample_users[1].id),
        TaskParticipant(task=sample_tasks[0].id, user=sample_users[2].id),
        TaskParticipant(task=sample_tasks[1].id, user=sample_users[3].id),
        TaskParticipant(task=sample_tasks[1].id, user=sample_users[4].id),
        TaskParticipant(task=sample_tasks[2].id, user=sample_users[0].id),
    ]

    for tp in sample_task_participants:
        try:
            await tp.save()
        except:
            continue
