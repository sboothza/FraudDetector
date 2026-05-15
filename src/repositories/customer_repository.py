from dependencies import CreateSession
from models.customer import Customer
from repositories.repository import Repository


class CustomerRepository(Repository):
    model = Customer

    def add(self, first_name: str, last_name: str, email: str, id_number: str, currency_code: str) -> Customer:
        session = CreateSession()
        customer = Customer(first_name=first_name, last_name=last_name, email=email, id_number=id_number,
                            currency_code=currency_code)
        session.add(customer)
        session.commit()
        session.expunge(customer)
        return customer
