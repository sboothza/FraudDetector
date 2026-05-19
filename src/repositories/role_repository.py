from sqlalchemy.orm import Session

from models.role import Role
from repositories.Lookup import Lookup
from repositories.repository import Repository


class RoleRepository(Repository, Lookup):
    model = Role

    def __init__(self, session: Session):
        Repository.__init__(self, session)
        Lookup.__init__(self, self, "name")

    def map_names_to_roles(self, roles: list[str]) -> list[Role]:
        return self.session.query(Role).filter(Role.name.in_(roles)).all()

    def add(self, name: str, description: str) -> Role:
        role = Role(name=name, description=description)
        self.session.add(role)
        self.session.commit()
        self.session.refresh(role)
        self.session.expunge(role)
        self._data[role.name] = role
        return role
