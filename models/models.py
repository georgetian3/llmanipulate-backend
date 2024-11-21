from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel
import pytz

class NewUser(SQLModel, table=False):
    demographics: dict = Field(default_factory=dict, sa_column=Column(JSON))
    personality: dict = Field(default_factory=dict, sa_column=Column(JSON))
    task_type: str = Field(nullable=False)
    agent_type: str = Field(nullable=False)


class User(NewUser, table=True):  # contains fields common for all user-related models
    id: str = Field(primary_key=True)
    is_admin: bool


class NewResponse(SQLModel, table=False):
    task_id: int
    initial_scores: dict = Field(default_factory=dict, sa_column=Column(JSON))
    conv_history: dict = Field(default_factory=dict, sa_column=Column(JSON))
    final_scores: dict = Field(default_factory=dict, sa_column=Column(JSON))


class Response(NewResponse, table=True):
    id: int | None = Field(primary_key=True, exclude=True)
    user_id: str = Field(foreign_key="user.id")
    time_created: datetime


class LLMPrompt(BaseModel):
    # TODO: complete model
    user_id: str
    task_id: int
    prompt: str


class LLMResponse(BaseModel):
    # TODO: complete model
    error: str | None = None
    response: str


class ErrorResponse(BaseModel):
    detail: str
