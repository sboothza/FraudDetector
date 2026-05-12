from sqlalchemy.orm import Session

from models.role import Role
from repositories.repository import Repository


class RoleRepository(Repository):
    model = Role


    def map_names_to_roles(self, roles:list[str])->list[Role]:
        return self.session.query(Role).filter(Role.name.in_(roles)).all()

    def add(self, name:str, description:str):
        role = Role(name=name, description=description)
        self.session.add(role)

