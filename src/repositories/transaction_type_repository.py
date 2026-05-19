from sqlalchemy.orm import Session

from models.transaction_type import TransactionType
from repositories.Lookup import Lookup
from repositories.repository import Repository


class TransactionTypeRepository(Repository, Lookup):
    model = TransactionType

    def __init__(self, session: Session):
        Repository.__init__(self, session)
        Lookup.__init__(self, self, "name")

    def add(self, name: str, description: str) -> TransactionType:
        tt = TransactionType(name=name, description=description)
        self.session.add(tt)
        self.session.commit()
        self.session.refresh(tt)
        self.session.expunge(tt)
        self._data[tt.name] = tt
        return tt
