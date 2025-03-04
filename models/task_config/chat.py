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
    # the chat history will be substituted into the string {chat_history}
    prompt: str


class Chat(BaseComponent):
    type: Literal["chat"] = "chat"
    label: Translations | None = None
    agents: list[Agent] = []
    order: list[UUID4] | None = []
    all_users: bool

    def validate_response(self, response):
        return None