from datetime import datetime

from pydantic import UUID4, BaseModel
from sqlmodel import Field, SQLModel

from models.models import SaveMixin, UuidId


class ChatParticipant(SQLModel, table=True):
    
    chat: UUID4 = Field(
        primary_key=True, foreign_key="chathistory.id", ondelete="CASCADE"
    )
    participant: UUID4 = Field(primary_key=True)


class ChatMessageCreate:
    message: str


class ChatMessageRead(UuidId, ChatMessageCreate):
    chat: UUID4 = Field(foreign_key="chathistory.id", ondelete="CASCADE")
    sender: UUID4 = Field(foreign_key="user.id", ondelete="CASCADE")
    timestamp: datetime


class ChatMessage(ChatMessageRead, SaveMixin, table=True): ...


class ChatHistoryBase(UuidId): ...


class ChatHistoryRead(UuidId):
    messages: list[ChatMessageRead]


class ChatHistory(ChatHistoryBase, SaveMixin, table=True): ...
