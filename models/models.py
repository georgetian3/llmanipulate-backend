from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel


# class NewTask(SQLModel, table=False):
#     task_name: str = Field(nullable=False)
#     initial_scores: dict = Field(default_factory=dict, sa_column=Column(JSON))
#     conv_history: dict = Field(default_factory=dict, sa_column=Column(JSON))
#     final_scores: dict = Field(default_factory=dict, sa_column=Column(JSON))
#     time_created: datetime
#     user_id: Optional[int] = Field(default=None, foreign_key="user.id")


# class Task(NewTask, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     user: Optional["User"] = Relationship(back_populates="tasks")



# class User(BaseUser, table=True):  # the actual model to be stored in the db
#     id: Optional[int] = Field(primary_key=True)
#     user_code: str = Field(unique=True, nullable=False)
#     tasks: List[Task] = Relationship(back_populates="user")
#     # exclude=True if we want to remove this field when converting into JSON, i.e. returning via API
#     password_hash: str = Field(nullable=False, exclude=True)

class BaseUser(SQLModel, table=False):
    demographics: dict = Field(default_factory=dict, sa_column=Column(JSON))
    personality: dict = Field(default_factory=dict, sa_column=Column(JSON))
    task_type: str = Field(nullable=False)
    agent_type: str = Field(nullable=False)

class NewUser(SQLModel, table=False):
    creator_id: str # ensure only admin can create user


class User(BaseUser, table=True):  # contains fields common for all user-related models
    id: str = Field(primary_key=True)
    is_admin: bool


class Response(SQLModel, table=True):  # We probably want a table to store user responses?
    id: Optional[int] = Field(primary_key=True, exclude=True)
    task_id: int = Field(foreign_key="task.id")
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