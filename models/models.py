from datetime import UTC, datetime
from typing import Self
from uuid import uuid4

from pydantic import UUID4, BaseModel
from sqlmodel import Field, SQLModel

from models.database import get_session


class CreatedMixin(SQLModel):
    created_timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class UpdatedMixin(SQLModel):
    updated_timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Demographic(SQLModel, table=False):
    age: int | None
    sex: bool  # TODO: update DEI


class UuidId(SQLModel):
    id: UUID4 = Field(primary_key=True, default_factory=uuid4)


class LLMInput(BaseModel):
    user_id: str
    task_id: str
    message: str
    map: list


class LLMResponse(BaseModel):
    error: str | None = None
    response: str
    agent_data: dict


class ErrorResponse(BaseModel):
    detail: str

class SaveMixin(SQLModel):

    async def save(self) -> Self:
        print('getting session')
        async with get_session() as session:
            print('adding')
            session.add(self)
            print('commiting')
            await session.commit()
            print('committed')
            await session.refresh(self)
        return self