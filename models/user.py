from uuid import uuid4
from pydantic import UUID4
from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from models.mixins import OrmMixin
from models.models import UuidId

UserID = UUID4 | None


class TaskAddMixin(SQLModel):
    tasks_add: list[UUID4] = Field([], description="Tasks to add this user to")


class UserBase(OrmMixin):
    attributes: dict = Field({}, sa_column=Column(JSON))
    active: bool = Field(
        True, description="Whether this user is allowed to login and submit responses"
    )


class UserRead(UserBase, UuidId):
    is_admin: bool = False


class UserCreate(UserBase, TaskAddMixin):
    id: UUID4 | None = Field(primary_key=True, default=uuid4)


class UserUpdate(UserCreate, TaskAddMixin, UuidId):
    tasks_remove: list[UUID4] = Field(
        [], description="Tasks tasks to remove this user from"
    )


class User(UserUpdate, table=True): ...
