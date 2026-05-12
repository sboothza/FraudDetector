from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.user import User


class Role(Base):
    __tablename__ = "role"

    name: Mapped[str] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(nullable=False, default="")
    users: Mapped[list["User"]] = relationship(
        secondary="user_role",
        back_populates="roles",
    )
