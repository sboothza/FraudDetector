import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import RequireUser
from converters import to_customer_summary, to_transaction_summary
from dependencies import get_db
from exceptions import NotFoundError
from repositories.customer_repository import CustomerRepository
from repositories.transaction_repository import TransactionRepository
from schemas import ApiResponse, CustomerTransactionsData

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{customer_id}/transactions", response_model=ApiResponse)
async def get_customer_transactions(
    customer_id: int,
    _: RequireUser,
    session: Session = Depends(get_db),
) -> ApiResponse:
    customer_repo = CustomerRepository(session)
    customer = customer_repo.get_by_id(customer_id)
    if customer is None:
        raise NotFoundError(
            f"Customer {customer_id} not found",
            data={"customer_id": customer_id},
        )

    transactions = TransactionRepository(session).get_by_customer_id(customer_id)
    logger.info(
        "Retrieved %s transactions for customer id=%s",
        len(transactions),
        customer_id,
    )

    return ApiResponse(
        code=200,
        message="Customer transactions retrieved",
        success=True,
        data=CustomerTransactionsData(
            customer=to_customer_summary(customer),
            transactions=[to_transaction_summary(t) for t in transactions],
            transaction_count=len(transactions),
        ).model_dump(),
    )
