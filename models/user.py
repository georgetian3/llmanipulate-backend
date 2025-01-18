from uuid import UUID

from fastapi_users import schemas
from fastapi_users_db_sqlmodel import SQLModelBaseOAuthAccount, SQLModelBaseUserDB
from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship


class UserRead(schemas.BaseUser[UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass


class User(SQLModelBaseUserDB, table=True):

    oauth_accounts: list["OAuthAccount"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "joined"}
    )

    demographics: dict = Field(default_factory=dict, sa_column=Column(JSON))
    personality: dict = Field(default_factory=dict, sa_column=Column(JSON))
    agent_type: int = Field(default_factory=int, ge=0, le=2)
    task_type: int = Field(default_factory=int, ge=0, le=1)


    responses: list["Response"] = Relationship(back_populates="user")

    @property
    def response_count(self) -> int:
        """Return the count of responses linked to the user."""
        return len(self.responses)



class OAuthAccount(SQLModelBaseOAuthAccount, table=True):
    user: User | None = Relationship(back_populates="oauth_accounts")

