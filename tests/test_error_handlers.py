import pytest
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from pydantic import BaseModel

from error_handlers import (
    app_error_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from exceptions import BadRequestError, NotFoundError, UnauthorizedError


def _build_test_app() -> FastAPI:
    app = FastAPI()
    app.add_exception_handler(BadRequestError, app_error_handler)
    app.add_exception_handler(NotFoundError, app_error_handler)
    app.add_exception_handler(UnauthorizedError, app_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    class ItemRequest(BaseModel):
        name: str

    @app.get("/not-found")
    async def not_found():
        raise NotFoundError("missing", data={"id": 1})

    @app.get("/unauthorized")
    async def unauthorized():
        raise UnauthorizedError("bad credentials")

    @app.post("/validate")
    async def validate(body: ItemRequest):
        return {"ok": True}

    @app.get("/boom")
    async def boom():
        raise RuntimeError("unexpected")

    return app


@pytest.fixture
def client():
    return TestClient(_build_test_app(), raise_server_exceptions=False)


def test_not_found_returns_api_response_shape(client):
    response = client.get("/not-found")

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["code"] == 404
    assert body["message"] == "missing"
    assert body["data"] == {"id": 1}


def test_unauthorized_includes_www_authenticate_header(client):
    response = client.get("/unauthorized")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.json()["message"] == "bad credentials"


def test_validation_error_returns_422(client):
    response = client.post("/validate", json={})

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Validation error"
    assert "errors" in body["data"]


def test_unhandled_exception_returns_500(client):
    response = client.get("/boom")

    assert response.status_code == 500
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "An unexpected error occurred"
