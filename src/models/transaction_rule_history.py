from typing import TYPE_CHECKING

import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.transaction import Transaction
    from models.rule import Rule


class TransactionRuleHistory(Base):
    __tablename__ = "transaction_rule_history"

    id: Mapped[int] = mapped_column(primary_key=True, auto_increment=True)
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transaction.id"), nullable=False)
    transaction: Mapped["Transaction"] = relationship(back_populates="transaction_rule_history")
    run_date: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now(), nullable=False)
    rule_id: Mapped[int] = mapped_column(ForeignKey("rule.id"), nullable=False)
    rule: Mapped["Rule"] = relationship(back_populates="transaction_rule_history")
    result: Mapped[bool] = mapped_column(default=False, nullable=False)
    details: Mapped[str] = mapped_column(default="", nullable=False)
