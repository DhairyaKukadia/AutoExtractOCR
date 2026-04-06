from sqlalchemy import func, select

from app.config.constants import ReviewStatus
from app.data.models import MedicalRecord, User


class DashboardService:
    def __init__(self, session):
        self.session = session

    def summary(self) -> dict[str, int]:
        total_records = self.session.scalar(select(func.count(MedicalRecord.id))) or 0
        pending = self.session.scalar(
            select(func.count(MedicalRecord.id)).where(
                MedicalRecord.review_status.in_(
                    [ReviewStatus.DRAFT.value, ReviewStatus.EXTRACTED.value, ReviewStatus.REVIEWED.value]
                )
            )
        ) or 0
        approved = self.session.scalar(
            select(func.count(MedicalRecord.id)).where(MedicalRecord.review_status == ReviewStatus.APPROVED.value)
        ) or 0
        total_users = self.session.scalar(select(func.count(User.id))) or 0
        return {'total_records': total_records, 'pending_review': pending, 'approved': approved, 'total_users': total_users}
