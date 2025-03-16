from datetime import datetime
from uuid import uuid4

from pydantic import UUID4, BaseModel
from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from models.mixins import OrmMixin
from models.task_config.chat import AgentConfig


class ChatParticipantBase(SQLModel):
    chat: UUID4 = Field(foreign_key="chathistory.id", ondelete="CASCADE")


class ChatParticipantRead(ChatParticipantBase):
    name: str
    active: bool


class Agent(AgentConfig, table=True):
    id: UUID4 = Field(primary_key=True, default_factory=uuid4)


class ChatParticipant(ChatParticipantBase, table=True):
    id: UUID4 = Field(primary_key=True, default_factory=uuid4)
    user: UUID4 | None = Field(foreign_key="user.id")
    agent: UUID4 | None = Field(foreign_key="agent.id")


class ChatMessageRead(SQLModel):
    id: UUID4
    chat: UUID4 = Field(foreign_key="chathistory.id", ondelete="CASCADE")
    message: str
    sender: UUID4
    timestamp: datetime


class ChatMessage(ChatMessageRead, OrmMixin, table=True):
    id: UUID4 = Field(primary_key=True, default_factory=uuid4)
    sender: UUID4 = Field(foreign_key="chatparticipant.id")


class ChatRead(BaseModel):
    id: UUID4
    messages: list[ChatMessageRead]


class Chat(OrmMixin, table=True):
    id: UUID4 = Field(primary_key=True, default_factory=uuid4)
    task: UUID4 = Field(foreign_key="task.id", ondelete="CASCADE")
    component: str


class WebsocketReceive(BaseModel):
    user: UUID4
    task: UUID4
    component: str
    typing: bool
    message: str


class WebsocketSend(BaseModel):
    turn: UUID4 | None = None
    messages: list[ChatMessageRead] | None = None
    typing: list[UUID4] | None = None
    participants: list[ChatParticipant] | None = None
    error: str | None = None
