from typing import Any

from fastapi import HTTPException

from models.exceptions import ErrorResponse


def create_doc(exception: HTTPException):
    return {
        exception.status_code: {"model": ErrorResponse, "description": exception.detail}
    }


def create_docs(*args: HTTPException) -> dict[int | str, dict[str, Any]]:
    docs: dict[int | str, dict[str, Any]] = {}
    for exception in args:
        docs |= create_doc(exception)
    return docs
