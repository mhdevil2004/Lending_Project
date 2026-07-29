"""Custom exceptions and global error handlers."""

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class AppException(Exception):
    def __init__(self, message: str, status_code: int = 500) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class ConflictException(AppException):
    def __init__(self, message: str = "Resource already exists") -> None:
        super().__init__(message, status.HTTP_409_CONFLICT)


def _error_response(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "message": message, "status": status_code},
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
        return _error_response(exc.status_code, exc.message)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details = "; ".join(
            f"{' -> '.join(str(loc) for loc in e['loc'])}: {e['msg']}"
            for e in exc.errors()
        )
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"Validation failed — {details}",
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(
        _request: Request, _exc: SQLAlchemyError
    ) -> JSONResponse:
        logger.error("Database error", exc_info=True)
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "A database error occurred. Please try again later.",
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        _request: Request, _exc: Exception
    ) -> JSONResponse:
        logger.error("Unhandled error", exc_info=True)
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "An internal server error occurred.",
        )
