from copy import deepcopy
from datetime import datetime
from typing import Any, Optional, Type

from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo
from sqlalchemy import JSON, Column, Tuple
from sqlmodel import Field, SQLModel


class NewUser(SQLModel, table=False):
    demographics: dict = Field(default_factory=dict, sa_column=Column(JSON))
    personality: dict = Field(default_factory=dict, sa_column=Column(JSON))
    task_type: str = Field(nullable=False)
    agent_type: str = Field(nullable=False)


class User(NewUser, table=True):  # contains fields common for all user-related models
    id: str = Field(primary_key=True)
    is_admin: bool

# PartialUser is used in updating a user where `id` is the only required field to be sent in the request
class PartialUser(BaseModel):
    id: str
    demographics: dict | None = Field(None)
    personality: dict | None = Field(None)
    task_type: str | None = Field(None)
    agent_type: str | None = Field(None)

class NewResponse(SQLModel, table=False):
    task_id: int
    initial_scores: dict = Field(default_factory=dict, sa_column=Column(JSON))
    conv_history: dict = Field(default_factory=dict, sa_column=Column(JSON))
    final_scores: dict = Field(default_factory=dict, sa_column=Column(JSON))


class Response(NewResponse, table=True):
    id: int | None = Field(primary_key=True, exclude=True)
    user_id: str = Field(foreign_key="user.id")
    time_created: datetime


class LLMInput(BaseModel):
    # TODO: complete model
    user_id: str
    task_id: int
    message: str


class LLMResponse(BaseModel):
    error: str | None = None
    response: str


class ErrorResponse(BaseModel):
    detail: str