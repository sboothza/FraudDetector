from models.role import Role
from repositories.repository import Repository


class RoleRepository(Repository):
    model = Role

    def map_names_to_roles(self, roles: list[str]) -> list[Role]:
        return self.session.query(Role).filter(Role.name.in_(roles)).all()

    def add(self, name: str, description: str) -> Role:
        role = Role(name=name, description=description)
        self.session.add(role)
        self.session.commit()
        self.session.expunge(role)
        return role
