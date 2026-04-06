from sqlalchemy import select

from app.data.models import FormTemplate


class TemplateRepository:
    def __init__(self, session):
        self.session = session

    def list_active(self) -> list[FormTemplate]:
        stmt = select(FormTemplate).where(FormTemplate.is_active.is_(True)).order_by(FormTemplate.template_name)
        return list(self.session.scalars(stmt))

    def list_active_by_category(self, category: str) -> list[FormTemplate]:
        stmt = (
            select(FormTemplate)
            .where(FormTemplate.is_active.is_(True), FormTemplate.form_category == category)
            .order_by(FormTemplate.template_name)
        )
        return list(self.session.scalars(stmt))

    def get_by_name(self, template_name: str) -> FormTemplate | None:
        return self.session.scalar(select(FormTemplate).where(FormTemplate.template_name == template_name))
