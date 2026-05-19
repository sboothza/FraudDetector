import datetime
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from auth import CurrentUser, get_current_user
from converters import to_transaction_summary
from dependencies import get_db
from main import app


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def user_override():
    async def override_user():
        return CurrentUser(subject="tamrin", roles=["user"])

    app.dependency_overrides[get_current_user] = override_user
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}


def test_get_customer_transactions_not_found(client, user_override, auth_headers):
    session = MagicMock()
    customer_repo = MagicMock()
    customer_repo.get_by_id.return_value = None

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    with pytest.MonkeyPatch.context() as patcher:
        patcher.setattr("routers.customers.CustomerRepository", lambda s: customer_repo)
        response = client.get("/customers/999/transactions", headers=auth_headers)

    app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 404
    assert response.json()["success"] is False


def test_get_customer_transactions_returns_customer_and_transactions(
    client, user_override, auth_headers
):
    session = MagicMock()

    customer = MagicMock()
    customer.id = 1
    customer.first_name = "Stephen"
    customer.last_name = "Booth"
    customer.email = "stephen@email"
    customer.id_number = "740315"
    customer.balance = 1000.0
    customer.currency_code = "zar"
    customer.base_balance = 1000.0

    transaction = MagicMock()
    transaction.id = 10
    transaction.transaction_id = "txn-1"
    transaction.reference = "ref-1"
    transaction.create_date = datetime.datetime(2026, 5, 12, 12, 0, 0)
    transaction.amount = 100.0
    transaction.currency_code = "zar"
    transaction.base_amount = 100.0
    transaction.debit_credit = "DR"
    transaction.processed = True
    transaction.transaction_type.name = "payment"
    transaction.transaction_status.name = "posted"
    transaction.channel.name = "internaltransfer"

    customer_repo = MagicMock()
    customer_repo.get_by_id.return_value = customer

    trans_repo = MagicMock()
    trans_repo.get_by_customer_id.return_value = [transaction]

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    with pytest.MonkeyPatch.context() as patcher:
        patcher.setattr("routers.customers.CustomerRepository", lambda s: customer_repo)
        patcher.setattr("routers.customers.TransactionRepository", lambda s: trans_repo)
        response = client.get("/customers/1/transactions", headers=auth_headers)

    app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["customer"]["id"] == 1
    assert body["data"]["transaction_count"] == 1
    assert body["data"]["transactions"][0]["transaction_id"] == "txn-1"


def test_transaction_summary_maps_related_names():
    transaction = MagicMock()
    transaction.id = 1
    transaction.transaction_id = "abc"
    transaction.reference = "ref"
    transaction.create_date = datetime.datetime(2026, 1, 2, 3, 4, 5)
    transaction.amount = 50.0
    transaction.currency_code = "usd"
    transaction.base_amount = 800.0
    transaction.debit_credit = "CR"
    transaction.processed = False
    transaction.transaction_type.name = "payment"
    transaction.transaction_status.name = "pending"
    transaction.channel.name = "mobile"

    summary = to_transaction_summary(transaction)

    assert summary.transaction_type == "payment"
    assert summary.transaction_status == "pending"
    assert summary.channel == "mobile"
