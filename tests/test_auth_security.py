from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

import configuration
import rate_limit
from auth import CurrentUser, get_current_user
from main import app

AUTH_HEADERS = {"Authorization": "Bearer test-token"}


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture(autouse=True)
def reset_rate_limits():
    rate_limit.reset_login_rate_limits()
    original_max = configuration.LOGIN_RATE_LIMIT_MAX
    original_window = configuration.LOGIN_RATE_LIMIT_WINDOW_SECONDS
    configuration.LOGIN_RATE_LIMIT_MAX = 3
    configuration.LOGIN_RATE_LIMIT_WINDOW_SECONDS = 60
    yield
    rate_limit.reset_login_rate_limits()
    configuration.LOGIN_RATE_LIMIT_MAX = original_max
    configuration.LOGIN_RATE_LIMIT_WINDOW_SECONDS = original_window


def test_process_transaction_requires_authentication(client):
    response = client.post("/process/transaction", json={"transaction_id": 1})
    assert response.status_code == 401
    assert response.json()["message"] == "Not authenticated"


def test_process_all_requires_admin_role(client):
    async def override_user():
        return CurrentUser(subject="tamrin", roles=["user"])

    app.dependency_overrides[get_current_user] = override_user
    try:
        response = client.post("/process/process_all", headers=AUTH_HEADERS)
        assert response.status_code == 403
        assert response.json()["message"] == "Insufficient permissions"
    finally:
        app.dependency_overrides.clear()


@patch("routers.auth.UserRepository")
def test_login_rate_limit(mock_user_repo_cls, client):
    user_repo = MagicMock()
    user_repo.verify_username_password.return_value = None
    mock_user_repo_cls.return_value = user_repo

    for _ in range(3):
        response = client.post(
            "/auth/login",
            json={"username": "admin", "password": "wrong"},
        )
        assert response.status_code == 401

    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "wrong"},
    )
    assert response.status_code == 429
    assert "Too many login attempts" in response.json()["message"]
