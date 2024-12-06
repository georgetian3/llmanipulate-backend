import os

from fastapi import APIRouter, FastAPI, Depends, HTTPException
from sqladmin import Admin, ModelView
from sqlmodel import SQLModel, Field
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from dataclasses import dataclass
from starlette.requests import Request
from models.models import User, Response, NewUser, NewResponse
from services.user import create_user
ADMIN_ACCESS_CODE = "123"

def get_env(key, default=None):
    return os.getenv(key, default)

def int_or_none(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

# Dynamic database configuration
@dataclass
class DatabaseConfig:
    HOST: str = get_env("DATABASE_HOST", "localhost")
    PORT: int = int_or_none(get_env("DATABASE_PORT", 5432))
    DATABASE: str = get_env("DATABASE_DATABASE", "myapp_db")
    USERNAME: str = get_env("DATABASE_USERNAME", "myapp_user")
    PASSWORD: str = get_env("DATABASE_PASSWORD", "secure_password")
    DRIVERNAME: str = get_env("DATABASE_DRIVERNAME", "postgresql+asyncpg")

    def get_uri(self) -> str:
        return f"{self.DRIVERNAME}://{self.USERNAME}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE}"

# Build the database URI dynamically
db_config = DatabaseConfig()
DATABASE_URL = db_config.get_uri()
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Define admin views
class UserAdmin(ModelView, model=User):
    column_list = [User.id,User.demographics, User.is_admin, User.task_type, User.agent_type,
                        User.demographics, User.personality, "response_count"]


    form_create_rules = ["demographics", "personality", "task_type", "agent_type"]
    form_args = {
        "demographics": {"default": {"lang": "en", "name": "John Test"}},
        "personality": {"default":{"Extraversion": 3.0, "Agreeableness": 3.0, "Conscientiousness": 3.0, "Emotional Stability": 3.0, "Openness": 3.0}},
        "task_type":  {"default": 0},
        "agent_type": {"default": 2}}

    async def insert_model(self, request: Request, data: dict):
        # Custom logic for inserting the model
        new_user = NewUser(**data)
        user = await create_user(new_user)
        return user


class ResponseAdmin(ModelView, model=Response):
    column_list = [Response.id, Response.user_id, Response.task_name, Response.time_created,
                     Response.initial_scores, Response.conv_history, Response.final_scores]

# Admin Router
admin_router = APIRouter()

def setup_admin(app: FastAPI):
    admin = Admin(app=app, engine=engine)
    admin.add_view(UserAdmin)
    admin.add_view(ResponseAdmin)



@admin_router.on_event("startup")
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)