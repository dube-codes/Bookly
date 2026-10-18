from fastapi import FastAPI, status
from typing import Any, Callable
from fastapi.requests import Request
from fastapi.responses import JSONResponse


class BooklyException(Exception):
    """This is the base class for all bookly errors"""

    pass


class InvalidToken(BooklyException):
    """User has provided an invalid or expired token"""

    pass


def create_exception_handler(
    status_code: int, initial_detail: Any
) -> Callable[[Request, Exception], JSONResponse]:

    async def exception_handler(request: Request, exc: BooklyException):
        return JSONResponse(content=initial_detail, status_code=status_code)

    return exception_handler


def register_all_errors(app: FastAPI):
    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Token is invalid or expired token..!",
                "error_code": "Invalid Token",
            },
        ),
    )

    app.exception_handler(500)


async def internal_server_error(request, exc):
    return JSONResponse(
        content={
            "message": "Oops..! something went wrong",
            "error_code": "server_error",
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
