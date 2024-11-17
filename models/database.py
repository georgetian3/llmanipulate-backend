import asyncio
from dataclasses import asdict

import nest_asyncio
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from config import DatabaseConfig

nest_asyncio.apply()


class Database:

    def __init__(self, config: DatabaseConfig):
        url = URL.create(**{k.lower(): v for k, v in asdict(config).items()})
        self._engine = create_async_engine(url, echo=False)
        self._async_session_maker: sessionmaker = sessionmaker(  # type: ignore
            self._engine, class_=AsyncSession
        )

    async def create(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    async def reset(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
        await self.create()

    def get_session(self) -> AsyncSession:
        return self._async_session_maker()


_DATABASE = Database(DatabaseConfig())
asyncio.run(_DATABASE.create())


def get_session():
    return _DATABASE.get_session()
