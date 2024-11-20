from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class NewUser(SQLModel, table=False):
    demographics: dict = Field(default_factory=dict, sa_column=Column(JSON))
    personality: dict = Field(default_factory=dict, sa_column=Column(JSON))
    task_type: str = Field(nullable=False)
    agent_type: str = Field(nullable=False)


class User(NewUser, table=True):  # contains fields common for all user-related models
    id: str = Field(primary_key=True)
    is_admin: bool


class Response(
    SQLModel, table=True
):  # We probably want a table to store user responses?
    id: int | None = Field(primary_key=True, exclude=True)
    task_id: int
    user_id: str = Field(foreign_key="user.id")
    time_created: datetime
    initial_scores: dict = Field(default_factory=dict, sa_column=Column(JSON))
    conv_history: dict = Field(default_factory=dict, sa_column=Column(JSON))
    final_scores: dict = Field(default_factory=dict, sa_column=Column(JSON))


class LLMPrompt(BaseModel):
    # TODO: complete model
    user_id: str
    prompt: str


class LLMResponse(BaseModel):
    # TODO: complete model
    response: str


class ErrorResponse(BaseModel):
    detail: str
