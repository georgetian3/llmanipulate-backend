from typing import Literal, Self

from pydantic import model_validator
from sqlmodel import Field

from models.task_config.agent import AgentConfig
from models.task_config.base_component import BaseComponent, Translations


class ChatConfig(BaseComponent):
    type: Literal["chat"] = "chat"
    label: Translations | None = None
    agents: list[AgentConfig] = []
    order: list[str] = Field(
        [],
        description="Order of conversation, required if any agents are participating in the chat."
        "Each element of this list is either an agent ID to indicate that agent's turn,"
        "or the string 'human' to indicate a human's turn. The number of `human`s in `order"
        "must match `humans_required` if `humans_required` is not None.",
    )
    min_messages: int = Field(
        0, ge=0, description="Minimum number of messages for a chat to be valid"
    )
    max_messages: int = Field(
        99999,
        ge=0,
        description="Maximum number of messages for a chat, the conversation will end after this many messages",
    )
    humans_required: int | None = Field(
        None, ge=0, description="Number of humans per chat, leave None for no limit"
    )

    @model_validator(mode="after")
    def validate_model(self) -> Self:
        if self.min_messages > self.max_messages:
            raise ValueError("min_messages cannot be greater than max_messages")
        agent_ids = {agent.id for agent in self.agents}
        if len(self.agents) != len(agent_ids):
            raise ValueError("Agent IDs must be unique")
        for participant in self.order:
            if participant != "human" and participant not in agent_ids:
                raise ValueError(f"Invalid agent ID: '{participant}'")
        if self.humans_required is None:
            if self.order or self.agents:
                raise ValueError(
                    "A chat with unlimited humans cannot have agents nor order"
                )
        elif (human_count := self.order.count("human")) != self.humans_required:
            raise ValueError(
                f"Order expected {self.humans_required} humans, got {human_count}"
            )
        return self

    def validate_response(self, _):
        return
