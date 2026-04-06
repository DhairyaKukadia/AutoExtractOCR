from datetime import datetime

from sqlalchemy import and_, func, select

from app.data.models import ExtractedField, MedicalRecord


class RecordRepository:
    def __init__(self, session):
        self.session = session

    def create_record(self, record: MedicalRecord, fields: list[ExtractedField]) -> MedicalRecord:
        self.session.add(record)
        self.session.flush()
        for field in fields:
            field.medical_record_id = record.id
            self.session.add(field)
        self.session.commit()
        self.session.refresh(record)
        return record

    def count_records_for_year(self, year: int) -> int:
        year_start = datetime(year, 1, 1)
        year_end = datetime(year + 1, 1, 1)
        stmt = select(func.count(MedicalRecord.id)).where(and_(MedicalRecord.created_at >= year_start, MedicalRecord.created_at < year_end))
        return self.session.scalar(stmt) or 0

    def list_records(
        self,
        category: str = '',
        status: str = '',
        patient_name: str = '',
        patient_identifier: str = '',
        record_number: str = '',
        limit: int = 50,
        offset: int = 0,
    ) -> list[MedicalRecord]:
        stmt = select(MedicalRecord).order_by(MedicalRecord.created_at.desc())
        if category:
            stmt = stmt.where(MedicalRecord.form_category == category)
        if status:
            stmt = stmt.where(MedicalRecord.review_status == status)
        if patient_name:
            stmt = stmt.where(MedicalRecord.patient_name.ilike(f'%{patient_name}%'))
        if patient_identifier:
            stmt = stmt.where(MedicalRecord.patient_identifier.ilike(f'%{patient_identifier}%'))
        if record_number:
            stmt = stmt.where(MedicalRecord.record_number.ilike(f'%{record_number}%'))
        stmt = stmt.limit(limit).offset(offset)
        return list(self.session.scalars(stmt))

    def count_records(
        self,
        category: str = '',
        status: str = '',
        patient_name: str = '',
        patient_identifier: str = '',
        record_number: str = '',
    ) -> int:
        stmt = select(func.count(MedicalRecord.id))
        if category:
            stmt = stmt.where(MedicalRecord.form_category == category)
        if status:
            stmt = stmt.where(MedicalRecord.review_status == status)
        if patient_name:
            stmt = stmt.where(MedicalRecord.patient_name.ilike(f'%{patient_name}%'))
        if patient_identifier:
            stmt = stmt.where(MedicalRecord.patient_identifier.ilike(f'%{patient_identifier}%'))
        if record_number:
            stmt = stmt.where(MedicalRecord.record_number.ilike(f'%{record_number}%'))
        return self.session.scalar(stmt) or 0

    def get_by_id(self, record_id: int) -> MedicalRecord | None:
        return self.session.get(MedicalRecord, record_id)
