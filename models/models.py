from uuid import uuid4

from pydantic import UUID4, BaseModel
from sqlmodel import Field, SQLModel


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
