from app.config.constants import FORM_CATEGORIES, Role
from app.data.models import FormTemplate
from app.data.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService


def seed_data(session) -> None:
    user_repo = UserRepository(session)
    auth = AuthService(session)

    if not user_repo.get_by_username('admin'):
        user_repo.create(
            username='admin',
            password_hash=auth.hash_password('Admin@123'),
            full_name='System Administrator',
            role=Role.ADMIN,
            is_active=True,
        )

    if not user_repo.get_by_username('operator'):
        user_repo.create(
            username='operator',
            password_hash=auth.hash_password('Operator@123'),
            full_name='Default Operator',
            role=Role.OPERATOR,
            is_active=True,
        )

    if not user_repo.get_by_username('reviewer'):
        user_repo.create(
            username='reviewer',
            password_hash=auth.hash_password('Reviewer@123'),
            full_name='Default Reviewer',
            role=Role.REVIEWER,
            is_active=True,
        )

    if not session.query(FormTemplate).first():
        for category in FORM_CATEGORIES:
            session.add(
                FormTemplate(
                    template_name=f'{category} Default Template',
                    description=f'Baseline template for {category}',
                    form_category=category,
                    version='1.0',
                    is_active=True,
                )
            )
        session.commit()
