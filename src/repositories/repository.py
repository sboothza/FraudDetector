from typing import TypeVar, Generic

from sqlalchemy.orm import Session

from models.base import Base

T = TypeVar("T", bound=Base)


class Repository(Generic[T]):
    model: type[T]
    session: Session

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, id) -> T | None:
        return self.session.query(self.model).filter_by(id=id).first()
