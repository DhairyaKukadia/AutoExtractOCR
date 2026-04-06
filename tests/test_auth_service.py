from app.config.constants import Role
from app.data.models import User
from app.services.auth_service import AuthService
from tests.conftest import make_test_session


def test_auth_hash_and_login_updates_last_login():
    session = make_test_session()
    auth = AuthService(session)
    user = User(
        username='alice',
        password_hash=auth.hash_password('Password123'),
        full_name='Alice Smith',
        role=Role.ADMIN,
        is_active=True,
    )
    session.add(user)
    session.commit()

    logged_in = auth.login('alice', 'Password123')
    assert logged_in is not None
    assert logged_in.last_login_at is not None


def test_auth_rejects_inactive_user():
    session = make_test_session()
    auth = AuthService(session)
    user = User(
        username='bob',
        password_hash=auth.hash_password('Password123'),
        full_name='Bob Smith',
        role=Role.OPERATOR,
        is_active=False,
    )
    session.add(user)
    session.commit()

    logged_in = auth.login('bob', 'Password123')
    assert logged_in is None


def test_auth_rejects_wrong_password_without_updating_last_login():
    session = make_test_session()
    auth = AuthService(session)
    user = User(
        username='carol',
        password_hash=auth.hash_password('Password123'),
        full_name='Carol Smith',
        role=Role.OPERATOR,
        is_active=True,
    )
    session.add(user)
    session.commit()

    logged_in = auth.login('carol', 'WrongPassword')
    assert logged_in is None

    refreshed = session.query(User).filter_by(username='carol').one()
    assert refreshed.last_login_at is None
