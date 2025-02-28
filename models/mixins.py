from datetime import UTC, datetime
from typing import Self

from sqlmodel import Field, SQLModel, select

from models.database import get_session


class CreatedMixin(SQLModel):
    created_timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class UpdatedMixin(SQLModel):
    updated_timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class OrmMixin(SQLModel):
    @classmethod
    async def get(cls, pk) -> Self | None:
        async with get_session() as session:
            return await session.get(cls, pk)

    @classmethod
    async def all(cls) -> list[Self]:
        async with get_session() as session:
            return list((await session.execute(select(cls))).scalars().all())

    async def save(self, refresh: bool = True) -> Self:
        async with get_session() as session:
            session.add(self)
            await session.commit()
            if refresh:
                await session.refresh(self)
        return self
