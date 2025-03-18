from datetime import datetime
from uuid import uuid4

from pydantic import UUID4, BaseModel
from sqlalchemy import ForeignKeyConstraint
from sqlmodel import Field, SQLModel

from models.mixins import OrmMixin


# ChatParticipant
class ChatParticipantBase(SQLModel):
    name: str


class ChatParticipantRead(ChatParticipantBase):
    active: bool
    typing: bool


class ChatParticipant(ChatParticipantBase, table=True):
    user_id: UUID4 = Field(primary_key=True, foreign_key="user.id", ondelete="CASCADE")
    chat_id: UUID4 = Field(primary_key=True, foreign_key="chat.id", ondelete="CASCADE")


# ChatMessage
class ChatMessageRead(SQLModel):
    id: UUID4
    message: str
    timestamp: datetime
    sender: str
    chat_id: UUID4


class ChatMessage(ChatMessageRead, OrmMixin, table=True):
    id: UUID4 = Field(primary_key=True, default_factory=uuid4)
    chat_id: UUID4
    sender: UUID4

    __table_args__ = (
        ForeignKeyConstraint(
            ["chat_id", "sender"],
            ["chatparticipant.chat_id", "chatparticipant.user_id"],
            ondelete="CASCADE",
        ),
    )


# Chat
class ChatRead(BaseModel):
    id: UUID4
    messages: list[ChatMessageRead]


class Chat(OrmMixin, table=True):
    id: UUID4 = Field(primary_key=True, default_factory=uuid4)
    task_id: UUID4 = Field(foreign_key="task.id", ondelete="CASCADE")
    component_id: str


# Websocket
class WebsocketReceive(BaseModel):
    user: UUID4
    chat: UUID4
    typing: bool
    message: str


class WebsocketSend(BaseModel):
    turn: UUID4 | None = None
    chat_id: UUID4
    messages: list[ChatMessageRead] | None = None
    participants: list[ChatParticipantRead] | None = None
    error: str | None = None
