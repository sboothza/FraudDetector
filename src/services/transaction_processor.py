import datetime
import threading

from sqlalchemy.orm import Session

from dependencies import CreateSession
from models.transaction import Transaction
from repositories.rule_repository import RuleRepository
from repositories.transaction_repository import TransactionRepository
from repositories.transaction_rule_history_repository import TransactionRuleHistoryRepository
from rules.rule import Rule
from utils import resolve_type


class TransactionProcessor:
    rules: list[Rule] = []
    transaction_window: datetime.timedelta

    def __init__(self, transaction_window: datetime.timedelta):
        session = CreateSession()
        try:
            self.transaction_window = transaction_window
            rule_repo = RuleRepository(session)
            rule_entities = rule_repo.get_all()

            for rule in rule_entities:
                rule_type = resolve_type(rule.type_name)
                rule_obj = rule_type(rule.id, rule.parameters)
                self.rules.append(rule_obj)
        finally:
            session.close()

    def process_transaction(self, transaction: Transaction) -> tuple[bool, str]:
        run_date: datetime.datetime = datetime.datetime.now()
        session = CreateSession()
        with TransactionRepository(session) as trans_repo:
            overall_result, overall_text = self._process_transaction_internal(transaction, session, run_date)
            trans_repo.flag_as_processed(transaction)
            return overall_result, overall_text

    def _process_transaction_internal(self, transaction: Transaction, session: Session, run_date: datetime.datetime) -> \
    tuple[bool, str]:
        customer = transaction.customer
        min_transaction_date = transaction.create_date - self.transaction_window
        overall_result: bool = True
        overall_text: str = ""

        with TransactionRepository(session) as trans_repo:
            all_transactions = trans_repo.get_for_customer_timerange(customer.id, min_transaction_date)
            with TransactionRuleHistoryRepository(session) as trans_rule_history_repo:
                for rule in self.rules:
                    result, text = rule.process_rule(session, customer, all_transactions.copy(), transaction)
                    trans_rule_history_repo.add(transaction, run_date, rule, result, text)
                    if not result:
                        overall_result = False

                    overall_text += text

        return overall_result, overall_text

    def process_batch(self, count: int) -> None:
        thread = threading.Thread(
            target=self._run_batch,
            args=(count,),
            name="transaction-batch",
            daemon=True,
        )
        thread.start()

    def _run_batch(self, count: int) -> None:
        session = CreateSession()
        try:
            with TransactionRepository(session) as trans_repo:
                transactions = trans_repo.get_unprocessed_transactions(count)
                run_date = datetime.datetime.now()
                for transaction in transactions:
                    self._process_transaction_internal(transaction, session, run_date)

                trans_repo.flag_all_as_processed(transactions)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
