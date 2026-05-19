import json

from sqlalchemy.orm import Session

from dependencies import CreateSession
from models.rule import Rule
from repositories.repository import Repository


class RuleRepository(Repository):
    model = Rule

    def get_all(self) -> list[Rule]:
        return self.session.query(Rule).filter(Rule.active == True).all()

    def add(self, name: str, description: str, type_name: str, parameters: dict) -> Rule:
        rule = Rule(name=name, description=description, type_name=type_name, parameters=json.dumps(parameters))
        self.session.add(rule)
        self.session.commit()
        self.session.refresh(rule)
        self.session.expunge(rule)
        return rule
