from typing import Literal

from pydantic import UUID4, BaseModel

from models.task_config.base_component import BaseComponent, Translations


class Participant(BaseModel):
    id: UUID4
    name: str


class Human(Participant):
    type: Literal["human"] = "human"


class Agent(Participant):
    type: Literal["agent"] = "agent"
    endpoint: str
    api_key: str
    prompt: str


class Chat(BaseComponent):
    type: Literal["chat"] = "chat"
    label: Translations | None = None
    participants: list[Participant] = []
    order: list[UUID4] | None = []
