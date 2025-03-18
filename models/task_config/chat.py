from typing import Literal, Self

from pydantic import model_validator
from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from models.task_config.base_component import BaseComponent, Translations


class AgentConfig(SQLModel):
    id: str = Field(
        description="Similar to component ID, must be unique within this task, used to correlate chat messages with the agent that produced it."
    )
    display_name: str | None = Field(
        description="The name that will be displayed in chat, leave empty to make the agent look like a human user"
    )
    model_name: str = ""
    endpoint: str = ""
    api_key: str = ""
    attributes: dict = Field({}, sa_column=Column(JSON))
    base_prompt: str = ""
    # the chat history will be substituted into the string {chat_history}
    prompt: str = ""


class ChatConfig(BaseComponent):
    type: Literal["chat"] = "chat"
    label: Translations | None = None
    agents: list[AgentConfig] = []
    order: list[int | Literal["human"]] | None = Field(
        [],
        description="Order of conversation, required if any agents are participating in the chat. Elements of this list are either an integer indicating the index (starting from 0) of the agent in the list `agents`, or the string 'human' to indicate a human's turn",
    )
    min_messages: int = Field(0, ge=0)
    max_messages: int = Field(99999, ge=0)
    humans_required: int | None = Field(None, ge=0, description="Number of humans per chat, leave None for no limit")

    @model_validator(mode="after")
    def validate_model(self) -> Self:
        if self.min_messages > self.max_messages:
            raise ValueError("min_messages cannot be greater than max_messages")
        return self

    def validate_response(self, response):
        return None
