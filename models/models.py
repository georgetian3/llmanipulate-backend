from datetime import datetime
from typing import List, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel


class NewTask(SQLModel, table=False):
    task_name: str = Field(nullable=False)
    initial_scores: dict = Field(default_factory=dict, sa_column=Column(JSON))
    conv_history: dict = Field(default_factory=dict, sa_column=Column(JSON))
    final_scores: dict = Field(default_factory=dict, sa_column=Column(JSON))
    timestamp: datetime
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")


class Task(NewTask, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user: Optional["User"] = Relationship(back_populates="tasks")


class NewUser(SQLModel, table=False):
    demographics: dict = Field(default_factory=dict, sa_column=Column(JSON))
    personality: dict = Field(default_factory=dict, sa_column=Column(JSON))
    task_type: str = Field(nullable=False)
    agent_type: str = Field(nullable=False)


class User(NewUser, table=True):
    id: Optional[int] = Field(primary_key=True)
    user_code: str = Field(unique=True, nullable=False)
    tasks: List[Task] = Relationship(back_populates="user")
