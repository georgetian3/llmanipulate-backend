from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel, Relationship


from models.user import User




class NewResponse(SQLModel, table=False):
    task_name: str
    initial_scores: dict = Field(default_factory=dict, sa_column=Column(JSON))
    conv_history: dict = Field(default_factory=dict, sa_column=Column(JSON))
    final_scores: dict = Field(default_factory=dict, sa_column=Column(JSON))
    user_id: str = Field(foreign_key="user.id")



class Response(NewResponse, table=True):
    id: int | None = Field(primary_key=True, exclude=True)
    time_created: datetime
    user: User = Relationship(back_populates="responses")


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