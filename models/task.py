from __future__ import annotations

from uuid import uuid4

from pydantic import UUID4, BaseModel, ValidationInfo, field_validator, model_validator
from sqlmodel import JSON, Column, Field, SQLModel

from models.mixins import CreatedMixin, OrmMixin, UpdatedMixin
from models.task_config.responses import ComponentResponseType
from models.task_config.task_config import TaskConfig
from models.user import OptionalUserID


class TaskBase(BaseModel):
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
    def remove_secrets(cls, config: TaskConfig):
        for component in config.components:
            if component.type == "chat":
                component.agents = []
        return config


class Task(OrmMixin, TaskBase, table=True):

    id: UUID4 = Field(primary_key=True, default_factory=uuid4)
    public: bool


class TaskParticipantBase(OrmMixin):
    task: UUID4 = Field(primary_key=True, foreign_key="task.id", ondelete="CASCADE")
    user: UUID4 = Field(primary_key=True, foreign_key="user.id", ondelete="CASCADE")


class TaskParticipantRead(TaskParticipantBase):
    completed: bool


class TaskParticipantCreate(BaseModel):
    user: OptionalUserID


class TaskParticipant(TaskParticipantBase, table=True): ...


TaskResponseType = dict[str, ComponentResponseType]


class TaskResponseBase(SQLModel):
    response: TaskResponseType = Field(sa_column=Column(JSON))

    @model_validator(mode="after")
    def validate_response(self, info: ValidationInfo) -> TaskResponseBase:
        if not info.context:
            return self
        task_config = TaskConfig.model_validate(info.context["task_config"])
        # for each component in a task config
        for component in task_config.components:
            # get the response for this compoment
            component_response = self.response.get(component.id)
            # if the response for this component is missing
            if component_response is None:
                # new response cannot have less answers than the old response
                # optional components can be ignored
                if not component.optional:
                    raise ValueError(f"Component '{component.id}': missing response")
            else:
                # let each component validate the type/structure of its response
                try:
                    component.validate_response(component_response)
                except ValueError as e:
                    raise ValueError(f"Component '{component.id}': {e}") from e
        return self


class TaskResponseCreate(TaskResponseBase): ...


class TaskResponseRead(CreatedMixin, UpdatedMixin, TaskResponseBase):
    task: UUID4 = Field(primary_key=True, foreign_key="task.id", ondelete="CASCADE")
    user: UUID4 = Field(primary_key=True, foreign_key="user.id", ondelete="CASCADE")


class TaskResponse(TaskResponseRead, OrmMixin, table=True):
    __tablename__ = "task_response"
