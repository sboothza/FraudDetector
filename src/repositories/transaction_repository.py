import datetime

from dependencies import CreateSession
from models.transaction import Transaction
from repositories.currency_repository import CurrencyRepository
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

    def add(self, transaction_id: str, reference: str, amount: float, currency_code: str, debit_credit: str,
            customer_id: int, transaction_type_id: int, transaction_status_id: int) -> Transaction:
        session = CreateSession()
        currency = CurrencyRepository(session).get_by_id(currency_code)
        base_amount = currency.amount_to_base(amount)

        transaction = Transaction(
            transaction_id=transaction_id,
            reference=reference,
            amount=amount,
            base_amount=base_amount,
            currency_code=currency_code,
            debit_credit=debit_credit,
            customer_id=customer_id,
            transaction_type_id=transaction_type_id,
            transaction_status_id=transaction_status_id)

        session.add(transaction)
        session.commit()
        session.expunge(transaction)
        return transaction
