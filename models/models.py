from datetime import datetime
from uuid import uuid4

from pydantic import UUID4, BaseModel
from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel

from models.user import User, UserID


class Demographic(SQLModel, table=False):
    age: int | None
    sex: bool  # TODO: update DEI


class UuidId(SQLModel):
    id: UUID4 = Field(primary_key=True, default_factory=uuid4)


class NewResponse(SQLModel, table=False):
    task_name: str
    initial_scores: dict = Field(default_factory=dict, sa_column=Column(JSON))
    conv_history: dict = Field(default_factory=dict, sa_column=Column(JSON))
    final_scores: dict = Field(default_factory=dict, sa_column=Column(JSON))
    user_id: UserID = Field(foreign_key="user.id")


class Response(NewResponse, table=True):
    id: int | None = Field(primary_key=True, exclude=True)
    time_created: datetime
    user: "User" = Relationship(back_populates="responses")  # Proper relationship


class LLMInput(BaseModel):
    user_id: str
    task_id: str
    message: str
    map: list


class LLMResponse(BaseModel):
    error: str | None = None
    response: str
    agent_data: dict


class ErrorResponse(BaseModel):
    detail: str


class ChatParticipant(SQLModel, table=True):
    chat: UUID4 = Field(primary_key=True, foreign_key="chathistory.id")
    participant: UUID4 = Field(primary_key=True)


class ChatMessage(UuidId, table=True):
    chat: UUID4 = Field(foreign_key="chathistory.id")
    sender: UUID4
    message: str
    timestamp: datetime


class ChatHistory(UuidId, table=True): ...


class ChatHistoryRead(BaseModel):
    id: UUID4
    messages: list[ChatMessage]
