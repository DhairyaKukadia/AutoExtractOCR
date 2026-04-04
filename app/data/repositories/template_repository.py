from sqlalchemy import select

from app.data.models import FormTemplate


class TemplateRepository:
    def __init__(self, session):
        self.session = session

    def list_active(self) -> list[FormTemplate]:
        return list(self.session.scalars(select(FormTemplate).where(FormTemplate.is_active.is_(True))))
