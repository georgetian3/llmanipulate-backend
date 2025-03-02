from uuid import UUID

from fastapi import Depends
from fastapi_users import schemas
from fastapi_users_db_sqlmodel import (
    SQLModelBaseOAuthAccount,
    SQLModelBaseUserDB,
    SQLModelUserDatabaseAsync,
)
from pydantic import UUID4
from sqlalchemy import JSON, Column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Field

from models.database import get_async_session
from models.mixins import OrmMixin


class UserRead(schemas.BaseUser[UUID]):
    id: UUID4
    name: str


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass


class User(SQLModelBaseUserDB, OrmMixin, table=True):
    # oauth_accounts: list["OAuthAccount"] = Relationship(
    #     back_populates="user", sa_relationship_kwargs={"lazy": "joined"}
    # )
    name: str | None = None

    demographics: dict = Field(default_factory=dict, sa_column=Column(JSON))
    personality: dict = Field(default_factory=dict, sa_column=Column(JSON))
    agent_type: int = Field(default_factory=int, ge=0, le=2)
    task_type: int = Field(default_factory=int, ge=0, le=1)


UserID = UUID4


class OAuthAccount(SQLModelBaseOAuthAccount, table=True):
    ...
    # user: User | None = Relationship(back_populates="oauth_accounts")


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLModelUserDatabaseAsync(session, User, OAuthAccount)  # noqa: F405
