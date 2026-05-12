import datetime

from sqlalchemy.orm import Session

from models.customer import Customer
from models.transaction import Transaction
from repositories.transaction_repository import TransactionRepository
from rules.rule import Rule
from utils import parse_timedelta


class TransactionNumberLimitRule(Rule):
    def __init__(self, parameters: dict):
        super().__init__(parameters)
        self.transaction_count = parameters["transaction_count"]
        self.transaction_delay = parse_timedelta(parameters["transaction_delay"])
        self.transaction_window = parse_timedelta(parameters["transaction_window"])

    def process_rule(self, session: Session, customer: Customer, customer_transactions: list[Transaction],
                     root_transaction: Transaction) -> tuple[bool, str]:
        min_transaction_date = root_transaction.create_date - self.transaction_window
        transactions = [t for t in customer_transactions if t.create_date >= min_transaction_date]
        result_value: bool = True
        result_text: str = ""

        if len(transactions) > self.transaction_count:
            result_value = False
            result_text += f"Too many transactions in the given window ({self.transaction_window}).\r\n)"

        prior_transactions = [
            transaction
            for transaction in transactions
            if transaction.create_date < root_transaction.create_date
        ]
        if prior_transactions:
            prev_transaction = max(prior_transactions, key=lambda transaction: transaction.create_date)
            if root_transaction.create_date - prev_transaction.create_date < self.transaction_delay:
                result_value = False
                result_text += (
                    f"Transaction ({root_transaction.transaction_id}) is too soon after the previous "
                    f"transaction ({prev_transaction.transaction_id}) - ({root_transaction.create_date}) "
                    f"too soon after ({prev_transaction.create_date}) - window ({self.transaction_delay}).\r\n)"
                )

        return result_value, result_text
