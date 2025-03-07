from __future__ import annotations

from uuid import uuid4

from pydantic import UUID4, BaseModel, model_validator
from sqlmodel import JSON, Column, Field, SQLModel

from models.mixins import CreatedMixin, OrmMixin, UpdatedMixin
from models.task_config.base_component import ComponentIdType
from models.task_config.responses import ComponentResponseType
from models.task_config.task_config import TaskConfig
from models.user import UserID, UserRead

TaskID = UUID4


class TaskBase(OrmMixin):
    id: TaskID = Field(primary_key=True, default_factory=uuid4)
    config: TaskConfig = Field(sa_column=Column(JSON))
    public: bool = False


class TaskRead(TaskBase):
    creator: UserRead


class Task(TaskBase, table=True):
    creator: UserID = Field(foreign_key="user.id", ondelete="CASCADE")


class TaskParticipant(OrmMixin, table=True):
    task: TaskID = Field(primary_key=True, foreign_key="task.id", ondelete="CASCADE")
    user: UserID = Field(primary_key=True, foreign_key="user.id", ondelete="CASCADE")


class TaskResponseBase(SQLModel):
    draft: bool = False
    response: dict[ComponentIdType, ComponentResponseType] = Field(
        sa_column=Column(JSON)
    )


class TaskResponseCreate(TaskResponseBase): ...


class TaskResponseRead(CreatedMixin, UpdatedMixin, TaskResponseBase):
    task: TaskID = Field(primary_key=True, foreign_key="task.id", ondelete="CASCADE")
    user: UserID = Field(primary_key=True, foreign_key="user.id", ondelete="CASCADE")


class TaskResponse(TaskResponseRead, OrmMixin, table=True):
    __tablename__ = "task_response"


class MyTasks(BaseModel):
    created: list[TaskRead]
    participating: list[TaskRead]


class UserTasksWithResponsesParticipated(BaseModel):
    tasks: list[TaskRead]
    responses: list[TaskResponseRead]


class UserTasksWithResponses(BaseModel):
    created: list[TaskRead]
    participated: list[UserTasksWithResponsesParticipated]
