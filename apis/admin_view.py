import os

from fastapi import APIRouter, FastAPI
from sqladmin import Admin, ModelView
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import URL
from dataclasses import dataclass
from starlette.requests import Request
from models.database import _DATABASE
from models.models import User, Response, NewUser
from services.user import create_user
import asyncio
from dataclasses import asdict

ADMIN_ACCESS_CODE = "123"
from dotenv import load_dotenv
from typing import Any, TypeVar


class NoDefault: ...


class MissingEnvironmentVariable(Exception): ...


T = TypeVar("T")


def get_env(variable: str, default: T | NoDefault = NoDefault()) -> str | T:
    try:
        return os.environ[variable]
    except KeyError:
        if isinstance(default, NoDefault):
            raise MissingEnvironmentVariable(
                f"Missing environment variable: {variable}"
            )
        return default


def int_or_none(x: Any) -> int | None:
    try:
        return int(x)
    except Exception:
        return None


load_dotenv()


# Dynamic database configurations
@dataclass
class DatabaseConfig:
    HOST: str | None = get_env("DATABASE_HOST", None)
    PORT: int = int_or_none(get_env("DATABASE_PORT", None))
    DATABASE: str = get_env("DATABASE_DATABASE", None)
    USERNAME: str = get_env("DATABASE_USERNAME", None)
    PASSWORD: str = get_env("DATABASE_PASSWORD", None)
    DRIVERNAME: str = get_env("DATABASE_DRIVERNAME", None)


class Database:

    def __init__(self, config: DatabaseConfig):
        url = URL.create(**{k.lower(): v for k, v in asdict(config).items()})
        self._engine = create_async_engine(url, echo=False)
        self._async_session_maker: sessionmaker = sessionmaker(
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

SessionLocal = _DATABASE._async_session_maker

# Define admin views
class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.demographics,
        User.is_admin,
        User.task_type,
        User.agent_type,
        User.personality,
        "response_count",
    ]

    form_create_rules = ["demographics", "personality", "task_type", "agent_type"]
    form_args = {
        "demographics": {"default": {"lang": "en", "name": "John Test"}},
        "personality": {
            "default": {
                "Extraversion": 3.0,
                "Agreeableness": 3.0,
                "Conscientiousness": 3.0,
                "Emotional Stability": 3.0,
                "Openness": 3.0,
            }
        },
        "task_type": {"default": 0},
        "agent_type": {"default": 2},
    }

    async def insert_model(self, request: Request, data: dict):
        # Custom logic for inserting the model
        new_user = NewUser(**data)
        user = await create_user(new_user)
        return user


class ResponseAdmin(ModelView, model=Response):
    column_list = [
        Response.id,
        Response.user_id,
        Response.task_name,
        Response.time_created,
        Response.initial_scores,
        Response.conv_history,
        Response.final_scores,
    ]


# Admin Router
admin_router = APIRouter()


def setup_admin(app: FastAPI):
    admin = Admin(app=app, engine=_DATABASE._engine)
    admin.add_view(UserAdmin)
    admin.add_view(ResponseAdmin)

