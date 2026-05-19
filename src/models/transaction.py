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
    from models.transaction_rule_history import TransactionRuleHistory
    from models.channel import Channel


class Transaction(Base):
    __tablename__ = "transaction"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    transaction_id: Mapped[str] = mapped_column(nullable=False, default="")
    reference: Mapped[str] = mapped_column(nullable=False, default="")
    create_date: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now(), nullable=False)
    amount: Mapped[float] = mapped_column(default=0, nullable=False)
    currency_code: Mapped[str] = mapped_column(ForeignKey("currency.code"), nullable=False)
    currency: Mapped["Currency"] = relationship()
    base_amount: Mapped[float] = mapped_column(default=0, nullable=False)
    debit_credit: Mapped[str] = mapped_column(default="DR", nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"), default=0, nullable=False)
    customer: Mapped["Customer"] = relationship(back_populates="transactions")
    transaction_type_id: Mapped[int] = mapped_column(ForeignKey("transaction_type.id"), default=0, nullable=False)
    transaction_type: Mapped["TransactionType"] = relationship()
    transaction_status_id: Mapped[int] = mapped_column(ForeignKey("transaction_status.id"), default=0, nullable=False)
    transaction_status: Mapped["TransactionStatus"] = relationship()
    channel_id: Mapped[int] = mapped_column(ForeignKey("channel.id"), nullable=False)
    channel: Mapped["Channel"] = relationship()
    processed:Mapped[bool] = mapped_column(default=False, nullable=False)
    transaction_rule_history: Mapped[list["TransactionRuleHistory"]] = relationship(back_populates="transaction")
