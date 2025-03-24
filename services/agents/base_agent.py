from typing import TYPE_CHECKING, ClassVar, Final, Type

from pydantic import BaseModel

from models.chat import ChatMessageRead

if TYPE_CHECKING:
    from models.task_config.agent import AgentConfig


class BaseAgentAttributes(BaseModel): ...


class BaseAgent:
    attribute_model: Final[Type[BaseModel]] = BaseAgentAttributes

    def __init__(self, config: "AgentConfig"):
        self.config = config
        self.attributes = self.attribute_model.model_validate(config.attributes)
        self.chat_history: list[ChatMessageRead] = []

    def set_chat_history(self, chat_history: list[ChatMessageRead]) -> None:
        self.chat_history = sorted(chat_history, key=lambda x: x.timestamp)

    async def get_response(self) -> str:
        raise NotImplementedError()
