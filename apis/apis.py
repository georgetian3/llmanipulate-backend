import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from apis.admin_view import admin_router, setup_admin
from apis.chat import router
from apis.responses import response_router
from apis.tasks import router as task_router
from apis.users import user_router
from config import ServerConfig
from models.database import _DATABASE
from services.user import init_admin


@asynccontextmanager
async def lifespan(api: FastAPI):
    await _DATABASE.create()
    await init_admin()
    yield


api = FastAPI(lifespan=lifespan)

api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", ServerConfig.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


setup_admin(api)

api.include_router(response_router)
api.include_router(router, tags=["chat"])
api.include_router(user_router, tags=["users"])
api.include_router(admin_router)
api.include_router(task_router, tags=["tasks"])


@api.get("/")
async def root():
    return {"message": "Welcome to the LLManipulate Backend ;)"}


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
