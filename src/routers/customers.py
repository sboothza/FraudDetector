import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import get_current_subject
from dependencies import get_db
from exceptions import NotFoundError
from models.transaction import Transaction
from repositories.customer_repository import CustomerRepository
from repositories.transaction_repository import TransactionRepository
from schemas import ApiResponse, CustomerSummary, CustomerTransactionsData, TransactionSummary

router = APIRouter()
logger = logging.getLogger(__name__)


def _transaction_summary(transaction: Transaction) -> TransactionSummary:
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


@router.get("/{customer_id}/transactions", response_model=ApiResponse)
async def get_customer_transactions(
    customer_id: int,
    _: str = Depends(get_current_subject),
    session: Session = Depends(get_db),
) -> ApiResponse:
    customer_repo = CustomerRepository(session)
    customer = customer_repo.get_by_id(customer_id)
    if customer is None:
        raise NotFoundError(
            f"Customer {customer_id} not found",
            data={"customer_id": customer_id},
        )

    trans_repo = TransactionRepository(session)
    transactions = trans_repo.get_by_customer_id(customer_id)

    data = CustomerTransactionsData(
        customer=CustomerSummary(
            id=customer.id,
            first_name=customer.first_name,
            last_name=customer.last_name,
            email=customer.email,
            id_number=customer.id_number,
            balance=customer.balance,
            currency_code=customer.currency_code,
            base_balance=customer.base_balance,
        ),
        transactions=[_transaction_summary(transaction) for transaction in transactions],
        transaction_count=len(transactions),
    )

    logger.info(
        "Retrieved %s transactions for customer id=%s",
        len(transactions),
        customer_id,
    )

    return ApiResponse(
        code=200,
        message="Customer transactions retrieved",
        success=True,
        data=data.model_dump(),
    )
