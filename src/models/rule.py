import datetime
import json

from sqlalchemy.orm import Mapped, mapped_column

from exceptions import BadRequestError
from models.base import Base
from rules.rule import Rule as RuleObj
from utils import resolve_type


class Rule(Base):
    __tablename__ = "rule"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(default="", nullable=False, unique=True)
    description: Mapped[str] = mapped_column(default="", nullable=False)
    type_name: Mapped[str] = mapped_column(default="", nullable=False)
    parameters: Mapped[str] = mapped_column(default="", nullable=False)
    create_date: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now(), nullable=False)
    active: Mapped[bool] = mapped_column(default=True, nullable=False)

    def get_rule(self) -> RuleObj:
        try:
            rule_type = resolve_type(self.type_name)
            parameters = json.loads(self.parameters) if self.parameters else {}
            if not isinstance(parameters, dict):
                raise ValueError("parameters must be a JSON object")
            return rule_type(self.id, parameters)
        except BadRequestError:
            raise
        except (ValueError, TypeError, ImportError, json.JSONDecodeError) as exc:
            raise BadRequestError(
                f"Invalid rule configuration for rule id {self.id}: {exc}",
                data={"rule_id": self.id, "type_name": self.type_name},
            ) from exc
