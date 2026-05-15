from sqlalchemy.orm import Session

from models.transaction_type import TransactionType
from repositories.repository import Repository


class TransactionTypeRepository(Repository):
    model = TransactionType


    def add(self, name:str, description:str)->TransactionType:
        tt = TransactionType(name=name, description=description)
        self.session.add(tt)
        self.session.commit()
        self.session.expunge(tt)
        return tt
