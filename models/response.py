
from datetime import datetime
from sqlalchemy import JSON, Column
from sqlmodel import SQLModel, Field, Relationship

from models.user import User


class ResponseCreate(SQLModel):
    task_name: str
    initial_scores: dict = Field(default_factory=dict, sa_column=Column(JSON))
    conv_history: dict = Field(default_factory=dict, sa_column=Column(JSON))
    final_scores: dict = Field(default_factory=dict, sa_column=Column(JSON))



class Response(ResponseCreate, table=True):
    id: int | None = Field(primary_key=True, exclude=True)
    user_id: str = Field(foreign_key="user.id")
    time_created: datetime
    user: User = Relationship(back_populates="responses")