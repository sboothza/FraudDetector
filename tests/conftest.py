import os

# Use in-memory SQLite for tests (no Postgres required).
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest

from services.transaction_processor import TransactionProcessor


@pytest.fixture(autouse=True)
def reset_processor_rules():
    TransactionProcessor._rules = []
    yield
    TransactionProcessor._rules = []
