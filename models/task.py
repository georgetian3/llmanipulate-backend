from typing import Hashable

from sqlmodel import JSON, Column, Field, SQLModel

from models.task_config.base_component import ComponentIdType
from models.task_config.responses import ComponentResponseType
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


class TaskResponseCreate(SQLModel):
    task: TaskID = Field(primary_key=True, foreign_key="task.id")
    draft: bool = False
    response: dict[ComponentIdType, ComponentResponseType] = Field(sa_column=Column(JSON))

    def validate_response(self, task_config: TaskConfig) -> bool:
        for component in task_config.components:
            component_response = self.response.get(component.id)
            if component_response is None:
                if self.draft:
                    continue
                print("Missing response for component:", component.id)
                return False
            if not component.validate_response(component_response):
                return False
        return True


class TaskResponse(TaskResponseCreate, table=True):
    creator: UserID = Field(primary_key=True, foreign_key="user.id")
