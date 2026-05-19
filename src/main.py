import logging

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from error_handlers import (
    app_error_handler,
    http_exception_handler,
    sqlalchemy_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from exceptions import AppError
from logging_config import setup_logging
from middleware.request_logging import RequestLoggingMiddleware
from routers import auth as auth_router, customers as customers_router, process as process_router
from schemas import ApiResponse

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Fraudulent Transaction API", version="1.0.0")
app.add_middleware(RequestLoggingMiddleware)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(customers_router.router, prefix="/customers", tags=["customers"])
app.include_router(process_router.router, prefix="/process", tags=["process"])


@app.on_event("startup")
async def on_startup() -> None:
    logger.info("Fraudulent Transaction API started")


@app.get("/", response_model=ApiResponse)
async def index():
    """Health check endpoint."""
    return ApiResponse(
        code=200,
        message="Fraudulent Transaction API",
        success=True,
        data={},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")
