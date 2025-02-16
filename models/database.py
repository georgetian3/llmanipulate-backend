import asyncio
from dataclasses import asdict
from contextlib import asynccontextmanager

import asyncpg
from sqlalchemy import URL, create_engine
import sqlalchemy
import sqlalchemy.dialects
import sqlalchemy.dialects.postgresql
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from config import DatabaseConfig
from models.models import *
from services.logging import get_logger
from sqlalchemy.exc import ProgrammingError

logger = get_logger(__name__)

class Database:

    def __init__(self, config: DatabaseConfig):
        self._url = URL.create(**{k.lower(): v for k, v in asdict(config).items()})
        self._engine = create_async_engine(self._url)
        self._async_session_maker: sessionmaker = sessionmaker(
            self._engine, class_=AsyncSession
        )

    async def create(self):
        url = self._url._replace(database=None)
        # No need to create DB for sqlite
        if 'sqlite' not in url.drivername:
            async with create_async_engine(url).execution_options(isolation_level="AUTOCOMMIT").connect() as conn:
                try:
                    await conn.execute(sqlalchemy.text(f"CREATE DATABASE {self._url.database}"))
                    logger.info(f"Database {self._url.database} created ")
                except Exception as e:
                    if "already exists" not in str(e):
                        logger.exception("Error creating database")
        async with self._engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    async def reset(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
        await self.create()

    def get_session(self) -> AsyncSession:
        return self._async_session_maker()

_DATABASE = Database(DatabaseConfig())

@asynccontextmanager
async def get_session():
    session = _DATABASE.get_session()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
