from models.task_config.base_component import Translations
from models.task_config.task_config import TaskConfig

SAMPLE_TASK_CONFIG = TaskConfig(
    name=Translations(languages={"en": "sample task name"}),
    pages=[],
    public=True,
)
