from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from apis.tasks import task_router
from apis.users import user_router
from models.models import  User
from models.database import get_session


api = FastAPI()

api.include_router(task_router)
api.include_router(user_router)

@api.get("/")
async def root():
    return {"message": "Welcome to the LLManipulate Backend ;) "}

@user_router.post("/authenticate", response_model=User)
async def authenticate_user(user_code: str, session: AsyncSession = Depends(get_session)):
    query = select(User).where(User.user_code == user_code)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user