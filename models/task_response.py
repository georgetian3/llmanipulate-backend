from typing import Self

from pydantic import UUID4, ValidationInfo, model_validator
from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from models.mixins import CreatedMixin, OrmMixin
from models.task_config.responses import ComponentResponseType
from models.task_config.task_config import TaskConfig

TaskResponseType = dict[str, ComponentResponseType]


class TaskResponseBase(SQLModel):
    response: TaskResponseType = Field(sa_column=Column(JSON))

    @model_validator(mode="after")
    def validate_response(self, info: ValidationInfo) -> Self:
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
                # chat optional components can be ignored
                if not component.optional and component.type != "chat":
                    raise ValueError(f"Component '{component.id}': missing response")
            else:
                # let each component validate the type/structure of its response
                try:
                    component.validate_response(component_response)
                except ValueError as e:
                    raise ValueError(f"Component '{component.id}': {e}") from e
        return self


class TaskResponseCreate(TaskResponseBase): ...


class TaskResponseRead(CreatedMixin, TaskResponseBase):
    task: UUID4 = Field(primary_key=True, foreign_key="task.id", ondelete="CASCADE")
    user_id: UUID4 = Field(primary_key=True, foreign_key="user.id", ondelete="CASCADE")


class TaskResponse(TaskResponseRead, OrmMixin, table=True):
    __tablename__ = "task_response"
