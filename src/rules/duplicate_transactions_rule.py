from sqlalchemy.orm import Session

from models.customer import Customer
from models.transaction import Transaction
from repositories.transaction_repository import TransactionRepository
from rules.rule import Rule
from utils import parse_timedelta


class DuplicateTransactionsRule(Rule):
    def __init__(self, id: int, parameters: dict):
        super().__init__(id, parameters)
        self.transaction_window = parse_timedelta(parameters["transaction_window"])

    def process_rule(self, session: Session, customer: Customer, customer_transactions: list[Transaction],
                     root_transaction: Transaction) -> tuple[bool, str]:
        result_value: bool = True
        result_text: str = ""
        min_transaction_date = root_transaction.create_date - self.transaction_window
        transactions = [t for t in customer_transactions if t.create_date >= min_transaction_date]
        trans = next(t for t in transactions if t.base_amount == root_transaction.base_amount)

        if trans:
            result_value = False
            result_text += f"Duplicate transactions for value ({root_transaction.base_amount}) found within window ({self.transaction_window})\r\n)"

        return result_value, result_text
