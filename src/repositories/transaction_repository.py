import datetime

from sqlalchemy.orm import Session

from models.transaction import Transaction
from repositories.repository import Repository


class TransactionRepository(Repository):
    model = Transaction


    def get_for_customer_timerange(
            self,
            customer_id: int,
            min_transaction_date: datetime.datetime,
    ) -> list[Transaction]:
        return self.session.query(Transaction).filter(self.model.customer_id == customer_id,
                                                      self.model.create_date >= min_transaction_date, ).all()

    def flag_as_processed(self, transaction: Transaction):
        transaction.processed = True

    def get_unprocessed_transactions(self, count: int) -> list[Transaction]:
        return self.session.query(Transaction).filter(Transaction.processed == False).limit(count).all()

    def flag_all_as_processed(self, transactions: list[Transaction]):
        for transaction in transactions:
            transaction.is_processed = True

