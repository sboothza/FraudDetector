import datetime

from sqlalchemy.orm import Session

from models.rule import Rule
from models.transaction import Transaction
from models.transaction_rule_history import TransactionRuleHistory
from repositories.repository import Repository


class TransactionRuleHistoryRepository(Repository):
    model = TransactionRuleHistory

    def add(self, transaction: Transaction, run_date: datetime.datetime, rule: Rule, result: bool,
            details: str) -> TransactionRuleHistory:
        trh = TransactionRuleHistory(transaction_id=transaction.transaction_id, run_date=run_date, rule_id=rule.id,
                                     result=result, details=details)
        self.session.add(trh)
        self.session.commit()
        self.session.expunge(trh)
        return trh
