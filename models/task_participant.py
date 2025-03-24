from pydantic import UUID4
from sqlmodel import Field

from models.mixins import OrmMixin


class TaskParticipantBase(OrmMixin):
    task_id: UUID4 = Field(primary_key=True, foreign_key="task.id", ondelete="CASCADE")
    user_id: UUID4 = Field(primary_key=True, foreign_key="user.id", ondelete="CASCADE")


class TaskParticipantRead(TaskParticipantBase):
    completed: bool


class TaskParticipant(TaskParticipantBase, table=True):
    __tablename__ = "task_participant"
