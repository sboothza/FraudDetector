import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from configuration import BATCH_COUNT
from dependencies import get_db, time_window
from exceptions import BadRequestError, NotFoundError
from repositories.transaction_repository import TransactionRepository
from schemas import ApiResponse, ProcessTransactionRequest
from services.transaction_processor import TransactionProcessor

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/transaction", response_model=ApiResponse)
async def process_transaction(
    body: ProcessTransactionRequest,
    session: Session = Depends(get_db),
) -> ApiResponse:
    trans_repo = TransactionRepository(session)
    transaction = trans_repo.get_by_id(body.transaction_id)
    if transaction is None:
        raise NotFoundError(
            f"Transaction {body.transaction_id} not found",
            data={"transaction_id": body.transaction_id},
        )

    if transaction.processed:
        raise BadRequestError(
            "Transaction has already been processed",
            data={"transaction_id": body.transaction_id},
        )

    processor = TransactionProcessor(time_window)
    result, text = processor.process_transaction(transaction, session)
    logger.info(
        "Processed transaction id=%s transaction_id=%s success=%s",
        transaction.id,
        transaction.transaction_id,
        result,
    )
    return ApiResponse(code=200, success=result, message=text)


@router.post("/process_all", response_model=ApiResponse)
async def process_all() -> ApiResponse:
    logger.info("Starting batch processing for up to %s transactions", BATCH_COUNT)
    processor = TransactionProcessor(time_window)
    processor.process_batch(BATCH_COUNT)
    return ApiResponse(
        code=202,
        success=True,
        message="Batch processing started",
    )
