from sqlalchemy.orm import Session

from models.user import User
from repositories.repository import Repository
from repositories.role_repository import RoleRepository
from security import password_hasher


class UserRepository(Repository):
    model = User

    def get_by_username(self, username: str) -> User | None:
        return self.session.query(self.model).filter_by(username=username).first()

    def verify_username_password(self, username: str, password: str) -> User | None:
        user = self.get_by_username(username)
        if user is None or not user.active:
            return None

        if not password_hasher.verify(password, user.password_hash):
            return None

        return user

    def add(self, username: str, password: str, roles: list[str]) -> User | None:
        user = User(username=username, password=password_hasher.hash(password))
        roles_repo = RoleRepository(self.session)
        role_list = roles_repo.map_names_to_roles(roles)
        user.roles.append(role_list)
        self.session.add(user)
