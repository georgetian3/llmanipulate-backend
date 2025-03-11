from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.exceptions import HTTPException
from fastapi.openapi.models import HTTPBearer as HTTPBearerModel
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security.http import HTTPBase
from fastapi.security.utils import get_authorization_scheme_param
from pydantic import UUID4
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from typing_extensions import Annotated, Doc

from models.user import User, UserRead


class OptionalHTTPBearer(HTTPBase):
    """
    Same as FastAPI's HTTPBearer, except allows the credentials to be optional
    """

    def __init__(
        self,
        *,
        bearerFormat: Annotated[str | None, Doc("Bearer token format.")] = None,
        scheme_name: Annotated[
            str | None,
            Doc(
                """
                Security scheme name.

                It will be included in the generated OpenAPI (e.g. visible at `/docs`).
                """
            ),
        ] = None,
        description: Annotated[
            str | None,
            Doc(
                """
                Security scheme description.

                It will be included in the generated OpenAPI (e.g. visible at `/docs`).
                """
            ),
        ] = None,
        auto_error: Annotated[
            bool,
            Doc(
                """
                By default, if the HTTP Bearer token is not provided (in an
                `Authorization` header), `HTTPBearer` will automatically cancel the
                request and send the client an error.

                If `auto_error` is set to `False`, when the HTTP Bearer token
                is not available, instead of erroring out, the dependency result will
                be `None`.

                This is useful when you want to have optional authentication.

                It is also useful when you want to have authentication that can be
                provided in one of multiple optional ways (for example, in an HTTP
                Bearer token or in a cookie).
                """
            ),
        ] = True,
    ):
        self.model = HTTPBearerModel(bearerFormat=bearerFormat, description=description)
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error

    async def __call__(
        self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
        authorization = request.headers.get("Authorization")
        scheme, credentials = get_authorization_scheme_param(authorization)
        return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)


security = OptionalHTTPBearer()


def current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
):
    return credentials.credentials


EXCEPTION_403 = HTTPException(403, "Unauthorized")


async def current_admin(user_id: UUID4 | None = Depends(current_user)) -> User:
    if not user_id:
        raise EXCEPTION_403
    admin = await User.get(user_id)
    if not admin:
        raise EXCEPTION_403
    return admin


router = APIRouter(prefix="/auth")


@router.post("/login", response_model=UserRead)
async def login(user_id: UUID = Depends(current_user)):
    return await User.get(user_id)
