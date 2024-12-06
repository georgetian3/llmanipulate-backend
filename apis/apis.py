from fastapi import FastAPI, HTTPException, Request,Depends

from apis.chat import chat_router
from apis.responses import response_router
from apis.users import user_router
from apis.admin_view import admin_router, setup_admin
from fastapi.middleware.cors import CORSMiddleware

api = FastAPI()

setup_admin(api)

api.include_router(response_router)
api.include_router(chat_router)
api.include_router(user_router)
api.include_router(admin_router)


api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@api.get("/")
async def root():
    return {"message": "Welcome to the LLManipulate Backend ;)"}

