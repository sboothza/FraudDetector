from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.currency import Currency


class Customer(Base):
    __tablename__ = "customer"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    first_name: Mapped[str] = mapped_column(default="", nullable=False)
    last_name: Mapped[str] = mapped_column(default="", nullable=False)
    email: Mapped[str] = mapped_column(default="", nullable=False)
    id_number: Mapped[str] = mapped_column(default="", nullable=False, unique=True, index=True)
    balance: Mapped[float] = mapped_column(default=0, nullable=False)
    currency_code: Mapped[str] = mapped_column(ForeignKey("currency.code"), default="", nullable=False)
    currency: Mapped[Currency] = relationship(back_populates="customer")
    base_balance: Mapped[float] = mapped_column(default=0, nullable=False)

