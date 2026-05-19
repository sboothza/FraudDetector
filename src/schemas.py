from typing import Any

from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    code: int = 200
    message: str
    success: bool = True
    data: dict[str, Any] = Field(default_factory=dict)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProcessTransactionRequest(BaseModel):
    transaction_id: int


class TransactionSummary(BaseModel):
    id: int
    transaction_id: str
    reference: str
    create_date: str
    amount: float
    currency_code: str
    base_amount: float
    debit_credit: str
    processed: bool
    transaction_type: str
    transaction_status: str
    channel: str


class CustomerSummary(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    id_number: str
    balance: float
    currency_code: str
    base_balance: float


class CustomerTransactionsData(BaseModel):
    customer: CustomerSummary
    transactions: list[TransactionSummary]
    transaction_count: int

