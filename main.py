# import asyncio

# from config import Config
# from models.database import Database
# from models.models import NewUser
# from services.user import UserService

# db = Database(Config().DATABASE)


# async def main():
#     await db.reset()
#     user_service = UserService(Config(), db)

#     new_user = NewUser(
#         demographics={"a": "b"},
#         personality={"mb": "ti"},
#         task_type="task_type",
#         agent_type="agent_type",
#     )

#     user = await user_service.create_user(new_user)
#     print(user)
#     users = await user_service.get_all_users()
#     print(users)


# asyncio.run(main())


from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
