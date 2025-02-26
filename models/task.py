from sqlmodel import JSON, Column, Field, SQLModel

from models.models import CreatedMixin, SaveMixin, UpdatedMixin
from models.task_config.base_component import ComponentIdType
from models.task_config.responses import ComponentResponseType
from models.task_config.task_config import TaskConfig
from models.user import UserID

TaskID = int


class TaskBase(SaveMixin):
    id: TaskID | None = Field(primary_key=True)
    creator: UserID = Field(foreign_key="user.id", ondelete="CASCADE")
    config: TaskConfig = Field(sa_column=Column(JSON))
    public: bool = False


class TaskRead(TaskBase): ...


class Task(TaskBase, table=True): ...


class TaskParticipant(SaveMixin, table=True):
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
    CreatedMixin, UpdatedMixin, TaskResponseCreate, SaveMixin, table=True
):
    __tablename__ = "task_response"
    user: UserID = Field(primary_key=True, foreign_key="user.id", ondelete="CASCADE")
