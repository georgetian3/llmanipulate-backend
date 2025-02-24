from typing import Hashable

from sqlmodel import JSON, Column, Field, SQLModel

from models.task_config.task_config import TaskConfig
from models.user import UserID

TaskID = int

class Task(SQLModel, table=True):
    id: int | None = Field(primary_key=True)
    creator: UserID = Field(foreign_key="user.id")
    config: TaskConfig = Field(sa_column=Column(JSON))
    public: bool = False


class TaskParticipants(SQLModel, table=True):
    task: TaskID = Field(primary_key=True, foreign_key="task.id")
    user: UserID = Field(primary_key=True, foreign_key="user.id")


class TaskResponse(SQLModel, table=True):
    task: TaskID = Field(primary_key=True, foreign_key="task.id")
    creator: UserID = Field(primary_key=True, foreign_key="user.id")
    # response: dict[Hashable,]
