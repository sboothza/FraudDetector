import datetime

from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Rule(Base):
    __tablename__ = "rule"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(default="", nullable=False, unique=True)
    description: Mapped[str] = mapped_column(default="", nullable=False)
    type_name: Mapped[str] = mapped_column(default="", nullable=False)
    parameters: Mapped[str] = mapped_column(default="", nullable=False)
    create_date: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now(), nullable=False)
    active: Mapped[bool] = mapped_column(default=True, nullable=False)
