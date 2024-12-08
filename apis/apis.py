from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apis.chat import chat_router
from apis.responses import response_router
from apis.users import user_router


api = FastAPI()
api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
api.include_router(response_router)
api.include_router(chat_router)
api.include_router(user_router)



@api.get("/")
async def root():
    return {"message": "Welcome to the LLManipulate Backend ;)"}
