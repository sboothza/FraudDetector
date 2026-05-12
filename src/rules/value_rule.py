from sqlalchemy.orm import Session

from models.customer import Customer
from models.transaction import Transaction
from rules.rule import Rule


class ValueRule(Rule):
    def __init__(self, parameters: dict):
        super().__init__(parameters)
        self.high_value = parameters['high_value']
        self.low_value = parameters['low_value']

    def process_rule(self, session: Session,customer: Customer, customer_transactions:list[Transaction], root_transaction: Transaction) -> tuple[bool, str]:
        result_value: bool = True
        result_text: str = ""

        if root_transaction.base_amount > self.high_value:
            result_value = False
            result_text += f"Transaction amount ({root_transaction.base_amount}) exceeds high limit of ({self.high_value})\r\n"

        if root_transaction.base_amount < self.low_value:
            result_value = False
            result_text += f"Transaction amount ({root_transaction.base_amount}) is lower than low limit of ({self.low_value})\r\n"

        return result_value, result_text
