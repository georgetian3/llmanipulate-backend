from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, field_validator
from sqlmodel import Field, SQLModel


class Demographic(SQLModel, table=False):
    age: int | None
    sex: bool  # TODO: update DEI


class UuidId(SQLModel):
    id: str = Field(primary_key=True)

    # default ID in validator instead of default factory, as otherwise marked
    @field_validator("id", mode="before")
    def default_id(cls, value: Any) -> str:
        if not isinstance(value, UUID) or not UUID(value):
            return uuid4()
        return value

class LLMInput(BaseModel):
    user_id: str
    task_id: str
    message: str
    map: list


class LLMResponse(BaseModel):
    error: str | None = None
    response: str
    agent_data: dict
