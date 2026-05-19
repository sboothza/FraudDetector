from models.customer import Customer
from models.transaction import Transaction
from schemas import CustomerSummary, TransactionSummary


def to_customer_summary(customer: Customer) -> CustomerSummary:
    return CustomerSummary(
        id=customer.id,
        first_name=customer.first_name,
        last_name=customer.last_name,
        email=customer.email,
        id_number=customer.id_number,
        balance=customer.balance,
        currency_code=customer.currency_code,
        base_balance=customer.base_balance,
    )


def to_transaction_summary(transaction: Transaction) -> TransactionSummary:
    return TransactionSummary(
        id=transaction.id,
        transaction_id=transaction.transaction_id,
        reference=transaction.reference,
        create_date=transaction.create_date.isoformat(),
        amount=transaction.amount,
        currency_code=transaction.currency_code,
        base_amount=transaction.base_amount,
        debit_credit=transaction.debit_credit,
        processed=transaction.processed,
        transaction_type=transaction.transaction_type.name,
        transaction_status=transaction.transaction_status.name,
        channel=transaction.channel.name,
    )
