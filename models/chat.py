from datetime import UTC, datetime
from typing import Final
from uuid import uuid4

from pydantic import UUID4, BaseModel
from sqlalchemy import JSON, Column, DateTime, ForeignKeyConstraint
from sqlmodel import Field, SQLModel

from models.mixins import OrmMixin

NULL_UUID4: Final[UUID4] = UUID4("00000000-0000-4000-8000-000000000000")

# ChatParticipant
class ChatParticipantBase(SQLModel):
    name: str


class ChatParticipantRead(ChatParticipantBase):
    active: bool
    typing: bool


class ChatParticipant(OrmMixin, ChatParticipantBase, table=True):
    user_id: UUID4 = Field(NULL_UUID4, primary_key=True, foreign_key="user.id", ondelete="CASCADE")
    agent_id: str = Field("", primary_key=True)
    chat_id: UUID4 = Field(primary_key=True, foreign_key="chat.id", ondelete="CASCADE")


# ChatMessage
class ChatMessageRead(SQLModel):
    id: UUID4
    message: str
    timestamp: datetime
    sender: str
    chat_id: UUID4


class ChatMessageReadAdmin(SQLModel):
    id: UUID4
    message: str
    timestamp: datetime
    sender_id: str
    sender_display_name: str
    chat_id: UUID4


class ChatMessage(OrmMixin, table=True):
    id: UUID4 = Field(primary_key=True, default_factory=uuid4)
    message: str
    chat_id: UUID4
    user_id: UUID4 = NULL_UUID4
    agent_id: str = ""
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True)),
    )
    __table_args__ = (
        ForeignKeyConstraint(
            ["chat_id", "user_id", "agent_id"],
            ["chatparticipant.chat_id", "chatparticipant.user_id", "chatparticipant.agent_id"],
            ondelete="CASCADE",
        ),
    )

# Chat
class ChatReadAdmin(BaseModel): # for admin view
    id: UUID4
    component_id: str
    messages: list[ChatMessageReadAdmin]


class Chat(OrmMixin, table=True):
    id: UUID4 = Field(primary_key=True, default_factory=uuid4)
    task_id: UUID4 = Field(foreign_key="task.id", ondelete="CASCADE")
    component_id: str
    order: list[str] = Field(
        [],
        sa_column=Column(JSON),
        description="Order of the chat participants."
        "If the participant is an agent, the order will contain its ID as specified in the task config"
        "If the participant is a user, the order will contain the user's ID"
        "E.g. if the order within the task config is ['agent-gpt3', 'human', 'agent-gpt4o', 'human', 'agent-deepseek01']"
        "Then this order might contain ['agent-gpt3', '10fe6383-d36a-4e0e-b281-9db043484a0a', 'agent-gpt4o', '642ad147-8788-480d-86a1-d9fe9c893cc3', 'agent-deepseek01']",
    )


# Websocket
class WebsocketReceive(BaseModel):
    typing: bool
    message: str


class WebsocketSend(BaseModel):
    chat_id: UUID4 = ""
    turn: str = ""
    messages: list[ChatMessageRead] = []
    me: str = ""
    participants: list[ChatParticipantRead] = []
    error: str = ""
