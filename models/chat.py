from datetime import datetime
from typing import List, Optional

from pydantic import UUID4, BaseModel
from sqlmodel import Field, SQLModel


from models.mixins import OrmMixin
from models.models import UuidId


class ChatParticipant(SQLModel, table=True):
    
    chat: UUID4 = Field(
        primary_key=True, foreign_key="chathistory.id", ondelete="CASCADE"
    )
    participant: UUID4 = Field(primary_key=True)


class ChatMessageCreate:
    message: str


class ChatMessageRead(UuidId, ChatMessageCreate):
    chat: UUID4 = Field(foreign_key="chathistory.id", ondelete="CASCADE")
    sender_uuid: Optional[UUID4] = Field(default=None, foreign_key="user.id", ondelete="CASCADE")  # ✅ Human sender
    sender_agent: Optional[str] = Field(default=None, max_length=50)  # ✅ Agent sender (no FK)
    timestamp: datetime


class ChatMessage(ChatMessageRead, OrmMixin, table=True): ...


class ChatHistoryBase(UuidId): ...


class ChatHistoryRead(UuidId):
    messages: list[ChatMessageRead]


class ChatHistory(ChatHistoryBase, OrmMixin, table=True): ...

