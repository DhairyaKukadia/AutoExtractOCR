from app.config.constants import Role
from app.data.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.utils.validators import min_length, required


class UserService:
    def __init__(self, session):
        self.repo = UserRepository(session)
        self.auth = AuthService(session)

    def create_user(self, username: str, password: str, full_name: str, role: str, is_active: bool = True):
        required(username, 'Username')
        required(password, 'Password')
        required(full_name, 'Full name')
        min_length(password, 8, 'Password')
        if role not in {Role.ADMIN, Role.OPERATOR}:
            raise ValueError('Invalid role')
        if self.repo.get_by_username(username):
            raise ValueError('Username already exists')
        return self.repo.create(
            username=username,
            password_hash=self.auth.hash_password(password),
            full_name=full_name,
            role=role,
            is_active=is_active,
        )

    def set_user_active(self, user_id: int, is_active: bool):
        user = self.repo.set_active(user_id, is_active)
        if not user:
            raise ValueError('User not found')
        return user

    def list_users(self):
        return self.repo.list_all()
