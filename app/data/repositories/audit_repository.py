from datetime import datetime

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

    def list_filtered(
        self,
        *,
        user_id: int | None = None,
        action: str = '',
        status: str = '',
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 500,
    ) -> list[AuditLog]:
        stmt = select(AuditLog).order_by(AuditLog.timestamp.desc())
        if user_id is not None:
            stmt = stmt.where(AuditLog.user_id == user_id)
        if action:
            stmt = stmt.where(AuditLog.action.ilike(f'%{action}%'))
        if status:
            stmt = stmt.where(AuditLog.status == status)
        if date_from:
            stmt = stmt.where(AuditLog.timestamp >= date_from)
        if date_to:
            stmt = stmt.where(AuditLog.timestamp <= date_to)
        stmt = stmt.limit(limit)
        return list(self.session.scalars(stmt))
