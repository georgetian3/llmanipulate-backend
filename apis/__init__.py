from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.routing import APIRoute


from apis.chat import router as chat_router
from apis.responses import router as response_router
from apis.users import router as user_router
from fastapi.middleware.cors import CORSMiddleware

from config import config
from models.database import _DATABASE
from models.user import UserCreate, UserRead, UserUpdate
from services.user import auth_backend, fastapi_users

from httpx_oauth.clients.facebook import FacebookOAuth2
from httpx_oauth.clients.github import GitHubOAuth2
from httpx_oauth.clients.google import GoogleOAuth2

@asynccontextmanager
async def lifespan(api: FastAPI):
    await _DATABASE.create()
    # await init_admin()
    yield

api = FastAPI(lifespan=lifespan)

api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", config.frontend_url],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


api.include_router(response_router)
api.include_router(chat_router)
api.include_router(user_router)



if config.oauth_google_client_id and config.oauth_google_client_secret:
    api.include_router(
        fastapi_users.get_oauth_router(
            GoogleOAuth2(
                config.oauth_google_client_id, config.oauth_google_client_secret
            ),
            auth_backend,
            config.secret,
        ),
        prefix="/auth/google",
        tags=["auth"],
    )

if config.oauth_facebook_client_id and config.oauth_facebook_client_secret:
    api.include_router(
        fastapi_users.get_oauth_router(
            FacebookOAuth2(
                config.oauth_facebook_client_id,
                config.oauth_facebook_client_secret,
                ["https://www.googleapis.com/auth/userinfo.email"],
            ),
            auth_backend,
            config.SECRET,
        ),
        prefix="/auth/facebook",
        tags=["auth"],
    )

if config.oauth_github_client_id and config.oauth_github_client_secret:
    api.include_router(
        fastapi_users.get_oauth_router(
            GitHubOAuth2(
                config.oauth_github_client_id,
                config.oauth_github_client_secret,
                ["user:email"],
            ),
            auth_backend,
            config.secret,
        ),
        prefix="/auth/github",
        tags=["auth"],
    )

api.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth", tags=["auth"]
)
api.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
api.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
api.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
api.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

"""
Simplify operation IDs so that generated API clients have simpler function
names.

Should be called only after all routes have been added.

# https://fastapi.tiangolo.com/advanced/path-operation-advanced-configuration/#using-the-path-operation-function-name-as-the-operationid
"""
for route in api.routes:
    if isinstance(route, APIRoute):
        route.operation_id = route.name
