from dependencies import CreateSession
from repositories.channel_repository import ChannelRepository
from repositories.currency_repository import CurrencyRepository
from repositories.customer_repository import CustomerRepository
from repositories.role_repository import RoleRepository
from repositories.transaction_status_repository import TransactionStatusRepository
from repositories.transaction_type_repository import TransactionTypeRepository
from repositories.user_repository import UserRepository


def seed():
    session = CreateSession()

    with RoleRepository(session) as roles_repo:
        roles_repo.add("admin", "Administrator")
        roles_repo.add("user", "User")

    with UserRepository(session) as user_repository:
        user_repository.add("admin", "admin", ["admin"])
        user_repository.add("stephen", "stephen", ["user"])

    with TransactionStatusRepository(session) as trans_status_repo:
        trans_status_repo.add("pending", "Pending")
        trans_status_repo.add("authorized", "Authorized")
        trans_status_repo.add("posted", "Posted")
        trans_status_repo.add("failed", "Failed")
        trans_status_repo.add("rejected", "Rejected")
        trans_status_repo.add("reversed", "Reversed")
        trans_status_repo.add("disputed", "Disputed")

    with TransactionTypeRepository(session) as trans_type_repo:
        trans_type_repo.add("payment", "Payment")
        trans_status_repo.add("refund", "Refund")
        trans_status_repo.add("transfer", "Transfer")
        trans_status_repo.add("withdrawal", "Withdrawal")
        trans_status_repo.add("fee", "Fee")
        trans_status_repo.add("chargeback", "Chargeback")

    with ChannelRepository(session) as channel_repo:
        channel_repo.add("debitcard", "DebitCard")
        channel_repo.add("creditcard", "CreditCard")
        channel_repo.add("wire", "Wire")
        channel_repo.add("mobile", "Mobile")
        channel_repo.add("atm", "ATM")
        channel_repo.add("internaltransfer", "InternalTransfer")

    with CurrencyRepository(session) as currency_repo:
        currency_repo.add("zar", "South African Rand", "R", 1, True)
        currency_repo.add("usd", "United States Dollar", "$", 16.52, False)
        currency_repo.add("eur", "Euro", "E", 19.4, False)
        currency_repo.add("yen", "Yen", "Y", 0.1, False)

    with CustomerRepository(session) as customer_repo:
        customer_repo.add("Stephen", "Booth", "stephen@email", "740315", "zar")
        customer_repo.add("Tamrin", "Booth", "tamrin@email", "800315", "usd")

if __name__ == "__main__":
    seed()