from typing import Any
from uuid import UUID, uuid4

from pydantic import UUID4, BaseModel, field_validator
from sqlmodel import Field, SQLModel


class Demographic(SQLModel, table=False):
    age: int | None
    sex: bool  # TODO: update DEI


class UuidId(SQLModel):
    id: UUID4 = Field(primary_key=True)

    @field_validator("id", mode="before")
    def default_id(cls, value: Any) -> UUID4:
        if not isinstance(value, UUID):
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
