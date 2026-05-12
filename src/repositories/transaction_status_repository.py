from sqlalchemy.orm import Session

from models.transaction_status import TransactionStatus
from repositories.repository import Repository


class TransactionStatusRepository(Repository):
    model = TransactionStatus


    def add(self, name:str, description:str):
        status = TransactionStatus(name=name, description=description)
        self.session.add(status)