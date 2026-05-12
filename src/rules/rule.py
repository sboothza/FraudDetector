from sqlalchemy.orm import Session

from models.customer import Customer
from models.transaction import Transaction


class Rule:
    id: int
    parameters: dict

    def __init__(self, id: int, parameters: dict):
        self.id = id
        self.parameters = parameters

    def process_rule(self, session: Session, customer: Customer, customer_transactions: list[Transaction],
                     root_transaction: Transaction) -> tuple[bool, str]:
        ...
