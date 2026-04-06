from sqlalchemy import func, select

from app.data.models import AuditLog, MedicalRecord, User


class DashboardService:
    def __init__(self, session):
        self.session = session

    def summary(self) -> dict[str, int | list[str]]:
        total_records = self.session.scalar(select(func.count(MedicalRecord.id))) or 0
        pending = self.session.scalar(select(func.count(MedicalRecord.id)).where(MedicalRecord.review_status.in_(['draft', 'extracted', 'reviewed']))) or 0
        approved = self.session.scalar(select(func.count(MedicalRecord.id)).where(MedicalRecord.review_status == 'approved')) or 0
        rejected = self.session.scalar(select(func.count(MedicalRecord.id)).where(MedicalRecord.review_status == 'rejected')) or 0
        total_users = self.session.scalar(select(func.count(User.id))) or 0

        recent_logs = list(
            self.session.scalars(select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(10))
        )
        recent_activity = [f"{log.timestamp}: {log.action} ({log.status})" for log in recent_logs]

        return {
            'total_records': total_records,
            'pending_review': pending,
            'approved': approved,
            'rejected': rejected,
            'total_users': total_users,
            'recent_activity': recent_activity,
        }
