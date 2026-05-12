from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import datetime

from models.base import Base


if TYPE_CHECKING:
    from models.customer import Customer
    from models.currency import Currency
    from models.transaction_type import TransactionType
    from models.transaction_status import TransactionStatus


class Transaction(Base):
    __tablename__ = "transaction"

    id: Mapped[int] = mapped_column(primary_key=True, auto_increment=True)
    transaction_id: Mapped[str] = mapped_column(nullable=False, default="")
    reference: Mapped[str] = mapped_column(nullable=False, default="")
    create_date: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now(), nullable=False)
    amount: Mapped[float] = mapped_column(default=0, nullable=False)
    currency_code: Mapped[str] = mapped_column(ForeignKey("currency.code"), nullable=False)
    currency:Mapped["Currency"] = relationship(back_populates="transaction")
    base_amount: Mapped[float] = mapped_column(default=0, nullable=False)
    debit_credit: Mapped[str] = mapped_column(default="DR", nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"), default=0, nullable=False)
    customer: Mapped["Customer"] = relationship(back_populates="transaction")
    transaction_type_id: Mapped[int] = mapped_column(ForeignKey("transaction_type.id"), default=0, nullable=False)
    transaction_type: Mapped["TransactionType"] = relationship(back_populates="transaction")
    transaction_status_id: Mapped[int] = mapped_column(ForeignKey("transaction_status.id"), default=0, nullable=False)
    transaction_status: Mapped["TransactionStatus"] = relationship(back_populates="transaction")
    processed:Mapped[bool] = mapped_column(default=False, nullable=False)
