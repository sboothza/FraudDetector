import datetime
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from exceptions import BadRequestError
from rules.rule import Rule
from services.transaction_processor import TransactionProcessor


def _mock_repo_context(**repo_attrs) -> MagicMock:
    """Configure a repository class mock for use as a context manager."""
    repo = MagicMock(**repo_attrs)
    context = MagicMock()
    context.__enter__.return_value = repo
    context.__exit__.return_value = False
    return context


class PassRule(Rule):
    def process_rule(self, session, customer, customer_transactions, root_transaction):
        return True, ""


class FailRule(Rule):
    def process_rule(self, session, customer, customer_transactions, root_transaction):
        return False, "rule failed\r\n"


def _make_transaction(
    *,
    transaction_id: str = "txn-1",
    customer_id: int = 1,
    create_date: datetime.datetime | None = None,
    base_amount: float = 100.0,
) -> MagicMock:
    customer = MagicMock()
    customer.id = customer_id

    transaction = MagicMock()
    transaction.transaction_id = transaction_id
    transaction.customer = customer
    transaction.create_date = create_date or datetime.datetime(2026, 5, 12, 12, 0, 0)
    transaction.base_amount = base_amount
    transaction.processed = False
    return transaction


def _make_rule_entity(*, rule_id: int, type_name: str, parameters: dict | None = None) -> MagicMock:
    entity = MagicMock()
    entity.id = rule_id
    entity.type_name = type_name
    entity.parameters = parameters or {}
    return entity


@patch("services.transaction_processor.CreateSession")
@patch("services.transaction_processor.RuleRepository")
def test_init_loads_rules_from_repository(
    mock_rule_repo_cls,
    mock_create_session,
):
    session = MagicMock()
    mock_create_session.return_value = session
    rule_entity = _make_rule_entity(rule_id=1, type_name="rules.rule.Rule")
    rule_entity.get_rule.return_value = PassRule(1, {})
    mock_rule_repo_cls.return_value.get_all.return_value = [rule_entity]

    processor = TransactionProcessor(datetime.timedelta(hours=1))

    assert processor.transaction_window == datetime.timedelta(hours=1)
    assert len(TransactionProcessor._rules) == 1
    assert isinstance(TransactionProcessor._rules[0], PassRule)
    rule_entity.get_rule.assert_called_once()
    session.close.assert_called_once()


@patch("services.transaction_processor.CreateSession")
@patch("services.transaction_processor.RuleRepository")
def test_init_does_not_reload_rules_when_already_cached(
    mock_rule_repo_cls,
    mock_create_session,
):
    TransactionProcessor._rules = [PassRule(1, {})]

    TransactionProcessor(datetime.timedelta(hours=1))

    mock_rule_repo_cls.return_value.get_all.assert_not_called()
    assert len(TransactionProcessor._rules) == 1


@patch("services.transaction_processor.CreateSession")
@patch("services.transaction_processor.RuleRepository")
def test_init_raises_bad_request_for_invalid_rule_type(
    mock_rule_repo_cls,
    mock_create_session,
):
    rule_entity = _make_rule_entity(rule_id=7, type_name="invalid.Rule")
    rule_entity.get_rule.side_effect = BadRequestError(
        "Invalid rule configuration for rule id 7: unknown type",
        data={"rule_id": 7, "type_name": "invalid.Rule"},
    )
    mock_rule_repo_cls.return_value.get_all.return_value = [rule_entity]

    with pytest.raises(BadRequestError) as exc_info:
        TransactionProcessor(datetime.timedelta(hours=1))

    assert exc_info.value.code == 400
    assert "rule id 7" in exc_info.value.message
    assert exc_info.value.data == {"rule_id": 7, "type_name": "invalid.Rule"}


@patch("services.transaction_processor.TransactionRuleHistoryRepository")
@patch("services.transaction_processor.TransactionRepository")
def test_process_transaction_internal_passes_all_rules(
    mock_trans_repo_cls,
    mock_history_repo_cls,
):
    TransactionProcessor._rules = [PassRule(1, {}), PassRule(2, {})]
    session = MagicMock(spec=Session)
    transaction = _make_transaction()
    trans_repo = MagicMock()
    trans_repo.get_for_customer_timerange.return_value = [transaction]
    mock_trans_repo_cls.return_value = _mock_repo_context()
    mock_trans_repo_cls.return_value.__enter__.return_value = trans_repo
    history_repo = MagicMock()
    mock_history_repo_cls.return_value = _mock_repo_context()
    mock_history_repo_cls.return_value.__enter__.return_value = history_repo
    run_date = datetime.datetime(2026, 5, 12, 12, 0, 0)

    processor = TransactionProcessor.__new__(TransactionProcessor)
    processor.transaction_window = datetime.timedelta(hours=1)

    result, text = processor._process_transaction_internal(transaction, session, run_date)

    assert result is True
    assert text == ""
    trans_repo.get_for_customer_timerange.assert_called_once_with(
        transaction.customer.id,
        transaction.create_date - datetime.timedelta(hours=1),
    )
    assert history_repo.add.call_count == 2


