import datetime

from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class TransactionType(Base):
    __tablename__ = "transaction_type"

    id:Mapped[int]=mapped_column(primary_key=True, autoincrement=True)
    name:Mapped[str]=mapped_column(default="", nullable=False)
    description:Mapped[str]=mapped_column(default="", nullable=False)
    active:Mapped[bool]=mapped_column(default=True, nullable=False)
    create_date:Mapped[datetime.datetime]=mapped_column(default=datetime.datetime.now(), nullable=False)