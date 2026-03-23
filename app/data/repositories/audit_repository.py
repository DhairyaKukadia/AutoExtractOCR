from sqlalchemy import select

from app.data.models import AuditLog


class AuditRepository:
    def __init__(self, session):
        self.session = session

    def create(self, **kwargs) -> AuditLog:
        log = AuditLog(**kwargs)
        self.session.add(log)
        self.session.commit()
        self.session.refresh(log)
        return log

    def list_recent(self, limit: int = 200) -> list[AuditLog]:
        stmt = select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit)
        return list(self.session.scalars(stmt))
