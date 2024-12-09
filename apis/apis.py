from fastapi import FastAPI

from apis.chat import chat_router
from apis.responses import response_router
from apis.users import user_router
from apis.admin_view import admin_router, setup_admin
from fastapi.middleware.cors import CORSMiddleware

from config import ServerConfig



api = FastAPI()

api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", ServerConfig.FRONTEND_URL],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_admin(api)

api.include_router(response_router)
api.include_router(chat_router)
api.include_router(user_router)
api.include_router(admin_router)





@api.get("/")
async def root():
    return {"message": "Welcome to the LLManipulate Backend ;)"}

