from uuid import UUID

from models.task import Task, TaskParticipant
from models.task_config.examples import sample_task_config
from models.task_config.task_config import TaskConfig
from models.user import User, UserCreate
from services.user import create_participant


async def load_fixtures():
    user_uuids = [
        "73cf13cc-09a2-4f11-8d9b-50e34a7bbce0",
        "d3e9eaec-3468-406d-af7c-fe1c87f07f1c",
    ]
    sample_users = []
    for user_uuid in user_uuids:
        try:
            user = await create_participant(UserCreate(id=UUID(user_uuid)))
        except:
            user = await User.get(UUID(user_uuid))
        sample_users.append(user)

    sample_task_configs = [
        TaskConfig(**sample_task_config.model_dump()),
        TaskConfig(**sample_task_config.model_dump()),
        TaskConfig(**sample_task_config.model_dump()),
    ]
    sample_task_configs[0].name.languages["en"] = "Sample Task 1"
    sample_task_configs[1].name.languages["en"] = "Sample Task 2"
    sample_task_configs[2].name.languages["en"] = "Sample Task 3"
    sample_task_configs[2].login_required = False

    sample_tasks = [
        Task(
            id=UUID("642ad1478788480d86a1d9fe9c893cc3"),
            config=sample_task_configs[0],
        ),
        Task(
            id=UUID("abec92d8f34a4df9b4df26494f6bb760"),
            config=sample_task_configs[1],
        ),
        Task(
            id=UUID("10fe6383d36a4e0eb2819db043484a0a"),
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
        TaskParticipant(task=sample_tasks[0].id, user=sample_users[1].id),
        TaskParticipant(task=sample_tasks[1].id, user=sample_users[1].id),
        TaskParticipant(task=sample_tasks[1].id, user=sample_users[0].id),
        TaskParticipant(task=sample_tasks[2].id, user=sample_users[0].id),
    ]

    for tp in sample_task_participants:
        try:
            await tp.save()
        except:
            continue
