from dependencies import CreateSession, engine
from models import Base
from repositories.channel_repository import ChannelRepository
from repositories.currency_repository import CurrencyRepository
from repositories.customer_repository import CustomerRepository
from repositories.role_repository import RoleRepository
from repositories.rule_repository import RuleRepository
from repositories.transaction_repository import TransactionRepository
from repositories.transaction_status_repository import TransactionStatusRepository
from repositories.transaction_type_repository import TransactionTypeRepository
from repositories.user_repository import UserRepository


def seed():
    session = CreateSession()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with (RoleRepository(session) as roles_repo, TransactionStatusRepository(session) as trans_status_repo,
          TransactionTypeRepository(session) as trans_type_repo, ChannelRepository(session) as channel_repo,
          CurrencyRepository(session) as currency_repo):
        roles_repo.add("admin", "Administrator")
        roles_repo.add("user", "User")

        with UserRepository(session) as user_repository:
            user_repository.add("admin", "admin", ["admin"])
            user_repository.add("stephen", "stephen", ["admin", "user"])
            user_repository.add("tamrin", "tamrin", ["user"])

        trans_status_repo.add("pending", "Pending")
        trans_status_repo.add("authorized", "Authorized")
        trans_status_repo.add("posted", "Posted")
        trans_status_repo.add("failed", "Failed")
        trans_status_repo.add("rejected", "Rejected")
        trans_status_repo.add("reversed", "Reversed")
        trans_status_repo.add("disputed", "Disputed")

        trans_type_repo.add("payment", "Payment")
        trans_type_repo.add("refund", "Refund")
        trans_type_repo.add("transfer", "Transfer")
        trans_type_repo.add("withdrawal", "Withdrawal")
        trans_type_repo.add("fee", "Fee")
        trans_type_repo.add("chargeback", "Chargeback")

        channel_repo.add("debitcard", "DebitCard")
        channel_repo.add("creditcard", "CreditCard")
        channel_repo.add("wire", "Wire")
        channel_repo.add("mobile", "Mobile")
        channel_repo.add("atm", "ATM")
        channel_repo.add("internaltransfer", "InternalTransfer")

        currency_repo.add("zar", "South African Rand", "R", 1, True)
        currency_repo.add("usd", "United States Dollar", "$", 16.52, False)
        currency_repo.add("eur", "Euro", "E", 19.4, False)
        currency_repo.add("yen", "Yen", "Y", 0.1, False)

        with CustomerRepository(session) as customer_repo, TransactionRepository(session) as trans_repo:
            bank = customer_repo.add("Bank", "", "bank@email", "00000", "zar", 100000)

            stephen = customer_repo.add("Stephen", "Booth", "stephen@email", "740315", "zar", 1000)
            trans_repo.add("123", "123", 100, "zar", "DR", stephen.id, trans_type_repo.get_by_name("payment").id,
                        trans_status_repo.get_by_name("posted").id, channel_repo.get_by_name("internaltransfer").id)
            trans_repo.add("123", "123", 100, "zar", "CR", bank.id, trans_type_repo.get_by_name("payment").id,
                        trans_status_repo.get_by_name("posted").id, channel_repo.get_by_name("internaltransfer").id)

            trans_repo.add("456", "456", 100, "zar", "DR", stephen.id, trans_type_repo.get_by_name("payment").id,
                        trans_status_repo.get_by_name("posted").id, channel_repo.get_by_name("internaltransfer").id)
            trans_repo.add("456", "456", 100, "zar", "CR", bank.id, trans_type_repo.get_by_name("payment").id,
                        trans_status_repo.get_by_name("posted").id, channel_repo.get_by_name("internaltransfer").id)

            tamrin = customer_repo.add("Tamrin", "Booth", "tamrin@email", "800315", "usd", 500)
            trans_repo.add("321", "321", 100, "zar", "DR", tamrin.id, trans_type_repo.get_by_name("payment").id,
                        trans_status_repo.get_by_name("posted").id, channel_repo.get_by_name("internaltransfer").id)
            trans_repo.add("321", "321", 100, "zar", "CR", bank.id, trans_type_repo.get_by_name("payment").id,
                        trans_status_repo.get_by_name("posted").id, channel_repo.get_by_name("internaltransfer").id)

            trans_repo.add("654", "654", 100, "zar", "DR", tamrin.id, trans_type_repo.get_by_name("payment").id,
                        trans_status_repo.get_by_name("posted").id, channel_repo.get_by_name("internaltransfer").id)
            trans_repo.add("654", "654", 100, "zar", "CR", bank.id, trans_type_repo.get_by_name("payment").id,
                        trans_status_repo.get_by_name("posted").id, channel_repo.get_by_name("internaltransfer").id)

        with RuleRepository(session) as rule_repo:
            rule_repo.add("Balance", "Balance Rule", "rules.balance_rule.BalanceRule", {})
            rule_repo.add("DuplicateTransaction", "Duplicate Transaction Rule", "rules.duplicate_transactions_rule.DuplicateTransactionsRule",
                        {"transaction_window": "1d"})
            rule_repo.add("Value", "Value Rule", "rules.value_rule.ValueRule", {"high_value": 10000, "low_value": 10})
            rule_repo.add("TransactionNumberLimit", "TransactionNumberLimitRule Rule", "rules.transaction_number_limit_rule.TransactionNumberLimitRule",
                        {"transaction_count": 3, "transaction_delay": "1s", "transaction_window": "1h"})

    session.commit()
    session.close()

if __name__ == "__main__":
    seed()
