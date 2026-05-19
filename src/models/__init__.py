"""Import all models so association tables and mappers are registered."""

from models.base import Base
from models.channel import Channel
from models.currency import Currency
from models.customer import Customer
from models.role import Role
from models.rule import Rule
from models.transaction import Transaction
from models.transaction_rule_history import TransactionRuleHistory
from models.transaction_status import TransactionStatus
from models.transaction_type import TransactionType
from models.user import User
from models.user_role import UserRole

__all__ = [
    "Base",
    "Channel",
    "Currency",
    "Customer",
    "Role",
    "Rule",
    "Transaction",
    "TransactionRuleHistory",
    "TransactionStatus",
    "TransactionType",
    "User",
    "UserRole",
]
