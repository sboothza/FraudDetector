from dependencies import CreateSession
from models.customer import Customer
from repositories.currency_repository import CurrencyRepository
from repositories.repository import Repository


class CustomerRepository(Repository):
    model = Customer

    def add(self, first_name: str, last_name: str, email: str, id_number: str, currency_code: str, balance:float) -> Customer:
        with CurrencyRepository(self.session) as currency_repo:
            currency = currency_repo.get_by_name(currency_code)
            base_amount = currency.amount_to_base(balance)
            customer = Customer(first_name=first_name, last_name=last_name, email=email, id_number=id_number,
                                currency_code=currency_code, balance=balance, base_balance=base_amount)
            self.session.add(customer)
            self.session.commit()
            self.session.refresh(customer)
            self.session.expunge(customer)
            return customer
