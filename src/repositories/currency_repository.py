from sqlalchemy import update

from models.currency import Currency
from repositories.repository import Repository


class CurrencyRepository(Repository):
    model = Currency
    base_currency: Currency | None = None

    def get_by_id(self, id) -> Currency:
        return self.session.query(Currency).filter_by(code=id).first()

    def get_base_currency(self) -> Currency:
        if not CurrencyRepository.base_currency:
            CurrencyRepository.base_currency = self.session.query(Currency).filter_by(is_default=True).first()

        return CurrencyRepository.base_currency

    def add(self, code: str, name: str, symbol: str, exchange_rate: float, is_default: bool) -> Currency:
        if is_default:
            self.session.execute(
                update(Currency)
                .values(is_default=False)
            )

        currency = Currency(code=code, name=name, symbol=symbol, exchange_rate=exchange_rate, is_default=is_default)
        self.session.add(currency)
        self.session.commit()
        self.session.expunge(currency)
        return currency
