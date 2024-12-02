from typing import Annotated

from fastapi import Header, HTTPException, status

from models.database import get_session
from models.models import ErrorResponse, User

NOT_AUTHENTICATED = "Not authenticated"
NOT_ADMIN = "Admin privileges required"
NOT_FOUND = "Object not found"

NOT_AUTHENTICATED_HTTP_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail=NOT_AUTHENTICATED
)
NOT_ADMIN_HTTP_EXCEPTION = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN, detail=NOT_ADMIN
)
NOT_FOUND_HTTP_EXCEPTION = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND
)


def check_auth(need_admin: bool):
    async def _auth_required(user_id: Annotated[str, Header]):
        async with get_session() as session:
            user = await session.get(User, user_id)
        if not user:
            raise NOT_AUTHENTICATED_HTTP_EXCEPTION
        if need_admin and not user.is_admin:
            raise NOT_ADMIN_HTTP_EXCEPTION

    return _auth_required


AUTH_RESPONSES = {
    exception.status_code: {"model": ErrorResponse, "description": exception.detail}
    for exception in (NOT_AUTHENTICATED_HTTP_EXCEPTION, NOT_ADMIN_HTTP_EXCEPTION)
}
