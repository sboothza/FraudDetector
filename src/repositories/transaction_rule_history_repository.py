import datetime

from sqlalchemy.orm import Session

from models.rule import Rule
from models.transaction import Transaction
from models.transaction_rule_history import TransactionRuleHistory
from repositories.repository import Repository


class TransactionRuleHistoryRepository(Repository):
    model = TransactionRuleHistory

    def add(self, transaction: Transaction, run_date: datetime.datetime, rule: Rule, result: bool,
        details: str):
        """ Add a new transaction rule history entry.
            Doesn't commit the session, so the caller must commit the session.
        Args:
            transaction: The transaction to add the rule history entry for
            run_date: The date and time the rule was run
            rule: The rule that was run
            result: The result of the rule
            details: The details of the rule
        """
        trh = TransactionRuleHistory(transaction_id=transaction.id, run_date=run_date, rule_id=rule.id,
                                     result=result, details=details)
        self.session.add(trh)        
