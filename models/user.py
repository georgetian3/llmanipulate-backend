from uuid import uuid4

from pydantic import UUID4, BaseModel
from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from models.mixins import OrmMixin

OptionalUserID = UUID4 | None

description_active = "Whether this user is allowed to login and submit responses"


class UserRead(BaseModel):
    id: UUID4
    attributes: dict
    admin: bool
    active: bool = Field(description=description_active)


class UserUpsert(SQLModel):
    id: UUID4 | None = None
    attributes: dict | None = None
    active: bool | None = Field(None, description=description_active)
    tasks_add: list[UUID4] = Field([], description="Tasks to add this user to")
    tasks_remove: list[UUID4] = Field(
        [], description="Tasks tasks to remove this user from"
    )


class User(OrmMixin, table=True):
    id: UUID4 = Field(primary_key=True, default_factory=uuid4)
    attributes: dict = Field({}, sa_column=Column(JSON))
    admin: bool = False
    active: bool = Field(True, description=description_active)
