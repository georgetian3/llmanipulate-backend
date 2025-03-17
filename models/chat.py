from datetime import datetime
from uuid import uuid4

from pydantic import UUID4, BaseModel
from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from models.mixins import OrmMixin


class ChatParticipantBase(SQLModel):
    chat: UUID4 = Field(primary_key=True, foreign_key="chat.id", ondelete="CASCADE")
    name: str


class ChatParticipantRead(ChatParticipantBase):
    active: bool
    typing: bool


class ChatParticipant(ChatParticipantBase, table=True):
    id: UUID4 = Field(primary_key=True)



class ChatMessageRead(SQLModel):
    id: UUID4
    chat: UUID4 = Field(foreign_key="chat.id", ondelete="CASCADE")
    message: str
    sender: UUID4
    timestamp: datetime


class ChatMessage(ChatMessageRead, OrmMixin, table=True):
    id: UUID4 = Field(primary_key=True, default_factory=uuid4)
    sender: UUID4 = Field(foreign_key="chatparticipant.id", ondelete="CASCADE")


class ChatRead(BaseModel):
    id: UUID4
    messages: list[ChatMessageRead]


class Chat(OrmMixin, table=True):
    id: UUID4 = Field(primary_key=True, default_factory=uuid4)
    task: UUID4 = Field(foreign_key="task.id", ondelete="CASCADE")
    component: str


class WebsocketReceive(BaseModel):
    user: UUID4
    chat: UUID4
    typing: bool
    message: str


class WebsocketSend(BaseModel):
    turn: UUID4 | None = None
    chat: UUID4
    messages: list[ChatMessageRead] | None = None
    participants: list[ChatParticipantRead] | None = None
    error: str | None = None
