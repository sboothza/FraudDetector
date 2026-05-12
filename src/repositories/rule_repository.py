from sqlalchemy.orm import Session

from models.rule import Rule
from repositories.repository import Repository


class RuleRepository(Repository):
    model = Rule


    def get_all(self)->list[Rule]:
        return self.session.query(Rule).filter(Rule.active == True).all()
