from sqlalchemy import select

from app.data.models import User


class UserRepository:
    def __init__(self, session):
        self.session = session

    def get_by_username(self, username: str) -> User | None:
        return self.session.scalar(select(User).where(User.username == username))

    def list_all(self) -> list[User]:
        return list(self.session.scalars(select(User).order_by(User.username)))

    def get_by_id(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def create(self, **kwargs) -> User:
        user = User(**kwargs)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def set_active(self, user_id: int, is_active: bool) -> User | None:
        user = self.get_by_id(user_id)
        if not user:
            return None
        user.is_active = is_active
        self.session.commit()
        self.session.refresh(user)
        return user
