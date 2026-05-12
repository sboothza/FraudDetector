from sqlalchemy.orm import Mapped, mapped_column
import datetime

from models.base import Base


class Currency(Base):
    __tablename__ = "currency"
    code: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(default="")
    symbol: Mapped[str] = mapped_column(default="")
    exchange_rate: Mapped[float] = mapped_column(default=1, nullable=False)
    is_default: Mapped[bool] = mapped_column(default=False, nullable=False)
    create_date: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now(), nullable=False)
