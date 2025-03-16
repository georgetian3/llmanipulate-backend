from models.database import _DATABASE
from models.task import TaskCreate
from models.task_config.base_component import Translations
from models.task_config.task_config import TaskConfig
from services.tasks import create_task


async def test_create_task() -> None:
    await _DATABASE.reset()

    task_create = TaskCreate(
        config=TaskConfig(
            name=Translations(languages={"en": "sample task name"}),
            pages=[],
            public=True,
        )
    )
    task_read = await create_task(task_create)
    assert (
        isinstance(task_read.config, TaskConfig)
        and task_read.config == task_create.config
        and task_read.public == task_create.config.public
    )
