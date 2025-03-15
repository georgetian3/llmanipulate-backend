import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from apis.chat import chat_router as chat_router
from apis.responses import router as response_router
from apis.tasks import router as task_router
from apis.users import router as user_router
from models.database import _DATABASE
from models.fixtures import load_fixtures
from services.logging import get_logger
from services.user import init_admin
from settings import SETTINGS


@asynccontextmanager
async def lifespan(api: FastAPI):
    await _DATABASE.create()
    if SETTINGS.load_fixtures:
        await load_fixtures()
    await init_admin()
    yield


api = FastAPI(lifespan=lifespan)

api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", SETTINGS.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


api.include_router(chat_router, tags=["chats"])
api.include_router(user_router, tags=["users"])
api.include_router(task_router, tags=["tasks"])
api.include_router(response_router, tags=["responses"])

"""
Simplify operation IDs so that generated API clients have simpler function
names.

Should be called only after all routes have been added.

# https://fastapi.tiangolo.com/advanced/path-operation-advanced-configuration/#using-the-path-operation-function-name-as-the-operationid
"""
for route in api.routes:
    if isinstance(route, APIRoute):
        route.operation_id = route.name


logger = get_logger(__name__)


with open("openapi.json", "w", encoding="utf-8") as f:
    json.dump(api.openapi(), f, indent=2, ensure_ascii=False)
