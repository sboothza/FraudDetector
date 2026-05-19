from sqlalchemy.orm import Session

from models.customer import Customer
from models.transaction import Transaction
from rules.rule import Rule


class BalanceRule(Rule):

    def process_rule(self, session: Session,customer: Customer, customer_transactions:list[Transaction], root_transaction: Transaction) -> tuple[bool, str]:
        result_value: bool = True
        result_text: str = ""
        balance = customer.base_balance

        if root_transaction.base_amount > balance:
            result_value = False
            result_text += f"Transaction amount ({root_transaction.base_amount}) exceeds customer balance ({balance})\r\n"

        return result_value, result_text