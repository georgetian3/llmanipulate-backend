from pydantic import UUID4
from sqlalchemy import JSON, Column
from sqlmodel import Field

from models.mixins import OrmMixin
from models.models import UuidId

UserID = UUID4 | None


class UserBase(OrmMixin, UuidId):
    attributes: dict = Field({}, sa_column=Column(JSON))


class UserRead(UserBase):
    is_admin: bool = False


class UserCreate(UserBase): ...


class UserUpdate(UserBase): ...


class User(UserRead, table=True): ...
