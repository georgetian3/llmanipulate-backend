from typing import Literal, Self

from pydantic import BaseModel, field_validator, model_validator
from sqlmodel import Field

from services.agents.base_agent import BaseAgent


def get_subclasses(cls):
    for subclass in cls.__subclasses__():
        yield from get_subclasses(subclass)
        yield subclass


AGENT_TYPE_MAP: dict[str, type[BaseAgent]] = {
    cls.__name__: cls for cls in get_subclasses(BaseAgent)
}


class AgentConfig(BaseModel):
    id: str = Field(
        description="Similar to component ID, must be unique within a task, used to correlate chat messages with the agent that produced it."
    )
    type: Literal[tuple(AGENT_TYPE_MAP.keys())]  # type: ignore
    display_name: str | None = Field(None,
        description="The name that will be displayed in chat, leave empty to make the agent look like a human user"
    )
    attributes: dict = Field({}, description="Attributes specific to the agent type")

    def create(self) -> BaseAgent:
        return AGENT_TYPE_MAP[self.type](self)

    @model_validator(mode="after")
    def validate_response(self) -> Self:
        AGENT_TYPE_MAP[self.type].attribute_model.model_validate(self.attributes)
        return self
