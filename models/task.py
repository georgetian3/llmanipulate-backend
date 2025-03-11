from __future__ import annotations

from uuid import uuid4

from pydantic import UUID4, BaseModel, ValidationInfo, model_validator
from sqlmodel import JSON, Column, Field, SQLModel

from models.mixins import CreatedMixin, OrmMixin, UpdatedMixin
from models.task_config.base_component import ComponentIdType
from models.task_config.responses import ComponentResponseType
from models.task_config.task_config import TaskConfig
from models.user import UserID

TaskID = UUID4


class TaskBase(OrmMixin):
    id: TaskID = Field(primary_key=True, default_factory=uuid4)
    config: TaskConfig = Field(sa_column=Column(JSON))


class TaskRead(TaskBase): ...


class Task(TaskBase, table=True): ...


class TaskParticipant(OrmMixin, table=True):
    task: TaskID = Field(primary_key=True, foreign_key="task.id", ondelete="CASCADE")
    user: UserID = Field(primary_key=True, foreign_key="user.id", ondelete="CASCADE")


TaskResponseType = dict[ComponentIdType, ComponentResponseType]


class TaskResponseBase(SQLModel):
    response: TaskResponseType = Field(sa_column=Column(JSON))

    @model_validator(mode="after")
    def validate_response(self, info: ValidationInfo) -> TaskResponseBase:
        if not info.context:
            return self
        task_config = TaskConfig.model_validate(info.context["task_config"])
        existing_response = (
            TaskResponse.model_validate(x)
            if (x := info.context["existing_response"])
            else None
        )

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
