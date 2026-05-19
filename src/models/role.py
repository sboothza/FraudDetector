from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Role(Base):
    __tablename__ = "role"

    name: Mapped[str] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(nullable=False, default="")
