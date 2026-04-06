from datetime import datetime

from passlib.context import CryptContext

from app.data.repositories.user_repository import UserRepository

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class AuthService:
    def __init__(self, session):
        self.session = session
        self.user_repo = UserRepository(session)

    def verify_password(self, plain_password: str, password_hash: str) -> bool:
        return pwd_context.verify(plain_password, password_hash)

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def login(self, username: str, password: str):
        user = self.user_repo.get_by_username(username)
        if not user or not user.is_active:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        user.last_login_at = datetime.utcnow()
        self.session.commit()
        return user
