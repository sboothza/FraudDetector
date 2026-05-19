from typing import TYPE_CHECKING
import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.user_role import UserRole

if TYPE_CHECKING:
    from models.role import Role


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    active: Mapped[bool] = mapped_column(default=True, nullable=False)
    create_date: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now(), nullable=False)
    roles: Mapped[list["Role"]] = relationship(secondary=UserRole.__table__)
