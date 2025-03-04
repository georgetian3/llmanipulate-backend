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

class MyTasks(BaseModel):
    created: list[TaskRead]
    participating: list[TaskRead]

class Task(TaskBase, table=True):
    creator: UserID = Field(foreign_key="user.id", ondelete="CASCADE")


class TaskParticipant(OrmMixin, table=True):
    task: TaskID = Field(primary_key=True, foreign_key="task.id", ondelete="CASCADE")
    user: UserID = Field(primary_key=True, foreign_key="user.id", ondelete="CASCADE")


class TaskResponseBase(SQLModel):
    task: TaskID = Field(primary_key=True, foreign_key="task.id", ondelete="CASCADE")
    draft: bool = False
    response: dict[ComponentIdType, ComponentResponseType] = Field(
        sa_column=Column(JSON)
    )


class TaskResponseCreate(TaskResponseBase):
    def validate_response(self, task_config: TaskConfig) -> None:
        for component in task_config.components:
            component_response = self.response.get(component.id)
            if component_response is None:
                if self.draft:
                    continue
                raise ValueError(f"Missing response for component: {component.id}")
            component.validate_response(component_response)


class TaskResponseRead(TaskResponseBase): ...


class TaskResponse(
    CreatedMixin, UpdatedMixin, TaskResponseCreate, OrmMixin, table=True
):
    __tablename__ = "task_response"
    user: UserID = Field(primary_key=True, foreign_key="user.id", ondelete="CASCADE")
