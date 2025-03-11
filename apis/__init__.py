import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from apis.auth import router as auth_router
from apis.chat import router as chat_router
from apis.responses import router as response_router
from apis.tasks import router as task_router
from apis.users import router as user_router
from models.database import _DATABASE
from models.fixtures import load_fixtures
from settings import settings


@asynccontextmanager
async def lifespan(api: FastAPI):
    await _DATABASE.create()
    if settings.load_fixtures:
        await load_fixtures()
    yield


api = FastAPI(lifespan=lifespan)

api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


api.include_router(auth_router, tags=["auth"])
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


with open("openapi.json", "w", encoding="utf-8") as f:
    json.dump(api.openapi(), f, indent=2, ensure_ascii=False)