@patch("services.transaction_processor.TransactionRuleHistoryRepository")
@patch("services.transaction_processor.TransactionRepository")
def test_process_transaction_internal_fails_when_any_rule_fails(
    mock_trans_repo_cls,
    mock_history_repo_cls,
):
    TransactionProcessor._rules = [PassRule(1, {}), FailRule(2, {})]
    session = MagicMock(spec=Session)
    transaction = _make_transaction()
    trans_repo = MagicMock()
    trans_repo.get_for_customer_timerange.return_value = []
    mock_trans_repo_cls.return_value = _mock_repo_context()
    mock_trans_repo_cls.return_value.__enter__.return_value = trans_repo
    mock_history_repo_cls.return_value = _mock_repo_context()

    processor = TransactionProcessor.__new__(TransactionProcessor)
    processor.transaction_window = datetime.timedelta(hours=1)

    result, text = processor._process_transaction_internal(
        transaction,
        session,
        datetime.datetime(2026, 5, 12, 12, 0, 0),
    )

    assert result is False
    assert "rule failed" in text


@patch("services.transaction_processor.TransactionRepository")
def test_process_transaction_flags_transaction_as_processed(mock_trans_repo_cls):
    TransactionProcessor._rules = [PassRule(1, {})]
    session = MagicMock(spec=Session)
    transaction = _make_transaction()
    trans_repo = MagicMock()
    mock_trans_repo_cls.return_value = _mock_repo_context()
    mock_trans_repo_cls.return_value.__enter__.return_value = trans_repo

    processor = TransactionProcessor.__new__(TransactionProcessor)
    processor.transaction_window = datetime.timedelta(hours=1)

    with patch.object(processor, "_process_transaction_internal", return_value=(True, "ok")):
        result, text = processor.process_transaction(transaction, session)

    assert result is True
    assert text == "ok"
    trans_repo.flag_as_processed.assert_called_once_with(transaction)


@patch("services.transaction_processor.threading.Thread")
def test_process_batch_starts_background_thread(mock_thread_cls):
    processor = TransactionProcessor.__new__(TransactionProcessor)
    processor.transaction_window = datetime.timedelta(hours=1)
    mock_thread = mock_thread_cls.return_value

    processor.process_batch(25)

    mock_thread_cls.assert_called_once_with(
        target=processor._run_batch,
        args=(25,),
        name="transaction-batch",
        daemon=True,
    )
    mock_thread.start.assert_called_once()


@patch("services.transaction_processor.CreateSession")
@patch("services.transaction_processor.TransactionRepository")
def test_run_batch_processes_transactions_and_commits(
    mock_trans_repo_cls,
    mock_create_session,
):
    session = MagicMock()
    mock_create_session.return_value = session
    transactions = [_make_transaction(transaction_id="a"), _make_transaction(transaction_id="b")]
    trans_repo = MagicMock()
    trans_repo.get_unprocessed_transactions.return_value = transactions
    mock_trans_repo_cls.return_value = _mock_repo_context()
    mock_trans_repo_cls.return_value.__enter__.return_value = trans_repo

    processor = TransactionProcessor.__new__(TransactionProcessor)
    processor.transaction_window = datetime.timedelta(hours=1)

    with patch.object(processor, "_process_transaction_internal", return_value=(True, "")) as mock_internal:
        processor._run_batch(10)

    trans_repo.get_unprocessed_transactions.assert_called_once_with(10)
    assert mock_internal.call_count == 2
    trans_repo.flag_all_as_processed.assert_called_once_with(transactions)
    session.commit.assert_called_once()
    session.close.assert_called_once()


@patch("services.transaction_processor.CreateSession")
@patch("services.transaction_processor.TransactionRepository")
def test_run_batch_rolls_back_on_error(
    mock_trans_repo_cls,
    mock_create_session,
):
    session = MagicMock()
    mock_create_session.return_value = session
    trans_repo = MagicMock()
    trans_repo.get_unprocessed_transactions.side_effect = RuntimeError("db down")
    mock_trans_repo_cls.return_value = _mock_repo_context()
    mock_trans_repo_cls.return_value.__enter__.return_value = trans_repo

    processor = TransactionProcessor.__new__(TransactionProcessor)
    processor.transaction_window = datetime.timedelta(hours=1)

    processor._run_batch(5)

    session.rollback.assert_called_once()
    session.close.assert_called_once()
    session.commit.assert_not_called()
