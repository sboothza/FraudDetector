from sqlalchemy.orm import Session

from models.customer import Customer
from repositories.repository import Repository


class CustomerRepository(Repository):
    model = Customer

    # def __init__(self, session: Session):
    #     super().__init__(session)

