from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.exceptions import HTTPException
from fastapi.openapi.models import HTTPBearer as HTTPBearerModel
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security.http import HTTPBase
from fastapi.security.utils import get_authorization_scheme_param
from starlette.requests import Request
from typing_extensions import Doc

from models.user import OptionalUserID, User


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

EXCEPTION_403 = HTTPException(403, "Unauthorized")
EXCEPTION_404 = HTTPException(404, "Not found")
EXCEPTION_422 = HTTPException(422, "Invalid format")


def current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> OptionalUserID:
    user_id = credentials.credentials
    if not user_id:
        return None
    try:
        return UUID(user_id)
    except:
        raise EXCEPTION_422


async def current_admin(user_id: OptionalUserID = Depends(current_user)) -> User:
    if not user_id:
        raise EXCEPTION_403
    admin = await User.get(user_id)
    if not admin:
        raise EXCEPTION_403
    return admin


ADMIN_DEP = [Depends(current_admin)]
