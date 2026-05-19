import datetime

from sqlalchemy.orm import joinedload

from models import Currency, Customer
from models.transaction import Transaction
from repositories.currency_repository import CurrencyRepository
from repositories.customer_repository import CustomerRepository
from repositories.repository import Repository


class TransactionRepository(Repository):
    model = Transaction

    def get_by_customer_id(self, customer_id: int) -> list[Transaction]:
        return (
            self.session.query(Transaction)
            .options(
                joinedload(Transaction.currency),
                joinedload(Transaction.transaction_type),
                joinedload(Transaction.transaction_status),
                joinedload(Transaction.channel),
            )
            .filter(self.model.customer_id == customer_id)
            .order_by(Transaction.create_date.desc())
            .all()
        )

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
            transaction.processed = True

    def add(self, transaction_id: str, reference: str, amount: float, currency_code: str, debit_credit: str,
            customer_id: int, transaction_type_id: int, transaction_status_id: int, channel_id: int) -> Transaction:

        with CustomerRepository(self.session) as customer_repo, CurrencyRepository(self.session) as currency_repo:
            currency: Currency = currency_repo.get_by_name(currency_code)
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
                transaction_status_id=transaction_status_id,
                channel_id=channel_id, )

            customer: Customer = customer_repo.get_by_id(customer_id)
            if debit_credit.lower() == "dr":
                customer.base_balance = customer.base_balance + base_amount
            else:
                customer.base_balance = customer.base_balance - base_amount

            native_currency = currency_repo.get_by_name(currency_code)
            native_amount = native_currency.base_to_amount(customer.base_balance)
            customer.balance = native_amount

            self.session.add(transaction)
            self.session.add(customer)
            self.session.commit()
            self.session.refresh(transaction)
            self.session.expunge(transaction)
            return transaction
