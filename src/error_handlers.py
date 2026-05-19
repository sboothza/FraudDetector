import logging

from fastapi import HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from exceptions import AppError
from schemas import ApiResponse

logger = logging.getLogger(__name__)


def _api_error_response(
    *,
    status_code: int,
    message: str,
    success: bool = False,
    data: dict | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    body = ApiResponse(
        code=status_code,
        message=message,
        success=success,
        data=data or {},
    )
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(),
        headers=headers,
    )


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    logger.warning(
        "App error %s on %s %s: %s",
        exc.code,
        request.method,
        request.url.path,
        exc.message,
    )
    headers = {"WWW-Authenticate": "Bearer"} if exc.code == 401 else None
    return _api_error_response(
        status_code=exc.code,
        message=exc.message,
        data=exc.data,
        headers=headers,
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    logger.warning(
        "HTTP error %s on %s %s",
        exc.status_code,
        request.method,
        request.url.path,
    )
    detail = exc.detail
    if isinstance(detail, str):
        message = detail
        data: dict = {}
    elif isinstance(detail, list):
        message = "Request failed"
        data = {"errors": jsonable_encoder(detail)}
    else:
        message = "Request failed"
        data = {"detail": jsonable_encoder(detail)}

    return _api_error_response(
        status_code=exc.status_code,
        message=message,
        data=data,
        headers=dict(exc.headers) if exc.headers else None,
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    errors = jsonable_encoder(exc.errors())
    logger.warning(
        "Validation error on %s %s: %s",
        request.method,
        request.url.path,
        errors,
    )
    return _api_error_response(
        status_code=422,
        message="Validation error",
        data={"errors": errors},
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    logger.exception(
        "Database error on %s %s: %s",
        request.method,
        request.url.path,
        exc,
    )
    return _api_error_response(
        status_code=500,
        message="A database error occurred",
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, AppError):
        return await app_error_handler(request, exc)

    logger.exception(
        "Unhandled error on %s %s: %s",
        request.method,
        request.url.path,
        exc,
    )
    return _api_error_response(
        status_code=500,
        message="An unexpected error occurred",
    )
