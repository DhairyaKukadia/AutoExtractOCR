from sqlalchemy import select

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

    def list_records(
        self,
        category: str = '',
        status: str = '',
        patient_name: str = '',
        patient_identifier: str = '',
        record_number: str = '',
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
        return list(self.session.scalars(stmt))

    def get_by_id(self, record_id: int) -> MedicalRecord | None:
        return self.session.get(MedicalRecord, record_id)
