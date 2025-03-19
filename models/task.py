from datetime import UTC, datetime
from uuid import uuid4

from pydantic import UUID4, field_validator
from sqlalchemy import DateTime
from sqlmodel import JSON, Column, Field, SQLModel

from models.mixins import OrmMixin
from models.task_config.task_config import TaskConfig


class TaskBase(SQLModel):
    config: TaskConfig = Field(sa_column=Column(JSON))

    def parse_config(self):
        self.config = TaskConfig.model_validate(self.config)


class TaskCreate(TaskBase): ...


class TaskRead(TaskBase):
    id: UUID4


class TaskReadParticipant(TaskRead):
    completed: bool

    @field_validator("config", mode="after")
    @classmethod
    def remove_secrets(cls, config: TaskConfig) -> TaskConfig:
        for component in config.components:
            if component.type == "chat":
                component.agents = []
        return config


class Task(OrmMixin, TaskRead, table=True):
    id: UUID4 = Field(primary_key=True, default_factory=uuid4)
    public: bool
    created_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True)),
    )
