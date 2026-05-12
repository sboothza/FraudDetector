from fastapi import APIRouter

from configuration import BATCH_COUNT
from dependencies import CreateSession, time_window
from models.transaction import Transaction
from schemas import ApiResponse
from services.transaction_processor import TransactionProcessor

router = APIRouter()


@router.post("/transaction", response_model=ApiResponse)
async def process_transaction(transaction: Transaction):
    processor = TransactionProcessor(time_window)
    result, text = processor.process_transaction(transaction)
    response = ApiResponse(success=result, message=text)
    return response


@router.post("/process_all", response_model=ApiResponse)
async def process_all():
    processor = TransactionProcessor(time_window)
    processor.process_batch(BATCH_COUNT)
    response = ApiResponse(success=True, message="Processing batch")
    return response
