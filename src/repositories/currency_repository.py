from sqlalchemy import update
from sqlalchemy.orm import Session

from models.currency import Currency
from repositories.Lookup import Lookup
from repositories.repository import Repository


class CurrencyRepository(Repository, Lookup):
    model = Currency
    base_currency: Currency | None = None

    def __init__(self, session: Session):
        Repository.__init__(self, session)
        Lookup.__init__(self, self, "code")

    def get_by_id(self, id) -> Currency:
        return self.session.query(Currency).filter_by(code=id).first()

    def get_base_currency(self) -> Currency:
        if not CurrencyRepository.base_currency:
            base = next(c for c in self._data.values() if c.is_default)
            CurrencyRepository.base_currency = base

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
        self.session.refresh(currency)
        self.session.expunge(currency)
        self._data[currency.code] = currency
        return currency
