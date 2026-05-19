from sqlalchemy.orm import Session

from models.transaction_status import TransactionStatus
from repositories.Lookup import Lookup
from repositories.repository import Repository


class TransactionStatusRepository(Repository, Lookup):
    model = TransactionStatus

    def __init__(self, session: Session):
        Repository.__init__(self, session)
        Lookup.__init__(self, self, "name")

    def add(self, name: str, description: str) -> TransactionStatus:
        status = TransactionStatus(name=name, description=description)
        self.session.add(status)
        self.session.commit()
        self.session.refresh(status)
        self.session.expunge(status)
        self._data[status.name] = status
        return status
