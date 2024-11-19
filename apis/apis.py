from fastapi import FastAPI
from apis.tasks import task_router
from apis.users import user_router
from apis.responses import response_router
from apis.chat import chat_router

api = FastAPI()

api.include_router(task_router)
api.include_router(response_router)
api.include_router(chat_router)
api.include_router(user_router)

@api.get("/")
async def root():
    return {"message": "Welcome to the LLManipulate Backend ;) "}