import platform

from app.data.repositories.audit_repository import AuditRepository


class AuditService:
    def __init__(self, session):
        self.repo = AuditRepository(session)

    def log(self, *, user_id: int | None, action: str, details: str = '', entity_type: str = '', entity_id: str = '', status: str = 'success') -> None:
        self.repo.create(
            user_id=user_id,
            action=action,
            action_details=details,
            entity_type=entity_type,
            entity_id=entity_id,
            status=status,
            machine_info=platform.node(),
        )
